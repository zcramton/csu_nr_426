"""
NR426 Final Project
Mapping Beaver Activity on Developed and Working Lands
Author: Zachary Cramton
Date: 3/3/2026

This project maps beaver activity in Colorado using CNHP-BRAT/COBAM beaver activity mapping data as well as NLCD Land
Cover and Fractional Impervious Surface data to identify likely human-beaver conflict areas to advise incorporating
beaver in urban watershed de-channelization.

Notes:
- Specific COBAM layer: BRAT Existing Dam Building Capacity
- For NLCD use base land cover raster and augment with fractional impervious surface if time allows.
"""

import arcpy
import os
import sys

# Define data sources
COBAM_url = r"https://services1.arcgis.com/KNdRU5cN6ENqCTjk/arcgis/rest/services/Legend_Test1/FeatureServer"
NLCD_LC_url = r"find ESRI living atlas layer"
NLCD_FIS_url = r"find ESRI living atlas layer"
# Partitioning Data
counties = r"check CNHP for COBAM partition"
states = r"Check ESRI living atlas for county/state/country data for NA."
watersheds = r"check CNHP for COBAM partition, Or HUCs?"

arcpy.env.workspace = r"FinalProject"

# Verify data and workspace
# if statements (could also use try-except but less good)

# Ask for user input differentiating COBAM delineator
# Specify Watershed/Counties/State
# Specify desired selection within the delineator

# Clip data to delineator
# Ask user if they want to save the layer or only use it for analysis in python memory
