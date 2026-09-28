#!/usr/bin/env python3
"""
SentinelEye - Synthetic Test Data Generator
Generates realistic, schema-compliant mock data for all 3 demo pairs and testing without external imagery.
Creates:
  1. demo_pair_01_pangong (Northern Border - Road Development, Sentinel-2)
  2. demo_pair_02_desert_outpost (Western Sector - Tactical Revetments, Sentinel-1 SAR)
  3. demo_pair_03_cloud_gap_fill (Eastern Sector - Mountain Outpost, Fmask Gap-Fill Warning)
Includes synthetic quicklook PNG thumbnails and change mask overlays.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import numpy as np
import cv2


def generate_sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def create_synthetic_png_pair(out_dir: Path, scenario_type: str = "road"):
    """
    Creates realistic synthetic 512x512 before/after images and binary change mask PNGs.
    """
    h, w = 512, 512

    # Baseline before image: terrain texture
    rng = np.random.RandomState(42)
    before_img = rng.randint(90, 140, (h, w, 3), dtype=np.uint8)

    # Add gentle landscape gradient
    for y in range(h):
        before_img[y, :, 0] = np.clip(before_img[y, :, 0] + (y // 8), 0, 255)
        before_img[y, :, 1] = np.clip(before_img[y, :, 1] + (y // 10), 0, 255)

    after_img = before_img.copy()
    change_mask = np.zeros((h, w), dtype=np.uint8)

    if scenario_type == "road":
        # Draw spur road across ridge: darker paved track in after_img
        cv2.line(after_img, (120, 240), (390, 250), (45, 50, 55), 14)
        cv2.line(change_mask, (120, 240), (390, 250), 255, 14)
        # Staging yard
        cv2.rectangle(after_img, (350, 230), (410, 290), (60, 65, 70), -1)
        cv2.rectangle(change_mask, (350, 230), (410, 290), 255, -1)
    elif scenario_type == "sar_outpost":
        # SAR coherence difference: metallic scatterers / revetments
        for offset in [0, 40, 80]:
            cv2.circle(after_img, (220 + offset, 256), 18, (230, 230, 240), -1)
            cv2.circle(change_mask, (220 + offset, 256), 18, 255, -1)
        cv2.line(after_img, (180, 200), (340, 200), (220, 220, 230), 8)
        cv2.line(change_mask, (180, 200), (340, 200), 255, 8)
    else:  # cloud gap fill
        # Mountain clearance
        cv2.rectangle(after_img, (200, 180), (320, 310), (80, 85, 90), -1)
        cv2.rectangle(change_mask, (200, 180), (320, 310), 255, -1)
        # Cloud artifact on before image
        cv2.circle(before_img, (280, 250), 60, (245, 248, 255), -1)

    cv2.imwrite(str(out_dir / "thumbnail_before.png"), before_img)
    cv2.imwrite(str(out_dir / "thumbnail_after.png"), after_img)
    cv2.imwrite(str(out_dir / "change_mask.png"), change_mask)


def generate_scenario_1_pangong(root: Path):
    s_dir = root / "demo_pair_01_pangong"
    s_dir.mkdir(parents=True, exist_ok=True)
    create_synthetic_png_pair(s_dir, "road")

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
            "centroid": [33.7291, 78.6812]
        },
        "bands": ["B02", "B03", "B04", "B08"],
        "cloud_cover_percentage": 0.2,
        "processing_steps_applied": [
            "radiometric_calibration", "orthorectification", "fmask_cloud_masking", "coregistration_phase_correlation"
        ],
        "source_provenance": {
            "agency": "ESA Copernicus",
            "license": "Open Access / Sovereign Defence Use",
            "archive_checksum_sha256": generate_sha256("scene_before_pangong"),
            "ingested_at": "2026-02-25T08:00:00Z",
            "local_file_path": "data/precomputed/demo_pair_01_pangong/thumbnail_before.png"
        }
    }

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
            "centroid": [33.7291, 78.6812]
        },
        "bands": ["B02", "B03", "B04", "B08"],
        "cloud_cover_percentage": 1.1,
        "processing_steps_applied": [
            "radiometric_calibration", "orthorectification", "fmask_cloud_masking", "coregistration_phase_correlation"
        ],
        "source_provenance": {
            "agency": "ESA Copernicus",
            "license": "Open Access / Sovereign Defence Use",
            "archive_checksum_sha256": generate_sha256("scene_after_pangong"),
            "ingested_at": "2026-02-25T08:05:00Z",
            "local_file_path": "data/precomputed/demo_pair_01_pangong/thumbnail_after.png"
        }
    }

    facts_record = {
        "schema_version": "1.0.0",
        "change_id": "CHG-2026-0042",
        "location": {
            "crs": "EPSG:4326",
            "centroid": [33.7291, 78.6812],
            "mgrs_grid_ref": "43RER12345678",
            "region_name": "Pangong Tso North Ridge Sector"
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
            "surface_type": "compacted_earth_paved"
        }
    }

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
                "preview_thumbnail_path": "data/precomputed/demo_pair_01_pangong/thumbnail_after.png"
            }
        ],
        "total_candidates_scanned": 1240,
        "execution_time_ms": 42.6,
        "index_type_used": "FAISS_IVFFlat_InnerProduct"
    }

    prev_hash = "0" * 64
    payload_hash = generate_sha256("CHG-2026-0042|CONFIRMED|CRITICAL|ANALYST-DEF-712|2026-02-25T11:30:00Z")
    chain_hash = generate_sha256(prev_hash + payload_hash)
    mock_pubkey = "a1b2c3d4" * 8
    mock_sig = generate_sha256(chain_hash + mock_pubkey) * 2

    analyst_decision = {
        "schema_version": "1.0.0",
        "decision_id": "DEC-2026-0105",
        "change_record_id": "CHG-2026-0042",
        "analyst_id": "ANALYST-DEF-712",
        "decision": "CONFIRMED",
        "tactical_priority": "CRITICAL",
        "notes": "Verified against Sentinel-2 multispectral baseline. Confirmed tactical spur road development.",
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

    briefing = """TACTICAL SATELLITE INTELLIGENCE BRIEF
