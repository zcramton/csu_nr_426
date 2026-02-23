"""
NR426 Lab3A
Completed by: Zachary Cramton
Date: 17FEB2026

Submitted without Lab 4A Demo, as instructed.

This lab practices the basics of using cursors and accessing tables. Given the choice between CO Stream Gauge Data
from USGS and Larimer County Trail data, I selected Larimer Trail data to practice table manipulation with. Optional
challenge 5b was completed, finding the trail with the highest delta elevation.
"""

# Import Modules
import arcpy
import os
import sys

# Data Path & Workspace Setup
trails = r"https://services1.arcgis.com/KNdRU5cN6ENqCTjk/arcgis/rest/services/Larimer_County_Trail_Popularity/FeatureServer/1"
arcpy.env.workspace = trails

if not arcpy.Exists(arcpy.env.workspace):
    print ("Data not found, check the source and try again.")
    print ("Program exiting...")
    sys.exit()

# Backup / Output paths
# Define path for data copy in part 4 to the default GDB
local_trails = os.path.join(arcpy.env.scratchGDB, "LarimerTrails_Local")

# ----- Variables -----
# Field Names (Column Headers)
name = "name"                # Name of the trail
surface = "surface"          # Surface type
popularity = "suit_score"    # Popularity (alias for suit_score)
max_elev = "max_elevat"      # Max elevation
min_elev = "min_elevat"      # Min elevation

# Input Values / Criteria
tgt_surf = "gravel"  # Try 'track' or 'concrete' later
pop_threshold = 1.7

# Backup / Output paths
backupName = "LarimerTrail_original"
outputLayer = "HighValue_Trails"

# 1. Returning Trail Names
print(f"--- Part 1: {tgt_surf.title()} Trails ---")

# Counter limit to prevent printing a long list into the console.
record_limit = 10

count = 0
# SearchCursor: (table, [fields], where_clause)
with arcpy.da.SearchCursor(
        in_table = trails,
        field_names = [name],
        where_clause = f"{surface} = '{tgt_surf}'"
) as cursor:
    for row in cursor:
        count += 1
        if count <= record_limit:
            print(f"{count}. {row[0]}")
print(f"{count} {tgt_surf} trails found.\n\n")


# 2. High-ranking Trails
print(f"--- Part 2: High-Ranking Trails (>{pop_threshold}) ---")

# Counters for print limit, unnamed trails, and total records
print_count = 0
unnamed_count = 0
total_high_rank = 0
max_display = 15

where_rank = f"{popularity} > {pop_threshold}"
with arcpy.da.SearchCursor(
        in_table = trails,
        field_names = [name, popularity],
        where_clause = where_rank
) as cursor:
    print(f"High Ranking Trails in Larimer County:\n")
    for row in cursor:
        total_high_rank += 1
        trail_name = row[0]
        # Round the popularity score to 1 decimal place
        trail_score = round(row[1], 1) if row[1] is not None else 0.0

        # Handle Null or empty names
        if trail_name is None or trail_name.strip() == "":
            unnamed_count += 1
        else:
            # Only print the first 15 named trails
            if print_count < max_display:
                print_count += 1
                print(f"{print_count}. {trail_name} | Score: {trail_score}")

# Final summary reporting
print(f"\nTrail Summary for Popularity Score > {pop_threshold}:")
print(f"There are {total_high_rank} trails owned by Larimer County with popularity score greater than {pop_threshold}.")
print(f"Of those, {unnamed_count} are unnamed trails.")
print("\n")

# 3A. Finding Elevation Extremes
print(f"--- Part 3A: Elevation Extremes ---")
# --- Find Highest Max Elevation ---
# Sort by max_elev DESC (Highest to Lowest)
sql_max = (None, f"ORDER BY {max_elev} DESC")

with arcpy.da.SearchCursor(
        in_table = trails,
        field_names = [name, max_elev],
        sql_clause = sql_max
) as cursor:
    # We only need the very first record (the top of the sorted list)
    for row in cursor:
        # Round elevation to 2 decimal places
        elev_val = round(row[1], 2) if row[1] is not None else 0.00
        print(f"Highest Trail: {row[0]} | Elevation: {elev_val:.2f} ft")
        break

# --- Find Lowest Min Elevation ---
# Use a WHERE clause to exclude 0 or NULL to avoid "placeholder" elevations
where_not_zero = f"{min_elev} > 0"
# Sort by min_elev ASC (Lowest to Highest)
sql_min = (None, f"ORDER BY {min_elev} ASC")

with arcpy.da.SearchCursor(
        in_table = trails,
        field_names = [name, min_elev],
        where_clause = where_not_zero,
        sql_clause = sql_min
) as cursor:
    # The first record here will be the absolute lowest
    for row in cursor:
        # Round elevation to 2 decimal places
        elev_val = round(row[1], 2) if row[1] is not None else 0.00
        print(f"Lowest Trail: {row[0]} | Elevation: {elev_val:.2f} ft")
        break
print("\n")

# 3b. Greatest Elevation Range
print("--- Part 3B: Greatest Elevation Range ---")

# Variables to store the record values
top_range_trail = ""
max_range_value = 0

# Pull name, and min/max elevation fields
with arcpy.da.SearchCursor(trails, [name, max_elev, min_elev]) as cursor:
    for row in cursor:
        # Check for Nulls to prevent math errors
        if row[1] is not None and row[2] is not None:
            # Calculate range: Max - Min
            current_range = row[1] - row[2]

            # If this trail's range is bigger than the current record, update it
            if current_range > max_range_value:
                max_range_value = current_range
                top_range_trail = row[0]

# Print the result formatted to 2 decimal places
print(f"The trail with the greatest range is {top_range_trail} with a delta of {max_range_value:.2f} ft.\n\n")

# 4. Update Nulls
# Update all records with a surface value of Null (None) to be Unknown.
print(f"--- Part 4: Updating Null Surface Values ---")

try:
    # Create a local copy if it doesn't exist
    if not arcpy.Exists(local_trails):
        print("Creating local copy of trails for editing...")
        arcpy.management.CopyFeatures(trails, local_trails)

    where_null = f"{surface} IS NULL OR {surface} = '' OR {surface} = ' '"

    with arcpy.da.UpdateCursor(
            in_table=local_trails, # Using local_trails instead of the cloud source
            field_names=[surface],
            where_clause=where_null
    ) as up_cursor:
        update_count = 0
        for row in up_cursor:
            row[0] = "Unknown"
            up_cursor.updateRow(row)
            update_count += 1

    print(f"Successfully updated {update_count} records in the local copy of Larimer Co Trail Popularity.")
    print(f"Find it in the default geodatabase at: {local_trails}")

except Exception as e:
    print(f"An error occurred in Part 4: {e}")

print("\nScript Execution Complete.")