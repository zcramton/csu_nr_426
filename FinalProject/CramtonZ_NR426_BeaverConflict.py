"""
NR426 Beaver Conflict & Restoration Analysis
CramtonZ_NR426_BeaverConflict.py
Zachary Cramton

Spatial screening tool for human-beaver conflict risk and restoration
opportunity. Intersects BRAT stream network capacity data with NLCD land
cover to produce per-segment conflict and restoration indices, then
summarizes results by a planning boundary (county, watershed, etc.).

This is a screening index, not a hydraulic model. BRAT capacity values
are modeled potential, not confirmed beaver presence. Validate with field
data before using in planning decisions.

Inputs:
    The boundary layer drives the analysis extent and planning unit attribution.
    Provide whatever polygon layer is relevant to your use case — county,
    HUC watershed, state, or a custom AOI. Pre-clip the layer to your area
    of interest before running if it covers a larger extent.

Outputs (all written to BeaverConflictAnalysis.gdb in output_dir):
    brat_clipped          - BRAT network clipped to boundary
    brat_riparian_buffer  - Segments buffered to riparian corridor
    nlcd_clipped          - NLCD land cover clipped to boundary
    conflict_risk         - Conflict Risk Index per stream segment
    restoration_opp       - Restoration Opportunity Index per segment
    planning_summary      - Mean index scores per boundary unit
    CramtonZ_BeaverConflict_Report.txt - Run summary report
"""

# Import Modules
import arcpy
import os
import sys
import datetime

from CramtonZ_NR426_BeaverConflict_Tools import (
    OUTPUT_LAYERS,
    LC_CONFIDENCE_THRESHOLD,
    clip_and_buffer_brat,
    clip_nlcd,
    compute_conflict_risk,
    compute_restoration_opp,
    compute_planning_summary,
    print_summary,
)


# ============================================================
# TOOL PARAMETERS
# ============================================================
# All NLCD inputs default to ESRI Living Atlas image services if left blank.
# Sign in to ArcGIS Online with a Living Atlas-enabled account before running.
# To use local files instead, set the path here or pass via GetParameterAsText.

# BRAT stream network polyline — must have oCC_EX and oCC_HPE fields
# Default: Colorado BRAT (via ArcGIS Online)
brat_fc = arcpy.GetParameterAsText(0)            # Input BRAT polyline feature class

# NLCD annual land cover image service or local raster
# Default: ESRI Living Atlas — USA NLCD Annual Land Cover
nlcd_raster = arcpy.GetParameterAsText(1)        # NLCD land cover raster or service URL

# Analysis boundary polygon — provide pre-clipped layer for your AOI.
# Common types: County, HUC-8 Watershed, HUC-12 Watershed, State, Custom AOI
boundary_fc = arcpy.GetParameterAsText(2)        # Analysis boundary polygon (required)

# Label for boundary type — used in report output only.
# Common values: "County", "HUC-8 Watershed", "HUC-12 Watershed", "State", "Custom AOI"
boundary_type = arcpy.GetParameterAsText(3)      # Boundary type label

# Riparian buffer distance in meters — typical range 30-300m
raw_buffer_m = arcpy.GetParameterAsText(4)       # Riparian buffer distance (meters)

# Folder where output GDB and report will be created
output_dir = arcpy.GetParameterAsText(5)         # Output folder path (required)

# Whether to overwrite existing outputs — "true" or "false"
raw_overwrite = arcpy.GetParameterAsText(6)      # Overwrite existing outputs

# NLCD fractional impervious surface — scales dev weights by actual imperviousness.
# Default: ESRI Living Atlas — USA NLCD Annual Land Cover Fractional Impervious Surface
# Set "" to skip FIS scaling and use class-based weights only.
impervious_raster = arcpy.GetParameterAsText(7)  # FIS raster or service URL (optional)

# NLCD land cover confidence — flags low-confidence segments for field review.
# Default: ESRI Living Atlas — USA NLCD Annual Land Cover Confidence
# Set "" to skip confidence flagging.
confidence_raster = arcpy.GetParameterAsText(8)  # Confidence raster or service URL (optional)

# BRAT existing capacity field name — defaults to oCC_EX (CO BRAT / COBAM).
# Set only if your BRAT layer uses a different field name.
raw_ex_field  = arcpy.GetParameterAsText(9)       # Existing capacity field name (optional)

# BRAT historic/potential capacity field name — defaults to oCC_PT (CO BRAT / COBAM).
# Set only if your BRAT layer uses a different field name.
raw_hpe_field = arcpy.GetParameterAsText(10)      # Historic/potential capacity field name (optional)


