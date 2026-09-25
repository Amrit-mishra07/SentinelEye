"""
SentinelEye - Satellite Tile Metadata Schema
Defines metadata, spatial bounding geometry, sensor parameters, and preprocessing provenance.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class SensorType(str, Enum):
    SENTINEL_2 = "Sentinel-2"
    SENTINEL_1_SAR = "Sentinel-1-SAR"
    LANDSAT_8 = "Landsat-8"
    LANDSAT_9 = "Landsat-9"
    BHUVAN_CARTOSAT = "Bhuvan-Cartosat"
    CUSTOM_UAV = "Custom-UAV"


class GeoCoordinates(BaseModel):
    crs: str = Field(
        default="EPSG:4326",
        description="Coordinate Reference System (default EPSG:4326 WGS84)",
    )
    bbox: List[float] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="Bounding box [min_lon, min_lat, max_lon, max_lat]",
    )
    centroid: List[float] = Field(
        ...,
        min_length=2,
        max_length=2,
        description="Center coordinate [latitude, longitude]",
    )
    geometry: Optional[Dict[str, Any]] = Field(
        default=None,
        description="GeoJSON geometry object (e.g. Polygon coordinates)",
    )


class SourceProvenance(BaseModel):
    agency: str = Field(..., description="Data provider or space agency (e.g., ESA, ISRO, USGS)")
    license: str = Field(..., description="Data licensing declaration")
    archive_checksum_sha256: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="SHA-256 hash of original archive package for tamper-evidence",
    )
    ingested_at: str = Field(..., description="ISO 8601 timestamp of local ingestion")
    local_file_path: str = Field(..., description="Relative local file path to raster tile")


class TileMetadata(BaseModel):
    schema_version: str = Field(default="1.0.0", description="Schema specification version")
    tile_id: str = Field(..., description="Unique tile identifier (e.g., TILE-S2-43RER-20260220-001)")
    scene_id: str = Field(..., description="Original scene product ID")
    sensor: SensorType = Field(..., description="Originating satellite sensor platform")
    acquisition_date: str = Field(..., description="Acquisition timestamp in ISO 8601 UTC format")
    resolution_meters: float = Field(..., gt=0.0, description="Spatial resolution in meters per pixel")
    coordinates: GeoCoordinates = Field(..., description="Spatial bounding box and centroid")
    bands: List[str] = Field(..., description="Ordered list of spectral/polarimetric bands (e.g., ['B02', 'B03', 'B04', 'B08'])")
    cloud_cover_percentage: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Cloud coverage percentage (null for SAR)",
    )
    processing_steps_applied: List[str] = Field(
        default_factory=list,
        description="Ordered list of preprocessing steps applied (e.g., orthorectification, fmask_cloud_masking, coregistration)",
    )
    source_provenance: SourceProvenance = Field(..., description="Source provenance and tamper-evident checksum")

    @field_validator("bands")
    @classmethod
    def validate_bands_non_empty(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("Tile must contain at least one spectral band")
        return v
