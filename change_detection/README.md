# Multi-Temporal Change Detection Module

**Module Owner**: Gargi (Change Detection Models & Scoring)  
**Problem Statement**: PS26227 — Multi-Temporal Change Analysis

## Scope & Responsibilities
- Primary change detection pipeline: Bitemporal Image Transformer (`BIT`) and Bi-temporal Adapter Network (`BAN`).
- Fallback & validation pipeline: Change Vector Analysis (`CVA`) and `BFAST / BFAST-Lite` for multi-temporal trend verification.
- Fine-grained tactical detection: `SAHI` (Slicing Aided Hyper Inference) + lightweight YOLO for small tactical assets (vehicles, field artillery, shelters).
- High precision thresholding: Minimize false alarms from seasonal vegetation or solar illumination changes.
- Fallback orchestration: When transformer confidence is borderline or GPU VRAM is strained, automatically activate the deterministic CVA fallback pipeline.
- Export candidate changes conforming to `schemas/change_record.json` (the Facts Dictionary input).

## Key Interfaces
- `detect_changes_bit(before_img: np.ndarray, after_img: np.ndarray) -> ChangeMask`
- `detect_changes_cva_fallback(before_img: np.ndarray, after_img: np.ndarray) -> ChangeMask`
- `run_change_pipeline(before_tile_id: str, after_tile_id: str, use_fallback: bool = False) -> List[ChangeRecord]`
- `fuse_and_score_changes(candidates: List[RawChange]) -> List[ChangeRecord]`
