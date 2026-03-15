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
    BeaverConflictAnalysisReport.txt - Run summary report
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
    clip_ancillary_raster,
)


# ============================================================
# TOOL PARAMETERS
# ============================================================
# All NLCD inputs default to ESRI Living Atlas image services if left blank.
# Sign in to ArcGIS Online with a Living Atlas-enabled account before running.
# To use local files instead, set the path here or pass via GetParameterAsText.

# Folder where output GDB and report will be created
output_dir = arcpy.GetParameterAsText(0)         # Output folder path (required)

# Analysis boundary polygon — provide pre-clipped layer for your AOI.
# Common types: County, HUC-8 Watershed, HUC-12 Watershed, State, Custom AOI
boundary_fc = arcpy.GetParameterAsText(1)        # Analysis boundary polygon (required)

# Label for boundary type — used in report output only.
# Common values: "County", "HUC-8 Watershed", "HUC-12 Watershed", "State", "Custom AOI"
boundary_type = arcpy.GetParameterAsText(2)      # Boundary type label

# BRAT stream network polyline — must have oCC_EX and oCC_PT fields
# Default: Colorado BRAT (via ArcGIS Online)
brat_fc = arcpy.GetParameterAsText(3)            # Input BRAT polyline feature class

# BRAT existing capacity field name — defaults to oCC_EX (CO BRAT / COBAM).
# Set only if your BRAT layer uses a different field name.
raw_ex_field  = arcpy.GetParameterAsText(4)      # Existing capacity field name (optional)

# BRAT historic/potential capacity field name — defaults to oCC_PT (CO BRAT / COBAM).
# Set only if your BRAT layer uses a different field name.
raw_hpe_field = arcpy.GetParameterAsText(5)      # Historic/potential capacity field name (optional)

# NLCD annual land cover image service or local raster
# Default: ESRI Living Atlas — USA NLCD Annual Land Cover
nlcd_raster = arcpy.GetParameterAsText(6)        # NLCD land cover raster or service URL

# NLCD fractional impervious surface — scales dev weights by actual imperviousness.
# Default: ESRI Living Atlas — USA NLCD Annual Land Cover Fractional Impervious Surface
# Set "" to skip FIS scaling and use class-based weights only.
impervious_raster = arcpy.GetParameterAsText(7)  # FIS raster or service URL (optional)

# NLCD land cover confidence — flags low-confidence segments for field review.
# Default: ESRI Living Atlas — USA NLCD Annual Land Cover Confidence
# Set "" to skip confidence flagging.
confidence_raster = arcpy.GetParameterAsText(8)  # Confidence raster or service URL (optional)

# Riparian buffer distance in meters — typical range 30-300m
raw_buffer_m = arcpy.GetParameterAsText(9)       # Riparian buffer distance (meters)

# Whether to overwrite existing outputs — "true" or "false"
raw_overwrite = arcpy.GetParameterAsText(10)     # Overwrite existing outputs


# ============================================================
# CONSTANTS
# ============================================================

report_name     = "BeaverConflictAnalysisReport.txt"
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

# FeatureServer URLs pointing to the service root (no trailing layer index) cannot be
# described or queried directly — arcpy requires a specific layer endpoint.
# Append /0 to any FeatureServer URL that does not already end with a layer number.
if "FeatureServer" in brat_fc and not brat_fc.rstrip("/").split("/")[-1].isdigit():
    brat_fc = brat_fc.rstrip("/") + "/0"

buffer_m  = int(raw_buffer_m)  if raw_buffer_m  != "" else DEFAULT_BUFFER_M
overwrite = raw_overwrite.lower() != "false" if raw_overwrite != "" else True
ex_field  = raw_ex_field  if raw_ex_field  != "" else DEFAULT_EX_FIELD
hpe_field = raw_hpe_field if raw_hpe_field != "" else DEFAULT_HPE_FIELD

arcpy.AddMessage("\nChecking inputs...")

# Check Spatial Analyst before anything else
if arcpy.CheckExtension("Spatial") != "Available":
    arcpy.AddError("Spatial Analyst extension is not available.")
    arcpy.AddError("This tool requires Spatial Analyst. Check your license and try again.")
    sys.exit(1)

# Check required parameters with no defaults
for label, val in [("boundary_fc", boundary_fc), ("output_dir", output_dir)]:
    if val == "":
        arcpy.AddError(f"{label} is required but was not provided.")
        sys.exit(1)

# Check all input layers exist
for label, path in [("BRAT", brat_fc), ("NLCD", nlcd_raster), ("Boundary", boundary_fc)]:
    if not arcpy.Exists(path):
        arcpy.AddError(f"{label} not found at: {path}")
        sys.exit(1)
    arcpy.AddMessage(f"\t> {label} found: {path}")

# Check optional rasters — warn and disable if unreachable, do not exit
for label, path in [("FIS", impervious_raster), ("Confidence", confidence_raster)]:
    if path != "":
        if not arcpy.Exists(path):
            arcpy.AddWarning(f"{label} not found at: {path}")
            arcpy.AddWarning(f"{label} will be skipped.")
            if label == "FIS":
                impervious_raster = ""
            else:
                confidence_raster = ""
        else:
            arcpy.AddMessage(f"\t> {label} found: {path}")

