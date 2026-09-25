"""
SentinelEye - Facts Dictionary Change Record Schema
Defines verified change detection facts ingested by the constrained LLM briefing engine.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChangeType(str, Enum):
    CONSTRUCTION = "construction"
    SURFACE_CLEARANCE = "surface_clearance"
    WATER_EXTENT_CHANGE = "water_extent_change"
    ROAD_DEVELOPMENT = "road_development"
    FORTIFICATION_TRENCHING = "fortification_trenching"
    VEGETATION_LOSS = "vegetation_loss"
    VEHICLE_DEPOT_ACTIVITY = "vehicle_depot_activity"
    OTHER_TACTICAL_CHANGE = "other_tactical_change"


class TileReference(BaseModel):
    tile_id: str = Field(..., description="Unique identifier of reference tile")
    acquisition_date: str = Field(..., description="Acquisition timestamp in ISO 8601 UTC format")
    sensor: str = Field(..., description="Sensor platform name")


class ChangeLocation(BaseModel):
    crs: str = Field(default="EPSG:4326", description="Coordinate Reference System")
    centroid: List[float] = Field(
        ...,
        min_length=2,
        max_length=2,
        description="Center coordinate [latitude, longitude]",
    )
    mgrs_grid_ref: Optional[str] = Field(
        default=None,
        description="Military Grid Reference System (MGRS) coordinate (e.g., 43RER12345678)",
    )
    region_name: str = Field(..., description="Human-readable tactical sector or AOI label")
    polygon_geojson: Optional[Dict[str, Any]] = Field(
        default=None,
        description="GeoJSON geometry of the change footprint polygon",
    )


class GapFillDetails(BaseModel):
    gap_fill_method: Optional[str] = Field(
        default="none",
        description="Interpolation or gap-fill method applied (e.g., temporal_linear, sar_coherence_fill, none)",
    )
    gap_pixel_ratio: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Fraction of footprint pixels reconstructed or gap-filled (0.0 to 1.0)",
    )


class ChangeRecord(BaseModel):
    schema_version: str = Field(default="1.0.0", description="Schema specification version")
    change_id: str = Field(
        ...,
        description="Unique identifier for the tactical change fact (e.g., CHG-2026-0042)",
    )
    location: ChangeLocation = Field(..., description="Geospatial position and sector name")
    before_tile_ref: TileReference = Field(..., description="Reference to baseline observation tile")
    after_tile_ref: TileReference = Field(..., description="Reference to subsequent observation tile")
    change_type: ChangeType = Field(..., description="Taxonomy classification of detected change")
    earliest_supported_observation_date: str = Field(
        ...,
        description="Earliest date verified by sensor evidence when this change is observed",
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Fused confidence score from detection models (0.0 to 1.0)",
    )
    area_sq_meters: float = Field(
        ...,
        gt=0.0,
        description="Estimated physical footprint area in square meters",
    )
    source_models: List[str] = Field(
        ...,
        min_length=1,
        description="Models that contributed to detection (e.g., ['BIT', 'CVA', 'BAN', 'YOLO_SAHI'])",
    )
    is_reconstructed_or_gap_filled: bool = Field(
        ...,
        description="CRITICAL AUDIT FLAG: true if any pixel involved was reconstructed/gap-filled vs genuinely observed",
    )
    gap_fill_details: Optional[GapFillDetails] = Field(
        default=None,
        description="Details regarding gap-filling and pixel validity",
    )
    tactical_attributes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value metrics extracted (e.g., length_meters, estimated_width, ndvi_delta, sar_backscatter_delta_db)",
    )
