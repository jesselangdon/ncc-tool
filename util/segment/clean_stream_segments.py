# Name:         segment_points.py
# Author:       Jesse Langdon
# Desc:         This script merges a smaller stream segment with an adjacent stream segment if that segment is
#               longer, and shares a common attribute code (like a stream or OID).  This code is derived from a 
#               function posted to gis.stackexchange.com ((username: gotanuki) on Jan. 14, 2013.
# Revised:      January 6th, 2015

import os, sys, arcpy
arcpy.env.overwriteOutput = True

def cleanLineGeom(inLine,streamID,segID,lineClusterTolerance):
    lyrs = []
    inLineName = arcpy.Describe(inLine).name
    oidFieldName = arcpy.Describe(inLine).oidFieldName
    
    # Add new field to store field length values (to replace the "Shape_Length" or "Shape_Leng" fields)
    arcpy.AddField_management(inLine, "SegLen", "DOUBLE", "", "", "", "","NULLABLE", "NON_REQUIRED")
    arcpy.CalculateField_management(inLine, "SegLen", "!shape.length@meters!", "PYTHON_9.3")

    # Separate short and long lines into different layers, then select all longs that touch shorts
    shortLines = arcpy.MakeFeatureLayer_management(inLine,'shortLines',"SegLen" + ' <= '+ str(lineClusterTolerance))
    lyrs.append(shortLines)
    longLines = arcpy.MakeFeatureLayer_management(inLine,'longLines', "SegLen" + ' > '+str(lineClusterTolerance))
    lyrs.append(longLines)
    arcpy.SelectLayerByLocation_management(longLines,"BOUNDARY_TOUCHES",shortLines,'',"NEW_SELECTION")

    # Make a dictionary relating shortLine streamID/segID pairs to their origin- and endpoint coordinate pairs
    shortDict = {}
    rows = arcpy.SearchCursor(shortLines)
    for row in rows:
        shp = row.Shape
        shortDict[(row.getValue(streamID),row.getValue(segID))] = [(shp.firstPoint.X,shp.firstPoint.Y),(shp.lastPoint.X,shp.lastPoint.Y)]
    del rows

    # Make a dictionary relating longLine origin- and endpoint coordinate pairs to segIDs
    longDict = {}
    rows = arcpy.SearchCursor(longLines)
    for row in rows:
        shp = row.Shape
        firstCoords = (shp.firstPoint.X,shp.firstPoint.Y)
        lastCoords = (shp.lastPoint.X,shp.lastPoint.Y)
        longDict[firstCoords] = (row.getValue(streamID),row.getValue(segID))
        longDict[lastCoords] = (row.getValue(streamID),row.getValue(segID))
    del rows

    # Create new dictionary relating shortLine segIDs to longLine segIDs that share a point
    dissolveDict = {}
    # If a shortLine's coordinate pair matches an entry in longDict,
    # and the longLine's streamID matches, add their segIDs to dissolveDict
    for ids, coordPairs in shortDict.iteritems():
        for coords in [coordPairs[0],coordPairs[1]]:
            if coords in longDict.iterkeys():
                if longDict[coords][0] == ids[0]:
                    dissolveDict[ids[1]] = longDict[coords][1]

    # Give all longLines a 'dissolve' value equal to their segID
    arcpy.AddField_management(inLine,'dissolve','LONG')
    arcpy.SelectLayerByAttribute_management(longLines,"CLEAR_SELECTION")
    arcpy.CalculateField_management(longLines,'dissolve','[{0}]'.format(segID),'VB')

    # If shortLine in dissolveDict, give it a 'dissolve' value equal to the dissolveDict value
    # Else give it its own segID
    urows = arcpy.UpdateCursor(shortLines,'','',segID+';dissolve')
    for urow in urows:
        if dissolveDict.get(urow.getValue(segID)):
            urow.dissolve = dissolveDict[urow.getValue(segID)]
        else:
            urow.dissolve = urow.getValue(segID)
        urows.updateRow(urow)
    del urows

    arcpy.Dissolve_management(inLine, r'in_memory\seg_dslv', 'dissolve', '', 'MULTI_PART')
    cleaned = arcpy.JoinField_management(r'in_memory\seg_dslv', 'dissolve', inLine, segID, [segID, streamID])
    arcpy.DeleteField_management(cleaned, 'dissolve')

    return cleaned
