from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints._v1 import routers
from app.database import Base, engine
from app.websocket.manager import WSManager
import time
import os

manager = WSManager()

app = FastAPI(
    title='Washhup API',
    description='Car washing application',
    version='0.8.5',
)

# Only create tables if not in a testing environment or if explicitly requested
if os.getenv("ENV") != "testing":
    Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


app.include_router(routers.router)
