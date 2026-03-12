"""
NR426 Beaver Conflict & Restoration Analysis
CramtonZ_NR426_BeaverConflict_Tools.py
Zachary Cramton

Companion file to CramtonZ_NR426_BeaverConflict.py.
Contains all analysis functions and helper functions.
Not intended to be run directly.
"""

# Import Modules
import arcpy
import os


# ============================================================
# SHARED CONSTANTS
# ============================================================
# Constants used directly by the functions in this file.
# Tunable parameters (field name candidates, buffer default, GDB name, default URLs)
# remain in the main script.

# Output layer names inside the GDB
OUTPUT_LAYERS = {
    "brat_clipped":     "brat_clipped",
    "brat_buffer":      "brat_riparian_buffer",
    "nlcd_clipped":     "nlcd_clipped",
    "conflict_risk":    "conflict_risk",
    "restoration_opp":  "restoration_opp",
    "planning_summary": "planning_summary",
}

# NLCD development intensity weights (classes 21-24 only; all others = 0.0)
NLCD_DEV_WEIGHTS = {21: 0.2, 22: 0.4, 23: 0.7, 24: 1.0}

# NLCD 2021 class value range for remap table (11 = Open Water, 95 = Ice/Snow)
NLCD_VALUE_MIN = 11
NLCD_VALUE_MAX = 96   # Exclusive upper bound

# Risk classification breaks applied to all normalized 0-1 scores
# Format: (lower_bound, upper_bound, label)
RISK_CLASSES = [
    (0.00, 0.20, "Very Low"),
    (0.20, 0.40, "Low"),
    (0.40, 0.60, "Moderate"),
    (0.60, 0.80, "High"),
    (0.80, 1.01, "Very High"),   # 1.01 upper bound catches scores of exactly 1.0
]

# Land cover confidence threshold (0-100).
# Segments with mean buffer confidence below this value are flagged "Review"
# in lc_confidence_flag. Does not affect index scores.
LC_CONFIDENCE_THRESHOLD = 75

# Summary report display settings
SUMMARY_MAX_ROWS   = 25
SUMMARY_NAME_WIDTH = 24
SUMMARY_COL_WIDTH  = 14


# ============================================================
# ANALYSIS FUNCTIONS
# ============================================================

def clip_and_buffer_brat(brat_path, boundary_path, buffer_dist, output_gdb):
    """
    Clips BRAT to the analysis boundary, then buffers each segment to a riparian corridor.
    Returns (clipped_path, buffer_path) or (None, None) on failure.
    """
    try:
        brat_clip = os.path.join(output_gdb, OUTPUT_LAYERS["brat_clipped"])
        arcpy.analysis.Clip(brat_path, boundary_path, brat_clip)

        clip_count = int(arcpy.management.GetCount(brat_clip)[0])
        if clip_count == 0:
            print(f"\t> ERROR: BRAT clip produced zero features.")
            print(f"\t> Verify BRAT overlaps the boundary layer.")
            return None, None
        print(f"\t> Clipped BRAT: {clip_count} segment(s)")

        brat_buffer = os.path.join(output_gdb, OUTPUT_LAYERS["brat_buffer"])
        arcpy.analysis.Buffer(
            in_features=brat_clip,
            out_feature_class=brat_buffer,
            buffer_distance_or_field=f"{buffer_dist} Meters",
            dissolve_option="NONE",
        )
        print(f"\t> Riparian buffer ({buffer_dist}m): {clip_count} corridor polygon(s)")
        return brat_clip, brat_buffer

    except arcpy.ExecuteError:
        print(f"\t> ERROR in clip_and_buffer_brat:\n{arcpy.GetMessages(2)}")
        return None, None
    except Exception as e:
        print(f"\t> ERROR in clip_and_buffer_brat: {e}")
        return None, None


