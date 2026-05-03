# Veo AI Automator 🎬🤖

[![GitHub Actions Status](https://img.shields.io/badge/GitHub%20Actions-Active-success.svg)](https://github.com/features/actions)
[![Playwright](https://img.shields.io/badge/Playwright-Enabled-blue.svg)](https://playwright.dev/)
[![Python 3.10](https://img.shields.io/badge/Python-3.10-yellow.svg)](https://www.python.org/)

**Veo AI Automator** is a serverless, highly-efficient automation tool that transforms the [Veo AI Video Generator](https://veoaifree.com/veo-video-generator/) into a reliable API using **Playwright** and **GitHub Actions**.

By running on GitHub Actions, this project elegantly bypasses IP-based rate limits (6 videos/hour), providing you with unlimited AI video generation capabilities that can be integrated into your own workflows (like n8n, Make, or custom apps) via Webhooks.

---

## 🌟 Key Features

- **Unlimited Generations**: Utilizes GitHub Actions' rotating IP pool to bypass rate limits naturally.
- **Aspect Ratio Control**: Fully supports generating videos in both Landscape (16:9) and Portrait (9:16).
- **Asynchronous Webhook Delivery**: Fire-and-forget API calls. The system will automatically `POST` the final `.mp4` URL to your webhook once generation is complete.
- **Stealth Mode**: Built-in popup bypassing and anti-bot evasion strategies.
- **Zero Server Costs**: Runs entirely on GitHub's free CI/CD infrastructure.

---

## 🚀 How It Works

1. You send a trigger to GitHub Actions (manually or via API).
2. GitHub spins up a fresh runner with a clean IP.
3. The Playwright scraper (`scraper.py`) navigates the site, inputs your prompt, and waits for the AI.
4. Upon completion, the script captures the `mp4` URL and sends it directly to your provided Webhook URL.

---

## 🛠️ Setup & Installation

Since this project is designed for GitHub Actions, no local installation is required unless you wish to develop or debug.

### Deploying to Your GitHub
1. **Fork** or **Clone** this repository to your own GitHub account.
2. Ensure GitHub Actions are enabled in your repository settings (`Settings` > `Actions` > `General` > `Allow all actions`).
3. You are ready to go!

---

## 📖 Usage Guide

### Method 1: Trigger via n8n / REST API (Recommended)

You can trigger video generation from any application by making a simple API call to your GitHub repository.

**Endpoint:** `POST https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO_NAME/dispatches`

**Headers:**
```json
{
  "Authorization": "token YOUR_GITHUB_PERSONAL_ACCESS_TOKEN",
  "Accept": "application/vnd.github.v3+json"
}
```

**Body:**
```json
{
  "event_type": "generate_video",
  "client_payload": {
    "prompt": "A cinematic shot of a futuristic cyberpunk city in the rain, neon lights",
    "aspect_ratio": "VIDEO_ASPECT_RATIO_LANDSCAPE",
    "webhook_url": "https://your-webhook-url.com/endpoint"
  }
}
```

*Options for `aspect_ratio`: `VIDEO_ASPECT_RATIO_LANDSCAPE` or `VIDEO_ASPECT_RATIO_PORTRAIT`*

### Method 2: Manual Trigger via GitHub UI
1. Go to the **Actions** tab in your repository.
2. Select **Veo Video Generator** from the left sidebar.
3. Click **Run workflow**.
4. Fill in your Prompt, Aspect Ratio, and Webhook URL, then click **Run**.

---

## 📩 Webhook Responses

When the generation finishes (usually within 2-3 minutes), your webhook will receive a `POST` request.

**Success Response:**
```json
{
  "status": "success",
  "prompt": "A cinematic shot of a futuristic cyberpunk city in the rain, neon lights",
  "video_url": "https://veoaifree.com/wp-content/uploads/vids/example_video.mp4"
}
```

**Failure Response:**
```json
{
  "status": "failed",
  "prompt": "A cinematic shot of a futuristic cyberpunk city in the rain, neon lights"
}
```

---

## ⚠️ Disclaimer
This script interacts with a third-party website. It is intended for educational purposes and personal automation. Please respect the terms of service of the target website.
