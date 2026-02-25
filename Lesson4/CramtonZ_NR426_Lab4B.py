"""
NR426 Lab3A
Completed by: Zachary Cramton
Date: 17FEB2026

Submitted with Lab 4B demo deliverable (.png) as instructed.

This lab practices the basics of using select tools and accessing tables. It saves the report to a text file for easy
viewing.
"""
# Import Modules
import arcpy
import os
import sys
import datetime # Added for dating of text report

# Workspace Setup
dataLoc = r"L4LabData\RoadkillDataLab4.gdb"
arcpy.env.workspace = dataLoc
arcpy.env.overwriteOutput = True # Allows for multiple script executions.

# Check if the folder exists before asking for a filename
if not arcpy.Exists(dataLoc):
    print (f"The workspace does not exist at {dataLoc}. Check your path.")
    sys.exit()

# Feature Layer Initialization
arcpy.management.MakeFeatureLayer("RoadkillSightings_UTM", "roadkill_lyr")
roadkill = "roadkill_lyr"

arcpy.management.MakeFeatureLayer("HRVRoads", "roads_lyr")
roads = "roads_lyr"

# Reference HRVCounties for part 3
counties = "HRVCounties"

# ----- Extra: 6) Report Setup -----
# Define report name, time, and destination
reportName = "CramtonZ_NR426_Lab4B_Report.txt"
reportPath = os.path.join(os.path.dirname(dataLoc), reportName)
timestamp = datetime.datetime.now().strftime("%d%b%Y %H:%M:%S").upper()

# Update user on progress
print ("Generating Report...")

# Try except error handling
try:
    # Open the file and start the process
    with open (reportPath, 'w') as f:
        # Report header (Printing to file=f)
        print (f"{'=' * 60}", file = f)
        print (f"NR426 L4B: Selection Report", file = f)
        print (f"Generated on: {timestamp}", file = f)
        print (f"{'=' * 60}\n", file = f)

        # +++++ Base Assignment Activities +++++
        # ----- 1) EAH Solo Collection Points -----
        # Define query to find observations made by EAH alone.
        arcpy.management.SelectLayerByAttribute(
            in_layer_or_view = roadkill,
            selection_type = "NEW_SELECTION",
            where_clause = "OBSERVER = 'EAH'"
        )

        count1 = arcpy.management.GetCount(roadkill)[0]
        print (f"1. EAH made {count1} solo observations.\n", file = f)


        # ----- 2) EAH Total Collection Points -----
        # Use LIKE with % wildcard to find all observations where EAH was present

        arcpy.management.SelectLayerByAttribute(
            in_layer_or_view = roadkill,
            selection_type = "NEW_SELECTION",
            where_clause = "OBSERVER LIKE '%EAH%'"
        )

        count2 = arcpy.management.GetCount(roadkill)[0]
        print (f"2. EAH was involved in {count2} total observations.\n", file = f)


        # ----- 3) Create New FC With All Points In Ulster Co -----
        # Select the county
        ulsterCO = arcpy.management.MakeFeatureLayer(
            in_features = counties,
            out_layer= "ulster_county",
            where_clause= "COUNTY LIKE '%Ulster%'"
        )

        # Select points by location
        arcpy.management.SelectLayerByLocation(
            in_layer = roadkill,
            overlap_type = "INTERSECT",
            select_features = ulsterCO,
            selection_type = "NEW_SELECTION"
        )

        # Define output path
        ulster_fc = os.path.join(dataLoc, "Roadkill_UlsterCO")
        arcpy.management.CopyFeatures(roadkill, ulster_fc)

        # Report Results
        count3 = arcpy.management.GetCount(ulster_fc)[0]
        print (f"3. There are {count3} points in Ulster County", file = f)
        print (f"\tOutput Location: {ulster_fc}\n", file = f)


        # ----- 4) Buffer Striped Skunks in Ulster Co by 0.25 Miles -----
        # Using the active Ulster Selection from Part 3
        arcpy.management.SelectLayerByAttribute(
            in_layer_or_view = roadkill,
            selection_type = "SUBSET_SELECTION",
            where_clause = "SCIENTIFIC = 'Mephitis mephitis'"
        )

        # Define output path for skunk buffer
        skunk_qtrMi_buff = os.path.join(dataLoc, "Roadkill_Skunk_QtrMiBuff")

        # Run buffer tool around skunk points in Ulster CO
        arcpy.analysis.Buffer(
            in_features = roadkill, # Using subset selection of part 3
            out_feature_class = skunk_qtrMi_buff,
            buffer_distance_or_field = "0.25 Miles"
        )

        # Report results
        count4 = arcpy.management.GetCount(skunk_qtrMi_buff)[0]
        print(f"4. There are {count4} buffered Striped skunk observations in Ulster County", file=f)
        print(f"\tOutput Location: {skunk_qtrMi_buff}\n", file=f)


        # ----- 5) Buffer Roads 200ft; Check for Points NOT in Buffer
        # Clear selections from parts 3/4
        arcpy.management.SelectLayerByAttribute(roadkill, "CLEAR_SELECTION")

        # Define output path for road buffer
        road_buffer = os.path.join(dataLoc, "road_200ft_buff")

        # Create road buffer
        arcpy.analysis.Buffer(
            in_features = roads,
            out_feature_class = road_buffer,
            buffer_distance_or_field = "200 Feet",
        )

        # Select points NOT within the buffer
        arcpy.management.SelectLayerByLocation(
            in_layer = roadkill,
            overlap_type = "INTERSECT",
            select_features = road_buffer,
            selection_type = "NEW_SELECTION",
            invert_spatial_relationship = "INVERT" # Select observations outside of the road buffer.
        )

        # Report results
        count5 = arcpy.management.GetCount(roadkill)[0]
        print (f"5. There are {count5} observations beyond 200 ft of roads.\n", file = f)


    print(f"\nReport successfully saved to: {reportPath}")

except arcpy.ExecuteError:
    print (arcpy.GetMessages(2))

except Exception as e:
    print (f"An error occurred: {e}")


