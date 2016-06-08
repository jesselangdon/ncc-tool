# file name:	endpoint.py
# description:	The purpose of this script is to plot points at the downstream end of stream segments.
#				This code relies heavily on tools developed by others, including Clement Roux's 
#				(clement.roux@ens-lyon.fr) Fluvial Corridors toolbox.
# author:		Jesse Langdon
# dependencies:	ESRI arcpy module
# version:      0.2

import os, sys, arcpy

def plot_end(in_line, in_fields):
	end_point = arcpy.CreateFeatureclass_management("in_memory", "end_point", "POINT", "", "DISABLED", "DISABLED", in_line)
	arcpy.AddField_management(end_point, "LineOID", "DOUBLE")
	arcpy.AddField_management(end_point, "Value", "DOUBLE")
	with arcpy.da.SearchCursor(in_line, (in_fields)) as search:
		with arcpy.da.InsertCursor(end_point, ("SHAPE@", "LineOID", "Value")) as insert:
			for row in search:
				try:
					line_geom = row[0]
					length = float(line_geom.length)
					oid = str(row[1])
					start = arcpy.PointGeometry(line_geom.firstPoint)
					if in_line != "in_memory\line_dup":
						end = arcpy.PointGeometry(line_geom.lastPoint)
						insert.insertRow((end, oid, str(length)))
					else:
						prct_end = line_geom.positionAlongLine(0.85,True).firstPoint
						insert.insertRow((prct_end, oid, str(length)))
				except Exception as e:
					print e.message
	return end_point

def main(line, seg_length):
	
	arcpy.AddMessage("Plotting segment endpoints...")
	arcpy.MakeFeatureLayer_management(line, "in_line_lyr")
	fields = ["SHAPE@", "LineOID"]

	# Plot endpoints for all segments
	endPnt_all = plot_end(line, fields)
	arcpy.MakeFeatureLayer_management(endPnt_all, "endPnt_all_lyr")

	# Find duplicate endpoints
	arcpy.FindIdentical_management("endPnt_all_lyr", "dup_table", ["Shape"], 0.5, "#", "ONLY_DUPLICATES")
	arcpy.MakeTableView_management(r"dup_table", "dup_tblview")
	arcpy.JoinField_management("endPnt_all_lyr","LineOID","dup_tblview","IN_FID","#")
	arcpy.SelectLayerByAttribute_management("endPnt_all_lyr","NEW_SELECTION",""""IN_FID" IS NOT NULL""")
	arcpy.FeatureClassToFeatureClass_conversion("endPnt_all_lyr", "in_memory", "endPnt_dup")

	# Find segments with duplicate endpoints
	arcpy.JoinField_management("in_line_lyr", "OBJECTID", "dup_tblview", "IN_FID", "#")
	arcpy.SelectLayerByAttribute_management("in_line_lyr", "NEW_SELECTION", """"IN_FID" IS NOT NULL""")
	arcpy.FeatureClassToFeatureClass_conversion("in_line_lyr", "in_memory", "line_dup")
	arcpy.SelectLayerByAttribute_management("in_line_lyr", "SWITCH_SELECTION")
	arcpy.FeatureClassToFeatureClass_conversion("in_line_lyr", "in_memory", "line_nodup")

	# Re-plot endpoints for segments with duplicate endpoints
	endPnt_dup_final = plot_end(r"in_memory\line_dup", fields)
	arcpy.FeatureClassToFeatureClass_conversion(endPnt_dup_final, "in_memory", "endPnt_dup_final")
	endPnt_nodup_final = plot_end(r"in_memory\line_nodup", fields)
	arcpy.FeatureClassToFeatureClass_conversion(endPnt_nodup_final, "in_memory", "endPnt_nodup_final")
	finalEndpnt = arcpy.Merge_management(["in_memory\endPnt_nodup_final","in_memory\endPnt_dup_final"], r"in_memory\finalEndPnt")

	# clean up temp files
	arcpy.Delete_management("in_line_lyr")
	arcpy.Delete_management(r"dup_table")
	arcpy.Delete_management("dup_tblview")
	arcpy.Delete_management(endPnt_all)
	arcpy.Delete_management("endPnt_all_lyr")
	arcpy.Delete_management(r"in_memory\endPnt_dup")
	arcpy.Delete_management(r"in_memory\line_dup")
	arcpy.Delete_management(r"in_memory\line_nodup")
	arcpy.Delete_management(r"in_memory\endPnt_nodup_final")
	arcpy.Delete_management(r"in_memory\endPnt_dup_final")

	return finalEndpnt