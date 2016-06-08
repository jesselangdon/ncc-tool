# file name:	seg_network.py
# description:	This python script automates the process of segmenting a stream network based 
#				on a user-defined segment length, and plotting the downstream segment 
#				endpoints. 	 
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, the Fluvial Corridors toolbox, and custom python functions.
# version:      0.2

import os, sys, time, arcpy
# sys.path.insert( 0, r"C:\repo\segment")
import dslv_index as dslv
import segment
import transfer_strm_id as transfer_id
import endpoint

arcpy.env.overwriteOutput = True

## Input variables
# input_huc = arcpy.GetParameterAsText(0)
# input_strm = arcpy.GetParameterAsText(1)
# index_bool = arcpy.GetParameterAsText(2)
# strm_index = arcpy.GetParameterAsText(3)
# seg_len = arcpy.GetParameterAsText(4)
# outFGB = arcpy.GetParameterAsText(5)
# boolPnt = arcpy.GetParameterAsText(6)

def main(input_huc, input_strm, index_bool, strm_index, seg_len, outFGB, boolPnt):
	# Dissolve stream segments based on index field (i.e. GNIS name)
	if index_bool == "true":
		arcpy.AddMessage("Dissolving streams based on GNIS values...")
		strm_dslv = dslv.main(input_strm, strm_index)
	else:
		strm_dslv = input_strm

	# Split lines into segments
	arcpy.AddMessage("Segmenting streams...")
	strm_seg = segment.main(input_huc, strm_dslv, seg_len, outFGB)
	strm_seg_id = transfer_id.main(input_strm, strm_seg, outFGB)
	#arcpy.FeatureClassToFeatureClass_conversion(strm_seg_, outFGB, r"segments")

	# Plot segment endpoints (optional)
	if boolPnt == "true":
		strm_pts = endpoint.main(strm_seg_id, seg_len)
		arcpy.FeatureClassToFeatureClass_conversion(strm_pts, outFGB, "endpoints")
	else:
		pass

	arcpy.AddMessage("Process complete!")

	return strm_pts, strm_seg_id