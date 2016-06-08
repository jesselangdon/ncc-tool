# file name:	calc_params.py
# description:	This function calculates bankfull width, bankfull depth, shear
#				stress, and floodplain depth per stream segment.  The code is derived from a
#				script developed by Hiroo Imaki in support of a peer-reviewed research paper
#				published in 2014 (see Beechie, T., and H. Imaki (2014), Predicting natural
#				channel patterns based on landscape and geomorphic controls in the Columbia
#				River basin, USA, Water Resour. Res., 50, 39-57, doi: 10.1002/2013WR013629).	  
# author:		Jesse Langdon
# dependencies: ESRI arcpy module

import os, sys, arcpy
# arcpy.env.overwriteOutput = True

#temp variables
# outFGB = r"C:\_auto\outputs\test.gdb"
# inLine = outFGB + "\\seg_final"

# calculate bankful width
def bfw_calc(inLine, outFGB):
	arcpy.AddMessage("Calculating bankful width...")
	arcpy.MakeFeatureLayer_management(inLine, "inLine_bfw_lyr")
	arcpy.AddField_management("inLine_bfw_lyr", "bfw_m", "DOUBLE")
	# PRISM precipitation values are in millimeters, so convert to 
#	bfwOut = arcpy.CalculateField_management("inLine_bfw_lyr", "bfw_m", 
#									"""math.exp(-1.73229) * ((!fa! * 10.0 * 10.0 / 1000000.0)**0.39659) * (((!ppt!/!fa!)/10)**0.45304)""", "PYTHON_9.3")
	bfwOut = arcpy.CalculateField_management("inLine_bfw_lyr", "bfw_m", 
									"""math.exp(-1.73229) * ((!fa! * 10.0 * 10.0 / 1000000.0)**0.39659) * ((!ppt!)**0.45304)""", "PYTHON_9.3")
	return bfwOut

# calculate bankful depth
def bfd_calc(inLine, outFGB):
	arcpy.AddMessage("Calculating bankful depth...")
	arcpy.MakeFeatureLayer_management(inLine, "inLine_bfd_lyr")
	arcpy.AddField_management("inLine_bfd_lyr", "bfd_m", "DOUBLE")
	bfdOut = arcpy.CalculateField_management("inLine_bfd_lyr", "bfd_m", """0.145 * !bfw_m!**0.607""", "PYTHON_9.3")
	return bfdOut

#calculate shear stress
def ss_calc(inLine, outFGB):
	arcpy.AddMessage("Calculating shear stress...")
	arcpy.MakeFeatureLayer_management(inLine, "inLine_ss_lyr")
	arcpy.AddField_management("inLine_ss_lyr", "ss", "DOUBLE")
	ssOut = arcpy.CalculateField_management("inLine_ss_lyr", "ss", """9.81 * 999 * !Slope! * (!bfw_m! * !bfd_m!) / (!bfw_m! + 2 * !bfd_m!)""", "PYTHON_9.3")
	return ssOut

#calculate floodplain depth
def fpd_calc(inLine, outFGB):
	arcpy.AddMessage("Calculating floodplain depth...")
	arcpy.MakeFeatureLayer_management(inLine, "inLine_fpd_lyr")
	arcpy.AddField_management("inLine_fpd_lyr", "fpd_m", "DOUBLE")
	fpdOut = arcpy.CalculateField_management("inLine_fpd_lyr", "fpd_m", """!bfd_m! * 3""", "PYTHON_9.3")
	return fpdOut