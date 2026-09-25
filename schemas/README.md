# Shared Schemas & Data Contracts

This directory contains the central data contracts governing inter-module communication in **SentinelEye**. Every module must read and emit data conforming strictly to these specifications.

## 1. Schema Inventory

| Schema File | Pydantic Model (`.py`) | JSON Schema (`.json`) | Producer Module | Consumer Module |
|---|---|---|---|---|
| **Tile Metadata** | `tile_metadata.py` | `tile_metadata.json` | Ingestion (Anuj) | Retrieval, Change Detection |
| **Change Record** (Facts Dictionary) | `change_record.py` | `change_record.json` | Change Detection (Gargi) | LLM Briefing (Priyanshu) |
| **Analyst Decision** (Audit Chain) | `analyst_decision.py` | `analyst_decision.json` | UI / Review (Ram) | Audit Log (Priyanshu) |
| **Retrieval Result** | `retrieval_result.py` | `retrieval_result.json` | Retrieval (Gargi) | Frontend Search Gallery (Ram) |

---

## 2. Python Usage Example

All models can be imported directly from the `schemas` package:

```python
from schemas import (
    TileMetadata,
    ChangeRecord,
    ChangeType,
    AnalystDecision,
    RetrievalResult,
)

# Example: Validate a detected change record before passing to LLM Briefing
record = ChangeRecord.model_validate_json(raw_json_str)

# Access typed attributes safely
print(f"Detected {record.change_type} with confidence {record.confidence_score}")
if record.is_reconstructed_or_gap_filled:
    print("Warning: Pixel values include gap-filled data!")
```

---

## 3. Facts Dictionary Contract (For Priyanshu)
`schemas/change_record.json` represents the **sole permissible source of truth** for the LLM briefing engine. Under the zero-hallucination constraint:
- Every coordinate cited in the intelligence report must match `location.centroid` or `location.mgrs_grid_ref`.
- The reported timeframe must match `before_tile_ref.acquisition_date` and `earliest_supported_observation_date`.
- The LLM cannot add unverified physical dimensions or threat labels not present in `tactical_attributes`.

---

## 4. Tamper-Evident Hash Chain Contract (For Priyanshu & Ram)
`schemas/analyst_decision.json` defines the ledger entry format:
1. `previous_block_hash`: 64-char hex BLAKE3 hash of the preceding block (genesis block uses `0000000000000000000000000000000000000000000000000000000000000000`).
2. `payload_hash`: BLAKE3 hash of the decision payload (excluding `audit_crypto`).
3. `chain_hash`: BLAKE3 hash of `(previous_block_hash + payload_hash)`.
4. `signature`: Ed25519 signature over `chain_hash` using the duty analyst's private key.
