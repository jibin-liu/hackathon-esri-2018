import arcpy
import os


arcpy.env.overwriteOutput = True
arcpy.env.workspace = r'C:\Users\jibi8520\Documents\ArcGIS\Projects\MyProject\MyProject.gdb'
downtown = 'san_francisco_downtown'


def fishnet_to_bbox(fishnet):
    filename = r'.\sf.csv'
    sf = arcpy.SpatialReference(4326)
    projected = arcpy.Project_management(fishnet, 'projected', sf)
    with open(filename, 'w') as outfile:
        with arcpy.da.SearchCursor(projected, 'SHAPE@') as cur:
            for row in cur:
                extent = row[0].extent
                bbox = [extent.XMin, extent.YMin, extent.XMax, extent.YMax]
                outfile.write(','.join([str(e) for e in bbox]) + '\n')

fishnet_to_bbox(downtown)
