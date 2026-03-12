# Beaver Conflict & Restoration Analysis

Spatial screening tool for human-beaver conflict risk and restoration
opportunity. Intersects BRAT stream network capacity with NLCD land cover and 
factional impervious surface to score each stream segment, then summarizes results 
by planning boundary (state/county/municipality), watershed, or custom AOI).

All NLCD inputs default to ESRI Living Atlas image services. The analysis
boundary and output folder are the only inputs with no default.

The boundary layer drives the analysis extent and planning unit attribution.
Provide whatever polygon layer is relevant to your use case pre-clipped
to your area of interest.

Fractional impervious surface (FIS) and land cover confidence are optional
— both default to their Living Atlas services but can be disabled by
setting the parameter to `""`. - DOTHIS:: Resolve "Optional but really required"

**Course:** CSU NR426 — Programming for GIS 1  
**Author:** Zachary Cramton\
**Date:** 16 March 2026
---

## Files

```
beaver_conflict/
├── CramtonZ_NR426_BeaverConflict.py        # Entry point — set parameters and run
├── CramtonZ_NR426_BeaverConflict_Tools.py  # All functions and shared constants
├── README.md
└── requirements.txt
```

Both Python files must be in the same directory.

---

## Requirements

- ArcGIS Pro (Recommended: v3.6.2)
- Spatial Analyst extension (required — checked at runtime)
- Python 3.13 via the ArcGIS Pro conda environment (arcgispro-py3)
- Active ArcGIS portal sign-in with Living Atlas access when using default service URLs

---
## Instructions

This program is intended to be run as a custom script tool in ArcGIS Pro or independently with the ArcGIS Pro
interpreter in an IDE. 

