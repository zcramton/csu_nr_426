"""
NR426 Lab3A
Completed by: Zachary Cramton
Date: 10FEB2026

Submitted with L3A demo code template

This code will practice using arcpy list methods with data from the City of San Antonio, 
reporting details about the data. This code iterates through GDBs in a folder and writes a detailed
polygon report to a text file including titling the file with a user input name.

This program does attempt all optional goals but does not use the arcpy.walk function. Instead,
the program uses a for loop to cycle through all geodatabase files in the target folder,
in this case r"L3LabData" by default using relative referencing to the parent project of NR426.
"""

# Import Modules
import arcpy
import os
import sys
import datetime # Added for dating of printed report

# Workspace & Report Setup
dataLoc = r"L3LabData"

# Check if the folder exists before asking for a filename
if not arcpy.Exists(dataLoc):
    print(f"The workspace {dataLoc} does not exist. Check your path.")
    sys.exit()

# Get user input for the report name
user_filename = input("Enter the desired name for .txt report (e.g., SanAntonio_Report): ")
if not user_filename.endswith(".txt"):
    user_filename += ".txt"

report_path = os.path.join(dataLoc, user_filename)

# Update user on report processing progress.
print ("Report in Progress - Processing Data")

# Error Handling for Repeat File Names
# If file exists, append (1), (2), etc., until a unique name is found
counter = 1
base_name = os.path.splitext(report_path)[0]  # Gets path without .txt
while os.path.exists(report_path):
    report_path = f"{base_name}({counter}).txt"
    counter += 1

# Base Code to Produce Lab 3A Results for Each GDB in L3LabData
timestamp = datetime.datetime.now().strftime("%d%b%Y %H:%M:%S").upper()

# Open the file and start the process
with open(report_path, 'w') as f:
    # Header logic (Printing to file=f)
    print(f"{'=' * 60}", file=f)
    print(f"NR426 L3A: POLYGON REPORT", file=f)
    print(f"Generated on: {timestamp}", file=f)
    print(f"{'=' * 60}\n", file=f)

    # Set initial workspace to find the GDBs
    arcpy.env.workspace = dataLoc
    gdbList = arcpy.ListWorkspaces(wild_card="*", workspace_type="FileGDB")

    found_polygons = False

    for gdb in gdbList:
        # Set workspace to current GDB
        arcpy.env.workspace = gdb
        gdb_name = os.path.basename(gdb)

        print(f"DATABASE: {gdb_name}", file=f)
        print(f"{'-' * 30}", file=f)

        # List polygon Feature Classes
        fcList = arcpy.ListFeatureClasses(wild_card="*", feature_type="Polygon")

        if fcList:  # If the list is not empty
            found_polygons = True
            for fc in fcList:
                # Get Feature Count
                count_result = arcpy.management.GetCount(fc)
                featureCount = int(count_result[0])

                # Optional Challenge: Grammar Logic
                verb = "is" if featureCount == 1 else "are"
                plural = "" if featureCount == 1 else "s"

                print(f"FC Name: {fc}", file=f)
                print(f"\tThere {verb} {featureCount} feature{plural} in this feature class.", file=f)

                # List Fields
                print(f"\tThe attribute field names are:", file=f)
                for field in arcpy.ListFields(fc):
                    print(f"\t\t- {field.name}", file=f)
                print("", file=f)  # Spacing

            # PROGRESS UPDATE (to screen)
            print(f"\t> Found {len(fcList)} polygon layers.")
        else:
             print(f"\tNo polygon feature classes found in {gdb_name}.\n", file=f)
             print(f"\t> No polygons found.")

    # Final check if anything was found across ALL GDBs
    if not found_polygons:
        print("No polygon feature classes were found in any of the geo-databases.", file=f)

    # Mark the end of the report
    print(f"{'*' * 10} All geodatabase data in {dataLoc} reviewed. {'*' * 10}\n", file=f)

# Final message to the user's screen
print(f"\nData Processing Complete.")
print(f"The report has been saved as: {os.path.basename(report_path)}")
print(f"Report saved to: {os.path.abspath(report_path)}")
