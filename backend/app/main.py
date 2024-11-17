# from fastapi import FastAPI, Request, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi_limiter import FastAPILimiter
# from fastapi_limiter.depends import RateLimiter
# import redis.asyncio as redis

# # Import database setup
# from sqlalchemy.orm import Session
# from app.models.base import Base, engine, get_db
# from app.models.user import User
# from app.models.analysis import Analysis

# # Import the router for authentication and analysis
# from app.routes.auth import router as auth_router
# from app.routes.analysis import router as analysis_router  

# app = FastAPI(title="SafeSpace AI")

# @app.on_event("startup")
# async def startup():
#     # Initialize Redis-based rate limiter
#     redis_instance = redis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
#     await FastAPILimiter.init(redis_instance)
    
#     # Create database tables
#     print("Creating database tables...")
#     try:
#         # Base.metadata.create_all(bind=engine)
#         from app.models.base import create_tables
#         create_tables()
#         print("Tables created successfully!")
#     except Exception as e:
#         print(f"Error creating tables: {e}")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173"],  # This is for our vue.js frontend
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Root endpoint
# @app.get("/")
# async def read_root():
#     return {"message": "Welcome to SafeSpace AI"}

# # Include authentication routes
# app.include_router(auth_router, prefix="/auth")

# # Include analysis routes with rate limiting
# app.include_router(
#     analysis_router,
#     prefix="/api/v1/analysis", 
#     tags=["analysis"],
#     dependencies=[Depends(RateLimiter(times=10, seconds=60))]  # 10 requests per minute
# )
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from time import time
from collections import defaultdict

# Import database setup
from app.models.base import Base, engine, get_db
from app.models.user import User
from app.models.analysis import Analysis

# Import the router for authentication and analysis
from app.routes.auth import router as auth_router
from app.routes.analysis import router as analysis_router  

app = FastAPI(title="GNDRLens-AI")

# Optional: Basic in-memory rate limiter setup
request_counts = defaultdict(list)
RATE_LIMIT = 10  # max requests per period
TIME_PERIOD = 60  # time period in seconds (1 minute)

@app.on_event("startup")
async def startup():
    # Initialize the database
    print("Creating database tables...")
    try:
        from app.models.base import create_tables
        create_tables()
        print("Tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://gndrlens-ai.netlify.app"],  # Adjust for your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    analysis_router,
    prefix="/api/v1/analysis",
    tags=["analysis"],
)

# In-memory rate limiter function
def rate_limiter(request: Request):
    client_ip = request.client.host
    current_time = time()

    # Keep only the timestamps within the rate limit window
    request_counts[client_ip] = [timestamp for timestamp in request_counts[client_ip] if timestamp > current_time - TIME_PERIOD]

    if len(request_counts[client_ip]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests")

    request_counts[client_ip].append(current_time)

# Root endpoint with rate limiting
@app.get("/")
async def read_root(request: Request):
    rate_limiter(request)
    return {"message": "Welcome to GNDRLens-AI"}

# POST route for /api/v1/analysis (to match frontend)
@app.post("/api/v1/analysis")
async def create_analysis(request: Request, payload: dict):
    rate_limiter(request)
    # You can implement actual analysis logic here
    print(f"Received analysis payload: {payload}")
    return {"message": "Analysis request received", "data": payload}
