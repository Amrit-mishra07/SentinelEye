"""
Facts Dictionary Synthesizer.
Converts raw binary change masks + Fmask validity masks into typed ChangeRecord objects.
Performs connected component analysis, polygon extraction, physical metric measurement,
and crucial air-gap/sovereign pixel provenance auditing (is_reconstructed_or_gap_filled).
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import cv2

from schemas import (
    ChangeRecord,
    ChangeLocation,
    TileReference,
    ChangeType,
    GapFillDetails,
    TileMetadata,
)


def extract_polygons_from_mask(
    mask: np.ndarray,
    min_area_pixels: int = 25,
) -> List[Tuple[np.ndarray, float, Tuple[int, int, int, int]]]:
    """
    Finds external contours in a binary change mask and filters by minimum pixel area.
    Returns list of (contour_points, contour_area, (x, y, w, h)).
    """
    if mask is None or mask.size == 0:
        return []

    # Ensure mask is uint8 binary
    binary_mask = (mask > 0).astype(np.uint8) * 255

    contours, _ = cv2.findContours(
        binary_mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    valid_clusters = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area >= min_area_pixels:
            x, y, w, h = cv2.boundingRect(cnt)
            valid_clusters.append((cnt, area, (x, y, w, h)))

    return valid_clusters


def pixel_to_geographic(
    px_x: float,
    px_y: float,
    bbox: List[float],
    img_width: int = 512,
    img_height: int = 512,
) -> Tuple[float, float]:
    """
    Linearly maps image pixel coordinates (x, y) to geographic WGS84 [lat, lon].
    bbox is [min_lon, min_lat, max_lon, max_lat].
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    lon = min_lon + (px_x / img_width) * (max_lon - min_lon)
    # y=0 is at max_lat (top), y=img_height is at min_lat (bottom)
    lat = max_lat - (px_y / img_height) * (max_lat - min_lat)
    return round(lat, 6), round(lon, 6)


def check_gap_fill_intersection(
    contour: np.ndarray,
    fmask_valid_mask: Optional[np.ndarray],
    mask_shape: Tuple[int, int] = (512, 512),
) -> Tuple[bool, float]:
    """
    Audits whether any pixel inside the change polygon falls on a cloud,
    shadow, or gap-filled pixel (where fmask_valid_mask == 0).
    Returns (is_reconstructed_or_gap_filled, gap_pixel_ratio).
    """
    if fmask_valid_mask is None:
        return False, 0.0

    # Create a single polygon mask
    poly_mask = np.zeros(mask_shape, dtype=np.uint8)
    cv2.drawContours(poly_mask, [contour], -1, 255, -1)

    total_poly_pixels = np.count_nonzero(poly_mask)
    if total_poly_pixels == 0:
        return False, 0.0

    # Pixels where fmask is invalid (0) within the polygon
    invalid_mask = (fmask_valid_mask == 0).astype(np.uint8)
    gap_pixels = np.count_nonzero((poly_mask > 0) & (invalid_mask > 0))

    gap_ratio = float(gap_pixels / total_poly_pixels)
    is_gap_filled = bool(gap_pixels > 0)

    return is_gap_filled, round(gap_ratio, 4)


def classify_change_cluster(
    area_sq_meters: float,
    aspect_ratio: float,
    tactical_context: Optional[str] = None,
) -> ChangeType:
    """
    Determines preliminary tactical change classification based on geometry and elongation.
    High elongation (aspect ratio > 3.5) typically signifies road or trench development.
    Broad compact area signifies surface clearance or construction.
    """
    if aspect_ratio >= 3.5:
        return ChangeType.ROAD_DEVELOPMENT
    elif area_sq_meters > 10000:
        return ChangeType.SURFACE_CLEARANCE
    elif area_sq_meters > 2500:
        return ChangeType.CONSTRUCTION
    else:
        return ChangeType.OTHER_TACTICAL_CHANGE


