# LLM Schema, Grammar & Constrained Generation Specification (LLM_SCHEMA.md)

**Maintained by**: Priyanshu (LLM & Security Lead)  
**Project**: SentinelEye (PS26227)

---

## 1. Zero-Hallucination Design Principle
In defence intelligence operations, **precision strictly takes precedence over recall**, and hallucination of non-existent objects, coordinates, or timestamps is catastrophic.

The local LLM (Qwen-2.5-7B or Gemma-2-9B) functions **solely as a natural language synthesizer of the verified Facts Dictionary** (`schemas/change_record.json`). It does not hypothesize or invent facts beyond what the vision models verified and the analyst reviewed.

To mathematically prevent hallucination at inference time:
1. **GBNF (GGML BNF) Grammar Constraints**: Constrain the logits of `llama.cpp` so that only tokens adhering to the structured briefing template and verified entities can be decoded.
2. **Entity Attribution Check**: Post-generation regex validator ensures every coordinate, date, and metric in the briefing has an exact 1:1 match in the input `change_record` objects.
3. **Reconstructed Pixel Disclaimer**: If `is_reconstructed_or_gap_filled == True`, the LLM is programmatically forced to append a sovereign data integrity disclaimer.

---

## 2. Input: Facts Dictionary Structure
The briefing engine takes an array of verified `ChangeRecord` objects (`schemas/change_record.json`):

```json
[
  {
    "change_id": "CHG-2026-0042",
    "location": {
      "mgrs_grid_ref": "43RER12345678",
      "region_name": "Pangong North Ridge Sector",
      "centroid": [33.7291, 78.6812]
    },
    "before_tile_ref": {
      "tile_id": "T43RER_20251110",
      "acquisition_date": "2025-11-10T05:38:51Z",
      "sensor": "Sentinel-2"
    },
    "after_tile_ref": {
      "tile_id": "T43RER_20260220",
      "acquisition_date": "2026-02-20T05:39:09Z",
      "sensor": "Sentinel-2"
    },
    "change_type": "road_development",
    "earliest_supported_observation_date": "2026-02-20T05:39:09Z",
    "confidence_score": 0.94,
    "area_sq_meters": 14200.0,
    "source_models": ["BIT", "CVA"],
    "is_reconstructed_or_gap_filled": false,
    "tactical_attributes": {
      "length_meters": 1420.0,
      "estimated_width_meters": 10.0,
      "orientation": "E-W"
    }
  }
]
```

---

## 3. GBNF Grammar Specification (Draft)
```bnf
root ::= Briefing

Briefing ::= 
  "TACTICAL SATELLITE INTELLIGENCE BRIEF" "\n"
  "SECURITY CLASSIFICATION: RESTRICTED / AIR-GAPPED" "\n"
  "GENERATED: " IsoDate "\n\n"
  "1. EXECUTIVE SUMMARY\n" SummaryText "\n\n"
  "2. VERIFIED CHANGES OBSERVED (" Int " Item(s))\n" ChangeItemList "\n\n"
  "3. SENSOR PROVENANCE & DATA INTEGRITY\n" ProvenanceSection "\n\n"
  "4. ANALYST ACTION ITEMS\n" ActionItemsList "\n"

SummaryText ::= [a-zA-Z0-9 ,.;:()/-]+
IsoDate ::= [0-9]{4} "-" [0-9]{2} "-" [0-9]{2} "T" [0-9]{2} ":" [0-9]{2} ":" [0-9]{2} "Z"
Int ::= [1-9][0-9]*
...
```

---

## 4. Cryptographic Audit Log Integration
Once the briefing is verified by the duty analyst:
- Analyst decisions (`CONFIRMED`, `REJECTED`, `FLAGGED_FOR_REVISIT`) are captured in `schemas/analyst_decision.json`.
- Each record computes a `BLAKE3` hash of the canonical JSON payload chained with the hash of the preceding block.
- The analyst's local private key signs the chain hash using `Ed25519`.
