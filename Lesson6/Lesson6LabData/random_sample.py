# Python script: random_sample.py
# Author: Paul Zandbergen
# Modified by: Zachary Cramton
# Last Changes: 26FEB2026

# This script creates a random sample of input features based on
# a specified count and saves the results as a new feature class.

# Import modules.
import arcpy
import random
import sys

# Set inputs and outputs. Inputfc can be a shapefile or geodatabase
# feature class. Outcount cannot exceed the feature count of inputfc.
inputfc = arcpy.GetParameterAsText(0)
outputfc = arcpy.GetParameterAsText(1)
outcount = int(arcpy.GetParameterAsText(2))

try:
    # Create a list of all the IDs of the input features.
    inlist = []
    with arcpy.da.SearchCursor(inputfc, "OID@") as cursor:
        for row in cursor:
            id = row[0]
            inlist.append(id)

    # Create a random sample of IDs from the list of all IDs.
    randomlist = random.sample(inlist, outcount)

    # Use the random sample of IDs to create a new feature class.
    desc = arcpy.da.Describe(inputfc)
    fldname = desc["OIDFieldName"]
    sqlfield = arcpy.AddFieldDelimiters(inputfc, fldname)
    sqlexp = f"{sqlfield} IN {tuple(randomlist)}"
    arcpy.Select_analysis(inputfc, outputfc, sqlexp)

except:

    # Get feature count in FC
    inputFCcount = arcpy.management.GetCount(inputfc)

    # Report error if outcount selection is greater than available features
    if inputFCcount > outcount:
        invalidOut = (f"Cannot select more features than available. Select number less than {inputFCcount}. Ending operation...")
        arcpy.AddMessage(invalidOut, 2)
        sys.exit()
