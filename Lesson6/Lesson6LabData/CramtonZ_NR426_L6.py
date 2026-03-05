"""
Python script: CramtonZ_NR426_L6.py
Author: Paul Zandbergen
Modified by: Zachary Cramton
Last Changes: 26FEB2026

Random Feature Selector
ArcGIS Pro Custom Toolbox Script

This script selects a random sample of input features based on a specified count and saves the results as a new
feature class. Using random.sample() on a list of OIDs created with a SearchCursor.

To help with statistical validity while also providing flexibility, this script includes a significance threshold
parameter set by the user defaulting to 50% (preventing selection of the majority of features) to allow for
smaller data to be used when testing the script. For scientifically valid testing, it is likely a good idea to
use 10% as a basic statistical standard or assess the structure of the sampling used in random.sample() to
determine selection needs for statistical validity.

Parameters:
    0 - Input FC (shapefile or geodatabase FC)
    1 - Output FC path
    2 - Number of features to randomly select (int > 0)
    3 - Significance threshold as whole % 1-99 (default 50)

If viewing on GitHub, reference the photos in the Lesson6 directory for toolbox setup help.
"""

# Import modules.
import arcpy
import random
import sys
import os

# ============================================================
# TOOL PARAMETERS
# ============================================================
inputfc  = arcpy.GetParameterAsText(0)  # Input feature class
outputfc = arcpy.GetParameterAsText(1)  # Output feature class
raw_outcount  = arcpy.GetParameterAsText(2) # User input # to randomly select
raw_threshold = arcpy.GetParameterAsText(3) # User input % for significance


# ============================================================
# PARAMETER VALIDATION
# ============================================================

# ----- Validate Parameters -----
# Validate input path exists
if not arcpy.Exists(inputfc):
    arcpy.AddError(
        f"Input feature class not found: '{inputfc}'. "
        "Please verify the path and try again."
    )
    sys.exit(1)

# Validate output workspace exists
output_workspace = os.path.dirname(outputfc)
if not arcpy.Exists(output_workspace):
    arcpy.AddError(
        f"Output workspace does not exist: '{output_workspace}'. "
        "Please verify the output path and try again."
    )
    sys.exit(1)

# Validate outcount — must be a positive whole number.
try:
    outcount = int(raw_outcount)
    if outcount <= 0:
        arcpy.AddError(
            "Feature count must be a positive whole number (1 or greater). "
            "Please enter a valid number and try again."
        )
        sys.exit(1)
except ValueError:
    arcpy.AddError(
        f"'{raw_outcount}' is not a valid number. "
        "Please enter a positive whole number for the feature count."
    )
    sys.exit(1)

# Validate sig_threshold — whole number percentage between 1 and 99.
# Defaults to 50 if left blank. Converted to decimal for internal use.
try:
    sig_threshold = int(raw_threshold) if raw_threshold else 50
    if not 1 <= sig_threshold <= 99:
        arcpy.AddError(
            f"'{sig_threshold}' is not a valid significance threshold. "
            "Please enter a whole number between 1 and 99."
        )
        sys.exit(1)
except ValueError:
    arcpy.AddError(
        f"'{raw_threshold}' is not a valid significance threshold. "
        "Please enter a whole number between 1 and 99."
    )
    sys.exit(1)


# ============================================================
# PREPROCESSING & GENERAL VALIDATION
# ============================================================

# Convert whole number percentage to decimal for internal comparisons.
sig_threshold_decimal = sig_threshold / 100
arcpy.AddMessage(f"Significance threshold set to: {sig_threshold}%")

# Compare outcount against actual feature count before any geoprocessing runs.
arcpy.AddMessage(f"Validating inputs for: {inputfc}")

feature_count = int(arcpy.management.GetCount(inputfc).getOutput(0))
arcpy.AddMessage(f"  Input layer contains {feature_count} features.")
arcpy.AddMessage(f"  Requested selection count: {outcount}")

# Hard stop — cannot select more features than exist in the layer.
if outcount > feature_count:
    arcpy.AddError(
        f"Cannot select {outcount} features — the input layer only contains "
        f"{feature_count}. Please choose a number less than {feature_count} and try again."
    )
    sys.exit(1)

# Soft warning — above the user-defined threshold, the selection represents
# a significant portion of the population. The tool proceeds but warns the user.
if outcount > feature_count * sig_threshold_decimal:
    pct_selected = (outcount / feature_count) * 100
    recommended_max = int(feature_count * sig_threshold_decimal)
    arcpy.AddWarning(
        f"You are selecting {outcount} of {feature_count} features "
        f"({pct_selected:.1f}% of the dataset), which exceeds your significance "
        f"threshold of {sig_threshold}%. This selection does not meet the statistical "
        f"validity set by the significance threshold for randomness.\n"
        f"For a meaningful random sample, select no more than {recommended_max} features. "
        f"Proceeding with selection anyway."
    )

# ============================================================
# SELECTION
# ============================================================
try:
    arcpy.AddMessage("Reading OIDs from input feature class...")

    # Build a list of all valid OIDs from the input layer.
    # Iterating the cursor handles non-contiguous OIDs (gaps from deleted features) and loads the full
    # population into memory before random.sample() runs.
    inlist = []
    with arcpy.da.SearchCursor(inputfc, "OID@") as cursor:
        for row in cursor:
            inlist.append(row[0])

    arcpy.AddMessage(f"Selecting {outcount} features at random...")

    # Sample k unique OIDs without replacement.
    randomlist = random.sample(inlist, outcount)

    # Build the SQL WHERE clause for Select_analysis.
    desc     = arcpy.da.Describe(inputfc)
    fldname  = desc["OIDFieldName"]
    sqlfield = arcpy.AddFieldDelimiters(inputfc, fldname)

    # Handling single-item tuples explicitly for universal compatibility
    if len(randomlist) == 1:
        sqlexp = f"{sqlfield} = {randomlist[0]}"
    else:
        sqlexp = f"{sqlfield} IN {tuple(randomlist)}"

    arcpy.AddMessage(f"Writing selected features to: {outputfc}")
    arcpy.Select_analysis(inputfc, outputfc, sqlexp)

    arcpy.AddMessage(
        f"Complete. {outcount} randomly selected features written to:\n  {outputfc}"
    )

# Geoprocessing errors — surfaced separately.
except arcpy.ExecuteError:
    arcpy.AddError("> ArcPy Geoprocessing Error:")
    arcpy.AddError(arcpy.GetMessages(2))
    sys.exit(1)

# Catch-all for anything unexpected.
except Exception as e:
    arcpy.AddError(f"> Unexpected Error: {e}")
    sys.exit(1)