import arcpy
from arcpy.sa import *
import os

maindir = "L:\\Projects_active\\TNC_Riparian\\Gunnison\\2015\\"
smsdir = maindir + "SegmentMeanShift\\"
isodir = maindir + "ISO\\"
ecddir = isodir + "ECDfiles\\"
print(ecddir)

arcpy.CheckOutExtension("Spatial")

arcpy.env.workspace = maindir
# create segmented image for each tile
for tif in arcpy.ListRasters("*", "TIF"):
    inRast = tif
    spectral = "20"
    spatial = "20"
    min_seg_size = "1"
    bands = "4 1 2"
    if not os.path.exists(smsdir + "seg_" + str(tif)):
        seg_raster = SegmentMeanShift(inRast, spectral, spatial, min_seg_size, bands)
        seg_raster.save(smsdir + "seg_" + str(tif))
    else:
        print("SMS complete")
    
arcpy.env.workspace = smsdir
for tif in arcpy.ListRasters("*", "TIF"):
    print(tif)
    inSegRast = tif
    maxClasses = "15"
    out_def = ecddir + str(tif) + "_iso.ecd"
    maxIter = "20"
    minNumSamples = "10"
    skipFactor = "2"
    attributes = "COLOR;MEAN"
    if not os.path.exists(out_def):
        TrainIsoClusterClassifier(inSegRast, maxClasses, out_def, "", maxIter, minNumSamples, skipFactor, attributes)
    else:
        print("ecd complete")

        
        
        



