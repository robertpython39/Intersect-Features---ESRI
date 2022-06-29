#-------------------------------------------------------------------------------
# Name:        Intersect_Features
# Purpose:     intern
#
# Author:      rnicolescu
#
# Created:     29/06/2022
# Copyright:   (c) rnicolescu 2022
# Licence:     <your license here>
#-------------------------------------------------------------------------------

from arcpy import env
from datetime import datetime
import arcpy
import os
import glob
import shutil
import time

path_in = raw_input("Add path folder for processing:")
print "---> Processing path"
if path_in.endswith("\\"):
    path_in = path_in[0:-1]

main_source = os.path.join(*path_in.split("\\")[0:-1]).replace(":", ":\\") + "\\date_output"
temp_source = os.path.join(*path_in.split("\\")[0:-1]).replace(":", ":\\") + "\\temp_output"

def copy_files():
    global dt_string

    env.workspace = path_in
    env.overwriteOutput = True
    log_file = os.path.join(os.getcwd(), "log.txt")

    print "---> Processing Polygon shapefiles"
    with open(log_file, "a") as logFile:
        for file in glob.glob(path_in + "\\*.shp"):
            fn = os.path.basename(file)
            desc = arcpy.Describe(fn)
            geometryType = desc.shapeType
            if geometryType == 'Polygon':
                print "Processing {}".format(fn)
                arcpy.Copy_management(fn, out_data=temp_source + "\\{}".format(fn))
                logFile.write("{} added to temp folder for processing -- {}\n".format(fn, dt_string))
        logFile.close()

def intersect():
    log_file = os.path.join(os.getcwd(), "log.txt")

    env.workspace = temp_source
    env.overwriteOutput = True
    with open(log_file, "a") as log:
        print "--------------------------------Shapefiles List for processing--------------------------------"
        for shape in arcpy.ListFeatureClasses():
            print shape
        feature1 = raw_input("Select 1st shapefile for intersection:")
        log.write("---> 1st feature selected for checking intersection:{}\n".format(feature1))
        feature2 = raw_input("Select 2nd shapefile for intersection:")
        log.write("---> 2nd feature selected for checking intersection:{}\n".format(feature2))
        in_features = [feature1, feature2]
        result = main_source + "\\intersect_result__{}".format(in_features[0])
        arcpy.Intersect_analysis(in_features, result, join_attributes="ONLY_FID", output_type="INPUT")
        log.write("Created the result in {} -- {}\n".format(result, dt_string))


def date_field():
    env.workspace = main_source
    env.overwriteOutput = True

    for file in glob.glob(main_source + "\\*.shp"):
        fn = os.path.basename(file)
        arcpy.AddField_management(in_table=fn, field_name="Date", field_type="TEXT", field_length=80)
        expression = "!Date!.replace(!Date!,'" + str(time.strftime("%d/%m/%Y")) + "')"
        arcpy.CalculateField_management(file, 'Date', expression, 'PYTHON_9.3')

if __name__ == '__main__':
    globals()

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    with open(os.path.join(os.getcwd(), "log.txt"), "w") as logFile:
        if not os.path.exists(main_source):
            logFile.write("Main folder created succesfully -- {}\n".format(dt_string))
            os.makedirs(main_source)
        if not os.path.exists(temp_source):
            logFile.write("Temp folder created succesfully -- {}\n".format(dt_string))
            os.makedirs(temp_source)

    copy_files()
    intersect()
    date_field()

    shutil.rmtree(temp_source)

