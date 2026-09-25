"""
SentinelEye - Semantic Retrieval Result Schema
Defines responses for text-to-image and image-to-image semantic search via RemoteCLIP and FAISS.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class QueryType(str, Enum):
    TEXT = "text"
    IMAGE_CROP = "image_crop"
    MULTIMODAL = "multimodal"


class RetrievalFilters(BaseModel):
    aoi_bbox: Optional[List[float]] = Field(
        default=None,
        min_length=4,
        max_length=4,
        description="Bounding box [min_lon, min_lat, max_lon, max_lat]",
    )
    date_range: Optional[List[str]] = Field(
        default=None,
        min_length=2,
        max_length=2,
        description="[start_date, end_date] in ISO 8601 UTC format",
    )
    sensors: Optional[List[str]] = Field(
        default=None,
        description="Filter by sensor names (e.g. ['Sentinel-2', 'Landsat-8'])",
    )
    min_similarity: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum cosine similarity cutoff threshold",
    )


class ScoredTileCandidate(BaseModel):
    rank: int = Field(..., ge=1, description="1-based search result rank")
    tile_id: str = Field(..., description="Unique tile identifier")
    scene_id: str = Field(..., description="Parent satellite scene ID")
    sensor: str = Field(..., description="Sensor platform")
    acquisition_date: str = Field(..., description="Acquisition timestamp in ISO 8601 UTC format")
    similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Normalized cosine similarity between query and tile embedding (0.0 to 1.0)",
    )
    center_coordinates: List[float] = Field(
        ...,
        min_length=2,
        max_length=2,
        description="Center coordinate [latitude, longitude]",
    )
    preview_thumbnail_path: Optional[str] = Field(
        default=None,
        description="Local relative path to pre-rendered quicklook thumbnail",
    )
    matching_keywords: List[str] = Field(
        default_factory=list,
        description="Key semantic concepts activated in the visual crop",
    )


class RetrievalResult(BaseModel):
    schema_version: str = Field(default="1.0.0", description="Schema specification version")
    query_id: str = Field(..., description="Unique query session identifier")
    query_type: QueryType = Field(..., description="Input query modality")
    query_content: str = Field(
        ...,
        description="Natural language query string or relative path to query reference image crop",
    )
    applied_filters: RetrievalFilters = Field(
        default_factory=RetrievalFilters,
        description="Spatial, temporal, and sensor constraints applied during index search",
    )
    results: List[ScoredTileCandidate] = Field(
        default_factory=list,
        description="Ranked list of tile candidates ordered by descending similarity score",
    )
    total_candidates_scanned: int = Field(
        default=0,
        ge=0,
        description="Total vector embeddings evaluated across the offline index",
    )
    execution_time_ms: float = Field(
        ...,
        ge=0.0,
        description="Search execution latency in milliseconds",
    )
    index_type_used: str = Field(
        default="FAISS_IVFFlat_InnerProduct",
        description="Vector indexing strategy and similarity metric",
    )
