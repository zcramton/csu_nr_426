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
import os
import sys

from Lesson4.CramtonZ_NR426_L4Ademo import fldList

# Data Path & Workspace Setup
trails_url = r"https://services1.arcgis.com/KNdRU5cN6ENqCTjk/arcgis/rest/services/Larimer_County_Trail_Popularity/FeatureServer/"
arcpy.env.workspace = trails_url

if not arcpy.Exists(arcpy.env.workspace):
    print ("Data not found, check the source and try again.")
    print ("Program exiting...")
    sys.exit()

# ----- Variables -----
# trails = os.path.join(trails_url, "Trail_LC_NAD83_UTM13N")
# fldList = arcpy.ListFields("")
# tgtFld = "surface"
# tgtAttrib = "gravel"

# Field Names (Column Headers)
fld_name = "TRLNAME"       # Name of the trail
fld_surface = "surface"    # Surface type
fld_pop = "suit_score"     # Popularity (alias for suit_score)
fld_max_elev = "max_elevat"  # Max elevation
fld_min_elev = "min_elevat"  # Min elevation

# Input Values / Criteria
tgt_surf = "gravel"  # Try 'track' or 'concrete' later
pop_threshold = 1.7
record_limit = 10          # Counter limit for task 1d

# Backup / Output paths
backupName = "LarimerTrail_original"
outputLayer = "HighValue_Trails"

# 1. Return trail names for gravel trails
tgtFld = "surface"
tgtAttrib = 'gravel'

with arcpy.da.SearchCursor(
        in_table = trails,
        field_names = tgtFld,
        where_clause = f"{tgtFld} = '{tgtAttrib}'"
        ) as cursor:
    print ("Checking fields...")

    # for row in cursor:

# For field name = "surface" = "gravel" use a search cursor for read-only access
# to report trail names form the attribute table


# Optional: Add counter to only print the first 5-10 records
# Update the surface var to try a different surface type (Track)


# 2. High-ranking Trails
# Create a cursor with the appropriate where clause to return and print only the names
# and popularity values of trails above 1.7.


# 3. Highest Value in a Field
# Report the name of the trail with the highest "max_elevat" and the max elevation value.
# Repeat for "min_elevat" and value
# Consider reporting the top and bottom trail of each surface type


# 4. Update Nulls
# Create a copy of the trails layer, call it "LarimerTrail_original" this is a backup.
# Create the appropriate cursor and update all records with a surface value of Null (None) to be Unknown.
# An if statement could be used but would be slow, ideally use a where clause in the cursor.
# Make sure to save and commit


# 5. Optional Challenges
# Check document for optional additions


# "Popularity" is nickname/alias for "suit_score"
# # If table appears empty it may be "", " ", or null (python considers this None)
# # For null/None, use is/is not instead of ==