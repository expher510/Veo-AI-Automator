import asyncio
import logging
import os
import sys
import requests
from playwright.async_api import async_playwright
from playwright_stealth import stealth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VeoScraper:
    def __init__(self):
        self.url = "https://veoaifree.com/veo-video-generator/"

    @staticmethod
    def _normalize_video_url(url: str | None) -> str | None:
        if not url:
            return None
        # Some AJAX responses return /videos/uploads/ (404) while actual file lives under /video/uploads/.
        return url.replace("/videos/uploads/", "/video/uploads/")

    async def generate_video(self, prompt: str, aspect_ratio: str = "VIDEO_ASPECT_RATIO_LANDSCAPE"):
        async with async_playwright() as p:
            # We don't use a fixed proxy here as GitHub provides fresh IPs
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            
            await context.add_cookies([
                {"name": "ytHide", "value": "1", "domain": "veoaifree.com", "path": "/"},
                {"name": "ytPopup", "value": "1", "domain": "veoaifree.com", "path": "/"}
            ])

            page = await context.new_page()
            # await stealth(page) 
            
            logger.info(f"Navigating to {self.url}")
            await page.goto(self.url, wait_until="networkidle")

            logger.info("Opening settings menu")
            try:
                await page.click(".header_top svg.svg-setting", timeout=10000)
            except:
                await page.evaluate('document.querySelector(".header_top svg.svg-setting").click()')

            logger.info(f"Selecting aspect ratio: {aspect_ratio}")
            await page.locator("#aspect-ration").first.select_option(value=aspect_ratio, force=True)

            logger.info(f"Entering prompt: {prompt}")
            await page.locator("#fn__include_textarea").first.fill(prompt, force=True)

            video_url = None
            async def handle_response(response):
                nonlocal video_url
                if "admin-ajax.php" in response.url:
                    try:
                        data = await response.json()
                        if data and isinstance(data, dict):
                            if "data" in data and "url" in data["data"]:
                                video_url = self._normalize_video_url(data["data"]["url"])
                            elif "url" in data:
                                video_url = self._normalize_video_url(data["url"])
                    except: pass

            page.on("response", handle_response)
            await page.click("#generate_it")

            logger.info("Waiting for video generation...")
            max_wait = int(os.getenv("MAX_WAIT_SECONDS", "360"))
            elapsed = 0
            while elapsed < max_wait:
                if video_url: break
                video_element = await page.query_selector("video")
                if video_element:
                    video_url = self._normalize_video_url(await video_element.get_attribute("src"))
                    if video_url and not video_url.startswith("blob:"):
                        break
                
                download_link = await page.query_selector("a.only-video-download")
                if download_link:
                    video_url = self._normalize_video_url(await download_link.get_attribute("href"))
                    if video_url: break
                
                # Check for rate limit error
                error_msg = await page.evaluate('''() => {
                    const el = document.querySelector(".error, .alert-danger");
                    return el ? el.innerText : null;
                }''')
                if error_msg:
                    logger.error(f"Site error detected: {error_msg}")
                    await page.screenshot(path="error.png")
                    break

                await asyncio.sleep(5)
                elapsed += 5
            
            if not video_url:
                await page.screenshot(path="timeout.png")
                logger.error("Video URL not found within timeout.")

            await browser.close()
            return video_url

def send_webhook(webhook_url, data):
    try:
        requests.post(webhook_url, json=data)
        logger.info(f"Webhook sent successfully to {webhook_url}")
    except Exception as e:
        logger.error(f"Failed to send webhook: {e}")

if __name__ == "__main__":
    # Get inputs from environment variables (GitHub Actions style)
    prompt = os.getenv("VIDEO_PROMPT", "A beautiful sunrise over the ocean")
    aspect_ratio = os.getenv("VIDEO_ASPECT_RATIO", "VIDEO_ASPECT_RATIO_LANDSCAPE")
    webhook_url = os.getenv("WEBHOOK_URL")
    job_id = os.getenv("JOB_ID")

    logger.info(f"Starting generation for: {prompt} ({aspect_ratio})")
    
    video_link = asyncio.run(VeoScraper().generate_video(prompt, aspect_ratio))
    
    if video_link:
        print(f"::set-output name=video_url::{video_link}") # GitHub Actions output
        logger.info(f"SUCCESS: {video_link}")
        
        if webhook_url:
            send_webhook(webhook_url, {
                "status": "success",
                "prompt": prompt,
                "video_url": video_link,
                "job_id": job_id
            })
    else:
        logger.error("Failed to generate video.")
        if webhook_url:
            send_webhook(webhook_url, {"status": "failed", "prompt": prompt, "job_id": job_id})
        sys.exit(1)