def clip_nlcd(nlcd_path, boundary_path, output_gdb):
    """
    Clips NLCD to the analysis boundary and sets it as the arcpy snap raster and mask.
    Returns the clipped raster path or None on failure.
    """
    try:
        make_layer(boundary_path, "boundary_lyr_nlcd")

        extent = arcpy.Describe("boundary_lyr_nlcd").extent
        rect   = f"{extent.XMin} {extent.YMin} {extent.XMax} {extent.YMax}"

        nlcd_clip = os.path.join(output_gdb, OUTPUT_LAYERS["nlcd_clipped"])
        arcpy.management.Clip(
            in_raster=nlcd_path,
            rectangle=rect,
            out_raster=nlcd_clip,
            in_template_dataset="boundary_lyr_nlcd",
            clipping_geometry="ClippingGeometry",
            maintain_clipping_extent="NO_MAINTAIN_EXTENT",
        )

        # Verify clip produced data — all-NoData raster would cause silent failures downstream
        if arcpy.Raster(nlcd_clip).maximum is None:
            print(f"\t> ERROR: NLCD clip produced an all-NoData raster.")
            print(f"\t> Verify NLCD covers your area of interest.")
            return None

        # Use saved raster path — not the temp layer — so env mask stays valid
        arcpy.env.snapRaster = nlcd_clip
        arcpy.env.cellSize   = nlcd_clip
        arcpy.env.mask       = nlcd_clip

        print(f"\t> NLCD clipped and set as snap raster")
        return nlcd_clip

    except arcpy.ExecuteError:
        print(f"\t> ERROR in clip_nlcd:\n{arcpy.GetMessages(2)}")
        return None
    except Exception as e:
        print(f"\t> ERROR in clip_nlcd: {e}")
        return None
    finally:
        if arcpy.Exists("boundary_lyr_nlcd"):
            arcpy.management.Delete("boundary_lyr_nlcd")


def compute_conflict_risk(brat_buffer, ex_fld, nlcd_clip, boundary_path, output_gdb,
                          impervious_raster=None, confidence_raster=None):
    """
    Scores each segment: conflict_score = oCC_EX_norm x mean_dev_weight.
    Dev weight optionally scaled by FIS. Confidence flagged if raster provided.
    Tags each segment with its boundary unit name. Returns FC path or None on failure.
    """
    try:
        out_fc = os.path.join(output_gdb, OUTPUT_LAYERS["conflict_risk"])
        if arcpy.Exists(out_fc):
            arcpy.management.Delete(out_fc)
        arcpy.management.CopyFeatures(brat_buffer, out_fc)

        dev_weight_raster = reclassify_nlcd_dev_weight(nlcd_clip, impervious_raster)
        zonal_mean_to_field(out_fc, dev_weight_raster, "dev_weight_mean")
        normalize_field(out_fc, ex_fld, "oCC_EX_norm")

        add_field_if_missing(out_fc, "conflict_score", "DOUBLE")
        arcpy.management.CalculateField(
            out_fc, "conflict_score",
            "(!oCC_EX_norm! or 0.0) * (!dev_weight_mean! or 0.0)",
            "PYTHON3",
        )

        normalize_field(out_fc, "conflict_score", "conflict_score_norm")
        classify_score(out_fc, "conflict_score_norm", "conflict_class")

        # Warn if all scores are null — indicates a zonal stats or normalization failure
        scored = [r[0] for r in arcpy.da.SearchCursor(out_fc, ["conflict_score_norm"])
                  if r[0] is not None]
        if not scored:
            print(f"\t> Warning: All conflict_score_norm values are null.")
            print(f"\t> Check that the riparian buffer overlaps the NLCD raster.")

        # Land cover confidence — flag for review, does not affect index score
        if confidence_raster:
            zonal_mean_to_field(out_fc, arcpy.Raster(confidence_raster), "lc_confidence_mean")
            flag_lc_confidence(out_fc, "lc_confidence_mean")
            print(f"\t> LC confidence flagged (threshold: {LC_CONFIDENCE_THRESHOLD}%)")

        # Tag each segment with its boundary unit name for downstream filtering
        tag_segments_with_boundary(out_fc, boundary_path)

        print(f"\t> Conflict Risk Index: {int(arcpy.management.GetCount(out_fc)[0])} segments scored")
        return out_fc

    except arcpy.ExecuteError:
        print(f"\t> ERROR in compute_conflict_risk:\n{arcpy.GetMessages(2)}")
        return None
    except Exception as e:
        print(f"\t> ERROR in compute_conflict_risk: {e}")
        return None


