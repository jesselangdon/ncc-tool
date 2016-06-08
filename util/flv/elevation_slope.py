# -*- coding: utf-8 -*-kc
'''
Created on 21 fev. 2013
Last revision on 01 Jan. 2015

@author: Clement Roux

@contact: clement.roux@ens-lyon.fr
          CNRS - UMR5600 Environnement Ville Societe
          15 Parvis René Descartes, BP 7000, 69342 Lyon Cedex 07, France
         
@note: For each use of the FluvialCorridor toolbox leading to a publication, report, presentation or any other
       document, please refer the following article :
       Roux, C., Alber, A., Bertrand, M., Vaudor, L., Piegay, H., submitted. "FluvialCorridor": A new ArcGIS 
       package for multiscale riverscape exploration. Geomorphology
       
@summary: ElevationAndSlope is an open-source python and arcPy code.
          This script provides a characterization of linear UGO, DGO or AGO-scale databases with a set of topologic 
          metrics. From a DEM, five metrics are extracted : the upstream, downstream and mean elevations, the
          slope and the 3D slope. The slope is directly calculated as the ratio between the difference of elevation
          and the euclidean distance from up to downstream. The 3D slope is the ratio between the difference 
          of elevation and the river course length from up to downstream. 
          
'''
# This code was slightly revised by Jesse Langdon, 1/30/2015.

# Import of required libraries
import arcpy
from arcpy import env
from arcpy.sa import *
import flv_UpToDateShapeLengthField as UPD_SL

def elev_slope(inFC, DEM, Output):
  # creation of the output with the new fields
  arcpy.AddMessage("Creating output with new fields...") 

  Out = arcpy.CopyFeatures_management(inFC, "in_memory\\OutTemp")
  arcpy.AddField_management(Out, "Z_Up", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
  arcpy.AddField_management(Out, "Z_Down", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
  UPD_SL.UpToDateShapeLengthField(Out)

  arcpy.AddMessage("Converting input line into points and adding surface information...") 
  Pts = arcpy.FeatureVerticesToPoints_management(Out, "in_memory\\Pts", "BOTH_ENDS")
  arcpy.AddXY_management(Pts)

  # extraction and calculation of the topologic metrics
  arcpy.AddSurfaceInformation_3d(Out, DEM, "Z_MEAN", "BILINEAR")
  arcpy.AddSurfaceInformation_3d(Pts, DEM, "Z", "BILINEAR")
  arcpy.AddField_management(Out, "Slope", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
  arcpy.AddField_management(Out, "Slope3D", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

  arcpy.AddMessage("Calculating metrics...") 
  rows1 = arcpy.UpdateCursor(Out)
  rows2 = arcpy.SearchCursor(Pts)
  rows3 = arcpy.SearchCursor(Pts)
  line2 = rows2.next()
  line3 = rows3.next()
  line3 = rows3.next()

  for line1 in rows1 :
      line1.Z_Up = line2.Z
      line1.Z_Down = line3.Z
      
      try:
        line1.Slope = (line1.Z_Up - line1.Z_Down) / (((line3.POINT_X-line2.POINT_X)**2 + (line3.POINT_Y-line2.POINT_Y)**2)**0.5)
      except Exception as e:
        print e
        pass
      line1.Slope3D = (line1.Z_Up - line1.Z_Down) / line1.Shape_Length
      rows1.updateRow(line1)
      
      line2 = rows2.next()
      line2 = rows2.next()
      line3 = rows3.next()
      line3 = rows3.next()

  arcpy.CopyFeatures_management(Out, Output)

  # removing of the residual fields
  arcpy.AddMessage("Removing the residual fields...")
  fieldnamesfromFC = [f.name for f in arcpy.ListFields(Output)]
  fieldnamestoFC = [f.name for f in arcpy.ListFields(inFC)]
  for field in fieldnamesfromFC :
      if field not in fieldnamestoFC and field != "Z_Up" and field != "Z_Down" and field != "Z_Mean" and field != "Slope" and field != "Slope3D" :
          try :
              arcpy.DeleteField_management(Output, str(field))
          except :
              continue

  arcpy.AddMessage("Deleting temporary files...")
  arcpy.Delete_management(Pts)
  arcpy.Delete_management(Out)
  return Output