# Check buffer distance is a positive number
if buffer_m <= 0:
    arcpy.AddError(f"Buffer distance must be greater than 0. Got: {buffer_m}m")
    sys.exit(1)

# Check boundary is Polygon geometry
boundary_desc = arcpy.Describe(boundary_fc)
if boundary_desc.shapeType != "Polygon":
    arcpy.AddError(f"Boundary must be Polygon geometry. Found: {boundary_desc.shapeType}")
    arcpy.AddError("Provide a polygon layer — county, HUC, state, or custom AOI.")
    sys.exit(1)

# Check boundary has at least one feature
boundary_count = int(arcpy.management.GetCount(boundary_fc)[0])
if boundary_count == 0:
    arcpy.AddError("Boundary layer has no features.")
    sys.exit(1)
arcpy.AddMessage(f"\t> Boundary: {boundary_count} polygon(s)")

# Check BRAT is Polyline geometry
brat_desc = arcpy.Describe(brat_fc)
if brat_desc.shapeType != "Polyline":
    arcpy.AddError(f"BRAT must be Polyline geometry. Found: {brat_desc.shapeType}")
    sys.exit(1)

# Check BRAT for null geometries — warn but do not exit
with arcpy.da.SearchCursor(brat_fc, ["OID@", "SHAPE@"]) as cursor:
    null_geom = [row[0] for row in cursor if row[1] is None]
if null_geom:
    arcpy.AddWarning(
        f"{len(null_geom)} null geometries found in BRAT "
        f"(OIDs: {null_geom[:5]}{'...' if len(null_geom) > 5 else ''})"
    )
    arcpy.AddWarning(
        "These features will be skipped during clipping. Run Repair Geometry to fix."
    )
else:
    arcpy.AddMessage("\t> BRAT geometry: no null geometries found")

# Check BRAT and boundary extents overlap.
# projectAs() converts both extents to the output SR before comparing so that
# layers in different coordinate systems (e.g. BRAT in 5070, boundary in 4269)
# are compared in the same units.
target_sr    = arcpy.SpatialReference(OUTPUT_SR_WKID)
brat_ext     = brat_desc.extent.projectAs(target_sr)
boundary_ext = boundary_desc.extent.projectAs(target_sr)
if (brat_ext.XMax < boundary_ext.XMin or brat_ext.XMin > boundary_ext.XMax or
        brat_ext.YMax < boundary_ext.YMin or brat_ext.YMin > boundary_ext.YMax):
    arcpy.AddError("BRAT and boundary extents do not overlap.")
    arcpy.AddError(
        f"BRAT extent:     {brat_ext.XMin:.1f}, {brat_ext.YMin:.1f} — "
        f"{brat_ext.XMax:.1f}, {brat_ext.YMax:.1f}"
    )
    arcpy.AddError(
        f"Boundary extent: {boundary_ext.XMin:.1f}, {boundary_ext.YMin:.1f} — "
        f"{boundary_ext.XMax:.1f}, {boundary_ext.YMax:.1f}"
    )
    arcpy.AddError(
        "Verify both layers cover the same area and are in compatible projections."
    )
    sys.exit(1)
arcpy.AddMessage("\t> BRAT and boundary extents overlap")

# Check BRAT has required capacity fields
brat_fields = {f.name for f in arcpy.ListFields(brat_fc)}
if ex_field not in brat_fields:
    arcpy.AddError(f"Field '{ex_field}' not found in BRAT layer.")
    arcpy.AddError("Set raw_ex_field to the correct existing capacity field name.")
    sys.exit(1)
if hpe_field not in brat_fields:
    arcpy.AddError(f"Field '{hpe_field}' not found in BRAT layer.")
    arcpy.AddError("Set raw_hpe_field to the correct historic/potential capacity field name.")
    sys.exit(1)
arcpy.AddMessage(f"\t> BRAT fields: {ex_field} (EX), {hpe_field} (HPE)")

# Check oCC_EX values are not all null — normalization would silently fail
ex_values = [r[0] for r in arcpy.da.SearchCursor(brat_fc, [ex_field]) if r[0] is not None]
if not ex_values:
    arcpy.AddError(
        f"All values in '{ex_field}' are null. Cannot compute Conflict Risk Index."
    )
    sys.exit(1)

# Check NLCD coordinate system against the output SR.
# For local files, arcpy.management.Clip writes in the file's native SR — if it doesn't
# match OUTPUT_SR_WKID, the clipped raster and buffer polygons will misalign in zonal stats.
# For image service URLs, arcpy writes the clipped output using arcpy.env.outputCoordinateSystem
# (set to OUTPUT_SR_WKID below), so the GDB raster is always in the correct SR regardless of
# the service's native projection. Checking the service SR would produce a false error.
if nlcd_raster.startswith("https://"):
    arcpy.AddMessage(
        f"\t> NLCD: image service — clipped output will be written in WKID {OUTPUT_SR_WKID}"
    )
