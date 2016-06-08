# file name:	drainage.py
# description:	This function uses flow accumulation to calculate drainage area and
#				any other value that can be represented as a raster data set.  The
#				raster dataset is used to developed a weighted flow accumulation raster
#				dataset which is then divided by the original flow accumulation data,
#				resulting in a raster in which each cell 

# author:		Jesse Langdon
# dependencies: ESRI arcpy module, Spatial Analyst extension

import arcpy
from arcpy.sa import *

def drain_calc(inDEM, inSegPt, inSegLine, inFD, inFA, inPPT, outFGB):
    # Calculate weighted flow accumulation
    arcpy.AddMessage("Calculating weighted flow accumulation...")
    wt_fa = FlowAccumulation(inFD, inPPT, "FLOAT")
    wt_fa.save(outFGB + r"\fa_wt")

    # Calculate drainage area and ppt using segment endpoints
    arcpy.AddMessage("Calculating parameters per stream segment...")
    arcpy.Buffer_analysis(inSegPt, outFGB + "\\buf_01", "60 Meters", "FULL", "#", "NONE")
    # arcpy.CopyFeatures_management(outFGB + "\\buf_01", outFGB + "\\buf_02")
    arcpy.MakeFeatureLayer_management(outFGB + "\\buf_01", "buf_ly01")
    # arcpy.MakeFeatureLayer_management(outFGB + "\\buf_02", "buf_ly02")
    # arcpy.AddField_management("buf_ly02", "X", "DOUBLE")
    # arcpy.AddField_management("buf_ly02", "Y", "DOUBLE")
    # arcpy.AddField_management("buf_ly02", "XY", "TEXT")
    # arcpy.CalculateField_management("buf_ly02", "X", "!Shape.Centroid.X!", "PYTHON_9.3")
    # arcpy.CalculateField_management("buf_ly02", "Y", "!Shape.Centroid.Y!", "PYTHON_9.3")
    # arcpy.CalculateField_management("buf_ly02", "XY", """str(!X!) + "_" + str(!Y!)""", "PYTHON_9.3")
    # arcpy.Dissolve_management("buf_ly02", outFGB + "\\buf_dsv", ["XY"], [["LineOID", "FIRST"]])
    # arcpy.MakeFeatureLayer_management(outFGB + "\\buf_dsv", "buf_dsv_ly")
    # arcpy.AddJoin_management("buf_ly01", "LineOID", "buf_dsv_ly", "FIRST_LineOID", "KEEP_ALL")
    # arcpy.CopyFeatures_management("buf_ly01", outFGB + "\\buf_join")
    # arcpy.MakeFeatureLayer_management(outFGB + "\\buf_join", "buf_join_ly")
    # arcpy.SelectLayerByAttribute_management("buf_join_ly", "NEW_SELECTION", "buf_dsv_FIRST_LineOID IS NULL")
    # seg_pt_buf01 = arcpy.FeatureClassToFeatureClass_conversion("buf_join_ly", outFGB, "buf_sel_01")
    # arcpy.SelectLayerByAttribute_management("buf_join_ly", "SWITCH_SELECTION")
    # seg_pt_buf02 = arcpy.FeatureClassToFeatureClass_conversion("buf_join_ly", outFGB, "buf_sel_02")
    # arcpy.RemoveJoin_management("buf_ly01")

    # calculate zonal statistics per point buffer, only if there are records
    # result01 = arcpy.GetCount_management(seg_pt_buf01)
    # pt_buf01_cnt = int(result01.getOutput(0))
    #
    # if pt_buf01_cnt == 0:
    #     ZonalStatisticsAsTable(seg_pt_buf02, "LineOID", inFA, outFGB + "\\fa_max_02", "DATA", "MAXIMUM")
    #     arcpy.CopyRows_management(outFGB + "\\fa_max_02", outFGB + "\\fa_max_tbl")
    # else:
    #     ZonalStatisticsAsTable(seg_pt_buf01, "LineOID", inFA, outFGB + "\\fa_max_01", "DATA", "MAXIMUM")
    #     ZonalStatisticsAsTable(seg_pt_buf02, "LineOID", inFA, outFGB + "\\fa_max_02", "DATA", "MAXIMUM")
    #     arcpy.Merge_management([outFGB + "\\fa_max_01", outFGB + "\\fa_max_02"], outFGB + "\\fa_max_tbl")
    #
    # result02 = arcpy.GetCount_management(seg_pt_buf02)
    # pt_buf02_cnt = int(result02.getOutput(0))
    # if pt_buf02_cnt == 0:
    #     ZonalStatisticsAsTable(seg_pt_buf02, "LineOID", wt_fa, outFGB + "\\ppt_max_02", "DATA", "MAXIMUM")
    #     arcpy.CopyRows_management(outFGB + "\\ppt_max_02", outFGB + "\\ppt_max_tbl")
    # else:
    #     ZonalStatisticsAsTable(seg_pt_buf01, "LineOID", wt_fa, outFGB + "\\ppt_max_01", "DATA", "MAXIMUM")
    #     ZonalStatisticsAsTable(seg_pt_buf02, "LineOID", wt_fa, outFGB + "\\ppt_max_02", "DATA", "MAXIMUM")
    #     arcpy.Merge_management([outFGB + "\\ppt_max_01", outFGB + "\\ppt_max_02"], outFGB + "\\ppt_max_tbl")


    # YOU NEED TO CHANGE LineOID TO AN INTEGER FIELD.  CURRENTLY IT'S A DOUBLE, WHICH THIS FUNCTION DOESN'T LIKE!!!
    arcpy.AddField_management("buf_ly01", "LineOID_str", "TEXT")
    arcpy.CalculateField_management("buf_ly01", "LineOID_str", """!LineOID!""", "PYTHON_9.3")
    ZonalStatisticsAsTable("buf_ly01", "LineOID_str", inFA, outFGB + "\\fa_max_tbl", "DATA", "MAXIMUM")
    ZonalStatisticsAsTable("buf_ly01", "LineOID_str", wt_fa, outFGB + "\\ppt_max_tbl", "DATA", "MAXIMUM")


    # Add drainage and precipitation values to line segments
    arcpy.AddMessage("Adding drainage area and precipitation values to line segments...")
    arcpy.MakeFeatureLayer_management(inSegLine, "inSegLine_lyr")
    arcpy.AddField_management("inSegLine_lyr", "LineOIDtmp", "TEXT")
    arcpy.CalculateField_management("inSegLine_lyr", "LineOIDtmp", """!OBJECTID!""", "PYTHON_9.3")
    arcpy.AddField_management("inSegLine_lyr", "fa", "DOUBLE")
    arcpy.AddField_management("inSegLine_lyr", "ppt", "DOUBLE")
    arcpy.AddJoin_management("inSegLine_lyr", "LineOIDTmp", outFGB + "\\fa_max_tbl", "LINEOID_STR")
    arcpy.CalculateField_management("inSegLine_lyr", "fa", """!MAX!""", "PYTHON_9.3")
    arcpy.RemoveJoin_management("inSegLine_lyr")
    arcpy.AddJoin_management("inSegLine_lyr", "LineOIDTmp", outFGB + "\\ppt_max_tbl", "LINEOID_STR")
    arcpy.CalculateField_management("inSegLine_lyr", "ppt", """!MAX!""", "PYTHON_9.3")
    arcpy.RemoveJoin_management("inSegLine_lyr")
    arcpy.DeleteField_management("inSegLine_lyr", "LineOIDTmp")
    seg_calc = arcpy.CopyFeatures_management("inSegLine_lyr", outFGB + "\\seg_calc")

    # clean up all temporary files
    arcpy.AddMessage("Cleaning up temporary files...")
    arcpy.Delete_management(outFGB + "\\buf_01")
    arcpy.Delete_management(outFGB + "\\fa_max_tbl")
    arcpy.Delete_management(outFGB + "\\ppt_max_tbl")
    return seg_calc
