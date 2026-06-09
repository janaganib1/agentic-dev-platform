import os
import asyncio
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from main import run_full_pipeline

load_dotenv()

# ─── Logging Setup ────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ─── In-memory pipeline tracker ───────────────────────────────────────────────

active_pipelines: dict = {}


# ─── App Setup ────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Agentic Dev Platform API started")
    yield
    logger.info("🛑 Agentic Dev Platform API stopped")

app = FastAPI(
    title="Agentic Dev Platform",
    description="Webhook API to trigger the agentic pipeline from Jira",
    version="1.0.0",
    lifespan=lifespan
)


# ─── Health Check ─────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


# ─── Jira Webhook Endpoint ────────────────────────────────────────────────────

@app.post("/jira-webhook")
async def jira_webhook(request: Request):
    """
    Receives Jira automation webhook when ai-pipeline label is added.
    Triggers the full agentic pipeline asynchronously.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Extract issue details from Jira webhook payload
    issue = body.get("issue", {})
    issue_key = issue.get("key", "")
    fields = issue.get("fields", {})
    labels = fields.get("labels", [])
    summary = fields.get("summary", "")
    description = fields.get("description", "")

    logger.info(f"📩 Received webhook for issue: {issue_key}, labels: {labels}")

    # Only trigger if ai-pipeline label is present
    if "ai-pipeline" not in labels:
        logger.info(f"⏭️  Skipping {issue_key} — no ai-pipeline label")
        return JSONResponse(
            status_code=200,
            content={"status": "skipped", "reason": "no ai-pipeline label", "ticket": issue_key}
        )

    if not issue_key:
        raise HTTPException(status_code=400, detail="No issue key found in payload")

    # Avoid duplicate pipeline runs for the same ticket
    if issue_key in active_pipelines and active_pipelines[issue_key].get("status") == "running":
        logger.warning(f"⚠️  Pipeline already running for {issue_key}")
        return JSONResponse(
            status_code=200,
            content={"status": "already_running", "ticket": issue_key}
        )

    # Build requirement string from Jira story
    requirement = f"{summary}\n\n{description}".strip() if description else summary

    # Track and trigger pipeline
    active_pipelines[issue_key] = {
        "status": "running",
        "started_at": datetime.now().isoformat()
    }
    asyncio.create_task(trigger_pipeline(issue_key, requirement))

    logger.info(f"✅ Pipeline triggered for {issue_key}")
    return JSONResponse(
        status_code=202,
        content={"status": "triggered", "ticket": issue_key}
    )


# ─── Pipeline Status Endpoints ────────────────────────────────────────────────

@app.get("/pipeline/status/{issue_key}")
async def pipeline_status(issue_key: str):
    """Check the status of a running or completed pipeline."""
    if issue_key not in active_pipelines:
        raise HTTPException(status_code=404, detail=f"No pipeline found for {issue_key}")
    return {"ticket": issue_key, **active_pipelines[issue_key]}


@app.get("/pipeline/active")
async def list_active_pipelines():
    """List all active and recently completed pipelines."""
    return {"pipelines": active_pipelines}


# ─── Async Pipeline Trigger ───────────────────────────────────────────────────

async def trigger_pipeline(issue_key: str, requirement: str):
    """
    Async wrapper — calls run_full_pipeline() from main.py.
    All pipeline logic, state management and GitHub push lives in main.py.
    """
    logger.info(f"🚀 Starting pipeline for {issue_key}")
    try:
        result = await asyncio.to_thread(
            run_full_pipeline,
            requirement=requirement,
            ticket_id=issue_key,
            auto_approve=True
        )
        active_pipelines[issue_key].update({
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "stories_completed": result["stories_completed"],
            "stories_total": result["stories_total"],
            "project_folder": result["project_folder"],
            "branch_url": result.get("github", {}).get("branch_url", "")
        })
        logger.info(f"🏁 Pipeline complete for {issue_key}: {result['stories_completed']}/{result['stories_total']} stories")

    except Exception as e:
        logger.error(f"❌ Pipeline failed for {issue_key}: {str(e)}")
        active_pipelines[issue_key].update({
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        })