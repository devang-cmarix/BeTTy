import os

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.forces import router as force_router
from routers.aspiration import router as aspiration_router
from routers.baseline_router import router as baseline_router
from routers.gap_analysis_router import router as gap_analysis_router
from routers.plan_router import router as plan_router
from routers.task_router import router as task_router

app = FastAPI(
    title="Psychology Force Analysis API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(force_router)
app.include_router(aspiration_router)
app.include_router(baseline_router)
app.include_router(gap_analysis_router)
app.include_router(plan_router)
app.include_router(task_router)

@app.get("/")
def health():
    return {
        "status": "running"
    }
