import asyncio
from scraper import VeoScraper

async def run_test():
    scraper = VeoScraper()
    
    prompts = [
        ("A futuristic car driving through a neon city", "VIDEO_ASPECT_RATIO_LANDSCAPE"),
        ("A beautiful waterfall in a tropical jungle", "VIDEO_ASPECT_RATIO_PORTRAIT")
    ]
    
    for prompt, ratio in prompts:
        print(f"\n--- Testing Mode: {ratio} ---")
        try:
            result = await scraper.generate_video(prompt, aspect_ratio=ratio)
            print(f"SUCCESS: {result}")
        except Exception as e:
            print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