def compute_restoration_opp(brat_buffer, ex_fld, hpe_fld, nlcd_clip, boundary_path, output_gdb,
                             impervious_raster=None, confidence_raster=None):
    """
    Scores each segment: restoration_score = gap_norm x (1 - mean_dev_weight).
    Gap = max(0, oCC_PT - oCC_EX). Dev weight optionally scaled by FIS.
    Confidence flagged if raster provided. Tags each segment with boundary unit name.
    Returns FC path or None on failure.
    """
    try:
        out_fc = os.path.join(output_gdb, OUTPUT_LAYERS["restoration_opp"])
        if arcpy.Exists(out_fc):
            arcpy.management.Delete(out_fc)
        arcpy.management.CopyFeatures(brat_buffer, out_fc)

        add_field_if_missing(out_fc, "restoration_gap", "DOUBLE")
        arcpy.management.CalculateField(
            out_fc, "restoration_gap",
            f"max(0.0, (!{hpe_fld}! or 0.0) - (!{ex_fld}! or 0.0))",
            "PYTHON3",
        )

        dev_weight_raster = reclassify_nlcd_dev_weight(nlcd_clip, impervious_raster)
        zonal_mean_to_field(out_fc, dev_weight_raster, "dev_weight_mean")
        normalize_field(out_fc, "restoration_gap", "gap_norm")

        add_field_if_missing(out_fc, "restoration_score", "DOUBLE")
        arcpy.management.CalculateField(
            out_fc, "restoration_score",
            "(!gap_norm! or 0.0) * (1.0 - (!dev_weight_mean! or 0.0))",
            "PYTHON3",
        )

        normalize_field(out_fc, "restoration_score", "restoration_score_norm")
        classify_score(out_fc, "restoration_score_norm", "restoration_class")

        # Warn if all scores are null
        scored = [r[0] for r in arcpy.da.SearchCursor(out_fc, ["restoration_score_norm"])
                  if r[0] is not None]
        if not scored:
            print(f"\t> Warning: All restoration_score_norm values are null.")
            print(f"\t> Check that the riparian buffer overlaps the NLCD raster.")

        # Land cover confidence — flag for review, does not affect index score
        if confidence_raster:
            zonal_mean_to_field(out_fc, arcpy.Raster(confidence_raster), "lc_confidence_mean")
            flag_lc_confidence(out_fc, "lc_confidence_mean")
            print(f"\t> LC confidence flagged (threshold: {LC_CONFIDENCE_THRESHOLD}%)")

        # Tag each segment with its boundary unit name for downstream filtering
        tag_segments_with_boundary(out_fc, boundary_path)

        print(f"\t> Restoration Opportunity Index: {int(arcpy.management.GetCount(out_fc)[0])} segments scored")
        return out_fc

    except arcpy.ExecuteError:
        print(f"\t> ERROR in compute_restoration_opp:\n{arcpy.GetMessages(2)}")
        return None
    except Exception as e:
        print(f"\t> ERROR in compute_restoration_opp: {e}")
        return None


def compute_planning_summary(boundary_path, conflict_fc, restoration_fc, output_gdb):
    """
    Spatially joins mean conflict and restoration scores onto each boundary unit.
    Returns FC path or None on failure.
    """
    try:
        out_fc = os.path.join(output_gdb, OUTPUT_LAYERS["planning_summary"])
        if arcpy.Exists(out_fc):
            arcpy.management.Delete(out_fc)

        arcpy.management.CopyFeatures(boundary_path, out_fc)

        for join_fc, score_field, class_field in [
            (conflict_fc,    "conflict_score_norm",    "conflict_class"),
            (restoration_fc, "restoration_score_norm", "restoration_class"),
        ]:
            spatial_join_mean(out_fc, join_fc, score_field, class_field)

        unit_count = int(arcpy.management.GetCount(out_fc)[0])
        if unit_count == 0:
            print(f"\t> Warning: Planning summary has zero boundary units.")
            print(f"\t> Verify the boundary layer overlaps the BRAT data.")
        else:
            print(f"\t> Planning Summary: {unit_count} boundary unit(s)")
        return out_fc

    except arcpy.ExecuteError:
        print(f"\t> ERROR in compute_planning_summary:\n{arcpy.GetMessages(2)}")
        return None
    except Exception as e:
        print(f"\t> ERROR in compute_planning_summary: {e}")
        return None