# ============================================================
# CONSTANTS
# ============================================================

OUTPUT_GDB_NAME = "BeaverConflictAnalysis.gdb"
OUTPUT_SR_WKID  = 5070   # EPSG 5070 Conus Albers — matches NLCD native projection

# Default data sources — applied when the matching parameter is left blank.
# Living Atlas services require an ArcGIS Online account with Living Atlas access.
DEFAULT_BRAT_URL = (
    "https://services1.arcgis.com/KNdRU5cN6ENqCTjk/arcgis/rest/services"
    "/Legend_Test1/FeatureServer"
)
DEFAULT_NLCD_URL = (
    "https://di-nlcd.img.arcgis.com/arcgis/rest/services"
    "/USA_NLCD_Annual_LandCover/ImageServer"
)
DEFAULT_FIS_URL = (
    "https://di-nlcd.img.arcgis.com/arcgis/rest/services"
    "/USA_NLCD_Annual_LandCover_Fractional_Impervious_Surface/ImageServer"
)
DEFAULT_CONFIDENCE_URL = (
    "https://di-nlcd.img.arcgis.com/arcgis/rest/services"
    "/USA_NLCD_Annual_LandCover_Confidence/ImageServer"
)

# BRAT capacity field defaults (CO BRAT / COBAM).
# Override via raw_ex_field / raw_hpe_field parameters if your dataset differs.
DEFAULT_EX_FIELD  = "oCC_EX"
DEFAULT_HPE_FIELD = "oCC_PT"

# Default riparian buffer if raw_buffer_m is not set
DEFAULT_BUFFER_M = 100


# ============================================================
# PARAMETER COERCION & INPUT CHECKS
# ============================================================
# GetParameterAsText() always returns a string — "" when not set, never None.
# Living Atlas defaults are applied here before any existence checks.

brat_fc           = brat_fc           if brat_fc           != "" else DEFAULT_BRAT_URL
nlcd_raster       = nlcd_raster       if nlcd_raster       != "" else DEFAULT_NLCD_URL
impervious_raster = impervious_raster if impervious_raster != "" else DEFAULT_FIS_URL
confidence_raster = confidence_raster if confidence_raster != "" else DEFAULT_CONFIDENCE_URL

buffer_m  = int(raw_buffer_m)  if raw_buffer_m  != "" else DEFAULT_BUFFER_M
overwrite = raw_overwrite.lower() != "false" if raw_overwrite != "" else True
ex_field  = raw_ex_field  if raw_ex_field  != "" else DEFAULT_EX_FIELD
hpe_field = raw_hpe_field if raw_hpe_field != "" else DEFAULT_HPE_FIELD

print("\nChecking inputs...")

# Check Spatial Analyst before anything else
if arcpy.CheckExtension("Spatial") != "Available":
    print("\t> ERROR: Spatial Analyst extension is not available.")
    print("\t> This tool requires Spatial Analyst. Check your license and try again.")
    sys.exit()

# Check required parameters with no defaults
for label, val in [("boundary_fc", boundary_fc), ("output_dir", output_dir)]:
    if val == "":
        print(f"\t> ERROR: {label} is not set in the TOOL PARAMETERS block.")
        sys.exit()

# Check all input layers exist
for label, path in [("BRAT", brat_fc), ("NLCD", nlcd_raster), ("Boundary", boundary_fc)]:
    if not arcpy.Exists(path):
        print(f"\t> ERROR: {label} not found at: {path}")
        sys.exit()
    print(f"\t> {label} found: {path}")

# Check optional rasters — warn and disable if unreachable, do not exit
for label, path in [("FIS", impervious_raster), ("Confidence", confidence_raster)]:
    if path != "":
        if not arcpy.Exists(path):
            print(f"\t> Warning: {label} not found at: {path}")
            print(f"\t> {label} will be skipped.")
            if label == "FIS":
                impervious_raster = ""
            else:
                confidence_raster = ""
        else:
            print(f"\t> {label} found: {path}")

# Check buffer distance is a positive number
if buffer_m <= 0:
    print(f"\t> ERROR: Buffer distance must be greater than 0. Got: {buffer_m}m")
    sys.exit()

# Check boundary is Polygon geometry
boundary_desc = arcpy.Describe(boundary_fc)
if boundary_desc.shapeType != "Polygon":
    print(f"\t> ERROR: Boundary must be Polygon geometry. Found: {boundary_desc.shapeType}")
    print(f"\t> Provide a polygon layer — county, HUC, state, or custom AOI.")
    sys.exit()

