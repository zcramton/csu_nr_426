"""
Lab 4B Demo
Completed 19FEB2026 by Zachary Cramton

Throwaway script to explore and compare SQL queries and ArcPy select/search tools.
"""
import arcpy

roadkill = RoadkillSightings # Fake var for practice
query = "ZLAND_COVE = 'Deciduous woods'"
query2 = "ZLAND_COVE LIKE '%Deciduous%' Or ZLAND_COVE LIKE '%deciduous%'"
query_input = query2

# Stores selection in memory
arcpy.management.SelectLayerByAttribute(
    in_layer_or_view= roadkill,
    select_geometry= "",
    where_clause= query_input,
    invert_where_clause= "INVERT"
    )

# If looking for empty string vs. null
query3 = "ZLAND_COVE IS Null" # For true null values in SQL. Seen as NONE in Python.
query5 = "ZLAND_COVE == '' Or ZLAND_COVE == ' '" # For empty strings

# Use MakeFeatureLayer to make dedicated in memory layer before selecting features.
# See videos/slides for why.

# Copy features with CopyFeature Tool

# Using the CalculateField tool, troubleshoot/test the python equation in the py console
# Check slides to webpage with help for CalcField