def print_summary(summary_fc, bnd_type, report_file=None):
    """
    Prints a ranked summary table sorted by conflict score descending.
    Writes to console and to report_file simultaneously if provided.
    Capped at SUMMARY_MAX_ROWS rows.
    """
    name_field   = detect_name_field(summary_fc)
    all_fields   = {f.name for f in arcpy.ListFields(summary_fc)}
    score_fields = [f for f in ["conflict_score_norm", "restoration_score_norm"]
                    if f in all_fields]
    read_fields  = ["OID@"] + ([name_field] if name_field else []) + score_fields

    rows = []
    with arcpy.da.SearchCursor(summary_fc, read_fields) as cursor:
        for row in cursor:
            rows.append(row)

    sort_idx = 2 if name_field else 1
    rows.sort(key=lambda r: r[sort_idx] or 0.0, reverse=True)

    lines = []
    lines.append("=" * 62)
    lines.append(f"  BEAVER CONFLICT & RESTORATION — RESULTS SUMMARY")
    lines.append(f"  Boundary: {bnd_type}")
    lines.append("=" * 62)

    hdr = f"  {'OID':<6}"
    if name_field:
        hdr += f"{'Unit':<{SUMMARY_NAME_WIDTH}}"
    hdr += f"{'Conflict':>{SUMMARY_COL_WIDTH}}{'Restoration':>{SUMMARY_COL_WIDTH}}"
    lines.append(hdr)
    lines.append("  " + "-" * 58)

    for row in rows[:SUMMARY_MAX_ROWS]:
        idx  = 0
        oid  = row[idx]; idx += 1
        name = str(row[idx])[:SUMMARY_NAME_WIDTH - 2] if name_field else ""
        idx += (1 if name_field else 0)
        line = f"  {oid:<6}"
        if name_field:
            line += f"{name:<{SUMMARY_NAME_WIDTH}}"
        for _ in score_fields:
            val   = row[idx] if row[idx] is not None else 0.0
            line += f"{val:>{SUMMARY_COL_WIDTH}.3f}"
            idx  += 1
        lines.append(line)

    if len(rows) > SUMMARY_MAX_ROWS:
        lines.append(
            f"  ... {len(rows) - SUMMARY_MAX_ROWS} more units — "
            f"see planning_summary layer for full results."
        )
    lines.append("=" * 62)
    lines.append(
        "  Risk classes:  " + "  |  ".join(
            f"{label} ({lo:.1f}-{hi:.1f})" for lo, hi, label in RISK_CLASSES
        )
    )

    for line in lines:
        print(line)
        if report_file:
            print(line, file=report_file)
    print()
    if report_file:
        print("", file=report_file)


# ============================================================
# HELPER FUNCTIONS
# ============================================================
# Called by the analysis functions above, not from the main flow.

def make_layer(path, layer_name):
    """Creates a temp feature layer, deleting any existing layer of the same name first."""
    if arcpy.Exists(layer_name):
        arcpy.management.Delete(layer_name)
    arcpy.management.MakeFeatureLayer(path, layer_name)


def tag_segments_with_boundary(fc, boundary_path):
    """
    Spatially joins the boundary unit name onto each stream segment so results
    can be filtered by planning unit (e.g. county or watershed) in the output layer.
    Writes to boundary_name (TEXT, length 100). Warns if no name field is detected.
    """
    name_field = detect_name_field(boundary_path)
    if not name_field:
        print(f"\t> Warning: No recognizable name field found in boundary layer.")
        print(f"\t> Segments will not be tagged with boundary unit names.")
        print(f"\t> Add your name field to detect_name_field() candidates if needed.")
        return

    fm   = arcpy.FieldMappings()
    fmap = arcpy.FieldMap()
    fmap.addInputField(boundary_path, name_field)
    fmap.mergeRule   = "FIRST"
    out_f            = fmap.outputField
    out_f.name       = "boundary_name"
    out_f.aliasName  = "Boundary Unit"
    out_f.length     = 100
    fmap.outputField = out_f
    fm.addFieldMap(fmap)

    tmp = "in_memory\\sjoin_boundary_tag"
    if arcpy.Exists(tmp):
        arcpy.management.Delete(tmp)

    arcpy.analysis.SpatialJoin(
        target_features=fc,
        join_features=boundary_path,
        out_feature_class=tmp,
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_ALL",
        field_mapping=fm,
        match_option="HAVE_THEIR_CENTER_IN",
    )

    # If center-based join leaves gaps (segments crossing boundaries), fall back to INTERSECT
    unmatched = [r[0] for r in arcpy.da.SearchCursor(tmp, ["boundary_name"])
                 if r[0] in (None, "")]
    if unmatched:
        arcpy.management.Delete(tmp)
        arcpy.analysis.SpatialJoin(
            target_features=fc,
            join_features=boundary_path,
            out_feature_class=tmp,
            join_operation="JOIN_ONE_TO_ONE",
            join_type="KEEP_ALL",
            field_mapping=fm,
            match_option="INTERSECT",
        )

    add_field_if_missing(fc, "boundary_name", "TEXT", field_length=100)
    arcpy.management.JoinField(fc, "OBJECTID", tmp, "TARGET_FID", ["boundary_name"])
    arcpy.management.Delete(tmp)
    print(f"\t> Segments tagged with boundary unit name from '{name_field}'")


