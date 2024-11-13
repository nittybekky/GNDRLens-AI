from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis

# Import database setup
from sqlalchemy.orm import Session
from app.models.base import Base, engine, get_db
from app.models.user import User
from app.models.analysis import Analysis

# Import the router for authentication and analysis
from app.routes.auth import router as auth_router
from app.routes.analysis import router as analysis_router  

app = FastAPI(title="SafeSpace AI")

@app.on_event("startup")
async def startup():
    # Initialize Redis-based rate limiter
    redis_instance = redis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_instance)
    
    # Create database tables
    print("Creating database tables...")
    try:
        # Base.metadata.create_all(bind=engine)
        from app.models.base import create_tables
        create_tables()
        print("Tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # This is for our vue.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to SafeSpace AI"}

# Include authentication routes
app.include_router(auth_router, prefix="/auth")

# Include analysis routes with rate limiting
app.include_router(
    analysis_router,
    prefix="/api/v1/analysis", 
    tags=["analysis"],
    dependencies=[Depends(RateLimiter(times=10, seconds=60))]  # 10 requests per minute
)