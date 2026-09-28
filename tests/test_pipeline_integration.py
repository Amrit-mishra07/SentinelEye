"""
Integration tests for the SentinelEye Master Pipeline Orchestrator.
Tests end-to-end data flow, BIT-to-CVA automatic fallback, facts dictionary synthesis,
and cryptographic audit chaining across both Live Inference and Replay modes.
"""

import pytest
import numpy as np

from pipeline.orchestrator import SentinelEyePipeline
from schemas import (
    RetrievalFilters,
    QueryType,
    DecisionType,
    TacticalPriority,
)


def test_pipeline_search():
    pipeline = SentinelEyePipeline(replay_mode=False)
    result = pipeline.search_imagery(
        query="road construction along northern ridge",
        query_type=QueryType.TEXT,
        filters=RetrievalFilters(min_similarity=0.5),
        top_k=3,
    )
    assert result.query_content == "road construction along northern ridge"
    assert len(result.results) > 0
    assert result.results[0].rank == 1
    assert result.results[0].similarity_score >= 0.5


def test_pipeline_change_detection_and_cva_fallback():
    pipeline = SentinelEyePipeline(replay_mode=False)

    before_meta = {
        "tile_id": "TILE-B-001",
        "acquisition_date": "2025-11-10T05:38:51Z",
        "sensor": "Sentinel-2",
        "coordinates": {"bbox": [78.65, 33.70, 78.71, 33.75]},
        "resolution_meters": 10.0,
    }
    after_meta = {
        "tile_id": "TILE-A-001",
        "acquisition_date": "2026-02-20T05:39:09Z",
        "sensor": "Sentinel-2",
    }

    # 1. Normal run (BIT)
    records, mask, conf, models = pipeline.detect_changes(
        before_meta=before_meta,
        after_meta=after_meta,
        use_cva_fallback=False,
    )
    assert len(records) > 0
    assert "BIT" in models
    assert conf >= 0.90

    # 2. Forced fallback trigger (simulates transformer low confidence or VRAM pressure)
    records_fb, mask_fb, conf_fb, models_fb = pipeline.detect_changes(
        before_meta=before_meta,
        after_meta=after_meta,
        force_fallback_trigger=True,
    )
    assert len(records_fb) > 0
    assert any("CVA" in m for m in models_fb)
    assert "BIT_LOW_CONF_FALLBACK" in models_fb


def test_pipeline_audit_chaining():
    pipeline = SentinelEyePipeline(replay_mode=False)

    # First decision
    dec1 = pipeline.commit_analyst_decision(
        change_record_id="CHG-001",
        analyst_id="ANALYST-DEF-712",
        decision=DecisionType.CONFIRMED,
    )
    assert dec1.audit_crypto.block_index == 1
    assert dec1.audit_crypto.previous_block_hash == "0" * 64

    # Second decision chained to first
    dec2 = pipeline.commit_analyst_decision(
        change_record_id="CHG-002",
        analyst_id="ANALYST-DEF-712",
        decision=DecisionType.REJECTED,
    )
    assert dec2.audit_crypto.block_index == 2
    assert dec2.audit_crypto.previous_block_hash == dec1.audit_crypto.chain_hash


def test_pipeline_full_cycle_replay_mode():
    # Verify stage demo zero-latency replay mode
    pipeline = SentinelEyePipeline(replay_mode=True)
    res = pipeline.run_full_cycle(
        query="road construction",
        scenario_id="demo_pair_01_pangong",
    )
    assert res.is_replay_mode is True
    assert len(res.change_records) > 0
    assert res.change_records[0].change_id == "CHG-2026-0042"
    assert "TACTICAL SATELLITE INTELLIGENCE BRIEF" in res.briefing_text
    assert res.analyst_decision is not None
    assert res.execution_time_ms < 100.0  # Ultra-fast <100ms stage response