def reclassify_nlcd_dev_weight(nlcd_raster_path, impervious_raster=None):
    """
    Reclassifies NLCD land cover to development weights (0.0-1.0).
    If impervious_raster is provided, weights are scaled by fractional imperviousness (FIS/100).
    Returns a Spatial Analyst raster object (not saved to disk).
    """
    remap_list = [
        [val, int(NLCD_DEV_WEIGHTS.get(val, 0.0) * 100)]
        for val in range(NLCD_VALUE_MIN, NLCD_VALUE_MAX)
    ]
    remap         = arcpy.sa.RemapValue(remap_list)
    reclass       = arcpy.sa.Reclassify(nlcd_raster_path, "Value", remap, "NODATA")
    weight_raster = arcpy.sa.Float(reclass) / 100.0

    if impervious_raster:
        # Scale class weight by fractional imperviousness (0-100 → 0-1).
        # Non-developed pixels have a base weight of 0.0, so FIS has no effect on them.
        fis           = arcpy.sa.Float(arcpy.Raster(impervious_raster)) / 100.0
        weight_raster = weight_raster * fis
        print(f"\t> FIS applied: dev weights scaled by fractional imperviousness")

    return weight_raster


def flag_lc_confidence(fc, confidence_field):
    """
    Writes 'Review' or 'OK' to lc_confidence_flag based on LC_CONFIDENCE_THRESHOLD.
    'Review' flags segments where mean buffer LC confidence is below the threshold.
    Does not modify index scores.
    """
    add_field_if_missing(fc, "lc_confidence_flag", "TEXT", field_length=10)
    codeblock = (
        f"def flag(v):\n"
        f"    if v is None: return 'No Data'\n"
        f"    return 'OK' if v >= {LC_CONFIDENCE_THRESHOLD} else 'Review'\n"
    )
    arcpy.management.CalculateField(
        fc, "lc_confidence_flag",
        f"flag(!{confidence_field}!)",
        "PYTHON3", codeblock,
    )


def zonal_mean_to_field(fc, value_raster, out_field):
    """
    Computes zonal mean of value_raster per polygon and writes result to out_field.
    Uses a unique in_memory table name per field to prevent session collisions.
    """
    add_field_if_missing(fc, out_field, "DOUBLE")

    zonal_tbl = f"in_memory\\zonal_{out_field}"
    if arcpy.Exists(zonal_tbl):
        arcpy.management.Delete(zonal_tbl)

    arcpy.sa.ZonalStatisticsAsTable(
        in_zone_data=fc,
        zone_field="OBJECTID",
        in_value_raster=value_raster,
        out_table=zonal_tbl,
        statistics_type="MEAN",
    )

    if int(arcpy.management.GetCount(zonal_tbl)[0]) == 0:
        print(f"\t> Warning: Zonal statistics for '{out_field}' produced no results.")
        print(f"\t> Verify the riparian buffer overlaps the NLCD raster extent.")
        arcpy.management.Delete(zonal_tbl)
        return

    arcpy.management.JoinField(fc, "OBJECTID", zonal_tbl, "OBJECTID_1", ["MEAN"])
    arcpy.management.CalculateField(
        fc, out_field,
        "!MEAN! if !MEAN! is not None else 0.0",
        "PYTHON3",
    )
    if "MEAN" in {f.name for f in arcpy.ListFields(fc)}:
        arcpy.management.DeleteField(fc, "MEAN")
    arcpy.management.Delete(zonal_tbl)


