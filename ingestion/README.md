# Ingestion & Preprocessing Module

**Module Owner**: Anuj (Data & Preprocessing)  
**Problem Statement**: PS26227 — Multi-Temporal Change Analysis

## Scope & Responsibilities
- Ingest optical and SAR satellite imagery (Sentinel-1/2, Landsat-8/9, Bhuvan/Cartosat).
- Preprocess imagery: radiometric calibration, orthorectification, coregistration between temporal pairs.
- Cloud, cloud-shadow, and snow masking using Fmask algorithm.
- Multi-temporal harmonization across sensors (e.g., matching pixel resolution, coordinate reference systems to UTM/WGS84).
- Export standardized image tiles conforming to `schemas/tile_metadata.json`.

## Key Interfaces
- `ingest_scene(source_path: str, sensor: str) -> List[TileMetadata]`
- `prepare_bitemporal_pair(before_tile_id: str, after_tile_id: str) -> BitemporalPair`
- `apply_fmask(tile_path: str) -> np.ndarray` (valid observation mask vs cloud/gap)

## Data Notes
Refer to `docs/DATA.md` for local dataset structure, sensor band orders, and coregistration parameters.
