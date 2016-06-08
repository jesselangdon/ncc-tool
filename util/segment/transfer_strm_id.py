# file name:	transfer_strm_ID.py
# description:	This Python script transfers the object ID of the original stream network polyline feature class to
#               to the associated stream segments. This code is a component of the NCC Tool, which is an automated
#				workflow for segmenting a stream network and populating those segments with a suite of parameters,
#               and then predicting and assigning natural channel classification types according to the methodology
#               outlined by Beechie and Imaki (2014). Specifically this tool was developed in support of the ISEMP
#				RiverStyles project, with the ultimate goal of providing information to be used in salmonid habitat
#               modeling. The midpoint plotting code was derived by a StackExchange solution posted by user Cecil
#               James (http://stackexchange.com/users/3677873/cecil-james).
# author:		Jesse Langdon
# dependencies: ESRI arcpy module

import arcpy
arcpy.env.overwriteOutput = True

def main(input_strm, input_seg, outFGB):

    arcpy.AddMessage("Transferring original stream reach object IDs to segments features...")

    # create copy of stream segments, which will include new stream ID field
    seg_id = arcpy.FeatureClassToFeatureClass_conversion(input_seg, outFGB, r"seg_id")

    # generate the midpoint for each segmented stream network
    arcpy.FeatureToPoint_management(input_seg, outFGB + "\midpoint", "INSIDE")
    arcpy.MakeFeatureLayer_management(outFGB + "\midpoint", "midpoint_lyr")

    # field mapping for the spatial join (this is from ESRI help resources example)
    # create FieldMap and FieldMapping objects
    fm_strmOID = arcpy.FieldMap()
    fm_segOID = arcpy.FieldMap()
    fms = arcpy.FieldMappings()
    # set field names from input files
    strm_oid = arcpy.Describe(input_strm).OIDFieldName
    line_oid = "LineOID" # from seg_id
    # add fields to FieldMap objects
    fm_strmOID.addInputField(input_strm, strm_oid)
    fm_segOID.addInputField(seg_id, line_oid)
    # set output field properties for FieldMap objects (this is pure ESRI clunkiness)
    strmOID_name = fm_strmOID.outputField
    strmOID_name.name = "strmOID"
    fm_strmOID.outputField = strmOID_name
    segOID_name = fm_segOID.outputField
    segOID_name.name = "LineOID"
    fm_segOID.outputField = segOID_name
    # add FieldMap objects to the FieldMappings object
    fms.addFieldMap(fm_strmOID)
    fms.addFieldMap(fm_segOID)

    # spatial join between midpoints and original stream network polyline feature class
    ##midpoint_join = r"in_memory\midpoint_join"
    midpoint_join = outFGB + "\midpoint_join"
    arcpy.SpatialJoin_analysis("midpoint_lyr", input_strm, midpoint_join, "JOIN_ONE_TO_MANY",
                               "KEEP_ALL", fms, "INTERSECT", 0.5)

    # join midpoints to segmented streams based on shared LineOID
    arcpy.MakeFeatureLayer_management(seg_id, "seg_id_lyr")
    arcpy.AddField_management("seg_id_lyr", "strmID", "TEXT")
    arcpy.AddJoin_management("seg_id_lyr", "LineOID", midpoint_join, "LineOID", "KEEP_ALL")
    arcpy.CalculateField_management("seg_id_lyr", "strmID", "!strmOID!", "PYTHON_9.3")
    arcpy.RemoveJoin_management("seg_id_lyr")

    return seg_id