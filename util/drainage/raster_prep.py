# file name:	raster_prep.py
# description:	This function preprocesses elevation and precipitation raster data,
#				then calculates flow direction and flow accumulation using the preprocessed
#				elevation data.  The resulting raster datasets can serve as inputs for
#				other tools that calculate drainage area, slope, and precipitation per
#				drainage basin.  		  
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, Spatial Analyst extension

import os, sys, arcpy
from arcpy.sa import *

# define preprocess DEM function
def raster_prep(in_dem, in_huc, input_ppt, outFGB):
	arcpy.AddMessage("Preprocessing the DEM...")
	arcpy.MakeRasterLayer_management(in_dem, r"in_dem_lyr")
	arcpy.MakeFeatureLayer_management(in_huc, r"in_huc_lyr")
	dem_clip = ExtractByMask(r"in_dem_lyr", r"in_huc_lyr")
	dem_smooth = FocalStatistics(dem_clip, NbrCircle(5, "CELL"))
	dem_fill = Fill(dem_smooth, "#")
	dem_fill.save(outFGB + "\\dem_fill")

	# create flow rasters
	arcpy.AddMessage("Calculating flow direction and accumulation...")
	fd = FlowDirection(dem_fill, "NORMAL")
	fd.save(outFGB + "\\flow_dir")
	fa = FlowAccumulation(fd)
	fa.save(outFGB + "\\flow_acc")

	# set raster environment parameters
	arcpy.env.extent = outFGB + "\\dem_fill"
	arcpy.env.snapRaster = outFGB + "\\dem_fill"
	arcpy.env.cellSize = outFGB + "\\dem_fill"
	arcpy.env.mask = outFGB + "\\dem_fill"

	# process precipitation raster data
	arcpy.AddMessage("Processing the precipitation data...")
	arcpy.MakeRasterLayer_management(input_ppt, "in_ppt_lyr")
	arcpy.Buffer_analysis("in_huc_lyr", outFGB + "\\huc_buf", "1 Kilometers", "FULL", "#", "ALL")
	arcpy.MakeFeatureLayer_management(outFGB + "\\huc_buf", r"huc_buf_lyr")
	ppt_clip = ExtractByMask("in_ppt_lyr", "huc_buf_lyr" )
	ppt_clip.save(outFGB + "\\ppt_clip")
	arcpy.MakeRasterLayer_management(outFGB + "\\ppt_clip", "ppt_clip_lyr")
	arcpy.Resample_management("ppt_clip_lyr", outFGB + "\\ppt_resmp", "10", "BILINEAR")
	ppt = outFGB + "\\ppt_resmp"

	# temp file clean up
	arcpy.Delete_management("in_ppt_lyr")
	arcpy.Delete_management("in_huc_lyr")
	arcpy.Delete_management("ppt_clip_lyr")
	arcpy.Delete_management(outFGB + "\\ppt_clip")

	return (fd, fa, ppt, dem_fill)