SECURITY CLASSIFICATION: RESTRICTED / AIR-GAPPED
AOI / SECTOR: PANGONG TSO NORTH RIDGE (MGRS: 43RER12345678)
GENERATED: 2026-02-25T11:35:00Z
TARGET CHANGE REF(S): CHG-2026-0042

1. EXECUTIVE SUMMARY
A high-confidence tactical change has been confirmed in the Pangong Tso North Ridge Sector. Multi-temporal change analysis comparing Sentinel-2 observations from 2025-11-10 to 2026-02-20 indicates newly developed spur road infrastructure with associated surface clearance covering ~14,200 sq meters.

2. VERIFIED CHANGES OBSERVED (1 Event)
- Event ID: CHG-2026-0042
  • Classification: Road Development
  • Coordinates: 33.7291° N, 78.6812° E (MGRS: 43RER12345678)
  • Physical Footprint: 14,200.0 sq meters (Length: ~1,420 m, Width: ~10 m)
  • Earliest Observation Date: 2026-02-20T05:39:09Z
  • Confidence Score: 94.0% (Model attribution: BIT, CVA)
  • Sovereign Data Integrity: GENUINE DIRECT SENSOR OBSERVATION

3. SENSOR PROVENANCE & DATA INTEGRITY
- Primary Platform: Sentinel-2 Multi-Spectral Instrument (ESA Copernicus open archive).
- Pixel Reconstruction Status: 100% cloud-free, genuinely observed pixels (is_reconstructed_or_gap_filled = FALSE).