def normalize_field(fc, in_field, out_field):
    """
    Min-max normalizes in_field to 0-1 and writes result to out_field.
    Sets out_field to 0.0 if all values are identical.
    """
    add_field_if_missing(fc, out_field, "DOUBLE")
    values = [r[0] for r in arcpy.da.SearchCursor(fc, [in_field]) if r[0] is not None]
    if not values:
        return
    vmin   = min(values)
    vrange = max(values) - vmin
    codeblock = (
        "def norm(v, vmin, vrange):\n"
        "    if v is None: return None\n"
        "    if vrange == 0: return 0.0\n"
        "    return (v - vmin) / vrange\n"
    )
    arcpy.management.CalculateField(
        fc, out_field,
        f"norm(!{in_field}!, {vmin}, {vrange})",
        "PYTHON3", codeblock,
    )


def classify_score(fc, score_field, class_field):
    """
    Assigns risk tier labels to class_field based on RISK_CLASSES breaks.
    TEXT fields are always created at length=20 for consistency.
    """
    add_field_if_missing(fc, class_field, "TEXT", field_length=20)
    lines  = ["def classify(v):"]
    lines += ["    if v is None: return 'No Data'"]
    for lo, hi, label in sorted(RISK_CLASSES, key=lambda x: x[0]):
        lines += [f"    if {lo} <= v < {hi}: return '{label}'"]
    lines += ["    return 'Very High'"]
    arcpy.management.CalculateField(
        fc, class_field,
        f"classify(!{score_field}!)",
        "PYTHON3", "\n".join(lines) + "\n",
    )


def spatial_join_mean(target_fc, join_fc, score_field, class_field):
    """
    Joins mean score and majority class from join_fc onto target_fc by intersection.
    Uses a unique in_memory table name per score_field to prevent session collisions.
    """
    fm = arcpy.FieldMappings()
    for field, rule in [(score_field, "MEAN"), (class_field, "MAJORITY")]:
        fmap = arcpy.FieldMap()
        try:
            fmap.addInputField(join_fc, field)
        except Exception:
            continue
        fmap.mergeRule   = rule
        out_f            = fmap.outputField
        out_f.name       = field
        fmap.outputField = out_f
        fm.addFieldMap(fmap)

    tmp = f"in_memory\\sjoin_{score_field}"
    if arcpy.Exists(tmp):
        arcpy.management.Delete(tmp)

    arcpy.analysis.SpatialJoin(
        target_features=target_fc,
        join_features=join_fc,
        out_feature_class=tmp,
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_ALL",
        field_mapping=fm,
        match_option="INTERSECT",
    )

    existing = {f.name for f in arcpy.ListFields(tmp)}
    for field in [score_field, class_field]:
        if field in existing:
            ftype   = "TEXT" if "class" in field else "DOUBLE"
            fkwargs = {"field_length": 20} if ftype == "TEXT" else {}
            add_field_if_missing(target_fc, field, ftype, **fkwargs)
            arcpy.management.JoinField(target_fc, "OBJECTID", tmp, "TARGET_FID", [field])
    arcpy.management.Delete(tmp)


def add_field_if_missing(fc, field_name, field_type, field_length=None):
    """
    Adds a field only if it does not already exist.
    Always pass field_length for TEXT fields — default of 255 chars is rarely appropriate.
    """
    if field_name not in {f.name for f in arcpy.ListFields(fc)}:
        if field_length is not None:
            arcpy.management.AddField(fc, field_name, field_type, field_length=field_length)
        else:
            arcpy.management.AddField(fc, field_name, field_type)


def detect_name_field(fc):
    """
    Returns the first recognizable name field found in fc, or None.
    Add field names here if your boundary layer uses a non-standard name field.
    """
    candidates = ["NAME", "BASENAME", "NAMELSAD", "name", "huc8", "huc10",
                  "huc12", "HUC_NAME", "UNIT_NAME", "WATERSHED"]
    existing   = {f.name for f in arcpy.ListFields(fc)}
    return next((c for c in candidates if c in existing), None)
