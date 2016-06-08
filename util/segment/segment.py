# file name:	segment.py
# description:	This Python script splits line objects in a polyline feature class based
#				on a user-defined length value.  Segments that share the same parent segment
#				ID, and are adjacent to each other, and with a segment length less than 95%
#				of the user-defined segment length, are merged to the adjacent segment 
#				(to remove "slivers").
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, the Fluvial Corridors toolbox.

import os, sys, arcpy
from ..flv import flv_ScratchWPathName as SWPN
from ..flv import flv_SLEM as dS
from ..segment import clean_stream_segments as cS

# Derived variable from inputs
# ScratchW = SWPN.ScratchWPathName ()

def main(huc_poly, in_hydro, seg_length, outFGB):

	DeleteTF = "true"

	# clip stream lines to huc polygon boundaries.
	arcpy.AddMessage("Clipping the stream network to the HUC boundaries...")
	clip_hydro = arcpy.Clip_analysis(in_hydro, huc_poly, r"in_memory\clip_hydro")
	
	# segmentation of the polyline
	arcpy.AddMessage("Using the SLEM script to segment the polyline feature...")
	SplitLine = dS.SLEM(clip_hydro, seg_length, r"in_memory\SplitLine", DeleteTF)
	
	arcpy.AddMessage("Sorting the segmented line...")
	outSort = outFGB + r"\segments"
	arcpy.Sort_management(SplitLine, outSort, [["Rank_UGO", "ASCENDING"], ["Distance", "ASCENDING"]])
	
	arcpy.AddField_management(outSort, "Rank_DGO", "LONG", "", "", "", "","NULLABLE", "NON_REQUIRED")
	fieldname = [f.name for f in arcpy.ListFields(outSort)]
	arcpy.CalculateField_management(outSort, "Rank_DGO", "!" + str(fieldname[0]) + "!", "PYTHON_9.3")

	#delete temporary files
	arcpy.AddMessage("Deleting temporary files...")
	arcpy.Delete_management(SplitLine)

	# merges adjacent stream segments if one is less than threshold.
	arcpy.AddMessage("Cleaning line segments...")
	clusterTolerance = float(seg_length) * 0.25
	clean_stream = cS.cleanLineGeom(outSort, "Rank_UGO", "Rank_DGO", clusterTolerance)
	arcpy.AddField_management(clean_stream, "LineOID", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED")
	arcpy.CalculateField_management(clean_stream, "LineOID", '"!OBJECTID!"', "PYTHON_9.3")
	arcpy.DeleteField_management(clean_stream, "Rank_UGO")
	arcpy.DeleteField_management(clean_stream, "Rank_DGO")
	return clean_stream