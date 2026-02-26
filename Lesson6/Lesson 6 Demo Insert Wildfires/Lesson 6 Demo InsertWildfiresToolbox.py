import arcpy, os

try:
    outputFC = arcpy.GetParameterAsText(0)
    fClassTemplate = arcpy.GetParameterAsText(1)
    f = open(arcpy.GetParameterAsText(2), 'r')

    #Syntax for Create Feature Class tool:
    #CreateFeatureclass(out_path, out_name, {geometry_type}, {template}, {has_m}, {has_z}, {spatial_reference},\
    #{config_keyword}, {spatial_grid_1}, {spatial_grid_2}, {spatial_grid_3}, {out_alias})

    arcpy.CreateFeatureclass_management(os.path.split(outputFC)[0], os.path.split(outputFC)[1], "point", fClassTemplate, "", "", fClassTemplate)

    lstFires = f.readlines()
    fields = ["SHAPE@XY", "CONFIDENCEVALUE"]
   
    with arcpy.da.InsertCursor(outputFC, fields) as cur:
        for fire in lstFires:
            if 'Latitude' in fire:
                continue
            vals = fire.split(",")
            latitude = float(vals[0])
            longitude = float(vals[1])
            confid = int(vals[2])
            row_values = [(longitude, latitude), confid]
            cur.insertRow(row_values)

except Exception as e:
    print("Error: " + e.args[0])
