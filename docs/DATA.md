# Satellite Data Specifications & Preprocessing Guide (DATA.md)

**Maintained by**: Anuj (Data & Preprocessing Lead)  
**Project**: SentinelEye (PS26227)

---

## 1. Supported Sensors & Satellite Constellations

| Sensor / Mission | Type | Native Resolution | Key Spectral Bands | Primary Defence Use-case |
|---|---|---|---|---|
| **Sentinel-2 (MSI)** | Optical Multi-spectral | 10m (VNIR), 20m (SWIR) | B02 (Blue), B03 (Green), B04 (Red), B08 (NIR), B11/B12 (SWIR) | Infrastructure development, vegetation clearance, airstrip paved surfaces |
| **Sentinel-1 (SAR)** | C-band Synthetic Aperture Radar | 10m (IW Ground Range) | VV, VH polarizations | All-weather/night surface disturbance, metallic vehicle detection, flood/water |
| **Landsat-8 / 9 (OLI-2/TIRS-2)**| Optical / Thermal | 15m (Pan), 30m (MS), 100m (Thermal) | Coastal, RGB, NIR, SWIR-1, SWIR-2, Thermal Infrared | Long-baseline multi-year temporal trend analysis, broad-area clearance |
| **ISRO Bhuvan / Cartosat / ResourceSat** | High-Res Optical | 0.8m - 5m | Panchromatic / LISS-IV VNIR | High-precision border outpost construction & vehicle track validation |

---

## 2. Directory Layout for Local Satellite Imagery

Satellite imagery is strictly kept offline in `data/` and excluded from git tracking:

```
data/
├── raw/
│   ├── sentinel2/
│   │   ├── S2A_MSIL2A_20251110T053851_R005_T43RER/
│   │   └── S2B_MSIL2A_20260220T053909_R005_T43RER/
│   ├── sentinel1/
│   │   └── S1A_IW_GRDH_1SDV_20260215T.../
│   └── landsat/
├── preprocessed/
│   ├── tiles_512/
│   │   ├── T43RER_20251110_RGBN.tif
│   │   ├── T43RER_20260220_RGBN.tif
│   │   └── metadata/
│   │       ├── T43RER_20251110.json
│   │       └── T43RER_20260220.json
│   └── masks/
│       └── T43RER_20260220_fmask.tif
└── precomputed/          <-- Used for Hackathon demo & instant fallback
    ├── demo_pair_01_pangong/
    ├── demo_pair_02_road_construction/
    └── demo_pair_03_outpost_clearance/
```

---

## 3. Preprocessing Standards & Requirements

1. **Coregistration**: Before/after pairs must be coregistered to sub-pixel accuracy (<0.5 pixel error) using phase correlation or AROSICS before feeding into BIT / CVA models.
2. **Atmospheric Correction**: Bottom-Of-Atmosphere (BOA) surface reflectance (Level-2A standard).
3. **Cloud & Shadow Masking (Fmask)**:
   - Pixel validity mask must accompany every tile.
   - Any gap-filled or interpolated pixel must have its metadata flag set: `is_reconstructed_or_gap_filled = True`.
4. **Coordinate Reference System (CRS)**:
   - All spatial geometries exported in GeoJSON must be formatted in **WGS84 (EPSG:4326)** for external interfaces.
   - Processing rasters are maintained in local UTM projection (e.g., EPSG:32643 for Northern India/Ladakh sectors) to ensure distance and area metrics are metric and undistorted.

---

## 4. Sample Before/After Demonstration Scenes Prepared for SIH 2026
- **Scene 1 (Northern Border - High Altitude Lake Sector)**: Infrastructure and road widening detection.
- **Scene 2 (Western Sector - Desert Cantonment)**: Vehicle staging and revetment clearance.
- **Scene 3 (Eastern Sector - Mountain Valley)**: New helipad and bridge construction under cloud-prone terrain (optical + SAR fusion).
