'''
NR426 Lesson 5 demo code
Your Lab 5 task is to correct and improve the code based on what we discuss in class
I *think* there are 8 errors to fix, plus several ways to improve the code

Updated Nov 2025
'''

import acrpy

#Set environments and variables
#Set path to your copy of US_states.shp
path = r""
arcpy.env.workspace = path
statesshp = "US_states.shp"
MaxYfld = "MaxY"
arcpy.AddField_management(statesshp, maxyfld, "Double")
#Calculate geometry to populate field with max y coordinate
print ("...updating geometry attributes...\n")
CalculateGeometryAttributes_management(statesshp, "MaxY EXTENT_MAX_Y")
#Use cursor to read values in table and return the state with the highest value,
#but only for the lower 48 states
print ("...creating the cursor and looping through...\n")
lower48sql = "STATE_NAME NOT IN ['Hawaii', 'Alaska']"
with arcpy.SearchCursor(statesshp, [MaxYfld, "STATE_NAME"], lower48sql) as cur:
    for row in cur
        mostnorth == max(cur, key=lambda row: row[0])
     state_name = mostnorth[1]
    theMaxYvalue = mostnorth[0]
print("The state containing the northernmost point in the lower 48 is: {state_name} with a latitude of {theMaxYvalue}.")
