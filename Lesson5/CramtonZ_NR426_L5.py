'''
NR426 Lesson 5 demo code
Modified by: Zachary Cramton
Date: 24FEB2026

Your Lab 5 task is to correct and improve the code based on what we discuss in class
I *think* there are 8 errors to fix, plus several ways to improve the code
Updated Nov 2025

This program finds the northernmost state in the contiguous US (lower 48) by:
  1. Adding a 'MaxY' field to the US_states shapefile
  2. Populating it with each state's maximum Y (latitude) coordinate
  3. Using a SearchCursor to identify the state with the highest MaxY value
'''

import arcpy
import sys

# ----- Env & Var Setup -----
#Set path
path = r"Lesson5"

# Set vars
statesshp = "US_states.shp"
MaxYfld = "MaxY"

# Build full path for source verification
fullPath = rf"{path}\{statesshp}"

# Using Try/Except Block for Error Handling
try:
    # ----- Pre-processing Checks -----
    # Check that input data exists
    print(f"\nChecking for input data: {fullPath}")
    if not arcpy.Exists(fullPath):
        raise FileNotFoundError(
            f"\t >ERROR: Input dataset not found.\n"
            f"\t\tExpected location: {fullPath}\n"
            f"\t\tPlease verify the path and filename and try again."
        )
    print(f"Input dataset found: {fullPath}")

    # Confirm vector input (fc/shp)
    print(f"\nVerifying input data type...")
    dsc = arcpy.da.Describe(fullPath)

    # Allowed vector geometry types
    VECTOR_TYPES = {"FeatureClass", "ShapeFile"}

    if dsc["dataType"] not in VECTOR_TYPES:
        raise TypeError(
            f"\n\t ERROR: Incorrect data type.\n"
            f"        Expected: a vector feature class or shapefile\n"
            f"        Found:    '{dsc['dataType']}' at {fullPath}\n"
            f"        Please supply a polygon/polyline/point feature class."
        )
    print(f"\tData type confirmed: '{dsc['dataType']}' "
          f"(geometry: {dsc.get('shapeType', 'N/A')})")

    # Enable overwrite output so existing outputs are not a blocker
    arcpy.env.overwriteOutput = True
    print(f"\nOverwrite output set to: {arcpy.env.overwriteOutput}")

    # Set workspace after checks are complete
    arcpy.env.workspace = path

    # ----- Main Processing -----
    # Add MaxY Field
    print (f"\n Adding field {MaxYfld} to {statesshp}...")

    # Only add the field if it does not already exist
    existing_fields = [f.name for f in arcpy.ListFields(statesshp)]
    if MaxYfld in existing_fields:
        print(f"Field '{MaxYfld}' already exists — skipping AddField.")
    else:
        arcpy.management.AddField(
            in_table    = statesshp,
            field_name  = MaxYfld,
            field_type  = "DOUBLE"
        )
        print(f"Field '{MaxYfld}' added successfully.")

    #Calculate geometry to populate field with max y coordinate
    print(f"\nCalculating geometry attributes (EXTENT_MAX_Y) ...")

    # geometry_property expects a list of [field, property] pairs
    arcpy.management.CalculateGeometryAttributes(
        in_features=statesshp,
        geometry_property=[[MaxYfld, "EXTENT_MAX_Y"]]
    )
    print(f"\t'{MaxYfld}' populated with EXTENT_MAX_Y values.")


    #Use cursor to read values in table and return the state with the highest value,
    #but only for the lower 48 states

    print(f"\nSearching for the northernmost lower-48 state ...")

    # SQL clause to exclude non-contiguous states
    lower48sql = "STATE_NAME NOT IN ('Hawaii', 'Alaska')"

    with arcpy.da.SearchCursor(
        statesshp,
        [MaxYfld, "STATE_NAME"],
        lower48sql
    ) as cur:
        # max() iterates the cursor once and returns the row with the
        # highest MaxY value — no for-loop needed
        mostnorth = max(cur, key=lambda row: row[0])

    state_name   = mostnorth[1]
    theMaxYvalue = mostnorth[0]

    # ----- Results -----
    print("\n" + "=" * 60)
    print("  RESULTS")
    print("=" * 60)
    print(
        f"\nThe state containing the northernmost point\n"
        f"  in the lower 48 is: {state_name}\n"
        f"  Maximum Latitude (MaxY): {theMaxYvalue:.4f}°\n"
    )
    print("=" * 60)

# --- Catch ArcPy-specific errors (licence issues, tool failures, etc.) ---
except arcpy.ExecuteError:
    arcpy_msgs = arcpy.GetMessages(2)       # severity 2 = errors only
    print(
        f"\n\t>ARCPY ERROR: A geoprocessing tool failed.\n"
        f"\tArcPy messages:\n{arcpy_msgs}"
    )
    sys.exit(1)

# --- Catch the custom pre-flight exceptions re-raised above ---
except (FileNotFoundError, TypeError) as e:
    print(e)
    sys.exit(1)

# --- Catch any other unexpected errors ---
except Exception as e:
    print(
        f"\n\t>UNEXPECTED ERROR: {type(e).__name__}: {e}\n"
        f"\tPlease review the script and input data."
    )
    sys.exit(1)