import asyncio
import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from scraper import VeoScraper

app = FastAPI(title="Veo Video Generator API")

# Store for task statuses
# task_id -> {"status": "pending/processing/completed/failed", "result": "url or error", "prompt": "..."}
tasks: Dict[str, Dict] = {}

# Queue for sequential processing
task_queue = asyncio.Queue()

class GenerateRequest(BaseModel):
    prompt: str
    aspect_ratio: str = "VIDEO_ASPECT_RATIO_LANDSCAPE"  # or VIDEO_ASPECT_RATIO_PORTRAIT

@app.on_event("startup")
async def startup_event():
    # Start the background worker
    asyncio.create_task(worker())

import os

# Optional Proxy Configuration (Set these in HF Space Secrets)
PROXY_SERVER = os.getenv("PROXY_SERVER") # e.g. http://proxy.example.com:8080
PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASS = os.getenv("PROXY_PASS")

proxy_config = None
if PROXY_SERVER:
    proxy_config = {"server": PROXY_SERVER}
    if PROXY_USER and PROXY_PASS:
        proxy_config["username"] = PROXY_USER
        proxy_config["password"] = PROXY_PASS

async def worker():
    scraper = VeoScraper(proxy=proxy_config)
    while True:
        # Get a task from the queue
        task_id, request_data = await task_queue.get()
        tasks[task_id]["status"] = "processing"
        
        try:
            logger_info(f"Processing task {task_id}: {request_data.prompt}")
            video_url = await scraper.generate_video(
                prompt=request_data.prompt,
                aspect_ratio=request_data.aspect_ratio
            )
            tasks[task_id]["status"] = "completed"
            tasks[task_id]["result"] = video_url
        except Exception as e:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["result"] = str(e)
        finally:
            task_queue.task_done()

def logger_info(msg):
    print(f"[WORKER] {msg}")

@app.post("/generate")
async def generate(request: GenerateRequest):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "pending",
        "result": None,
        "prompt": request.prompt,
        "aspect_ratio": request.aspect_ratio
    }
    
    # Add to queue
    await task_queue.put((task_id, request))
    
    return {"task_id": task_id, "status": "pending"}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks[task_id]

@app.get("/")
async def root():
    return {
        "message": "Veo Video Generator API is running",
        "endpoints": {
            "/generate": "POST - Start generation",
            "/status/{task_id}": "GET - Check progress"
        },
        "queue_size": task_queue.qsize()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