else:
    nlcd_desc = arcpy.Describe(nlcd_raster)
    nlcd_sr   = nlcd_desc.spatialReference
    if nlcd_sr.factoryCode != OUTPUT_SR_WKID:
        arcpy.AddError(f"NLCD is in {nlcd_sr.name} (WKID {nlcd_sr.factoryCode}).")
        arcpy.AddError(f"Tool output SR is {target_sr.name} (WKID {OUTPUT_SR_WKID}).")
        arcpy.AddError(f"Re-project NLCD to WKID {OUTPUT_SR_WKID} before running.")
        sys.exit(1)
    else:
        arcpy.AddMessage(f"\t> NLCD projection: {nlcd_sr.name} — matches output SR")

arcpy.AddMessage("\t> All inputs verified.\n")


# ============================================================
# REPORT SETUP
# ============================================================

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
        arcpy.AddMessage("--- Step 1/5: Setting Up Workspace ---")
        gdb_path = os.path.join(output_dir, OUTPUT_GDB_NAME)
        if not arcpy.Exists(gdb_path):
            arcpy.management.CreateFileGDB(output_dir, OUTPUT_GDB_NAME)
            arcpy.AddMessage(f"\t> Created GDB: {gdb_path}")
        else:
            arcpy.AddMessage(f"\t> Using existing GDB: {gdb_path}")

        arcpy.env.workspace              = gdb_path
        arcpy.env.overwriteOutput        = overwrite
        arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(OUTPUT_SR_WKID)
        print(f"Output GDB: {gdb_path}", file=report)

        # ----- 2) Clip Inputs -----
        arcpy.AddMessage("\n--- Step 2/5: Clipping Inputs ---")
        brat_clip, brat_buffer = clip_and_buffer_brat(
            brat_fc, boundary_fc, buffer_m, gdb_path
        )
        if not brat_clip or not brat_buffer:
            arcpy.AddError("BRAT clip/buffer failed. See errors above.")
            sys.exit(1)

        nlcd_clip = clip_nlcd(nlcd_raster, boundary_fc, gdb_path)
        if not nlcd_clip:
            arcpy.AddError("NLCD clip failed. See errors above.")
            sys.exit(1)

        # Clip FIS and confidence to local rasters before analysis.
        # arcpy.Raster() cannot operate on raw image service URLs — they must be
        # clipped to the GDB first, the same way NLCD is handled above.
        fis_local  = None
        conf_local = None
        if impervious_raster:
            fis_local = clip_ancillary_raster(
                impervious_raster, boundary_fc, "fis_clipped", gdb_path
            )
            if not fis_local:
                arcpy.AddWarning("FIS clipping failed — conflict scores will use class weights only.")
        if confidence_raster:
            conf_local = clip_ancillary_raster(
                confidence_raster, boundary_fc, "confidence_clipped", gdb_path
            )
            if not conf_local:
                arcpy.AddWarning("Confidence clipping failed — LC confidence flagging will be skipped.")

        # ----- 3) Conflict Risk Index -----
        arcpy.AddMessage("\n--- Step 3/5: Conflict Risk Index ---")
        conflict_fc = compute_conflict_risk(
            brat_buffer, ex_field, nlcd_clip, boundary_fc, gdb_path,
            impervious_raster=fis_local,
            confidence_raster=conf_local,
        )
        if not conflict_fc:
            arcpy.AddError("Conflict Risk Index failed. See errors above.")
            sys.exit(1)

        # ----- 4) Restoration Opportunity Index -----
        arcpy.AddMessage("\n--- Step 4/5: Restoration Opportunity Index ---")
        restoration_fc = compute_restoration_opp(
            brat_buffer, ex_field, hpe_field, nlcd_clip, boundary_fc, gdb_path,
            impervious_raster=fis_local,
            confidence_raster=conf_local,
        )
        if not restoration_fc:
            arcpy.AddError("Restoration Opportunity Index failed. See errors above.")
            sys.exit(1)

        # ----- 5) Planning Summary & Results -----
        arcpy.AddMessage("\n--- Step 5/5: Planning Summary & Results ---")
        summary_fc = compute_planning_summary(
            boundary_fc, conflict_fc, restoration_fc, gdb_path
        )
        if not summary_fc:
            arcpy.AddError("Planning Summary failed. See errors above.")
            sys.exit(1)

        print_summary(
            summary_fc,
            boundary_type or "Boundary",
            report_file=report,
        )

        print(f"\nOutputs written to: {gdb_path}", file=report)
        for layer in OUTPUT_LAYERS.values():
            print(f"\t- {layer}", file=report)

    arcpy.AddMessage(f"\nReport saved to: {report_path}")

except arcpy.ExecuteError:
    arcpy.AddError(arcpy.GetMessages(2))

except Exception as e:
    arcpy.AddError(f"An error occurred: {e}")

finally:
    arcpy.CheckInExtension("Spatial")

arcpy.AddMessage("\nScript Execution Complete.")
