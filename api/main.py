"""
SentinelEye Local REST API Service.
Allows the frontend dashboard to execute searches, change detection,
briefing generation, and audit logging over clean typed JSON endpoints.
"""

from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import os

from schemas import (
    RetrievalResult,
    ChangeRecord,
    AnalystDecision,
    RetrievalFilters,
    QueryType,
    DecisionType,
    TacticalPriority,
)
from pipeline.orchestrator import SentinelEyePipeline
from pipeline.replay_provider import ReplayScenarioProvider

app = FastAPI(
    title="SentinelEye Air-Gapped Intelligence API",
    description="Local sovereign REST service for satellite semantic retrieval and change analysis",
    version="1.0.0",
)

# Shared pipeline instance
pipeline = SentinelEyePipeline()


class SearchRequest(BaseModel):
    query: str
    query_type: QueryType = QueryType.TEXT
    filters: Optional[RetrievalFilters] = None
    scenario_id: str = "demo_pair_01_pangong"
    top_k: int = 5


class ChangeDetectionRequest(BaseModel):
    scenario_id: str = "demo_pair_01_pangong"
    use_cva_fallback: bool = False
    force_fallback_trigger: bool = False


class BriefingRequest(BaseModel):
    facts: List[ChangeRecord]
    scenario_id: str = "demo_pair_01_pangong"


class AuditCommitRequest(BaseModel):
    change_record_id: str
    analyst_id: str = "ANALYST-DEF-712"
    decision: DecisionType = DecisionType.CONFIRMED
    priority: TacticalPriority = TacticalPriority.CRITICAL
    notes: str = "Verified by duty analyst"


class ModeToggleRequest(BaseModel):
    replay_mode: bool


@app.get("/")
def get_root():
    return {
        "service": "SentinelEye Sovereign Satellite Intelligence Platform",
        "air_gap_compliant": True,
        "replay_mode": pipeline.replay_mode,
        "version": "1.0.0",
        "documentation": "/docs",
    }


@app.get("/api/scenarios")
def list_scenarios():
    provider = ReplayScenarioProvider()
    return {"scenarios": provider.list_scenarios()}


@app.post("/api/search", response_model=RetrievalResult)
def search_imagery(req: SearchRequest):
    return pipeline.search_imagery(
        query=req.query,
        query_type=req.query_type,
        filters=req.filters,
        top_k=req.top_k,
        scenario_id=req.scenario_id,
    )


@app.post("/api/detect-changes")
def detect_changes(req: ChangeDetectionRequest):
    before_meta = pipeline.replay_provider.get_tile_metadata(req.scenario_id, "before")
    after_meta = pipeline.replay_provider.get_tile_metadata(req.scenario_id, "after")

    records, mask, conf, models = pipeline.detect_changes(
        before_meta=before_meta,
        after_meta=after_meta,
        use_cva_fallback=req.use_cva_fallback,
        force_fallback_trigger=req.force_fallback_trigger,
        scenario_id=req.scenario_id,
    )
    return {
        "scenario_id": req.scenario_id,
        "records": records,
        "confidence": conf,
        "models_activated": models,
        "has_gap_filled_pixels": any(r.is_reconstructed_or_gap_filled for r in records),
    }


@app.post("/api/generate-briefing")
def generate_briefing(req: BriefingRequest):
    brief_text = pipeline.generate_briefing(req.facts, scenario_id=req.scenario_id)
    return {
        "scenario_id": req.scenario_id,
        "briefing_text": brief_text,
    }


@app.post("/api/audit/commit", response_model=AnalystDecision)
def commit_audit(req: AuditCommitRequest):
    return pipeline.commit_analyst_decision(
        change_record_id=req.change_record_id,
        analyst_id=req.analyst_id,
        decision=req.decision,
        priority=req.priority,
        notes=req.notes,
    )


@app.post("/api/mode/toggle")
def toggle_mode(req: ModeToggleRequest):
    pipeline.replay_mode = req.replay_mode
    os.environ["REPLAY_MODE"] = "true" if req.replay_mode else "false"
    return {
        "replay_mode": pipeline.replay_mode,
        "message": f"Operating mode switched to {'REPLAY (Cached)' if pipeline.replay_mode else 'LIVE INFERENCE'}",
    }
