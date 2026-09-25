#!/usr/bin/env python3
"""
SentinelEye - Synthetic Test Data Generator
Generates realistic, schema-compliant mock data for demo pairs and testing without external imagery.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
import hashlib


def generate_sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def main():
    repo_root = Path(__file__).resolve().parent.parent
    demo_dir = repo_root / "data" / "precomputed" / "demo_pair_01_pangong"
    demo_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating synthetic demonstration data in: {demo_dir}")

    # 1. Before Tile Metadata
    tile_before = {
        "schema_version": "1.0.0",
        "tile_id": "TILE-S2-43RER-20251110-001",
        "scene_id": "S2A_MSIL2A_20251110T053851_N0510_R005_T43RER",
        "sensor": "Sentinel-2",
        "acquisition_date": "2025-11-10T05:38:51Z",
        "resolution_meters": 10.0,
        "coordinates": {
            "crs": "EPSG:4326",
            "bbox": [78.6500, 33.7000, 78.7100, 33.7500],
            "centroid": [33.7291, 78.6812],
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [78.6500, 33.7000],
                        [78.7100, 33.7000],
                        [78.7100, 33.7500],
                        [78.6500, 33.7500],
                        [78.6500, 33.7000]
                    ]
                ]
            }
        },
        "bands": ["B02", "B03", "B04", "B08"],
        "cloud_cover_percentage": 0.2,
        "processing_steps_applied": [
            "radiometric_calibration",
            "orthorectification",
            "fmask_cloud_masking",
            "coregistration_phase_correlation"
        ],
        "source_provenance": {
            "agency": "ESA Copernicus",
            "license": "Open Access / Sovereign Defence Use",
            "archive_checksum_sha256": generate_sha256("scene_before_sample"),
            "ingested_at": "2026-02-25T08:00:00Z",
            "local_file_path": "data/precomputed/demo_pair_01_pangong/tile_before.tif"
        }
    }

    # 2. After Tile Metadata
    tile_after = {
        "schema_version": "1.0.0",
        "tile_id": "TILE-S2-43RER-20260220-001",
        "scene_id": "S2B_MSIL2A_20260220T053909_N0512_R005_T43RER",
        "sensor": "Sentinel-2",
        "acquisition_date": "2026-02-20T05:39:09Z",
        "resolution_meters": 10.0,
        "coordinates": {
            "crs": "EPSG:4326",
            "bbox": [78.6500, 33.7000, 78.7100, 33.7500],
            "centroid": [33.7291, 78.6812],
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [78.6500, 33.7000],
                        [78.7100, 33.7000],
                        [78.7100, 33.7500],
                        [78.6500, 33.7500],
                        [78.6500, 33.7000]
                    ]
                ]
            }
        },
        "bands": ["B02", "B03", "B04", "B08"],
        "cloud_cover_percentage": 1.1,
        "processing_steps_applied": [
            "radiometric_calibration",
            "orthorectification",
            "fmask_cloud_masking",
            "coregistration_phase_correlation"
        ],
        "source_provenance": {
            "agency": "ESA Copernicus",
            "license": "Open Access / Sovereign Defence Use",
            "archive_checksum_sha256": generate_sha256("scene_after_sample"),
            "ingested_at": "2026-02-25T08:05:00Z",
            "local_file_path": "data/precomputed/demo_pair_01_pangong/tile_after.tif"
        }
    }

    # 3. Facts Dictionary Change Record
    facts_record = {
        "schema_version": "1.0.0",
        "change_id": "CHG-2026-0042",
        "location": {
            "crs": "EPSG:4326",
            "centroid": [33.7291, 78.6812],
            "mgrs_grid_ref": "43RER12345678",
            "region_name": "Pangong Tso North Ridge Sector",
            "polygon_geojson": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [78.6750, 33.7250],
                        [78.6880, 33.7260],
                        [78.6890, 33.7320],
                        [78.6760, 33.7310],
                        [78.6750, 33.7250]
                    ]
                ]
            }
        },
        "before_tile_ref": {
            "tile_id": "TILE-S2-43RER-20251110-001",
            "acquisition_date": "2025-11-10T05:38:51Z",
            "sensor": "Sentinel-2"
        },
        "after_tile_ref": {
            "tile_id": "TILE-S2-43RER-20260220-001",
            "acquisition_date": "2026-02-20T05:39:09Z",
            "sensor": "Sentinel-2"
        },
        "change_type": "road_development",
        "earliest_supported_observation_date": "2026-02-20T05:39:09Z",
        "confidence_score": 0.94,
        "area_sq_meters": 14200.0,
        "source_models": ["BIT", "CVA"],
        "is_reconstructed_or_gap_filled": False,
        "gap_fill_details": {
            "gap_fill_method": "none",
            "gap_pixel_ratio": 0.0
        },
        "tactical_attributes": {
            "length_meters": 1420.0,
            "estimated_width_meters": 10.0,
            "bearing_degrees": 78.5,
            "surface_type": "compacted_earth_paved",
            "connectivity": "links_finger_ridgeline_to_logistics_hub"
        }
    }

    # 4. Retrieval Result
    retrieval_result = {
        "schema_version": "1.0.0",
        "query_id": "QRY-2026-9901",
        "query_type": "text",
        "query_content": "road development along northern ridge with heavy equipment clearance",
        "applied_filters": {
            "aoi_bbox": [78.60, 33.65, 78.75, 33.80],
            "date_range": ["2025-11-01T00:00:00Z", "2026-02-25T00:00:00Z"],
            "sensors": ["Sentinel-2"],
            "min_similarity": 0.65
        },
        "results": [
            {
                "rank": 1,
                "tile_id": "TILE-S2-43RER-20260220-001",
                "scene_id": "S2B_MSIL2A_20260220T053909_N0512_R005_T43RER",
                "sensor": "Sentinel-2",
                "acquisition_date": "2026-02-20T05:39:09Z",
                "similarity_score": 0.912,
                "center_coordinates": [33.7291, 78.6812],
                "preview_thumbnail_path": "data/precomputed/demo_pair_01_pangong/thumbnail_after.png",
                "matching_keywords": ["road development", "ridge construction", "surface clearance"]
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
                "matching_keywords": ["unpaved track", "ridgeline terrain"]
            }
        ],
        "total_candidates_scanned": 1240,
        "execution_time_ms": 42.6,
        "index_type_used": "FAISS_IVFFlat_InnerProduct"
    }

    # 5. Analyst Decision & Audit Crypto Block
    # Using SHA-256 fallback simulation for initial mock block
    prev_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    payload_str = f"CHG-2026-0042|CONFIRMED|CRITICAL|ANALYST-DEF-712|2026-02-25T11:30:00Z"
    payload_hash = generate_sha256(payload_str)
    chain_hash = generate_sha256(prev_hash + payload_hash)
    mock_pubkey = "a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90"
    mock_sig = generate_sha256(chain_hash + mock_pubkey) * 2  # 128 chars

    analyst_decision = {
        "schema_version": "1.0.0",
        "decision_id": "DEC-2026-0105",
        "change_record_id": "CHG-2026-0042",
        "analyst_id": "ANALYST-DEF-712",
        "analyst_station_id": "STATION-ALPHA-AIRGAP",
        "decision": "CONFIRMED",
        "tactical_priority": "CRITICAL",
        "notes": "Verified against Sentinel-2 multispectral baseline. Confirmed tactical ridgeline spur road construction.",
        "timestamp": "2026-02-25T11:30:00Z",
        "audit_crypto": {
            "block_index": 1,
            "previous_block_hash": prev_hash,
            "payload_hash": payload_hash,
            "chain_hash": chain_hash,
            "analyst_public_key": mock_pubkey,
            "signature": mock_sig
        }
    }

    # 6. Precomputed Intelligence Briefing Text
    briefing_text = """TACTICAL SATELLITE INTELLIGENCE BRIEF
