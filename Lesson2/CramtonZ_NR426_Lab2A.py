"""
NR426 Lab2A
Completed from template scripts by Zachary Cramton, 03FEB2026


Header code:
 Lesson 2a Demo script for NR426
 Written by Elizabeth Tulanowski, Jan. 2024

Purpose: The script will call basic arcpy methods and answer some spatial questions
>> Create variables for local and feature service data
   (from https://data-fcgov.opendata.arcgis.com/ )
>> Find trails that are in a park (Intersect tool)
>> Buffer bike infrastructure
>> Run Slope on a DEM
On your own, you will:
>>Find parks that are within the buffer
>>Run Hillshade on the DEM

"""

print ("* * * Starting script * * * \n")

#### Lab 2A in-class activity/Demo - do together

##  a-  Import necessary modules
import arcpy
import arcpy.sa
import os # Likely necessary for relative path referencing
from sys import exit

###  a- Set environments and variables
#Set the default workspace w/ relative referencing:
#arcpy.env.workspace = os.path.relpath(r"Lesson2") # Workspace path from cwd
arcpy.env.workspace = r"L2LabData\FtCollins.gdb"
arcpy.env.overwriteOutput = True

# #Use the workspace data, create variables for these layers: Trails, Parks, Bike_Infrastructure
# trails = "Trails"
# parks = "Parks"
#
# #a2 - Check that parks and trails exist
# if not arcpy.Exists(trails):
#     print (f"Error: The dataset at {trails} cannot be found! Exiting...")
#     sys.exit()
# elif not arcpy.Exists(parks):
#     print (f"Error: The dataset at {parks} cannot be found! Exiting...")
#     sys.exit()
# else:
#     print ("Dataset found. Proceeding with Intersect...")
#
# #b Use feature services with a URL and the Make Feature Layer tool:
# # Natural Habitat Geoservice URL: https://services1.arcgis.com/dLpFH5mwVvxSN4OE/arcgis/rest/services/Natural_Habitat/FeatureServer/0/query?outFields=*&where=1%3D1
# NhabURL = "https://services1.arcgis.com/dLpFH5mwVvxSN4OE/arcgis/rest/services/Natural_Habitat/FeatureServer/0"
# NatHabLayer= "NaturalHabitatLayer"
# arcpy.MakeFeatureLayer_management(NhabURL, NatHabLayer) #paste the url, variable name
#
# #Then use the variable NatHabLayer like a regular layer, in tools
#
# ##### Step 2 -
# ### c - Body of code - running tools and doing things
# trl_pk_int = "trl_pk_int"
#
# #  What trails go through a park? Set up and run Intersect on trails and parks.
# arcpy.analysis.Intersect([parks, trails], trl_pk_int)
#
# #  What trails allow horses? Set up and run the Select tool. Take a look at SQL expressions.
# arcpy.analysis.Select(
#     in_features = trails,
#     out_feature_class = "Trails_Horses",
#     where_clause = "HORSEUSE = 'Yes'"
# )
#
# ##  What if a script doesn't run correctly, and you have to re-run it, and overwrite outputs that were already created?
#
#
# #Import necessary items up top to use Spatial Analyst tools
# # d -  Run Slope on the DEM layer
# import arcpy.sa # Import arcpy SA
# DEM = "FtCollinsWestDEM" # Define DEM var
#
# # Check that extension exists
# if not arcpy.CheckExtension("Spatial") == "Available":
#     print("License for SA tools not available.")

# Run slope tool on DEM
#outSlope = arcpy.sa.Slope(DEM)
#outSlope.save(r"./Slope_FCWest")

## Step 4 - This part of the demo will pop into ArcGIS Pro to show you the Python window...
#Skipped

#Make sure you take the step to allow outputs to overwrite!

#####
#### Lab 2A self-directed activities - do on your own.
#Use the Lab 2 handout as your guide, it has full details. Below is just paraphrased to save space.
#Using line breaks and print statements, add good messaging to let the user know what tool is running.

# Redefining variables for clarity to clear any issues from the demo.
## Inputs
parks = "Parks"
natAreas = "Natural_Areas"
bikeRoutes = "Bike_Infrastructure"

# Outputs
parks300buff = "parks_300ft_buffer"
natAreas300buff = "natAreas_300ft_buffer"
parkSpacesBuff = "parkSpaces_combined_buffer"
parksBikeInt = "parks_bikes_intersect"

outputList = [parks300buff, natAreas300buff, parkSpacesBuff, parksBikeInt]

# Step 5 a - Buffer the Parks layer by 300 feet
arcpy.analysis.Buffer(
    in_features = parks,
    out_feature_class = parks300buff,
    buffer_distance_or_field = "300 Feet",
    line_side = "FULL",
    line_end_type = "ROUND",
    dissolve_option = "ALL",
    dissolve_field = None,
    method = "PLANAR"
)

# Step 5 b - Buffer the Natural Areas layer by 300 feet
arcpy.analysis.Buffer(
    in_features = natAreas,
    out_feature_class = natAreas300buff,
    buffer_distance_or_field = "300 Feet",
    line_side = "FULL",
    line_end_type = "ROUND",
    dissolve_option = "ALL",
    dissolve_field = None,
    method = "PLANAR"
)

# Step 5 c - Union the two buffered layers above
arcpy.analysis.Union(
    in_features = [natAreas300buff, parks300buff],
    out_feature_class = parkSpacesBuff,
    join_attributes = "ALL",
    cluster_tolerance = None,
    gaps = "GAPS"
)

# Step 5 d - Find bike infrastructure that is within the unioned output (Use Intersect).
# Force output_type = "LINE"
arcpy.analysis.Intersect(
    in_features = [bikeRoutes, parkSpacesBuff],
    out_feature_class = parksBikeInt,
    join_attributes = "ALL",
    cluster_tolerance = None,
    output_type = "LINE"
)

##You know should have a line layer showing bike routes within 300 feet of some sort of park area

# Step 6 - Print a well-formatted sentence telling the user where the output data can be found. Use variables and the arcpy.env.workspace
#            Don't manually type out the names of paths and files in your print statement.
for var in outputList:
    print (f"The {var} can be found at: {os.path.join(arcpy.env.workspace, var)}")

# Step 7 - Run the Hillshade tool on the DEM in the GDB (what needs to be imported up top for this?)
# If it wasn't imported above, "import arcpy.sa" would be required see line
FtCollinsWest_Hillshade = arcpy.sa.Hillshade(in_raster = "FtCollinsWest_DEM")
FtCollinsWest_Hillshade.save("FtCollinsWest_Hillshade")

#View your output data in ArcGIS to make sure things ran and look as expected

print ("***** Script finished! *****")