# Check boundary has at least one feature
boundary_count = int(arcpy.management.GetCount(boundary_fc)[0])
if boundary_count == 0:
    print(f"\t> ERROR: Boundary layer has no features.")
    sys.exit()
print(f"\t> Boundary: {boundary_count} polygon(s)")

# Check BRAT is Polyline geometry
brat_desc = arcpy.Describe(brat_fc)
if brat_desc.shapeType != "Polyline":
    print(f"\t> ERROR: BRAT must be Polyline geometry. Found: {brat_desc.shapeType}")
    sys.exit()

# Check BRAT for null geometries — warn but do not exit
with arcpy.da.SearchCursor(brat_fc, ["OID@", "SHAPE@"]) as cursor:
    null_geom = [row[0] for row in cursor if row[1] is None]
if null_geom:
    print(f"\t> Warning: {len(null_geom)} null geometries found in BRAT "
          f"(OIDs: {null_geom[:5]}{'...' if len(null_geom) > 5 else ''})")
    print(f"\t> These features will be skipped during clipping. Run Repair Geometry to fix.")
else:
    print(f"\t> BRAT geometry: no null geometries found")

# Check BRAT and boundary extents overlap
brat_ext     = brat_desc.extent
boundary_ext = boundary_desc.extent
if (brat_ext.XMax < boundary_ext.XMin or brat_ext.XMin > boundary_ext.XMax or
        brat_ext.YMax < boundary_ext.YMin or brat_ext.YMin > boundary_ext.YMax):
    print(f"\t> ERROR: BRAT and boundary extents do not overlap.")
    print(f"\t> BRAT extent:     {brat_ext.XMin:.1f}, {brat_ext.YMin:.1f} — "
          f"{brat_ext.XMax:.1f}, {brat_ext.YMax:.1f}")
    print(f"\t> Boundary extent: {boundary_ext.XMin:.1f}, {boundary_ext.YMin:.1f} — "
          f"{boundary_ext.XMax:.1f}, {boundary_ext.YMax:.1f}")
    print(f"\t> Verify both layers cover the same area and are in compatible projections.")
    sys.exit()
print(f"\t> BRAT and boundary extents overlap")

# Check BRAT has required capacity fields
brat_fields = {f.name for f in arcpy.ListFields(brat_fc)}
if ex_field not in brat_fields:
    print(f"\t> ERROR: Field '{ex_field}' not found in BRAT layer.")
    print(f"\t> Set raw_ex_field to the correct existing capacity field name.")
    sys.exit()
if hpe_field not in brat_fields:
    print(f"\t> ERROR: Field '{hpe_field}' not found in BRAT layer.")
    print(f"\t> Set raw_hpe_field to the correct historic/potential capacity field name.")
    sys.exit()
print(f"\t> BRAT fields: {ex_field} (EX), {hpe_field} (HPE)")

# Check oCC_EX values are not all null — normalization would silently fail
ex_values = [r[0] for r in arcpy.da.SearchCursor(brat_fc, [ex_field]) if r[0] is not None]
if not ex_values:
    print(f"\t> ERROR: All values in '{ex_field}' are null. Cannot compute Conflict Risk Index.")
    sys.exit()

# Check NLCD coordinate system against the output SR.
# For local files, arcpy.management.Clip writes in the file's native SR — if it doesn't
# match OUTPUT_SR_WKID, the clipped raster and buffer polygons will misalign in zonal stats.
# For image service URLs, arcpy writes the clipped output using arcpy.env.outputCoordinateSystem
# (set to OUTPUT_SR_WKID below), so the GDB raster is always in the correct SR regardless of
# the service's native projection. Checking the service SR would produce a false error.
if nlcd_raster.startswith("https://"):
    print(f"\t> NLCD: image service — clipped output will be written in WKID {OUTPUT_SR_WKID}")
else:
    nlcd_desc = arcpy.Describe(nlcd_raster)
    nlcd_sr   = nlcd_desc.spatialReference
    target_sr = arcpy.SpatialReference(OUTPUT_SR_WKID)
    if nlcd_sr.factoryCode != OUTPUT_SR_WKID:
        print(f"\t> ERROR: NLCD is in {nlcd_sr.name} (WKID {nlcd_sr.factoryCode}).")
        print(f"\t> Tool output SR is {target_sr.name} (WKID {OUTPUT_SR_WKID}).")
        print(f"\t> Re-project NLCD to WKID {OUTPUT_SR_WKID} before running.")
        sys.exit()
    else:
        print(f"\t> NLCD projection: {nlcd_sr.name} — matches output SR")