SECURITY CLASSIFICATION: RESTRICTED / AIR-GAPPED
SECTOR: PANGONG TSO NORTH RIDGE (MGRS: 43RER12345678)
GENERATED: 2026-02-25T11:35:00Z
FACTS RECORD REF: CHG-2026-0042

1. EXECUTIVE SUMMARY
A high-confidence tactical change has been confirmed in the Pangong Tso North Ridge Sector. Multi-temporal change analysis comparing Sentinel-2 observations from 2025-11-10 to 2026-02-20 indicates newly developed spur road infrastructure with associated surface clearance.

2. VERIFIED CHANGES OBSERVED (1 Event)
- Event ID: CHG-2026-0042
- Classification: Road Development
- Location: 33.7291° N, 78.6812° E (MGRS 43RER12345678)
- Dimensional Metrics: Linear length ~1,420 meters, estimated width 10.0 meters, total clearance footprint ~14,200 sq meters.
- Earliest Supported Date: 2026-02-20T05:39:09Z
- Model Attribution: Bitemporal Image Transformer (BIT) & Change Vector Analysis (CVA)
- Confidence Score: 0.94 (HIGH PRECISION)

3. SENSOR PROVENANCE & DATA INTEGRITY
- Primary Platform: Sentinel-2 Multi-Spectral Instrument (ESA Copernicus open archive).
- Pixel Reconstruction Status: Genuine observation. Fmask cloud screening verified 0% gap-filling (is_reconstructed_or_gap_filled = FALSE).

4. ANALYST ACTION ITEMS & AUDIT STATUS
- Duty Analyst ANALYST-DEF-712 CONFIRMED this finding at 2026-02-25T11:30:00Z under Priority CRITICAL.
- Audit Log Entry DEC-2026-0105 committed to BLAKE3 hash chain with Ed25519 digital signature.
"""

    # Write files to disk
    with open(demo_dir / "tile_before.json", "w") as f:
        json.dump(tile_before, f, indent=2)

    with open(demo_dir / "tile_after.json", "w") as f:
        json.dump(tile_after, f, indent=2)

    with open(demo_dir / "facts_record.json", "w") as f:
        json.dump(facts_record, f, indent=2)

    with open(demo_dir / "retrieval_result.json", "w") as f:
        json.dump(retrieval_result, f, indent=2)

    with open(demo_dir / "analyst_decision.json", "w") as f:
        json.dump(analyst_decision, f, indent=2)

    with open(demo_dir / "briefing.txt", "w") as f:
        f.write(briefing_text)

    print("Successfully generated all mock artifacts in data/precomputed/demo_pair_01_pangong!")


if __name__ == "__main__":
    main()
