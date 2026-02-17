# NR 426, Programming for GIS I, Lesson 4
# Adapted from Chapter 7 of Python Scripting for ArcGIS by Paul Zandbergen
# Feb. 2019, Elizabeth Tulanowski

# Purpose
# Select lines that are a Ferry Crossing and update a Yes value into a new field

# This AKroads.shp is available in the Lab 4 data folder

import arcpy

# Set workspace
arcpy.env.workspace = r"C:\Student"
mydata = "AKroads.shp"

# Add the new field
#AddField_management (in_table, field_name, field_type, {field_precision}, {field_scale}, {field_length}, {field_alias}, {field_is_nullable}, {field_is_required}, {field_domain})
#arcpy.AddField_management(mydata, "Ferry", "TEXT")

# Add the Ferry field, but only if it's not there
fldList = arcpy.ListFields(mydata, "Ferry")
if len(fldList)== 0:
    arcpy.AddField_management(mydata, "Ferry", "TEXT")
    print ("Successfully created the Ferry field")
else:
    print ("Ferry field already exists")

print("Creating the cursor...............")
with arcpy.da.UpdateCursor(mydata, ["Feature","Ferry"]) as cur:
    print ("Evaluating the fields.......")
    for row in cur:
        if row[0] == "Ferry Crossing":
            row[1] = "Yes"
        else:
            row[1] = "No"
        cur.updateRow(row)

print ("Script completed successfully. Go check {0} to see if the table was "
       "correctly updated".format(mydata))



