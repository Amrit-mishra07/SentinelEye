"""
SentinelEye Master Pipeline & Integration Orchestration Package.
Glues together Ingestion, Retrieval, Change Detection, Facts Synthesis,
Constrained LLM Briefings, and the Cryptographic Audit Ledger.
"""

from pipeline.facts_synthesizer import (
    mask_to_change_records,
    extract_polygons_from_mask,
    check_gap_fill_intersection,
)
from pipeline.mock_stubs import (
    MockModelRegistry,
    mock_remoteclip_embed,
    mock_bit_change_detect,
    mock_cva_change_detect,
    mock_llm_briefing,
    mock_audit_commit,
)
from pipeline.replay_provider import (
    ReplayScenarioProvider,
    get_available_scenarios,
    load_scenario_facts,
)
from pipeline.orchestrator import (
    SentinelEyePipeline,
    PipelineExecutionResult,
)

__all__ = [
    # Facts Synthesizer
    "mask_to_change_records",
    "extract_polygons_from_mask",
    "check_gap_fill_intersection",
    # Mock Stubs
    "MockModelRegistry",
    "mock_remoteclip_embed",
    "mock_bit_change_detect",
    "mock_cva_change_detect",
    "mock_llm_briefing",
    "mock_audit_commit",
    # Replay Provider
    "ReplayScenarioProvider",
    "get_available_scenarios",
    "load_scenario_facts",
    # Orchestrator
    "SentinelEyePipeline",
    "PipelineExecutionResult",
]
