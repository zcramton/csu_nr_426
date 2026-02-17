## Quick script for Luke Martin to convert GPX data

print "Starting script to convert GPX files..."

# Requires user input for the input folder name
folder = r"<enter your path here>"

print "Importing arcpy and sys..."
import arcpy, sys
arcpy.env.workspace = folder

# Create a list of the .gpx files
print "Creating list of gpx files in the folder..."
fileList = arcpy.ListFiles("*.gpx")


if len(fileList) == 0:
    print "There aren't any .gpx files in this folder, Exiting script"
    sys.exit()

else:
    print "There are " + len(fileList) + " gpx files to convert"
    # Loop through the list of .gpx files
    print "Converting the gpx files now..."
    for file in fileList:
        # Format the filename without the extension
        name = file[:-4]   ##Not sure how the files are read in - I'm assuming it will be abc.gpx
        outSHP = name+".shp"
        
        #Syntax for GPX to Features tool:
        #GPXToFeatures_conversion (Input_GPX_File, Output_Feature_class)
        try:
            arcpy.GPXToFeatures_conversion (file, outSHP)
            print "Converted " +file + " to " + outSHP
        except:
            print arcpy.GetMessages()

print "Script completed. Look at your folder to verify results."
