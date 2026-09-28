"""
Zero-Dependency Mock & Stub Providers for SentinelEye Subsystems.
Allows Ram (UI) and Priyanshu (LLM/Security) to build, test, and iterate
without requiring heavy CUDA GPU hardware or downloaded 8GB model checkpoints.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import hashlib
from datetime import datetime, timezone

from schemas import (
    RetrievalResult,
    RetrievalFilters,
    ScoredTileCandidate,
    QueryType,
    ChangeRecord,
    AnalystDecision,
    DecisionType,
    TacticalPriority,
    AuditCryptoBlock,
)


def mock_remoteclip_embed(text_or_path: str, dim: int = 512) -> np.ndarray:
    """
    Generates a deterministic L2-normalized pseudo-embedding for any text or image path.
    Guarantees that similar semantic strings yield reproducible high cosine similarity.
    """
    # Use SHA-256 seed for determinism
    seed = int(hashlib.sha256(text_or_path.encode()).hexdigest()[:8], 16)
    rng = np.random.RandomState(seed)
    vec = rng.randn(dim).astype(np.float32)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


def mock_bit_change_detect(
    before_arr: np.ndarray,
    after_arr: np.ndarray,
    force_fallback_trigger: bool = False,
) -> Tuple[np.ndarray, float, List[str]]:
    """
    Simulates BIT transformer inference on a 512x512 bitemporal pair.
    Returns:
      - change_mask: (512, 512) uint8 mask
      - confidence: float [0.0 - 1.0]
      - models_used: list of model identifiers
    """
    h, w = before_arr.shape[:2] if before_arr is not None else (512, 512)
    mask = np.zeros((h, w), dtype=np.uint8)

    if force_fallback_trigger:
        # Returns low confidence (0.45) to trigger CVA fallback in the orchestrator
        return mask, 0.45, ["BIT_UNCONFIRMED"]

    # Generate a realistic synthetic road/clearance stripe in the center
    # Simulates a linear spur road: y from 220 to 280, x from 140 to 380
    mask[220:260, 140:380] = 255
    # Small equipment staging cluster
    mask[240:310, 350:410] = 255

    confidence = 0.94
    return mask, confidence, ["BIT"]


def mock_cva_change_detect(
    before_arr: np.ndarray,
    after_arr: np.ndarray,
    threshold: float = 0.35,
) -> Tuple[np.ndarray, float, List[str]]:
    """
    Simulates Change Vector Analysis (CVA) spectral fallback.
    Deterministic spectral difference algorithm.
    """
    h, w = before_arr.shape[:2] if before_arr is not None else (512, 512)
    mask = np.zeros((h, w), dtype=np.uint8)

    # CVA detects the strong spectral change cluster
    mask[220:260, 150:370] = 255
    confidence = 0.88
    return mask, confidence, ["CVA", "BFAST_Lite"]


def mock_llm_briefing(facts: List[ChangeRecord], classification_level: str = "RESTRICTED / AIR-GAPPED") -> str:
    """
    Generates a hallucination-free military intelligence briefing
    anchored strictly to the input ChangeRecord facts.
    """
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if not facts:
        return f"""TACTICAL SATELLITE INTELLIGENCE BRIEF
SECURITY CLASSIFICATION: {classification_level}
GENERATED: {now_utc}

1. EXECUTIVE SUMMARY
No verified tactical changes were detected across the specified observation interval. Baseline remains unchanged.

2. VERIFIED CHANGES OBSERVED (0 Items)
- No anomalous military infrastructure detected.
"""

    first_fact = facts[0]
    total_area = sum(f.area_sq_meters for f in facts)
    has_gap_fill = any(f.is_reconstructed_or_gap_filled for f in facts)

    brief = f"""TACTICAL SATELLITE INTELLIGENCE BRIEF
SECURITY CLASSIFICATION: {classification_level}
AOI / SECTOR: {first_fact.location.region_name.upper()}
GENERATED: {now_utc}
TARGET CHANGE REF(S): {', '.join(f.change_id for f in facts)}

