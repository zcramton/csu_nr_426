# NR426 Lesson 3 - starter code for the list demo
# Completed by Zachary Cramton
# updated Feb 2023
# We'll start with this pseudocode and fill the rest in during the demo
# This code will wrun simple operations on a single dataset, then
# #   make a list of all FCs in a GDB and run the same operations in a loop for all FCs

#import modules
import arcpy

# Set environments and variables
# Set the workspace to your copy of the UnionCity GDB
arcpy.env.workspace = r"L3LabData\UnionCity.gdb"

# 1. Recall how to loop through a list and print each item
# buildings = ["Natural Resources", "Morgan Library", "Lory Student Center", "NESB"]
# print ("Select campus buildings include:")
# for x in mylist:
#      print (x)
# mylist.sort()


# 2. Run operations on one dataset: Describe the shapetype and Get the number of features for the Watersheds layer
dsc = arcpy.Describe("Watersheds")
print (f"The shapetype is: {dsc.shapeType}")
print (f"The feature count is {arcpy.management.GetCount('Watersheds')}")


# 3. Run operations on all the datasets in a workspace using a List method
# What list method do we use?
fcList = arcpy.ListFeatureClasses()
for fc in fcList:
    print (fc)
    dsc = arcpy.Describe(fc)
    print (f"\tThe shape type is: {dsc.shapeType}")
    print (f"\tThe feature count is {arcpy.management.GetCount(fc)}")

# First, print out the name of each feature class



# Then take what we did above and format it into a list to get the shapetype and Count for each feature class:

