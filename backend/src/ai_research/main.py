import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from ai_research.event_manager import event_manager, event_stream_response
from ai_research.schemas import ResearchRequest, ResearchResponse
from ai_research.services import execute_research

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_BACKEND_ROOT / ".env")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logging.basicConfig(level=logging.INFO)
    yield


app = FastAPI(title="AI Research API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "FRONTEND_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization", "Last-Event-ID"],
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok", "service": "AI Research API"}


@app.post("/api/research", response_model=ResearchResponse)
async def create_research(
    payload: ResearchRequest,
    request: Request,
) -> ResearchResponse:
    try:
        report = await execute_research(
            payload.topic,
            payload.run_id,
            event_manager,
        )
    except Exception as exc:
        logger.exception("Research run %s failed", payload.run_id)
        await event_manager.publish(
            payload.run_id,
            {
                "event": "run_failed",
                "run_id": str(payload.run_id),
                "message": "Research could not be completed. Check the backend logs and API configuration.",
            },
        )
        if request.app.debug:
            raise
        raise HTTPException(
            status_code=502,
            detail="Research could not be completed. Check the backend logs and API configuration.",
        ) from exc

    await event_manager.publish(
        payload.run_id,
        {"event": "run_completed", "run_id": str(payload.run_id)},
    )
    return ResearchResponse(run_id=payload.run_id, report=report)


@app.get("/api/research/events")
async def research_events(run_id: UUID):
    return event_stream_response(run_id)