4. ANALYST ACTION ITEMS
- Duty Analyst ANALYST-DEF-712 CONFIRMED this finding at 2026-02-25T11:30:00Z under Priority CRITICAL.
- Audit Log Entry DEC-2026-0105 committed to BLAKE3 hash chain with Ed25519 digital signature.
"""

    with open(s_dir / "tile_before.json", "w") as f:
        json.dump(tile_before, f, indent=2)
    with open(s_dir / "tile_after.json", "w") as f:
        json.dump(tile_after, f, indent=2)
    with open(s_dir / "facts_record.json", "w") as f:
        json.dump(facts_record, f, indent=2)
    with open(s_dir / "retrieval_result.json", "w") as f:
        json.dump(retrieval_result, f, indent=2)
    with open(s_dir / "analyst_decision.json", "w") as f:
        json.dump(analyst_decision, f, indent=2)
    with open(s_dir / "briefing.txt", "w") as f:
        f.write(briefing)


def generate_scenario_2_desert_outpost(root: Path):
    s_dir = root / "demo_pair_02_desert_outpost"
    s_dir.mkdir(parents=True, exist_ok=True)
    create_synthetic_png_pair(s_dir, "sar_outpost")

    tile_before = {
        "schema_version": "1.0.0",
        "tile_id": "TILE-S1-42RUH-20251201-002",
        "scene_id": "S1A_IW_GRDH_1SDV_20251201T010512_N001_R012_T42RUH",
        "sensor": "Sentinel-1-SAR",
        "acquisition_date": "2025-12-01T01:05:12Z",
        "resolution_meters": 10.0,
        "coordinates": {
            "crs": "EPSG:4326",
            "bbox": [70.8500, 27.1500, 70.9200, 27.2200],
            "centroid": [27.1845, 70.8921]
        },
        "bands": ["VV", "VH"],
        "cloud_cover_percentage": None,
        "processing_steps_applied": [
            "sar_radiometric_calibration", "range_doppler_terrain_correction", "speckle_filtering_lee"
        ],
        "source_provenance": {
            "agency": "ESA Copernicus",
            "license": "Open Access / Sovereign Defence Use",
            "archive_checksum_sha256": generate_sha256("scene_before_desert"),
            "ingested_at": "2026-02-25T08:10:00Z",
            "local_file_path": "data/precomputed/demo_pair_02_desert_outpost/thumbnail_before.png"
        }
    }

    tile_after = {
        "schema_version": "1.0.0",
        "tile_id": "TILE-S1-42RUH-20260215-002",
        "scene_id": "S1A_IW_GRDH_1SDV_20260215T010514_N001_R012_T42RUH",
        "sensor": "Sentinel-1-SAR",
        "acquisition_date": "2026-02-15T01:05:14Z",
        "resolution_meters": 10.0,
        "coordinates": {
            "crs": "EPSG:4326",
            "bbox": [70.8500, 27.1500, 70.9200, 27.2200],
            "centroid": [27.1845, 70.8921]
        },
        "bands": ["VV", "VH"],
        "cloud_cover_percentage": None,
        "processing_steps_applied": [
            "sar_radiometric_calibration", "range_doppler_terrain_correction", "speckle_filtering_lee"
        ],
        "source_provenance": {
            "agency": "ESA Copernicus",
            "license": "Open Access / Sovereign Defence Use",
            "archive_checksum_sha256": generate_sha256("scene_after_desert"),
            "ingested_at": "2026-02-25T08:15:00Z",
            "local_file_path": "data/precomputed/demo_pair_02_desert_outpost/thumbnail_after.png"
        }
    }

    facts_record = {
        "schema_version": "1.0.0",
        "change_id": "CHG-2026-0089",
        "location": {
            "crs": "EPSG:4326",
            "centroid": [27.1845, 70.8921],
            "mgrs_grid_ref": "42RUH89211845",
            "region_name": "Thar Western Sector Outpost"
        },
        "before_tile_ref": {
            "tile_id": "TILE-S1-42RUH-20251201-002",
            "acquisition_date": "2025-12-01T01:05:12Z",
            "sensor": "Sentinel-1-SAR"
        },
        "after_tile_ref": {
            "tile_id": "TILE-S1-42RUH-20260215-002",
            "acquisition_date": "2026-02-15T01:05:14Z",
            "sensor": "Sentinel-1-SAR"
        },
        "change_type": "vehicle_depot_activity",
        "earliest_supported_observation_date": "2026-02-15T01:05:14Z",
        "confidence_score": 0.91,
        "area_sq_meters": 8600.0,
        "source_models": ["BIT", "BAN", "YOLO_SAHI"],
        "is_reconstructed_or_gap_filled": False,
        "gap_fill_details": {
            "gap_fill_method": "none",
            "gap_pixel_ratio": 0.0
        },
        "tactical_attributes": {
            "sar_coherence_delta": 0.68,
            "estimated_vehicle_revetments": 3,
            "protective_berm_length_m": 420.0
        }
    }

    briefing = """TACTICAL SATELLITE INTELLIGENCE BRIEF
SECURITY CLASSIFICATION: RESTRICTED / AIR-GAPPED
AOI / SECTOR: THAR WESTERN SECTOR OUTPOST (MGRS: 42RUH89211845)
GENERATED: 2026-02-25T11:40:00Z
TARGET CHANGE REF(S): CHG-2026-0089

