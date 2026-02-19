"""
NR426 Lab3A
Completed by: Zachary Cramton
Date: 10FEB2026

Submitted with L3B demo code template

Use factory code to check projections.

"""

# Import Modules
import arcpy
import sys
import os

# ----- Setup -----
# Data location and workspace
dataLoc = r"L3LabData\RoadkillDataLab3.gdb"
arcpy.env.workspace = dataLoc
arcpy.env.overwriteOutput = True

print (os.getcwd())

# Confirm files exist
if not arcpy.Exists(dataLoc):
    print (f"\t> Error: Workspace {dataLoc} does not exist. Check the path and try again.")
    print ("\t> Exiting script...")
    sys.exit()
else:
    print (f"\t> Data Found at {dataLoc}:\n")

# Spatial Reference
# Factory Code for UTM Zone 18 NAD83
SRcode = 26918
tgtSR = arcpy.SpatialReference(SRcode)

# Clip Feature
clip_feature = "HRVCounties" # Clipping boundary

# ----- Processing -----

# ----- 1) Tables ------
# Check table count
tables = arcpy.ListTables(dataLoc)
print (f"\t- Number of Tables: {len(tables)}")

# ----- 2) Rasters -----
# 2a) Check raster count
rasters = arcpy.ListRasters()
print (f"\t- Number of Rasters: {len(rasters)}")

# Generate raster data summary
for r in rasters:
    dscR = arcpy.Describe(r)   # Set describe shortcut var
    srR = dscR.spatialReference # Identify current SR
    cellSize = arcpy.management.GetRasterProperties(r, 'CELLSIZEX') # Find raster spatial resolution
    units = srR.linearUnitName # Find SR units
    extent = dscR.extent       # Find raster spatial extent

    # 2b) Print data summary for current raster
    print(f"\n--- Raster Summary: {r} ---")
    print (f"SR: {srR.name} (Code: {srR.factoryCode}) | Cell Size: {cellSize} {units}")
    print (f"Extent Min: X[{extent.XMin}, {extent.YMin}], Y[{extent.XMax}, {extent.YMax}]")

    # 2c) Check Projection
    # Correct projection if needed
    if srR.factoryCode != SRcode:
        out_raster = f"{r}_UTM"
        if not arcpy.Exists(out_raster):
            print (f"\t> Projecting raster {r} to UTM...")
            arcpy.management.ProjectRaster(r, out_raster, tgtSR)
        else:
            print (f"{out_raster} already exists. Skipping...")


# ----- 3) Feature Classes -----
fcList = arcpy.ListFeatureClasses()

# 3a) Print the number of feature classes
print(f"\nNumber of Feature Classes: {len(fcList)}")

for fc in fcList:
    dscFC = arcpy.Describe(fc)
    fcName = dscFC.name
    srFC = dscFC.spatialReference
    fcCount = arcpy.management.GetCount(fc)
    extFC = dscFC.extent

    print(f"\n--- FC Summary: {fc} ---")
    print (f"\nFeature Count: {fcCount} | SR: {srFC.name}")
    print(f"Extent: X[{extFC.XMin}, {extFC.XMax}], Y[{extFC.YMin}, {extFC.YMax}]")

    # 3c) Clip layers to clip_feature
    final_output = f"{fc}_UTM_CLP"

    # Only proceed if the fc is not the boundary
    if fc != clip_feature and not arcpy.Exists(final_output):
        print(f"\t> Processing {fc} for output...")

        # Only project if not in target projection
        if "_UTM" in fc and srFC.factoryCode == SRcode:
            clip_input = fc
            print(f"\t> {fc} is already in UTM. Proceeding to Clip.")

        else:
            prj_output = f"{fc}_UTM"
            if not arcpy.Exists(prj_output):
                print(f"\t> Projecting {fc} to UTM...")
                arcpy.management.Project(fc, prj_output, tgtSR)
            else:
                print(f"Status: {prj_output} already exists.")
            # Use the new permanent UTM file for the next step
            clip_input = prj_output

        # Only clip if the feature has not already been clipped
        if "_CLP" not in fc:
            print(f"\t- Clipping {clip_input} to {clip_feature}...")
            arcpy.analysis.Clip(clip_input, clip_feature, final_output)
    else:
        print (f"\t> {final_output} already exists.")

# 5) Final Reporting
# List all contents after operations
print("\n" + "="*30)
print("FINAL GEODATABASE INVENTORY")
print("="*30)
print(f"Final Feature Classes: {arcpy.ListFeatureClasses()}")
print(f"Final Rasters: {arcpy.ListRasters()}")
print("="*30)

# Questions
print (f"Is listing creating separate variables for dscR and dscFC necessary?")
print (f"Since they aren't used it parallel it seems like it should be okay but probably better form.")
print (f"Same question for srR and srFC...")
