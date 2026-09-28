"""
Replay Mode Provider for SentinelEye.
Intercepts live inference requests when REPLAY_MODE=true and serves precomputed,
verified JSON artifacts from data/precomputed/ with <50ms response latency.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from schemas import (
    RetrievalResult,
    ChangeRecord,
    TileMetadata,
    AnalystDecision,
    RetrievalFilters,
    QueryType,
)


def get_precomputed_root() -> Path:
    """Returns the absolute path to data/precomputed."""
    return Path(__file__).resolve().parent.parent / "data" / "precomputed"


def get_available_scenarios() -> List[str]:
    """Returns list of precomputed scenario directory names."""
    root = get_precomputed_root()
    if not root.exists():
        return []
    return [d.name for d in root.iterdir() if d.is_dir() and not d.name.startswith(".")]


def load_scenario_facts(scenario_id: str) -> List[ChangeRecord]:
    """Loads ChangeRecord objects for a given scenario."""
    scenario_dir = get_precomputed_root() / scenario_id
    facts_file = scenario_dir / "facts_record.json"

    if not facts_file.exists():
        return []

    with open(facts_file, "r") as f:
        data = json.load(f)

    if isinstance(data, list):
        return [ChangeRecord.model_validate(item) for item in data]
    else:
        return [ChangeRecord.model_validate(data)]


class ReplayScenarioProvider:
    """
    Manages cached demo scenario data for zero-latency stage fallback.
    """

    def __init__(self, precomputed_dir: Optional[Path] = None):
        self.root = precomputed_dir or get_precomputed_root()

    def list_scenarios(self) -> List[Dict[str, str]]:
        """Returns metadata about each available scenario."""
        scenarios = []
        for s_name in get_available_scenarios():
            s_dir = self.root / s_name
            facts_file = s_dir / "facts_record.json"
            desc = s_name.replace("_", " ").title()
            if facts_file.exists():
                try:
                    with open(facts_file, "r") as f:
                        d = json.load(f)
                    if isinstance(d, dict):
                        region = d.get("location", {}).get("region_name", desc)
                        chg_type = d.get("change_type", "tactical change")
                        desc = f"{region} ({chg_type.replace('_', ' ')})"
                except Exception:
                    pass
            scenarios.append({"id": s_name, "label": desc})
        return scenarios

    def get_retrieval_result(self, scenario_id: str = "demo_pair_01_pangong") -> RetrievalResult:
        """Loads cached retrieval result for the scenario."""
        f_path = self.root / scenario_id / "retrieval_result.json"
        if f_path.exists():
            with open(f_path, "r") as f:
                return RetrievalResult.model_validate_json(f.read())

        # Fallback synthetic result
        return RetrievalResult(
            schema_version="1.0.0",
            query_id=f"REPLAY-QRY-{scenario_id}",
            query_type=QueryType.TEXT,
            query_content=f"tactical change analysis in {scenario_id}",
            results=[],
            execution_time_ms=12.4,
            index_type_used="REPLAY_CACHE",
        )

    def get_change_records(self, scenario_id: str = "demo_pair_01_pangong") -> List[ChangeRecord]:
        """Loads cached facts dictionary change records."""
        return load_scenario_facts(scenario_id)

    def get_tile_metadata(self, scenario_id: str, temporal_state: str = "after") -> Optional[TileMetadata]:
        """Loads tile metadata for 'before' or 'after'."""
        f_name = f"tile_{temporal_state}.json"
        f_path = self.root / scenario_id / f_name
        if f_path.exists():
            with open(f_path, "r") as f:
                return TileMetadata.model_validate_json(f.read())
        return None

    def get_briefing_text(self, scenario_id: str = "demo_pair_01_pangong") -> str:
        """Loads precomputed intelligence brief."""
        b_path = self.root / scenario_id / "briefing.txt"
        if b_path.exists():
            with open(b_path, "r") as f:
                return f.read()
        return "No briefing found in replay cache."

    def get_sample_decision(self, scenario_id: str = "demo_pair_01_pangong") -> Optional[AnalystDecision]:
        """Loads precomputed analyst decision and audit signature."""
        d_path = self.root / scenario_id / "analyst_decision.json"
        if d_path.exists():
            with open(d_path, "r") as f:
                return AnalystDecision.model_validate_json(f.read())
        return None
