import arcpy
#import os

try:
    arcpy.env.workspace = r"...\WildlandFires.gdb"
    f = open(r"...\NorthAmericaWildfires_2007275.txt", "r")
    lstFires = f.readlines()
    with arcpy.da.InsertCursor("FireIncidents",("SHAPE@XY","CONFIDENCEVALUE")) as cur:
            cntr = 1
            for fire in lstFires:
                    if 'Latitude' in fire:
                            continue
                    vals = fire.split(",")
                    latitude = float(vals[0])
                    longitude = float(vals[1])
                    confid = int(vals[2])
                    rowValue = [(longitude,latitude),confid]
                    cur.insertRow(rowValue)
                    print("Record number " + str(cntr) + " written to feature class")
                    cntr = cntr + 1
except Exception as e:
    print("Error: " + e.args[0])
finally:
    f.close()
