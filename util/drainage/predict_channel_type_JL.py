# file name:	predict_channel_type.py
# description:	This python script is a component of the NCC Tool, which is an automated workflow for segmenting
#				a stream network and populating those segments with a suite of parameters, and then predicting
#               and assigning natural channel classification types according to the methodology outlined by Beechie
#               and Imaki (2014). The NCC Tool was developed in support of the ISEMP RiverStyles project, with the
#				ultimate goal of providing information to be used in salmonid habitat modeling.  Much of the code
#               in this script was derived from code originally written by Hiroo Imaki.
# author:		Jesse Langdon
# dependencies: ESRI arcpy module

import arcpy

def main(input_strm, outFGB):

    # Add a new field to store the classification types
    arcpy.AddField_management()

    # Classification threshold settings
    threshold_bfw = 8 # Divides mountain and floodplain channel types
    threshold_confinement = 3.8 # Divides confined and unconfined channel types
    threshold_slope = -1.62 # Divides braided channel from other types
    threshold_r_stress = 15 # Relative shear stress threshold, splits straight from other types
    threshold_a = -0.61 # Slope threshold to divide meandering and island-braided
    threshold_b = 1.15 # Intercept threshold to divide meandering and island-braided

    # determine intermediate values for classification calculations
    # build lists of values for each parameter

    # Step 1 - split reaches into 'small' and 'large' types
    small_strm = arcpy.SelectLayerByAttribute_management(input_strm, "NEW_SELECTION", '"bfw_m" <' + str(threshold_bfw))
    large_strm = arcpy.SelectLayerByAttribute_management(input_strm, "NEW_SELECTION", '"!bfw_m!" <' + str(threshold_bfw))
    # Step 2 - use data access (da) update cursors for classification of 'small' stream reaches
    cursor_sm = arcpy.da.UpdateCursor(small_strm, ["Slope", "bfw_m", "bfd_m", "ss", "fpd_m", "channel_type"])
    for row in cursor_sm:
        if row[0] < 0.015:
            row[5] = "pool_riffle"
        elif (row[0] >= 0.015) and (row[0] < 0.03):
            row[5] = "plane_bed"
        elif (row[0] <= 0.03) and (row[0] <0.065):
            row[5] = "step_pool"
        elif row[0] >= 0.065:
            row[5] = "cascade"
        cursor_sm.updateRow(row)
        del row
    del small_strm

    # Step 3 - for 'large' streams, split reaches into 'confined' and 'unconfined'
    conf_strm = arcpy.SelectLayerByAttribute_management(large_strm, "NEW_SELECTION",
                                                            '("!fpw_m!"/"!bfw_m!") <' + str(threshold_confinement))
    arcpy.CalculateField_management(conf_strm, "channel_type", "confined", "PYTHON_9.3")
    unconf_strm = arcpy.SelectLayerByAttribute_management(large_strm, "NEW_SELECTION",
                                                              '("!fpw_m!"/"!bfw_m!") >' + str(threshold_confinement))
    del conf_strm
    # Step 4 - for unconfined reaches, classify into 4 floodplain stream stypes
    # Step 4a - split based on shear stress
    unconf_strm_straight = arcpy.SelectLayerByAttribute_management(unconf_strm, "NEW_SELECTION", '"!ss!" >' + str(threshold_r_stress))
    unconf_strm_curved = arcpy.SelectLayerByAttribute_management(unconf_strm, "NEW_SELECTION", '"!ss!" <' + str(threshold_r_stress))
    arcpy.CalculateField_management(unconf_strm_straight, "channel_type", "straight", "PYTHON_9.3")
    del unconf_strm_straight
    # Step 4b - classify reaches with slope greater than 0.4 as 'braided'
    unconf_strm_braid = arcpy.SelectLayerByAttribute_management(unconf_strm_curved, "NEW_SELECTION", '(log10("!slope!")) >' + str(threshold_slope))
    unconf_strm_other = arcpy.SelectLayerByAttribute_management(unconf_strm_curved, "NEW_SELECTION", '(log10("!slope!")) <' + str(threshold_slope))
    arcpy.CalculateField_management(unconf_strm_braid, "channel_type", "braided", "PYTHON_9.3")
    del unconf_strm_braid
    # Step 4c - split remaining reaches into 'island-braided' and 'meandering'
    unconf_strm_isl_braid = arcpy.SelectLayerByAttribute_management(unconf_strm_other, "NEW_SELECTION",
                                                                    '(log10("!slope!")) > (' + str(threshold_a) + '* (log10("!ppt!") + ' + str(threshold_b))
    unconf_strm_meander = arcpy.SelectLayerByAttribute_management(unconf_strm_other, "NEW_SELECTION",
                                                                  '(log10("!slope!")) <= (' + str(threshold_a) + '* (log10("!ppt!") + ' + str(threshold_b))
    arcpy.CalculateField_management(unconf_strm_isl_braid, "channel_type", "island_braided", "PYTHON_9.3")
    arcpy.CalculateField_management(unconf_strm_meander, "channel_type", "meandering", "PYTHON_9.3")
    del unconf_strm_isl_braid
    del unconf_strm_meander






