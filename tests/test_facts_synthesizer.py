"""
Unit & Integration tests for the Facts Dictionary Synthesizer.
Verifies polygon contour extraction, physical metric measurement,
and sovereign air-gap pixel provenance auditing (Fmask cloud/gap-fill overlap).
"""

import pytest
import numpy as np

from pipeline.facts_synthesizer import (
    extract_polygons_from_mask,
    check_gap_fill_intersection,
    classify_change_cluster,
    mask_to_change_records,
)
from schemas import ChangeType, TileMetadata, SensorType, GeoCoordinates, SourceProvenance


def test_extract_polygons_from_mask():
    mask = np.zeros((512, 512), dtype=np.uint8)
    # Cluster 1: 40x40 square = 1600 pixels (valid)
    mask[100:140, 100:140] = 255
    # Cluster 2: 3x3 square = 9 pixels (should be filtered out by min_area_pixels=25)
    mask[300:303, 300:303] = 255

    clusters = extract_polygons_from_mask(mask, min_area_pixels=25)
    assert len(clusters) == 1
    cnt, area, (x, y, w, h) = clusters[0]
    assert area >= 1500
    assert w == 40
    assert h == 40


def test_check_gap_fill_intersection_clear():
    # Polygon contour
    contour = np.array([[[50, 50]], [[100, 50]], [[100, 100]], [[50, 100]]], dtype=np.int32)
    # All pixels valid (1)
    fmask_valid = np.ones((512, 512), dtype=np.uint8)

    is_gap_filled, gap_ratio = check_gap_fill_intersection(contour, fmask_valid)
    assert is_gap_filled is False
    assert gap_ratio == 0.0


def test_check_gap_fill_intersection_with_clouds():
    contour = np.array([[[50, 50]], [[100, 50]], [[100, 100]], [[50, 100]]], dtype=np.int32)
    # Fmask has invalid/cloud pixels (0) overlapping top half of polygon
    fmask_valid = np.ones((512, 512), dtype=np.uint8)
    fmask_valid[50:75, 50:100] = 0  # 50% of the box is invalid

    is_gap_filled, gap_ratio = check_gap_fill_intersection(contour, fmask_valid)
    assert is_gap_filled is True
    assert 0.40 <= gap_ratio <= 0.60


def test_classify_change_cluster():
    # High aspect ratio -> road
    assert classify_change_cluster(area_sq_meters=5000, aspect_ratio=4.2) == ChangeType.ROAD_DEVELOPMENT
    # Large area compact -> surface clearance
    assert classify_change_cluster(area_sq_meters=15000, aspect_ratio=1.2) == ChangeType.SURFACE_CLEARANCE
    # Medium area -> construction
    assert classify_change_cluster(area_sq_meters=4000, aspect_ratio=1.5) == ChangeType.CONSTRUCTION


def test_mask_to_change_records_full():
    mask = np.zeros((512, 512), dtype=np.uint8)
    mask[200:260, 100:300] = 255  # Road-like strip

    before_meta = {
        "tile_id": "TILE-B-001",
        "acquisition_date": "2025-11-10T05:38:51Z",
        "sensor": "Sentinel-2",
        "coordinates": {"bbox": [78.65, 33.70, 78.71, 33.75]},
        "resolution_meters": 10.0,
    }
    after_meta = {
        "tile_id": "TILE-A-001",
        "acquisition_date": "2026-02-20T05:39:09Z",
        "sensor": "Sentinel-2",
    }

    records = mask_to_change_records(
        change_mask=mask,
        before_meta=before_meta,
        after_meta=after_meta,
        min_area_pixels=50,
        region_name="Test Ridge Sector",
    )

    assert len(records) == 1
    rec = records[0]
    assert rec.change_id.startswith("CHG-2026")
    assert rec.location.region_name == "Test Ridge Sector"
    assert rec.area_sq_meters > 5000
    assert rec.is_reconstructed_or_gap_filled is False
    assert rec.before_tile_ref.tile_id == "TILE-B-001"
    assert rec.after_tile_ref.tile_id == "TILE-A-001"
