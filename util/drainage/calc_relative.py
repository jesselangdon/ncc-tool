# file name:	calc_relative.py
# description:	This python script calculates relative parameters for each stream reach segment in a stream
#               network. Targeted parameters include slope and shear stress, although concievabley other metrics
#               could be calculated. This code is a component of the NCC Tool, which is an automated workflow for
#				segmenting a stream network and populating those segments with a suite of parameters, and then
#               predicting and assigning natural channel classification types according to the methodology outlined
#               by Beechie and Imaki (2014). Specifically this tool was developed in support of the ISEMP RiverStyles
#				project, with the ultimate goal of providing information to be used in salmonid habitat modeling.
#               Much of the code in this script was derived from code originally written by Hiroo Imaki.
# author:		Jesse Langdon
# dependencies: none

import arcpy

def main(input_strm, param, outFGB):

    # Add a new field to store the relative shear stress values
    arcpy.FeatureClassToFeatureClass_conversion(input_strm, r"in_memory", "rel_calc")
    rel_calc = arcpy.MakeFeatureLayer_management(r"in_memory\rel_calc", "rel_calc_lyr")
    #arcpy.FeatureClassToFeatureClass_conversion(input_strm, outFGB, "rel_calc")
    #arcpy.MakeFeatureLayer_management(outFGB + r"\rel_calc", "rel_calc_lyr")
    calc_field = param + "_r"
    arcpy.AddField_management("rel_calc_lyr", calc_field, "DOUBLE")

    # compile list of stream IDs
    strm_id = []
    with arcpy.da.SearchCursor("rel_calc_lyr", ["strmID"]) as cursor_sid:
        for row_sid in cursor_sid:
            strm_id.append(row_sid[0])
    strm_id_unique = sorted(set(strm_id))

    # use data access (da) update cursor to calculate relative values
    for id in strm_id_unique:
        arcpy.SelectLayerByAttribute_management("rel_calc_lyr", "NEW_SELECTION", """"strmID" = '%s'""" % id)
        cursor_param = arcpy.da.UpdateCursor("rel_calc_lyr", ["LineOID", param, calc_field])
        reach_counter = 1
        old_val = 0
        for row_param in cursor_param:
            print row_param[0]
            # store the parameter value for the first reach of the stream
            if reach_counter == 1:
                old_val = row_param[1]
                row_param[2] = old_val
                reach_counter += 1
                cursor_param.updateRow(row_param)
                continue
            # if other than the first stream reach, calculate relative value
            else:
                row_param[2] = abs(row_param[1] - old_val)
                reach_counter += 1
                cursor_param.updateRow(row_param)
        del row_param
        del cursor_param

    return rel_calc





