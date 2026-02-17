'''
Lesson 3B follow-along demo:
DESCRIBE method and properties
# Completed by Zachary Cramton

Updated Feb 2023

This script will:
write code for the group activity
Explore the hasattr method
Practice with the spatial reference class
'''


# --- Group Activity / Follow-along Demo: ---

import arcpy

#Set the workspace to UnionCity geodatabase
path = r"Lesson3\L3LabData\UnionCity.gdb"

arcpy.env.workspace = path
layer = "Watersheds"
raster = "DEM"

# #1
dsc = arcpy.Describe(path)
#a. How can you determine the type of geodatabase?
print (dsc.datatype)
print (dsc.workspacetype)
#b. How can you retrieve the path to this geodatabase?
print (dsc.catalogpath)

# #2
dsc = arcpy.Describe("Watersheds")
# a.	Write the code to determine the geometry type
print (dsc.shapetype)
#b.	Write the code to return some spatial reference properties (type, name, unit)
print (f"SR name: {dsc.SpatialReference.name}")
print (f"SR type: {dsc.SpatialReference.type}")
print (F"SR units: {dsc.SpatialReference.LinearUnitName}")
print (f"SR Code: {dsc.SpatialReference.factoryCode}")

# #3
###  Let's test out some properties on different inputs, with hasattr and spatial reference

dsc = arcpy.Describe(layer)
if hasattr(dsc, "dataType"):
    print (f"Data Type: {dsc.datatype}")
if hasattr(dsc, "format"):
    print (f"Format: {dsc.format}")
if hasattr(dsc, "dataSetType"):
    print (f"Data Set Type: {dsc.datasettype}")
if hasattr(dsc, "catalogPath"):
    print (f"Catalog Path: {dsc.catalogpath}")
if hasattr(dsc, "name"):
    print (f"Feature Type: {dsc.name}")