1. EXECUTIVE SUMMARY
SAR coherence difference analysis via Sentinel-1 has detected new vehicle revetments and protective earthen berming in the Thar Western Sector Outpost. Detections penetrate dust and nocturnal conditions with high radar backscatter signatures.

2. VERIFIED CHANGES OBSERVED (1 Event)
- Event ID: CHG-2026-0089
  • Classification: Vehicle Depot Activity
  • Coordinates: 27.1845° N, 70.8921° E (MGRS: 42RUH89211845)
  • Physical Footprint: 8,600.0 sq meters
  • Earliest Observation Date: 2026-02-15T01:05:14Z
  • Confidence Score: 91.0% (Model attribution: BIT, BAN, YOLO_SAHI)
  • Sovereign Data Integrity: GENUINE DIRECT SENSOR OBSERVATION

3. SENSOR PROVENANCE & DATA INTEGRITY
- Primary Sensor: Sentinel-1 C-band SAR (IW VV/VH).
- All-weather radar observation verified without cloud interference.
"""

    with open(s_dir / "tile_before.json", "w") as f:
        json.dump(tile_before, f, indent=2)
    with open(s_dir / "tile_after.json", "w") as f:
        json.dump(tile_after, f, indent=2)
    with open(s_dir / "facts_record.json", "w") as f:
        json.dump(facts_record, f, indent=2)
    with open(s_dir / "briefing.txt", "w") as f:
        f.write(briefing)


def generate_scenario_3_cloud_gap_fill(root: Path):
    s_dir = root / "demo_pair_03_cloud_gap_fill"
    s_dir.mkdir(parents=True, exist_ok=True)
    create_synthetic_png_pair(s_dir, "cloud_gap")

    tile_before = {
        "schema_version": "1.0.0",
        "tile_id": "TILE-L8-46RFP-20251015-003",
        "scene_id": "LC08_L2SP_135041_20251015_02_T1",
        "sensor": "Landsat-8",
        "acquisition_date": "2025-10-15T04:22:10Z",
        "resolution_meters": 15.0,
        "coordinates": {
            "crs": "EPSG:4326",
            "bbox": [92.0800, 27.5400, 92.1600, 27.6200],
            "centroid": [27.5810, 92.1245]
        },
        "bands": ["B02", "B03", "B04", "B05"],
        "cloud_cover_percentage": 22.4,
        "processing_steps_applied": [
            "radiometric_calibration", "fmask_cloud_masking", "temporal_gap_filling"
        ],
        "source_provenance": {
            "agency": "USGS / ISRO",
            "license": "Public Domain / Sovereign Defence Use",
            "archive_checksum_sha256": generate_sha256("scene_before_cloud"),
            "ingested_at": "2026-02-25T08:20:00Z",
            "local_file_path": "data/precomputed/demo_pair_03_cloud_gap_fill/thumbnail_before.png"
        }
    }

    tile_after = {
        "schema_version": "1.0.0",
        "tile_id": "TILE-S2-46RFP-20260218-003",
        "scene_id": "S2B_MSIL2A_20260218T042511_N0512_R005_T46RFP",
        "sensor": "Sentinel-2",
        "acquisition_date": "2026-02-18T04:25:11Z",
        "resolution_meters": 10.0,
        "coordinates": {
            "crs": "EPSG:4326",
            "bbox": [92.0800, 27.5400, 92.1600, 27.6200],
            "centroid": [27.5810, 92.1245]
        },
        "bands": ["B02", "B03", "B04", "B08"],
        "cloud_cover_percentage": 3.8,
        "processing_steps_applied": [
            "radiometric_calibration", "orthorectification", "fmask_cloud_masking"
        ],
        "source_provenance": {
            "agency": "ESA Copernicus",
            "license": "Open Access / Sovereign Defence Use",
            "archive_checksum_sha256": generate_sha256("scene_after_cloud"),
            "ingested_at": "2026-02-25T08:25:00Z",
            "local_file_path": "data/precomputed/demo_pair_03_cloud_gap_fill/thumbnail_after.png"
        }
    }

    # CRITICAL: Demonstrates sovereign provenance audit warning!
    facts_record = {
        "schema_version": "1.0.0",
        "change_id": "CHG-2026-0112",
        "location": {
            "crs": "EPSG:4326",
            "centroid": [27.5810, 92.1245],
            "mgrs_grid_ref": "46RFP12455810",
            "region_name": "Arunachal Eastern Mountain Ridge"
        },
        "before_tile_ref": {
            "tile_id": "TILE-L8-46RFP-20251015-003",
            "acquisition_date": "2025-10-15T04:22:10Z",
            "sensor": "Landsat-8"
        },
        "after_tile_ref": {
            "tile_id": "TILE-S2-46RFP-20260218-003",
            "acquisition_date": "2026-02-18T04:25:11Z",
            "sensor": "Sentinel-2"
        },
        "change_type": "construction",
        "earliest_supported_observation_date": "2026-02-18T04:25:11Z",
        "confidence_score": 0.79,
        "area_sq_meters": 6200.0,
        "source_models": ["BIT", "CVA"],
        "is_reconstructed_or_gap_filled": True,  # PROVENANCE AUDIT WARNING
        "gap_fill_details": {
            "gap_fill_method": "fmask_temporal_interpolation",
            "gap_pixel_ratio": 0.28
        },
        "tactical_attributes": {
            "structure_type": "mountain_outpost_helipad",
            "cloud_overlap_status": "partially_interpolated_baseline"
        }
    }

    briefing = """TACTICAL SATELLITE INTELLIGENCE BRIEF