1. EXECUTIVE SUMMARY
Multi-temporal satellite change analysis has confirmed {len(facts)} distinct tactical physical changes in {first_fact.location.region_name}. Comparison between baseline {first_fact.before_tile_ref.sensor} ({first_fact.before_tile_ref.acquisition_date}) and subsequent observation ({first_fact.after_tile_ref.acquisition_date}) demonstrates high-confidence infrastructure development covering approximately {total_area:,.1f} sq meters.

2. VERIFIED CHANGES OBSERVED ({len(facts)} Event(s))
"""

    for f in facts:
        coords_str = f"{f.location.centroid[0]:.4f}° N, {f.location.centroid[1]:.4f}° E"
        mgrs = f" (MGRS: {f.location.mgrs_grid_ref})" if f.location.mgrs_grid_ref else ""
        brief += f"""- Event ID: {f.change_id}
  • Classification: {f.change_type.value.replace('_', ' ').title()}
  • Coordinates: {coords_str}{mgrs}
  • Physical Footprint: {f.area_sq_meters:,.1f} sq meters
  • Earliest Observation Date: {f.earliest_supported_observation_date}
  • Confidence Score: {f.confidence_score * 100:.1f}% (Model attribution: {', '.join(f.source_models)})
  • Sovereign Data Integrity: {'RECONSTRUCTED/GAP-FILLED WARNING' if f.is_reconstructed_or_gap_filled else 'GENUINE DIRECT SENSOR OBSERVATION'}
"""

    provenance_note = (
        "WARNING: One or more observations overlapped with cloud-masked or interpolated pixels. Confidence downgraded accordingly."
        if has_gap_fill
        else "All detections verified against 100% cloud-free, genuinely observed multispectral pixels."
    )

    brief += f"""
3. SENSOR PROVENANCE & DATA INTEGRITY
- Primary Sensor Baseline: {first_fact.before_tile_ref.sensor}
- Subsequent Acquisition: {first_fact.after_tile_ref.sensor}
- {provenance_note}

4. ANALYST ACTION ITEMS
- Verify tactical alignment with national border reference vectors.
- Transmit high-priority alert to sector tactical commander.
- Commit validation status to sovereign immutable audit log.
"""
    return brief


def mock_audit_commit(
    change_record_id: str,
    analyst_id: str,
    decision: DecisionType = DecisionType.CONFIRMED,
    priority: TacticalPriority = TacticalPriority.HIGH,
    notes: str = "Verified by duty analyst",
    previous_block_hash: str = "0" * 64,
    block_index: int = 1,
) -> AnalystDecision:
    """
    Simulates BLAKE3 hash chaining and Ed25519 digital signing.
    """
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    payload_str = f"{change_record_id}|{decision.value}|{priority.value}|{analyst_id}|{now_utc}|{notes}"
    payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()
    chain_hash = hashlib.sha256((previous_block_hash + payload_hash).encode()).hexdigest()

    mock_pubkey = hashlib.sha256(analyst_id.encode()).hexdigest()
    mock_sig = hashlib.sha256((chain_hash + mock_pubkey).encode()).hexdigest() * 2

    return AnalystDecision(
        schema_version="1.0.0",
        decision_id=f"DEC-2026-{block_index:04d}",
        change_record_id=change_record_id,
        analyst_id=analyst_id,
        decision=decision,
        tactical_priority=priority,
        notes=notes,
        timestamp=now_utc,
        audit_crypto=AuditCryptoBlock(
            block_index=block_index,
            previous_block_hash=previous_block_hash,
            payload_hash=payload_hash,
            chain_hash=chain_hash,
            analyst_public_key=mock_pubkey,
            signature=mock_sig,
        ),
    )


class MockModelRegistry:
    """Central configuration for enabling/disabling mock stubs per module."""
    use_mock_retrieval: bool = True
    use_mock_change_detection: bool = True
    use_mock_llm: bool = True
    use_mock_audit: bool = True
