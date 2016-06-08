# file name:	dslv_index.py
# description:	This function dissolves all stream segments within a stream network polyline
#				dataset based on GNIS values.  This script was developed to provide functionality
#				to the Upstream Catchment Delineation tool. 
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, Spatial Analyst extension
# version:		0.2

import sys, arcpy

def main(in_strm, strm_index):
    arcpy.AddMessage("Select stream segments with " + strm_index + " values...")
    arcpy.MakeFeatureLayer_management(in_strm, "in_strm_lyr")
    fields = arcpy.ListFields("in_strm_lyr")
    for f in fields:
        if f.name == strm_index:
            f_type = f.type
    if f_type == 'Integer':
        expr_strm_wID = strm_index + " >= 0"
        arcpy.SelectLayerByAttribute_management("in_strm_lyr", "NEW_SELECTION", expr_strm_wID)
    elif f_type == 'String':
        expr_strm_wID = strm_index + " <> ''"
        arcpy.SelectLayerByAttribute_management("in_strm_lyr", "NEW_SELECTION", expr_strm_wID)
    strm_wID = arcpy.CopyFeatures_management("in_strm_lyr", r"in_memory\strm_wID")

    arcpy.AddMessage("Dissolving segments...")
    strm_dslvID = arcpy.Dissolve_management(strm_wID, r"in_memory\strm_dslvID", strm_index, "", "SINGLE_PART", "DISSOLVE_LINES")
    arcpy.SelectLayerByAttribute_management("in_strm_lyr", "SWITCH_SELECTION", "")
    strm_noID = arcpy.CopyFeatures_management("in_strm_lyr", r"in_memory\strm_noid")
    split_pnt = arcpy.Intersect_analysis([strm_dslvID, strm_noID], r"in_memory\split_pnt", "ONLY_FID", "", "point")
    strm_split = arcpy.SplitLineAtPoint_management(strm_dslvID, split_pnt, r"in_memory\strm_split", "5 meters")
    strm_dslvNoID = arcpy.Dissolve_management(strm_noID, r"in_memory\strm_dslvNoID", strm_index, "", "SINGLE_PART", "DISSOLVE_LINES")
    arcpy.Append_management(strm_dslvNoID, strm_split, "no_test", "", "")

    return strm_split