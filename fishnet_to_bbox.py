import arcpy
import os
import json


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


def fishnet_to_bbox_json(fishnet):
    basename = os.path.basename(fishnet).split('.')[0]
    filename = r'.\polygons.json'
    sf = arcpy.SpatialReference(4326)
    projected = arcpy.Project_management(fishnet, basename + 'projected', sf)
    out_d = dict()

    # write id and bbox to dictionary
    with arcpy.da.SearchCursor(projected, ['Id', 'SHAPE@']) as cur:
        for row in cur:
            oid = row[0]
            extent = row[1].extent
            bbox = [extent.YMin, extent.YMax, extent.XMin, extent.XMax]
            out_d[oid] = bbox

    # write to file
    with open(filename, 'w') as outfile:
        json.dump(out_d, outfile, indent=4)


if __name__ == '__main__':
    # fishnet_to_bbox(downtown)
    fishnet_to_bbox_json(r"\\wying\GeoPhoto\SFStreet\blocks_downtown.shp")
