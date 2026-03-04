'''
NR426 Lesson 5 demo code
Completed by: Zachary Cramton
Date: 24FEB2026

Your Lab 5 task is to correct and improve the code based on what we discuss in class
I *think* there are 8 errors to fix, plus several ways to improve the code

Updated Nov 2025
'''

import arcpy
import sys

# ----- Env & Var Setup -----
#Set path
path = r"L5LabData"

# Set vars
statesshp = "US_states.shp"
MaxYfld = "MaxY"

# Build full path for source verification
fullPath = rf"{path}\{statesshp}"

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


# ----- Main Processing -----
# Using Try/Except Block for Error Handling

try:
    # Add MaxY Field
    print (f"\n Adding field {MaxYfld} to {statesshp}...")

    arcpy.management.AddField(
        in_table = statesshp,
        field_name = MaxYfld,
        field_type = "DOUBLE"
    )

    #Calculate geometry to populate field with max y coordinate
    print ("...updating geometry attributes...\n")
    arcpy.management.CalculateGeometryAttributes(
        in_features = statesshp,
        geometry_property = "EXTENT_MAX_Y"
    )
    #Use cursor to read values in table and return the state with the highest value,
    #but only for the lower 48 states
    print ("...creating the cursor and looping through...\n")
    lower48sql = "STATE_NAME NOT IN ('Hawaii', 'Alaska')"
    with arcpy.da.SearchCursor(statesshp, [MaxYfld, "STATE_NAME"], lower48sql) as cur:
        for row in cur:
            mostnorth = max(cur, key=lambda row: row[0])
        state_name = mostnorth[1]
        theMaxYvalue = mostnorth[0]
    print (f"The state containing the northernmost point in the lower 48 is: {state_name} with a latitude of {theMaxYvalue}.")

    # Add:
    # Formatting and expanding print statements.
    # Ensure correct data formatting with dsc, exit if it is incorrect.

    # Look at geospatial centroid vibe coding lecture

print(f"\n[INFO] Checking for input data: {full_path}")
if not arcpy.Exists(full_path):
    raise FileNotFoundError(
        f"\n[ERROR] Input dataset not found.\n"
        f"        Expected location: {full_path}\n"
        f"        Please verify the path and filename and try again."
    )
print(f"[OK]   Input dataset found: {full_path}")