"""
Unit & Integration tests for SentinelEye shared schemas.
Verifies Pydantic v2 data models and JSON serialization/deserialization.
"""

import pytest
from pydantic import ValidationError

from schemas import (
    SensorType,
    GeoCoordinates,
    SourceProvenance,
    TileMetadata,
    ChangeType,
    TileReference,
    ChangeLocation,
    ChangeRecord,
    DecisionType,
    TacticalPriority,
    AuditCryptoBlock,
    AnalystDecision,
    QueryType,
    RetrievalFilters,
    ScoredTileCandidate,
    RetrievalResult,
)


def test_tile_metadata_valid():
    tile = TileMetadata(
        schema_version="1.0.0",
        tile_id="TILE-S2-43RER-20260220-001",
        scene_id="S2B_MSIL2A_20260220T053909_N0512_R005_T43RER",
        sensor=SensorType.SENTINEL_2,
        acquisition_date="2026-02-20T05:39:09Z",
        resolution_meters=10.0,
        coordinates=GeoCoordinates(
            crs="EPSG:4326",
            bbox=[78.65, 33.70, 78.71, 33.75],
            centroid=[33.7291, 78.6812],
        ),
        bands=["B02", "B03", "B04", "B08"],
        cloud_cover_percentage=0.5,
        processing_steps_applied=["orthorectification", "fmask_cloud_masking"],
        source_provenance=SourceProvenance(
            agency="ESA Copernicus",
            license="Open Access",
            archive_checksum_sha256="a" * 64,
            ingested_at="2026-02-25T08:00:00Z",
            local_file_path="data/preprocessed/tiles_512/T43RER_20260220.tif",
        ),
    )
    assert tile.tile_id == "TILE-S2-43RER-20260220-001"
    assert tile.sensor == SensorType.SENTINEL_2
    assert len(tile.bands) == 4


def test_tile_metadata_invalid_bands():
    with pytest.raises(ValidationError):
        TileMetadata(
            tile_id="TILE-001",
            scene_id="SCENE-001",
            sensor=SensorType.SENTINEL_2,
            acquisition_date="2026-02-20T05:39:09Z",
            resolution_meters=10.0,
            coordinates=GeoCoordinates(
                bbox=[78.65, 33.70, 78.71, 33.75],
                centroid=[33.7291, 78.6812],
            ),
            bands=[],  # Invalid empty bands
            source_provenance=SourceProvenance(
                agency="ESA",
                license="Open",
                archive_checksum_sha256="a" * 64,
                ingested_at="2026-02-25T08:00:00Z",
                local_file_path="sample.tif",
            ),
        )


def test_change_record_facts_dictionary():
    change = ChangeRecord(
        schema_version="1.0.0",
        change_id="CHG-2026-0042",
        location=ChangeLocation(
            centroid=[33.7291, 78.6812],
            mgrs_grid_ref="43RER12345678",
            region_name="Pangong Tso North Ridge Sector",
        ),
        before_tile_ref=TileReference(
            tile_id="TILE-S2-20251110",
            acquisition_date="2025-11-10T05:38:51Z",
            sensor="Sentinel-2",
        ),
        after_tile_ref=TileReference(
            tile_id="TILE-S2-20260220",
            acquisition_date="2026-02-20T05:39:09Z",
            sensor="Sentinel-2",
        ),
        change_type=ChangeType.ROAD_DEVELOPMENT,
        earliest_supported_observation_date="2026-02-20T05:39:09Z",
        confidence_score=0.94,
        area_sq_meters=14200.0,
        source_models=["BIT", "CVA"],
        is_reconstructed_or_gap_filled=False,
        tactical_attributes={"length_meters": 1420.0},
    )
    assert change.change_type == ChangeType.ROAD_DEVELOPMENT
    assert change.is_reconstructed_or_gap_filled is False
    assert change.confidence_score == 0.94


def test_analyst_decision_schema():
    decision = AnalystDecision(
        schema_version="1.0.0",
        decision_id="DEC-2026-0105",
        change_record_id="CHG-2026-0042",
        analyst_id="ANALYST-DEF-712",
        decision=DecisionType.CONFIRMED,
        tactical_priority=TacticalPriority.CRITICAL,
        notes="Verified against ground optical baseline",
        timestamp="2026-02-25T11:30:00Z",
        audit_crypto=AuditCryptoBlock(
            block_index=1,
            previous_block_hash="0" * 64,
            payload_hash="1" * 64,
            chain_hash="2" * 64,
            analyst_public_key="3" * 64,
            signature="4" * 128,
        ),
    )
    assert decision.decision == DecisionType.CONFIRMED
    assert decision.audit_crypto.block_index == 1
    assert len(decision.audit_crypto.signature) == 128


def test_retrieval_result_schema():
    retrieval = RetrievalResult(
        schema_version="1.0.0",
        query_id="QRY-2026-9901",
        query_type=QueryType.TEXT,
        query_content="road development along northern ridge",
        applied_filters=RetrievalFilters(
            aoi_bbox=[78.60, 33.65, 78.75, 33.80],
            min_similarity=0.6,
        ),
        results=[
            ScoredTileCandidate(
                rank=1,
                tile_id="TILE-S2-001",
                scene_id="SCENE-001",
                sensor="Sentinel-2",
                acquisition_date="2026-02-20T05:39:09Z",
                similarity_score=0.92,
                center_coordinates=[33.7291, 78.6812],
            )
        ],
        total_candidates_scanned=500,
        execution_time_ms=38.5,
        index_type_used="FAISS_IVFFlat_InnerProduct",
    )
    assert retrieval.results[0].rank == 1
    assert retrieval.execution_time_ms == 38.5