print("\t> All inputs verified.\n")


# ============================================================
# REPORT SETUP
# ============================================================

report_name = "CramtonZ_BeaverConflict_Report.txt"
report_path = os.path.join(output_dir, report_name)
timestamp   = datetime.datetime.now().strftime("%d%b%Y %H:%M:%S").upper()


# ============================================================
# MAIN ANALYSIS
# ============================================================

try:
    arcpy.CheckOutExtension("Spatial")
    os.makedirs(output_dir, exist_ok=True)

    with open(report_path, 'w') as report:

        # Report header
        print(f"{'=' * 60}", file=report)
        print(f"NR426 Beaver Conflict & Restoration Analysis", file=report)
        print(f"Generated: {timestamp}", file=report)
        print(f"Boundary: {boundary_type or 'N/A'}   |   Units: {boundary_count}", file=report)
        print(f"Buffer: {buffer_m}m   |   Overwrite: {overwrite}", file=report)
        print(f"BRAT fields: {ex_field} (EX), {hpe_field} (HPE)", file=report)
        print(f"NLCD source:       {nlcd_raster}", file=report)
        print(f"FIS source:        {impervious_raster or 'Not used'}", file=report)
        print(f"Confidence source: {confidence_raster or 'Not used'}", file=report)
        if confidence_raster:
            print(f"LC confidence threshold: {LC_CONFIDENCE_THRESHOLD}%", file=report)
        print(f"{'=' * 60}\n", file=report)

        # ----- 1) Workspace Setup -----
        print("--- Step 1/5: Setting Up Workspace ---")
        gdb_path = os.path.join(output_dir, OUTPUT_GDB_NAME)
        if not arcpy.Exists(gdb_path):
            arcpy.management.CreateFileGDB(output_dir, OUTPUT_GDB_NAME)
            print(f"\t> Created GDB: {gdb_path}")
        else:
            print(f"\t> Using existing GDB: {gdb_path}")

        arcpy.env.workspace              = gdb_path
        arcpy.env.overwriteOutput        = overwrite
        arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(OUTPUT_SR_WKID)
        print(f"Output GDB: {gdb_path}", file=report)

        # ----- 2) Clip Inputs -----
        print("\n--- Step 2/5: Clipping Inputs ---")
        brat_clip, brat_buffer = clip_and_buffer_brat(
            brat_fc, boundary_fc, buffer_m, gdb_path
        )
        if not brat_clip or not brat_buffer:
            print("\t> BRAT clip/buffer failed. See errors above. Exiting.")
            sys.exit()

        nlcd_clip = clip_nlcd(nlcd_raster, boundary_fc, gdb_path)
        if not nlcd_clip:
            print("\t> NLCD clip failed. See errors above. Exiting.")
            sys.exit()

        # ----- 3) Conflict Risk Index -----
        print("\n--- Step 3/5: Conflict Risk Index ---")
        conflict_fc = compute_conflict_risk(
            brat_buffer, ex_field, nlcd_clip, boundary_fc, gdb_path,
            impervious_raster=impervious_raster or None,
            confidence_raster=confidence_raster or None,
        )
        if not conflict_fc:
            print("\t> Conflict Risk Index failed. See errors above. Exiting.")
            sys.exit()

        # ----- 4) Restoration Opportunity Index -----
        print("\n--- Step 4/5: Restoration Opportunity Index ---")
        restoration_fc = compute_restoration_opp(
            brat_buffer, ex_field, hpe_field, nlcd_clip, boundary_fc, gdb_path,
            impervious_raster=impervious_raster or None,
            confidence_raster=confidence_raster or None,
        )
        if not restoration_fc:
            print("\t> Restoration Opportunity Index failed. See errors above. Exiting.")
            sys.exit()

        # ----- 5) Planning Summary & Results -----
        print("\n--- Step 5/5: Planning Summary & Results ---")
        summary_fc = compute_planning_summary(
            boundary_fc, conflict_fc, restoration_fc, gdb_path
        )
        if not summary_fc:
            print("\t> Planning Summary failed. See errors above. Exiting.")
            sys.exit()

        print_summary(
            summary_fc,
            boundary_type or "Boundary",
            report_file=report,
        )

        print(f"\nOutputs written to: {gdb_path}", file=report)
        for layer in OUTPUT_LAYERS.values():
            print(f"\t- {layer}", file=report)

    print(f"\nReport saved to: {report_path}")

except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    arcpy.CheckInExtension("Spatial")

print("\nScript Execution Complete.")
