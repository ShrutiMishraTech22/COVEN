"""
COVEN backend entrypoint.
Run with: uvicorn app.main:app --reload --port 8000
(run this command from inside the backend/ folder)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.api import cases, evidence, timeline, analysis, hypotheses, graph

app = FastAPI(title="COVEN API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cases.router)
app.include_router(evidence.router)
app.include_router(timeline.router)
app.include_router(analysis.router)
app.include_router(hypotheses.router)
app.include_router(graph.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}
