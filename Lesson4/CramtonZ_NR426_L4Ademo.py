# NR 426, Programming for GIS I, Lesson 4
# Script to select Ferry Crossings and add Yes to a new field
# Adapted from Chapter 7 of Python Scripting for ArcGIS by Paul Zandbergen
# Feb. 2025, Elizabeth Tulanowski

import arcpy

# Set workspace
arcpy.env.workspace = r".......Lesson4LabData"
mydata = "AKroads.shp"

# Add the new field
#AddField_management (in_table, field_name, field_type, {field_precision}, {field_scale}, {field_length}, {field_alias}, {field_is_nullable}, {field_is_required}, {field_domain})
#arcpy.AddField_management(mydata, "Ferry", "TEXT")

# Add the Ferry field, but only if it's not there
fldList = arcpy.ListFields(mydata, "Ferry")
if len(fldList)== 0:
    arcpy.management.AddField(mydata, "Ferry", "TEXT")
    print ("Successfully created the Ferry field")
else:
    print ("Ferry field already exists")

print("Creating the cursor...............")
#How do you create the cursor?
with arcpy.da.UpdateCursor(mydata, ["Feature", "Ferry"],"--QUERY GOES HERE---'") as cur:
    print (row[_] + row[_])
    print ("Evaluating the fields.......")
    for row in cur:
        if row[0] == "Ferry Crossing":
            row[1] = "Yes"
        else:
            row[1] = "No"
        # What field does row[0] refer to? What field does row[1] refer to?
        # Commit the change:
        cur.updateRow(row)

print ("Script completed successfully. Go check {0} to see if the table was "
       "correctly updated".format(mydata))


##  Practice with queries




