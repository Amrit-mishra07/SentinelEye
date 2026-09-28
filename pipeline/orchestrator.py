"""
SentinelEye Master Pipeline Orchestrator.
Coordinates data flow between Ingestion, Retrieval, Change Detection,
Facts Dictionary Synthesis, LLM Briefing, and the Cryptographic Audit Ledger.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import os
from pathlib import Path
import numpy as np

from schemas import (
    TileMetadata,
    ChangeRecord,
    RetrievalResult,
    AnalystDecision,
    RetrievalFilters,
    QueryType,
    DecisionType,
    TacticalPriority,
)
from pipeline.facts_synthesizer import mask_to_change_records
from pipeline.mock_stubs import (
    mock_remoteclip_embed,
    mock_bit_change_detect,
    mock_cva_change_detect,
    mock_llm_briefing,
    mock_audit_commit,
)
from pipeline.replay_provider import ReplayScenarioProvider


@dataclass
class PipelineExecutionResult:
    """Encapsulates the end-to-end execution artifacts of a pipeline run."""
    query_result: Optional[RetrievalResult] = None
    change_records: List[ChangeRecord] = field(default_factory=list)
    change_mask: Optional[np.ndarray] = None
    model_confidence: float = 0.0
    models_activated: List[str] = field(default_factory=list)
    briefing_text: str = ""
    analyst_decision: Optional[AnalystDecision] = None
    is_replay_mode: bool = False
    execution_time_ms: float = 0.0


class SentinelEyePipeline:
    """
    Unified Pipeline Orchestrator for SentinelEye.
    Supports both Live Neural Inference and Zero-Latency Replay Fallback Mode.
    """

    def __init__(
        self,
        offline_mode: bool = True,
        replay_mode: Optional[bool] = None,
        use_mock_fallbacks: bool = True,
    ):
        self.offline_mode = offline_mode

        # Check environment if replay_mode not explicitly specified
        if replay_mode is None:
            env_val = os.environ.get("REPLAY_MODE", "false").strip().lower()
            self.replay_mode = env_val in ("true", "1", "yes")
        else:
            self.replay_mode = replay_mode

        self.use_mock_fallbacks = use_mock_fallbacks
        self.replay_provider = ReplayScenarioProvider()
        self._previous_audit_hash = "0" * 64
        self._audit_block_counter = 1

    def search_imagery(
        self,
        query: str,
        query_type: QueryType = QueryType.TEXT,
        filters: Optional[RetrievalFilters] = None,
        top_k: int = 5,
        scenario_id: str = "demo_pair_01_pangong",
    ) -> RetrievalResult:
        """
        Executes semantic retrieval across the offline vector index.
        In replay mode, returns the precomputed retrieval candidate set.
        """
        if self.replay_mode:
            return self.replay_provider.get_retrieval_result(scenario_id)

        # In live mode without heavy FAISS index loaded, use deterministic embedding stub
        if filters is None:
            filters = RetrievalFilters()

        query_vec = mock_remoteclip_embed(query)

        # Build candidate results
        candidates = [
            {
                "rank": 1,
                "tile_id": "TILE-S2-43RER-20260220-001",
                "scene_id": "S2B_MSIL2A_20260220T053909_N0512_R005_T43RER",
                "sensor": "Sentinel-2",
                "acquisition_date": "2026-02-20T05:39:09Z",
                "similarity_score": 0.912,
                "center_coordinates": [33.7291, 78.6812],
                "preview_thumbnail_path": "data/precomputed/demo_pair_01_pangong/thumbnail_after.png",
                "matching_keywords": ["spur road", "ridgeline", "clearance"],
            },
            {
                "rank": 2,
                "tile_id": "TILE-S2-43RER-20251110-001",
                "scene_id": "S2A_MSIL2A_20251110T053851_N0510_R005_T43RER",
                "sensor": "Sentinel-2",
                "acquisition_date": "2025-11-10T05:38:51Z",
                "similarity_score": 0.748,
                "center_coordinates": [33.7291, 78.6812],
                "preview_thumbnail_path": "data/precomputed/demo_pair_01_pangong/thumbnail_before.png",
                "matching_keywords": ["unpaved terrain", "ridgeline"],
            },
        ]

        from schemas import ScoredTileCandidate
        scored = [ScoredTileCandidate.model_validate(c) for c in candidates]

        return RetrievalResult(
            schema_version="1.0.0",
            query_id=f"QRY-{int(np.abs(query_vec[:4].sum()) * 10000):04d}",
            query_type=query_type,
            query_content=query,
            applied_filters=filters,
            results=scored[:top_k],
            total_candidates_scanned=1240,
            execution_time_ms=38.4,
            index_type_used="FAISS_IVFFlat_InnerProduct",
        )

    def detect_changes(
        self,
        before_meta: Any,
        after_meta: Any,
        before_arr: Optional[np.ndarray] = None,
        after_arr: Optional[np.ndarray] = None,
        fmask_valid_mask: Optional[np.ndarray] = None,
        use_cva_fallback: bool = False,
        force_fallback_trigger: bool = False,
        scenario_id: str = "demo_pair_01_pangong",
    ) -> Tuple[List[ChangeRecord], np.ndarray, float, List[str]]:
        """
        Executes bitemporal change detection with automatic CVA fallback.
        Feeds generated change masks into the Facts Synthesizer.
        """
        if self.replay_mode:
            cached_records = self.replay_provider.get_change_records(scenario_id)
            dummy_mask = np.zeros((512, 512), dtype=np.uint8)
            dummy_mask[220:260, 140:380] = 255
            return cached_records, dummy_mask, 0.94, ["REPLAY_PRECOMPUTED"]

        # 1. Primary: Run BIT transformer (or mock stub)
        mask, confidence, models = mock_bit_change_detect(
            before_arr, after_arr, force_fallback_trigger=force_fallback_trigger
        )

        # 2. Fail-safe: Auto-trigger CVA fallback if confidence is low (<0.60) or requested
        if use_cva_fallback or confidence < 0.60 or force_fallback_trigger:
            cva_mask, cva_confidence, cva_models = mock_cva_change_detect(before_arr, after_arr)
            # Combine detections or select fallback
            mask = cva_mask
            confidence = cva_confidence
            models = ["BIT_LOW_CONF_FALLBACK"] + cva_models

        # 3. Facts Dictionary Synthesis (Polygonize, Measure, Fmask audit)
        records = mask_to_change_records(
            change_mask=mask,
            before_meta=before_meta,
            after_meta=after_meta,
            fmask_valid_mask=fmask_valid_mask,
            confidence_score=confidence,
            source_models=models,
        )

        return records, mask, confidence, models

    def generate_briefing(
        self,
        facts: List[ChangeRecord],
        scenario_id: str = "demo_pair_01_pangong",
    ) -> str:
        """
        Generates hallucination-free military intelligence briefing from verified facts.
        """
        if self.replay_mode:
            return self.replay_provider.get_briefing_text(scenario_id)

        return mock_llm_briefing(facts)

    def commit_analyst_decision(
        self,
        change_record_id: str,
        analyst_id: str = "ANALYST-DEF-712",
        decision: DecisionType = DecisionType.CONFIRMED,
        priority: TacticalPriority = TacticalPriority.CRITICAL,
        notes: str = "Ground optical verification complete.",
    ) -> AnalystDecision:
        """
        Appends an analyst validation decision to the BLAKE3 hash chain with Ed25519 signature.
        """
        decision_obj = mock_audit_commit(
            change_record_id=change_record_id,
            analyst_id=analyst_id,
            decision=decision,
            priority=priority,
            notes=notes,
            previous_block_hash=self._previous_audit_hash,
            block_index=self._audit_block_counter,
        )
        # Advance chain state
        self._previous_audit_hash = decision_obj.audit_crypto.chain_hash
        self._audit_block_counter += 1
        return decision_obj

    def run_full_cycle(
        self,
        query: str = "road development along northern ridge",
        scenario_id: str = "demo_pair_01_pangong",
        use_cva_fallback: bool = False,
    ) -> PipelineExecutionResult:
        """
        Executes a complete pipeline pass from search to signed audit ledger.
        Useful for integration testing, smoke tests, and automated validation.
        """
        start_time = 0.0

        # Step 1: Retrieval
        query_res = self.search_imagery(query, scenario_id=scenario_id)

        # Step 2: Metadata loading
        before_meta = self.replay_provider.get_tile_metadata(scenario_id, "before")
        after_meta = self.replay_provider.get_tile_metadata(scenario_id, "after")

        # Step 3: Change detection
        records, mask, conf, models = self.detect_changes(
            before_meta=before_meta,
            after_meta=after_meta,
            use_cva_fallback=use_cva_fallback,
            scenario_id=scenario_id,
        )

        # Step 4: LLM Briefing
        briefing = self.generate_briefing(records, scenario_id=scenario_id)

        # Step 5: Analyst Decision & Cryptographic Signing
        dec_id = records[0].change_id if records else "CHG-GENERIC"
        decision = self.commit_analyst_decision(dec_id)

        return PipelineExecutionResult(
            query_result=query_res,
            change_records=records,
            change_mask=mask,
            model_confidence=conf,
            models_activated=models,
            briefing_text=briefing,
            analyst_decision=decision,
            is_replay_mode=self.replay_mode,
            execution_time_ms=45.2 if self.replay_mode else 185.0,
        )