def mask_to_change_records(
    change_mask: np.ndarray,
    before_meta: Any,
    after_meta: Any,
    fmask_valid_mask: Optional[np.ndarray] = None,
    min_area_pixels: int = 25,
    confidence_score: float = 0.90,
    source_models: Optional[List[str]] = None,
    region_name: str = "Tactical AOI",
    id_prefix: str = "CHG-2026",
) -> List[ChangeRecord]:
    """
    Primary Facts Dictionary Synthesizer entrypoint.
    Transforms binary change mask into fully typed ChangeRecord objects.
    """
    if source_models is None:
        source_models = ["BIT", "CVA"]

    # Extract tile properties
    if isinstance(before_meta, dict):
        b_id = before_meta.get("tile_id", "TILE-BEFORE")
        b_date = before_meta.get("acquisition_date", "2025-11-10T05:38:51Z")
        b_sensor = before_meta.get("sensor", "Sentinel-2")
        bbox = before_meta.get("coordinates", {}).get("bbox", [78.65, 33.70, 78.71, 33.75])
        res_m = float(before_meta.get("resolution_meters", 10.0))
    elif isinstance(before_meta, TileMetadata):
        b_id = before_meta.tile_id
        b_date = before_meta.acquisition_date
        b_sensor = before_meta.sensor.value if hasattr(before_meta.sensor, "value") else str(before_meta.sensor)
        bbox = before_meta.coordinates.bbox
        res_m = float(before_meta.resolution_meters)
    else:
        b_id, b_date, b_sensor, bbox, res_m = "TILE-BEFORE", "2025-11-10T05:38:51Z", "Sentinel-2", [78.65, 33.70, 78.71, 33.75], 10.0

    if isinstance(after_meta, dict):
        a_id = after_meta.get("tile_id", "TILE-AFTER")
        a_date = after_meta.get("acquisition_date", "2026-02-20T05:39:09Z")
        a_sensor = after_meta.get("sensor", "Sentinel-2")
    elif isinstance(after_meta, TileMetadata):
        a_id = after_meta.tile_id
        a_date = after_meta.acquisition_date
        a_sensor = after_meta.sensor.value if hasattr(after_meta.sensor, "value") else str(after_meta.sensor)
    else:
        a_id, a_date, a_sensor = "TILE-AFTER", "2026-02-20T05:39:09Z", "Sentinel-2"

    clusters = extract_polygons_from_mask(change_mask, min_area_pixels=min_area_pixels)
    records: List[ChangeRecord] = []

    pixel_area_m2 = res_m * res_m
    img_h, img_w = change_mask.shape[:2]

    for idx, (contour, px_area, (bx, by, bw, bh)) in enumerate(clusters, start=1):
        change_id = f"{id_prefix}-{idx:04d}"

        # Centroid
        m = cv2.moments(contour)
        if m["m00"] != 0:
            cx_px = m["m10"] / m["m00"]
            cy_px = m["m01"] / m["m00"]
        else:
            cx_px = bx + bw / 2.0
            cy_px = by + bh / 2.0

        lat, lon = pixel_to_geographic(cx_px, cy_px, bbox, img_w, img_h)

        # Polygon coordinates in GeoJSON format
        poly_coords = []
        for pt in contour:
            px, py = pt[0]
            p_lat, p_lon = pixel_to_geographic(px, py, bbox, img_w, img_h)
            poly_coords.append([p_lon, p_lat])
        if poly_coords:
            poly_coords.append(poly_coords[0])  # Close polygon

        # Area & physical dimensions
        physical_area_m2 = float(px_area * pixel_area_m2)
        aspect_ratio = max(bw / max(bh, 1), bh / max(bw, 1))
        est_length = max(bw, bh) * res_m
        est_width = min(bw, bh) * res_m

        # Air-gap data integrity check (Fmask)
        is_gap_filled, gap_ratio = check_gap_fill_intersection(
            contour, fmask_valid_mask, mask_shape=(img_h, img_w)
        )

        chg_type = classify_change_cluster(physical_area_m2, aspect_ratio)

        record = ChangeRecord(
            schema_version="1.0.0",
            change_id=change_id,
            location=ChangeLocation(
                crs="EPSG:4326",
                centroid=[lat, lon],
                region_name=region_name,
                polygon_geojson={
                    "type": "Polygon",
                    "coordinates": [poly_coords],
                },
            ),
            before_tile_ref=TileReference(
                tile_id=b_id,
                acquisition_date=b_date,
                sensor=b_sensor,
            ),
            after_tile_ref=TileReference(
                tile_id=a_id,
                acquisition_date=a_date,
                sensor=a_sensor,
            ),
            change_type=chg_type,
            earliest_supported_observation_date=a_date,
            confidence_score=round(confidence_score, 3),
            area_sq_meters=round(physical_area_m2, 1),
            source_models=source_models,
            is_reconstructed_or_gap_filled=is_gap_filled,
            gap_fill_details=GapFillDetails(
                gap_fill_method="fmask_screening" if is_gap_filled else "none",
                gap_pixel_ratio=gap_ratio,
            ),
            tactical_attributes={
                "estimated_length_meters": round(est_length, 1),
                "estimated_width_meters": round(est_width, 1),
                "aspect_ratio": round(aspect_ratio, 2),
                "pixel_cluster_count": int(px_area),
            },
        )
        records.append(record)

    return records
