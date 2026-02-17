from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, validator
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
import random
from datetime import datetime

app = FastAPI(title="InstaCollect Public API - Demo Mode")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CollectRequest(BaseModel):
    tag: str
    limit: int = 10
    
    @validator("limit")
    def limit_guard(cls, v):
        if v > 20:
            raise ValueError("Max 20 posts per request")
        if v < 1:
            raise ValueError("Min 1 post")
        return v

# Sample data generator
def generate_dummy_posts(tag: str, limit: int):
    posts = []
    sample_captions = [
        f"Exploring the beauty of #{tag}. Amazing experience!",
        f"New discoveries about #{tag} that will blow your mind.",
        f"Why #{tag} matters more than you think. Read more...",
        f"The ultimate guide to #{tag} for beginners.",
        f"5 things you didn't know about #{tag}. Thread"
    ]
    
    for i in range(min(limit, 5)):
        post = {
            "url": f"https://www.instagram.com/p/DEMO{random.randint(1000, 9999)}/",
            "caption": sample_captions[i % len(sample_captions)],
            "caption_status": "short_text",
            "timestamp": datetime.now().isoformat() + "Z",
            "is_video": False,
            "hashtags": [tag, "demo", "sample"],
            "mentions": [],
            "source_tag": tag
        }
        posts.append(post)
    
    return posts

@app.post("/collect")
@limiter.limit("3/minute")
async def collect(request: Request, req: CollectRequest):
    try:
        # Generate dummy data instead of real scraping
        data = generate_dummy_posts(req.tag, req.limit)
        
        result = {
            "meta": {
                "tag": req.tag,
                "limit": req.limit,
                "collected": len(data),
                "timestamp": datetime.now().isoformat(),
                "mode": "demo"
            },
            "data": data,
            "files": None,
            "notice": "This is demo mode. Real scraping requires dedicated server."
        }
        
        return result
    except Exception as e:
        import traceback
        print(f"[ERROR] {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {
        "service": "InstaCollect",
        "status": "running",
        "mode": "demo",
        "note": "Demo version - Returns sample data for testing"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