### Setup
For user inputs through the script tool GUI use arcpy.GetParameterAsText() and follow 
the [instrucitons](https://pro.arcgis.com/en/pro-app/latest/help/analysis/geoprocessing/basics/create-a-python-script-tool.htm)
from ESRI's help page to set up the tool. To set up or make changes to the inputs open `CramtonZ_NR426_BeaverConflict.py` 
and fill in the **TOOL PARAMETERS** block near the top with your desired paths.

This program will generate a file geodatabase and a text report. This script will overwrite these files each 
time it runs. To save your files, move them to another directory or change these file names at the top of the
**CONSTANTS** block below **TOOL PARAMETERS**.

```python
# Required — no defaults
boundary_fc   = r"C:\data\Colorado_Counties.shp"   # pre-clipped to your AOI
output_dir    = r"C:\output\beaver_analysis"

# Optional — defaults shown; set local path to override, "" to use default
brat_fc           = ""   # defaults to CO Living Atlas BRAT
boundary_type     = "County"   # County, HUC-8 Watershed, HUC-12 Watershed, State, Custom AOI
raw_buffer_m      = "100"
raw_overwrite     = "true"
nlcd_raster       = ""   # defaults to USA NLCD Annual Land Cover
impervious_raster = ""   # defaults to USA NLCD Annual Fractional Impervious Surface
confidence_raster = ""   # defaults to USA NLCD Annual Land Cover Confidence
raw_ex_field      = ""   # defaults to oCC_EX
raw_hpe_field     = ""   # defaults to oCC_PT

# Optional - Change report names
report_name = "BeaverConflictAnalysisReport.txt"
OUTPUT_GDB_NAME = "BeaverConflictAnalysis.gdb"
```

Living Atlas services require signing in to the active portal in ArcGIS Pro
before running.

---

### How To Run

As a custom script tool, simply open and fill out the tool in the toolbox where you set it up.

From the ArcGIS Pro Python window:
```python
exec(open(r"C:\path\to\CramtonZ_NR426_BeaverConflict.py").read())
```

Or from any Python environment with arcpy on the path:
```
python CramtonZ_NR426_BeaverConflict.py
```

The script validates all inputs before running. Fix any reported errors
and re-run.

---

## Inputs

| Parameter | Description | Notes |
|---|---|---|
| `brat_fc` | BRAT polyline | Defaults to CO Living Atlas; must have `oCC_EX` and `oCC_PT` |
| `nlcd_raster` | NLCD land cover raster or URL | Defaults to Living Atlas image service |
| `boundary_fc` | Analysis boundary polygon | Pre-clipped to your AOI — **required** |
| `boundary_type` | Label for boundary type | Used in report only — see common values below |
| `raw_buffer_m` | Riparian buffer in meters | Default 100m; must be > 0 |
| `output_dir` | Output folder | Created if it doesn't exist — **required** |
| `raw_overwrite` | Overwrite outputs | `"true"` or `"false"` |
| `impervious_raster` | FIS raster or URL (optional) | Defaults to Living Atlas; `""` to skip FIS scaling |
| `confidence_raster` | Confidence raster or URL (optional) | Defaults to Living Atlas; `""` to skip confidence flagging |
| `raw_ex_field` | Existing capacity field name (optional) | Defaults to `oCC_EX`; set if your BRAT layer differs |
| `raw_hpe_field` | Historic/potential capacity field name (optional) | Defaults to `oCC_PT`; set if your BRAT layer differs |

**boundary_type common values:**  `"State"`, `"County"`, `"HUC-8 Watershed"`, `"HUC-12 Watershed"`, `"Custom AOI"`

### Boundary Layer
Provide any polygon layer clipped to your area of interest. The tool does
not apply state or other filters internally — what you bring in is what
gets analyzed. Each polygon in the boundary layer becomes one planning unit
in `planning_summary`, and each stream segment in `conflict_risk` and
`restoration_opp` is tagged with the name of the boundary unit it falls in.

The tool validates the boundary layer before running:
- Must be Polygon geometry (not Polyline or Point)
- Must contain at least one feature
- Must spatially overlap the BRAT layer extent

### NLCD Projection Note
When using a **local raster**, NLCD must be in **EPSG 5070 (Conus Albers)**. The
script checks this at startup and exits if it doesn't match. Reproject with Project Raster 
(WKID 5070) before running. To avoid unknowingly modifying user input data
or raster projection complications, this is not automated and local files must be projected
by the user. Reference the ESRI [help page](https://pro.arcgis.com/en/pro-app/3.4/tool-reference/data-management/project-raster.htm)
for more information about Project Raster. This check is necessary because `arcpy.management.Clip` writes the clipped output in the file's native SR, so a mismatch causes the raster and buffer 
polygons to silently misalign in zonal statistics.

When using a **Living Atlas image service URL**, the projection check is skipped.
`arcpy.management.Clip` writes the clipped output using `arcpy.env.outputCoordinateSystem`
(WKID 5070), so the GDB raster is always in the correct SR regardless of the
service's native projection. Checking the service SR would produce a false error.

### Default Data Sources

All Living Atlas URLs below are confirmed correct but have not yet been
tested end-to-end in the tool. Boundary REST URLs are unverified. DOTHIS:: confirm
each before use.

| Input | URL | Status |
|---|---|---|
| BRAT (Colorado) | `https://services1.arcgis.com/KNdRU5cN6ENqCTjk/arcgis/rest/services/Legend_Test1/FeatureServer` | URL confirmed, untested in tool |
| NLCD Land Cover | `https://di-nlcd.img.arcgis.com/arcgis/rest/services/USA_NLCD_Annual_LandCover/ImageServer` | URL confirmed, untested in tool |
| FIS | `https://di-nlcd.img.arcgis.com/arcgis/rest/services/USA_NLCD_Annual_LandCover_Fractional_Impervious_Surface/ImageServer` | URL confirmed, untested in tool |
| Confidence | `https://di-nlcd.img.arcgis.com/arcgis/rest/services/USA_NLCD_Annual_LandCover_Confidence/ImageServer` | URL confirmed, untested in tool |
| Census Counties | `https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/1` | Unverified |
| HUC-8 Watersheds | `https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer/4` | Unverified |
| HUC-12 Watersheds | `https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer/6` | Unverified |

### BRAT Data Sources
- **Colorado (default)**: Living Atlas — see `DEFAULT_BRAT_URL` in Constants block
- **Other regions**: No additional sources have been tested. Field names may
  differ — use `raw_ex_field` and `raw_hpe_field` to override defaults.

---

## Outputs

All saved to `BeaverConflictAnalysis.gdb` in your output directory, plus
a `CramtonZ_BeaverConflict_Report.txt` summary file.

| Layer | Description |
|---|---|
| `brat_clipped` | BRAT clipped to boundary |
| `brat_riparian_buffer` | Segments buffered to riparian corridor |
| `nlcd_clipped` | NLCD clipped to boundary |
| `conflict_risk` | Conflict Risk Index per stream segment |
| `restoration_opp` | Restoration Opportunity Index per segment |
| `planning_summary` | Mean scores per boundary unit |

### Key Output Fields

**conflict_risk**

| Field | Description |
|---|---|
| `oCC_EX_norm` | Existing capacity normalized 0–1 |
| `dev_weight_mean` | Mean dev weight in riparian buffer (class weight × FIS if enabled) |
| `conflict_score_norm` | Final conflict score (0–1) |
| `conflict_class` | Very Low / Low / Moderate / High / Very High |
| `lc_confidence_mean` | Mean NLCD LC confidence in buffer (0–100); present if confidence enabled |
| `lc_confidence_flag` | `OK` or `Review` based on `LC_CONFIDENCE_THRESHOLD`; present if confidence enabled |
| `boundary_name` | Name of the boundary unit each segment falls in (from boundary layer) |

**restoration_opp**

| Field | Description |
|---|---|
| `restoration_gap` | oCC_PT minus oCC_EX, floored at 0 |
| `gap_norm` | Restoration gap normalized 0–1 |
| `dev_weight_mean` | Mean dev weight in riparian buffer (class weight × FIS if enabled) |
| `restoration_score_norm` | Final restoration score (0–1) |
| `restoration_class` | Very Low / Low / Moderate / High / Very High |
| `lc_confidence_mean` | Mean NLCD LC confidence in buffer (0–100); present if confidence enabled |
| `lc_confidence_flag` | `OK` or `Review` based on `LC_CONFIDENCE_THRESHOLD`; present if confidence enabled |
| `boundary_name` | Name of the boundary unit each segment falls in (from boundary layer) |

---

## Index Formulas

**Conflict Risk**
```
conflict_score = oCC_EX_norm × mean_dev_weight_in_buffer
```

**Restoration Opportunity**
```
restoration_gap   = max(0, oCC_PT − oCC_EX)
restoration_score = gap_norm × (1 − mean_dev_weight)
```

**Development Weight (with FIS)**

When `impervious_raster` is enabled, the class-based weight is scaled by
the fractional impervious surface at each pixel before the zonal mean is
computed per buffer polygon:
```
dev_weight_pixel = class_weight × (FIS_pct / 100)
dev_weight_mean  = mean(dev_weight_pixel) over riparian buffer
```
Non-developed pixels (classes outside 21–24) have a class weight of 0.0,
so FIS has no effect on them regardless of value.

**Land Cover Confidence Flag**

`lc_confidence_flag` is informational only — it does not affect index scores.
Segments where the mean LC confidence within the riparian buffer falls below
`LC_CONFIDENCE_THRESHOLD` (default 75%) are flagged `"Review"`. These should
be field-verified before use in planning decisions. Change the threshold in
the `SHARED CONSTANTS` block of the Tools file.

**NLCD Development Weights**

| Class | Label | Weight |
|---|---|---|
| 21 | Developed, Open Space | 0.2 |
| 22 | Developed, Low Intensity | 0.4 |
| 23 | Developed, Medium Intensity | 0.7 |
| 24 | Developed, High Intensity | 1.0 |
| All others | Not developed | 0.0 |

**Risk Classes** (applied to all normalized scores)

| Score | Class |
|---|---|
| 0.0 – 0.2 | Very Low |
| 0.2 – 0.4 | Low |
| 0.4 – 0.6 | Moderate |
| 0.6 – 0.8 | High |
| 0.8 – 1.0 | Very High |

---

## Limitations

This tool is a **spatial screening index**, not a hydraulic model.

- BRAT capacity is modeled potential, not confirmed beaver presence
- NLCD 30m resolution may miss fine-scale land use variation
- FIS scaling improves precision within developed classes but does not
  capture non-impervious development pressures (e.g. agriculture, logging)
- LC confidence flag identifies uncertain classifications but does not
  correct them — treat flagged segments as primary candidates for field verification
- No DEM flood routing — does not model actual inundation extent
- Validate with field data before using results in planning decisions

---

# Testing Status

Nothing in this tool has been tested end-to-end against live data. The
table below tracks what has and hasn't been verified. Update this section
as testing is completed.

### Data Sources

| Item | Status |
|---|---|
| CO BRAT Living Atlas URL | URL confirmed, untested in tool |
| NLCD Land Cover Living Atlas URL | URL confirmed, untested in tool |
| FIS Living Atlas URL | URL confirmed, untested in tool |
| LC Confidence Living Atlas URL | URL confirmed, untested in tool |
| Census TIGER Counties REST URL | Unverified |
| USGS HUC-8 REST URL | Unverified |
| USGS HUC-12 REST URL | Unverified |

### Analysis Parameters

| Item | Status |
|---|---|
| NLCD dev weights (0.2 / 0.4 / 0.7 / 1.0) | Design decision — ecological validity unverified |
| LC confidence threshold (75%) | Design decision — not empirically validated |
| Default riparian buffer (100m) | Design decision — ecological appropriateness unverified |
| FIS scaling on non-developed pixels | Correct by design — untested in practice |

### Tool Behavior

| Item | Status |
|---|---|
| End-to-end run against live data | Untested |
| BRAT clip produces expected features | Untested |
| NLCD clip and zonal statistics alignment | Untested |
| Per-segment boundary attribution | Untested |
| `HAVE_THEIR_CENTER_IN` → `INTERSECT` fallback | Untested |
| `detect_name_field()` against real boundary layers | Untested |
| Planning summary aggregation | Untested |
| Report output formatting | Untested |
