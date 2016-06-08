# file name:	ncc.py
# description:	This python script automates the process of segmenting a stream network
#				and populating those segments with a suite of parameters, including slope,
#				elevation, upstream drainage area, upstream precipitation, bankfull width
#				and depth, and shear stress, according to the natural channel classification
#               methodology outlined by Beechie and Imaki (2014). The script was developed
#				in support of the ISEMP RiverStyles project, with ultimate goal of providing
#				information to be used in salmonid habitat modeling.
# author:		Jesse Langdon
# dependencies: ESRI arcpy module, Spatial Analyst extension, Fluvial Corridors toolbox
#				modules, and custom python scripts.


import os, sys, time, arcpy
from time import strftime
from util.segment import seg_network as seg
from util.flv import elevation_slope as eS
from util.drainage import raster_prep as rP
from util.drainage import drainage as dR
from util.drainage import bf_ss_calc as bF
from util.drainage import calc_relative as cR

arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("3D")
arcpy.env.overwriteOutput = True

# start processing time
startTime = time.time()
printTime = strftime("%a, %d %b %Y %H:%M:%S")
arcpy.AddMessage("Processing started at " + str(printTime))
arcpy.AddMessage("-------------------------------------")

# user-supplied input variables
####outFGB = arcpy.GetParameterAsText(0)
outFGB = r"C:\JL\Testing\ncc-tool\Methow_HUC6\test_20160530.gdb"
arcpy.env.workspace = outFGB
####hucPoly = arcpy.GetParameterAsText(1)
hucPoly = r"C:\JL\Testing\ncc-tool\Methow_HUC6\data\huc6.shp"
####hydroLine = arcpy.GetParameterAsText(2)
hydroLine = r"C:\JL\Testing\ncc-tool\Methow_HUC6\data\nhdplus_flowline_100k.shp"
####segLen = arcpy.GetParameterAsText(3)
segLen = 200
####inDEM = arcpy.GetParameterAsText(4)
inDEM = r"C:\JL\Testing\ncc-tool\Methow_HUC6\data\dem_10m.tif"
####inPPT = arcpy.GetParameterAsText(5)
inPPT = r"C:\JL\Testing\ncc-tool\Methow_HUC6\data\ppt_buf2km.tif"
index_bool = "true"
strm_index = "GNIS_ID"
boolPnt = "true"

# Prepare vector data for workflow
segEndpoints, cleanStream = seg.main(hucPoly, hydroLine, index_bool, strm_index, segLen, outFGB, boolPnt)

# Prepare raster data for workflow
flowDir, flowAcc, ppt, demFill =  rP.raster_prep(inDEM, hucPoly, inPPT, outFGB)

# Calculate weighted flow accumulation (i.e. precipitation)
wtCalc_lin = dR.drain_calc(inDEM, segEndpoints, cleanStream, flowDir, flowAcc, ppt, outFGB)

# Calculate slope (using the Fluvial Corridor ElevationSlope.py tool)
arcpy.AddMessage("Calculating slope per line segment...")
slopeOut = eS.elev_slope(wtCalc_lin, demFill, outFGB + "\\seg_final")

# Calculate bankfull flow values and shear stress
bfwOut = bF.bfw_calc(slopeOut, outFGB)
bfdOut = bF.bfd_calc(bfwOut, outFGB)
ssOut = bF.ss_calc(bfdOut, outFGB)
fpdOut = bF.fpd_calc(ssOut, outFGB)

# Calculate relative shear stress
rssOut = cR.main(fpdOut, "ss", outFGB)

# Check in ESRI extensions
arcpy.CheckInExtension("Spatial")
arcpy.CheckInExtension("3D")

# end processing time
printTime = strftime("%a, %d %b %Y %H:%M:%S")
arcpy.AddMessage("-------------------------------------")
arcpy.AddMessage("Processing complete at " + str(printTime))
curTime = time.time()
totalTime = curTime - startTime
arcpy.AddMessage("Total processing time was " + str(totalTime) + " seconds.")