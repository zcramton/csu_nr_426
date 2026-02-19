"""
NR426 Lab3A
Completed by: Zachary Cramton
Date: 10FEB2026

Submitted with L3B demo code template

Use factory code to check projections.

"""

# Import Modules
import arcpy
import os
import sys

# ----- Setup -----
# Data location and workspace
dataLoc = f"RoadkillDataLab3.gdb"
arcpy.env.workspace = dataLoc
arcpy.env.overwriteOutput = True

# Spatial Reference
# Factory Code for UTM Zone 18 NAD83
SRcode = 26918
tgtSR = arcpy.SpatialReference(SRcode)

# Clip Feature
clip_feature = "HRVCounties" # Clipping boundary

# Confirm files exist
if not arcpy.Exists(dataLoc):
    print (f"Error: Workspace {dataLoc} does not exist. Check the path and try again.")
    print ("Exiting script...")
    sys.exit()

# ----- Proceed with Processing -----
else:

    # ----- 2) Rasters -----
    # 2a) Check table and raster counts
    print (f"Data Found at {dataLoc}:\n")
    tables = arcpy.ListTables(dataLoc)
    print (f"\t- Number of Tables: {len(tables)}")
    rasters = arcpy.ListRasters(dataLoc)
    print (f"\t- Number of Rasters: {len(rasters)}")

    # Generate raster data summary
    for r in rasters:
        dscR = arcpy.Describe(r)   # Set describe shortcut var
        srR = dscR.spatialReference # Identify current SR
        cellSize = arcpy.management.GetRasterProperties(r, 'CellSizeX') # Find raster spatial resolution
        units = srR.linearUnitName # Find SR units
        extent = dscR.extent       # Find raster spatial extent

        # 2b) Print data summary for current raster
        print (f"Name: {r}")
        print (f"SR: {srR.name} | Cell Size: {cellSize} | Units: {units}")
        print (f"Extent Min: [{extent.XMin}, {extent.YMin}] to [{extent.XMax}, {extent.YMax}]")

        # 3b) Check Projection
        # If not projected in tgtSR, project.
        if srR.factoryCode != SRcode:
            out_raster = f"{r}_UTM"
            if not arcpy.Exists(out_raster):
                print (f"Projecting {r} to UTM...")
                arcpy.Project_management(r, out_raster,tgtSR)
            else:
                print (f"{out_raster} already exists.")


    # ----- 3) Feature Classes -----
    fcList = arcpy.ListFeatureClasses()

    # 3a) Print the number of feature classes
    print(f"\nNumber of Feature Classes: {len(fcList)}")

    # 3b) Generate feature class summary
    for fc in fcList:
        dscFC = arcpy.Describe(fc)
        fcName = dscFC.name
        srFC = dscFC.spatialReference
        fcCount = arcpy.management.GetCount(fc)

        print (f"\nFC Name: {fcName} | Count: {fcCount} | SR: {srFC}")

        # 3c) Clip layers to clip_feature
        if not fc == clip_feature and not fc.endswith("_CLP"):
          output_clip = f"{fc}_CLP"
            if not arcpy.Exists(output_clip):
                print(f"Clipping {fc} to {clip_feature}...")
                arcpy.analysis.Clip(fc, clip_feature, output_clip)
            else:
                pass
          fc = output_clip # Update fc reference for projection check

        # 3d) Project fc layers if not tgtSR
        # DOTHIS:: Resolve vaariable and filter conflicts
        if srFC.factoryCode != SRcode:
                prj_out = os.path.join(res_gdb_path, f"{fc}_UTM")
                if not arcpy.Exists(prj_out):
                    log_print(f"Projecting {active_layer} to UTM...")
                    arcpy.management.Project(active_layer, prj_out, target_sr)

# This doesn't seem to address the case where the name CONTAINS (rather than ends in)
# _UTM... should we use a different search/conditional term?





# Questions
print (f"Is listing creating separate variables for dscR and dscFC necessary?")
print (f"Since they aren't used it parallel it seems like it should be okay but probably better form.")
print (f"Same question for srR and srFC...")

# If not projected: then project
    # Check with describe and spatialreference factory code (26918 - check code in instruction doc)
#for x in rasterList:
#    if not prj = 26918:
#        project tool
#        outname = x + "_UTM" # dynamic naming

# If not clipped: then clip
#for x in fcList:
#    if x == "HRV_Counties" or "#DO THIS ADD IF x_CLP exists then don't clip x" or "if x.endswith("_clp") :
#        pass
#    else:
#        clip tool, clipping to counties

#    Consider using arcpy.extent.within()