SECURITY CLASSIFICATION: RESTRICTED / AIR-GAPPED
AOI / SECTOR: ARUNACHAL EASTERN MOUNTAIN RIDGE (MGRS: 46RFP12455810)
GENERATED: 2026-02-25T11:45:00Z
TARGET CHANGE REF(S): CHG-2026-0112

1. EXECUTIVE SUMMARY
Multi-temporal change analysis has flagged new mountain outpost and helipad construction in the Arunachal Eastern Mountain Ridge. Multi-sensor cross-comparison was utilized (Landsat-8 baseline against Sentinel-2 observation).

2. VERIFIED CHANGES OBSERVED (1 Event)
- Event ID: CHG-2026-0112
  • Classification: Construction (Helipad & Outpost Footprint)
  • Coordinates: 27.5810° N, 92.1245° E (MGRS: 46RFP12455810)
  • Physical Footprint: 6,200.0 sq meters
  • Earliest Observation Date: 2026-02-18T04:25:11Z
  • Confidence Score: 79.0% (Confidence adjusted due to cloud interpolation)
  • Sovereign Data Integrity: ⚠️ RECONSTRUCTED/GAP-FILLED WARNING (28.0% of baseline footprint reconstructed)

3. SENSOR PROVENANCE & DATA INTEGRITY
- Primary Baseline: Landsat-8 Operational Land Imager.
- Subsequent Observation: Sentinel-2 MSI.
- ⚠️ AUDIT DISCLAIMER: Fmask screening identified 28% cloud/cloud-shadow overlap on baseline scene. Pixels were gap-filled using temporal interpolation. Analyst caution advised; ground reconnaissance or SAR confirmation recommended before tactical escalation.
"""

    with open(s_dir / "tile_before.json", "w") as f:
        json.dump(tile_before, f, indent=2)
    with open(s_dir / "tile_after.json", "w") as f:
        json.dump(tile_after, f, indent=2)
    with open(s_dir / "facts_record.json", "w") as f:
        json.dump(facts_record, f, indent=2)
    with open(s_dir / "briefing.txt", "w") as f:
        f.write(briefing)


def main():
    repo_root = Path(__file__).resolve().parent.parent
    precomputed_dir = repo_root / "data" / "precomputed"
    precomputed_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating full suite of 3 demonstration scenarios in: {precomputed_dir}")

    generate_scenario_1_pangong(precomputed_dir)
    print("  ✓ Scenario 1: Northern Border - Pangong Lake Sector generated.")

    generate_scenario_2_desert_outpost(precomputed_dir)
    print("  ✓ Scenario 2: Western Sector - Thar Desert Outpost generated.")

    generate_scenario_3_cloud_gap_fill(precomputed_dir)
    print("  ✓ Scenario 3: Eastern Sector - Arunachal Mountain Ridge (Fmask Gap-Fill Warning) generated.")

    print("All 3 precomputed demonstration scenarios successfully generated with PNGs and metadata!")


if __name__ == "__main__":
    main()
