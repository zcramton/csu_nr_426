"""
NR426 Lab2B
Completed from template scripts by Zachary Cramton, 03FEB2026

This code will initially:
-- Clip one layer to another
-- Check that the input data exists before doing that clip
-- Return the number of features in the output using GetCount
-- Report the geometry type of the output using Describe shapetype

You will modify the code as directed in the lab handout to make it a little more sophisticated.
"""

print ( "*** Lab 2B Script by Zachary Cramton starting. \n")

## Lab 2B in-class activity / demo - complete with the class

# Import modules
import arcpy
import sys

#What needs to be added to run spatial analyst tools for rasters?
#import arcpy.sa

#  a - Set up environments and variables
arcpy.env.workspace = r"L2LabData\FtCollins.gdb"
arcpy.env.overwriteOutput = True

bikeRoutes = "Bike_Infrastructure"
trails = "Trails"
parks = "Parks"
natAreas = "Natural_Areas"
natAreaTrls = "Trails_in_natAreas" # Placeholder variable
nearParkBikeInf = "Nearest_bike_infrastructure_to_parks" # Placeholder variable
trailsAtStreams = "Trails_at_streams" # Placeholder variable

print ("Workspace setup complete, initial variables set. \n")
####

# # b - Review finding the syntax for, and running a basic tool: CLIP
# #Set up variables and clip Trails to Natural Areas
# if arcpy.Exists(trails):
#     arcpy.analysis.Clip(
#         in_features = trails,
#         clip_features = natAreas,
#         out_features = natAreaTrls
#     )
#     print (arcpy.GetMessages()) # Display geoprocessing messages
#     count = arcpy.management.GetCount(trails) # This tool returns a result object; use print(object[0]).
#     print (f" There are {count[0]} trail segments.")
# else:
#     print ("Clip failed, trails does not exist.")
#     exit()
#
# # c, d, e - Other arcpy methods: Exists, overwriteOutput, GetCount, Describe, GetMessage, AddMessage
# # See above
print ("Demo skipped, uncomment code to se it run. \n")

####
## Lab 2B self-directed activity - complete on your own

# 3 - Follow the requirements in the Lab 2 handout to write the necessary code (paraphrased below)
# Use good coding practices, comments, readability, and print messages

# a - Access the Fort Collins Hydrology lines feature layer (online) (like we did in 2A)
FtCoHydro_URL = f"https://services1.arcgis.com/dLpFH5mwVvxSN4OE/arcgis/rest/services/Hydrology/FeatureServer/0"

# b (and e) - Get distance to nearest bike path attached to each park (What tool do you use?)
# Check if inputs exist
if arcpy.Exists(bikeRoutes) and arcpy.Exists(parks):
    print ("Bike path and park data found, proceeding with proximity (Near) analysis... \n")
    nearParkBikeInf = arcpy.analysis.Near(
        in_features = bikeRoutes,
        near_features = parks,
        search_radius = "",
        distance_unit = "Feet", # It looks like I can exclude other inputs provided I write out what's what. This may cause issues in the future.
    )
# Determine which inputs are missing
elif arcpy.Exists(bikeRoutes):
    print ("Parks data not found, check the source and try again.")
    print ("Exiting program. \n")
    sys.exit()

elif arcpy.Exists(parks):
    print ("Bike route data not found, check the source and try again.")
    print ("Exiting program. \n")
    sys.exit()

# No data found, exit
else:
    print ("No data found, check the sources and try again.")
    print ("Exiting program. \n")
    sys.exit()

# Update user on code status.
print ("Bike path and park proximity analysis complete. \n")

# c (and e) - Where do trails cross streams? Could be a nice place for a break.
# # Intersect Hydrology and Trails

#Check for data a different way
if arcpy.Exists(trails) and arcpy.Exists(FtCoHydro_URL):

    # Run the analysis
    print ("Line hydrology and trail data found, proceeding with intersect analysis... \n")
    arcpy.analysis.Intersect(
        in_features = [FtCoHydro_URL, trails],
        out_feature_class = trailsAtStreams,
        join_attributes = "ALL",
        cluster_tolerance = None,
        output_type = "POINT" # Forcing point output
    )

elif arcpy.Exists(trails):
    # If trails is missing print error and exit
    print ("Trail data not found, check the source and try again.")
    print ("Exiting program. \n")
    sys.exit()

elif arcpy.Exists(FtCoHydro_URL):
    # If hydro is missing print error and exit
    print ("Hydrology data not found, check the source and try again.")
    print ("Exiting program. \n")
    sys.exit()

else:
    # No data found, exit
    print("No data found, check the sources and try again.")
    print("Exiting program. \n")
    sys.exit()

# d - Well formatted print statement stating the number of features in the output of the intersect
# (this number represents stream crossings of trails. Use GetCount)
# also try out the Describe method and report the geometry type (shapetype) of the output

# Update user on code status.
print ("Line hydrology and trail intersect analysis complete.")
print (f"There are {arcpy.management.GetCount(trailsAtStreams)} stream crossings in the mapped Fort Collins trail network.")
print (f"These data represent a {arcpy.Describe(trailsAtStreams).shapeType} feature class where trails cross a hydrological feature. \n")

# e: Go back up to steps b and c and modify to only run if the inputs exist, and make the script exit
# if it doesn't  (use sys.exit) - Done


# f - Modify the code above to put the Near and Intersect blocks in try-except statement, and return arcpy messaging
# with GetMessages
print ("Reattempting analyses framed in Try-Except Statements.")
# Code printed above rewritten to use try-except error handling
# Section B: Bike Route Proximity to Parks
try:
    nearParkBikeInf = arcpy.analysis.Near(
        in_features=bikeRoutes,
        near_features=parks,
        search_radius="",
        distance_unit="Feet",
        # It looks like I can exclude other inputs provided I write out what's what. This may cause issues in the future.
    )
    print ("Proximity analysis with Try-Except Statement Complete")
    
except:
    print ("Error executing proximity (Near) analysis. Check the error message and try again.")
    print (arcpy.GetMessages())
    sys.exit()

# Section C: Line Hydrology Intersect with Trails
try:
    print("Data found, proceeding with intersect analysis... \n")
    arcpy.analysis.Intersect(
        in_features=[FtCoHydro_URL, trails],
        out_feature_class=trailsAtStreams,
        join_attributes="ALL",
        cluster_tolerance=None,
        output_type="POINT"  # Forcing point output
    )

    print ("Intersect analysis with Try-Except Statement Complete.")
    print (f"There are {arcpy.management.GetCount(trailsAtStreams)} stream crossings in the mapped Fort Collins trail network.")
    print (f"These data represent a {arcpy.Describe(trailsAtStreams).shapeType} feature class where trails cross a hydrological feature. \n")

except:
    print ("Error executing intersect analysis. Check the error message and try again.")
    print (arcpy.GetMessages())
    sys.exit()

print ("*** Script completed ***")