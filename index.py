from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, validator
from insta_collect.service import InstaCollectService
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from mangum import Mangum
import os
import asyncio

# ===== APP INIT =====
app = FastAPI(title="InstaCollect Public API")

# ===== RATE LIMITER =====
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== SCHEMA =====
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

# ===== ENDPOINT =====
@app.post("/collect")
@limiter.limit("3/minute")
async def collect(request: Request, req: CollectRequest):
    try:
        result = await asyncio.to_thread(
            InstaCollectService.collect,
            tag=req.tag,
            limit=req.limit,
            profile_dir="ig_profile",
            auto_save=True
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {
        "service": "InstaCollect",
        "status": "running"
    }

# ===== VERCEL HANDLER =====
handler = Mangum(app)
