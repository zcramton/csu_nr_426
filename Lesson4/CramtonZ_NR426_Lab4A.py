"""
NR426 Lab3A
Completed by: Zachary Cramton
Date: 17FEB2026

Submitted without Lab 4A Demo, as instructed.

This lab practices the basics of using cursors and accessing tables. Given the choice between CO Stream Gauge Data
from USGS and Larimer County Trail data, I selected Larimer Trail data to practice table manipulation with.
"""

# Import Modules
import arcpy
import sys

# Data Path & Workspace Setup
trails = r"https://services1.arcgis.com/KNdRU5cN6ENqCTjk/arcgis/rest/services/Larimer_County_Trail_Popularity/FeatureServer/1"
arcpy.env.workspace = trails

if not arcpy.Exists(arcpy.env.workspace):
    print ("Data not found, check the source and try again.")
    print ("Program exiting...")
    sys.exit()

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
record_limit = 10          # Counter limit for part 1 to prevent printing a long list into the console.

# Backup / Output paths
backupName = "LarimerTrail_original"
outputLayer = "HighValue_Trails"

# 1. Returning Trail Names
print(f"--- Part 1: {tgt_surf.title()} Trails ---")
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
print(f"{count} {tgt_surf} trails found.\n")


# 2. High-ranking Trails
print(f"--- Part 2: High-Ranking Trails (>{pop_threshold}) ---")
where_rank = f"{popularity} > {pop_threshold}"
with arcpy.da.SearchCursor(
        in_table = trails,
        field_names = [name, popularity],
        where_clause = where_rank
) as cursor:
    for row in cursor:
        print(f"Trail: {row[0]} | Score: {row[1]}")
print("\n")


# 3. Finding Elevation Extremes
print(f"--- Part 3: Elevation Extremes ---")
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
        print(f"Highest Trail: {row[0]} | Elevation: {row[1]} ft")
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
        print(f"Lowest Trail: {row[0]} | Elevation: {row[1]} ft")
        break
print("\n")


# 4. Update Nulls
# Update all records with a surface value of Null (None) to be Unknown.
print(f"--- Part 4: Updating Null Surface Values ---")

# WHERE clause looking for true NULLs, empty strings, and single spaces
where_null = f"{surface} IS NULL OR {surface} = '' OR {surface} = ' '"

try:
    # Using UpdateCursor to modify the surface field
    with arcpy.da.UpdateCursor(
            in_table = trails,
            field_names = [surface],
            where_clause = where_null
    ) as up_cursor:
        update_count = 0
        for row in up_cursor:
            # Update the value in memory
            row[0] = "Unknown"

            # Commit the change for this specific row immediately
            up_cursor.updateRow(row)
            update_count += 1

    # Update user with a count of modified records.
    print(f"Successfully updated and committed {update_count} records.")

except Exception as e:
    print(f"An error occurred: {e}")

print("\nScript Execution Complete.")