# arcpy imports
import arcpy
from arcpy import env
arcpy.env.overwriteOutput = True

import metric_py


__author__ = ["Kent Sparrow",
              "Jamie Vanderheiden",
              "Nathan Quian",
              "Jeffry Ely, jeff.ely.08@gmail.com"]


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""

        self.label = "Develop METRIC Toolbox"
        self.alias = "Develop METRIC Toolbox"

        self.tools = [METRIC_run]
        return

class METRIC_run(object):
    
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "METRIC_Run"
        self.description = "This is the METRIC model"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName =   "Landsat 8 Metadata File",
            name =          "l8_meta",
            datatype =      "DEFile",
            parameterType = "Required",
            direction =     "Input")
        param0.filter.list = ['txt']

        param1 = arcpy.Parameter(
            displayName =   "Landsat 8 Band 2",
            name =          "l8_b2",
            datatype =      "GPRasterLayer",
            parameterType = "Required",
            direction =     "Input")

        param2 = arcpy.Parameter(
            displayName =   "Landsat 8 Band 3",
            name =          "l8_b3",
            datatype =      "GPRasterLayer",
            parameterType = "Required",
            direction =     "Input")

        param3 = arcpy.Parameter(
            displayName =   "Landsat 8 Band 4",
            name =          "l8_b4",
            datatype =      "GPRasterLayer",
            parameterType = "Required",
            direction =     "Input")

        param4 = arcpy.Parameter(
            displayName =   "Landsat 8 Band 5",
            name =          "l8_b5",
            datatype =      "GPRasterLayer",
            parameterType = "Required",
            direction =     "Input")

        param5 = arcpy.Parameter(
            displayName =   "Landsat 8 Band 6",
            name =          "l8_b6",
            datatype =      "GPRasterLayer",
            parameterType = "Required",
            direction =     "Input")

        param6 = arcpy.Parameter(
            displayName =   "Landsat 8 Band 7",
            name =          "l8_b7",
            datatype =      "GPRasterLayer",
            parameterType = "Required",
            direction =     "Input")

        param7 = arcpy.Parameter(
            displayName =   "Landsat 8 Band 10",
            name =          "l8_b10",
            datatype =      "GPRasterLayer",
            parameterType = "Required",
            direction =     "Input")

        param8 = arcpy.Parameter(
            displayName =   "Landsat 8 Band 11",
            name =          "l8_b11",
            datatype =      "GPRasterLayer",
            parameterType = "Required",
            direction =     "Input")

        param9 = arcpy.Parameter(
            displayName =   "DEM TIF File",
            name =          "DEM",
            datatype =      "GPRasterLayer",
            parameterType = "Required",
            direction =     "Input")

        param10 = arcpy.Parameter(
            displayName =   "shapefile of hot pixels",
            name =          "hot_pix",
            datatype =      "DEShapefile",
            parameterType = "Required",
            direction =     "Input")
        
        param11 = arcpy.Parameter(
            displayName =   "shapefile of cold pixels",
            name =          "cold_pix",
            datatype =      "DEShapefile",
            parameterType = "Required",
            direction =     "Input")

        param12 = arcpy.Parameter(
            displayName =   "Weather data text file",
            name =          "wx_file",
            datatype =      "DEFile",
            parameterType = "Required",
            direction =     "Input")
        param12.filter.list = ['txt']
        
        param13 = arcpy.Parameter(
            displayName =   "Reference crop type 'alfalfa' or 'grass'",
            name =          "crop",
            datatype =      "GPString",
            parameterType = "Required",
            direction =     "Input")
        param13.filter.list = ["alfalfa", "grass"]

        param14 = arcpy.Parameter(
            displayName =   "Time zone offset in decimal hours from GMT",
            name =          "timezone",
            datatype =      "GPDouble",
            parameterType = "Required",
            direction =     "Input")        

        param15 = arcpy.Parameter(
            displayName =   "Created Workspace to store outputs",
            name =          "workspace",
            datatype =      "GPString",
            parameterType = "Required",
            direction =     "Input")

        params = [param0, param1, param2, param3, param4, param5, param6, param7, param8,
                   param9, param10, param11, param12, param13, param14, param15]
        
        return params
    
    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True
    

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return
    

    def updateMessages(self, parameters): 
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return
    

    def execute(self, parameters, messages):
        """ Run tool sourcecode by calling metric.py """

        
        metric_workspace = str(parameters[15].value)
        metrci_workspace = metric_workspace.replace("\\","/")

        landsat_files   = [str(parameters[1].value),
                           str(parameters[2].value),
                           str(parameters[3].value),
                           str(parameters[4].value),
                           str(parameters[5].value),
                           str(parameters[6].value),
                           str(parameters[7].value),
                           str(parameters[8].value)]

        landsat_meta    = str(parameters[0].value)
        dem_path        = str(parameters[9].value)
        hot_shp_path    = str(parameters[10].value)
        cold_shp_path   = str(parameters[11].value)
        weather_path    = str(parameters[12].value)

        crop            = str(parameters[13].value)
        timezone        = float(parameters[14].value)

        testflag        = "ALL"
        recalc          = True

        # print parameters to screen
        for param in parameters:
            message = "{0} : {1}".format(str(param.name).ljust(12," "), param.value)
            print(message)
            arcpy.AddMessage(message)

        metric_py.run(metric_workspace, landsat_files, landsat_meta, dem_path,
                           hot_shp_path, cold_shp_path, weather_path, testflag,
                           recalc, crop, timezone)


# Manually run the metric model here
##if __name__ == "__main__":
##
##    tbx = Toolbox()
##    tool = METRIC_run()
##
##    workspace =     r"C:\Users\jwely\Desktop\metric_trub\Test_NC_man_tbx"
##
##    landsat_files =[r"C:\Users\jwely\Desktop\metric_trub\test_inputs_NC\input_landsat\final_clip2.tif",
##                    r"C:\Users\jwely\Desktop\metric_trub\test_inputs_NC\input_landsat\final_clip3.tif",
##                    r"C:\Users\jwely\Desktop\metric_trub\test_inputs_NC\input_landsat\final_clip4.tif",
##                    r"C:\Users\jwely\Desktop\metric_trub\test_inputs_NC\input_landsat\final_clip5.tif",
##                    r"C:\Users\jwely\Desktop\metric_trub\test_inputs_NC\input_landsat\final_clip6.tif",
##                    r"C:\Users\jwely\Desktop\metric_trub\test_inputs_NC\input_landsat\final_clip7.tif",
##                    r"C:\Users\jwely\Desktop\metric_trub\test_inputs_NC\input_landsat\final_clip10.tif",
##                    r"C:\Users\jwely\Desktop\metric_trub\test_inputs_NC\input_landsat\final_clip11.tif"]
##
##    landsat_meta    = r"C:\Users\jwely\Desktop\metric_trub\test_inputs_NC\input_landsat\NC_metadata.txt"
##    dem_path        = r"C:\Users\jwely\Desktop\metric_trub\test_inputs_NC\input_dem\grdn37ww78_13_UTM_Subset.tif"
##    hot_shp_path    = r"C:\Users\jwely\Desktop\metric_trub\test_inputs_NC\input_ref_pixels\nonirrigated_hot.shp"
##    cold_shp_path   = r"C:\Users\jwely\Desktop\metric_trub\test_inputs_NC\input_ref_pixels\irrigated_cool.shp"
##    weather_path    = r"C:\Users\jwely\Desktop\metric_trub\test_inputs_NC\input_weather\6564006671082dat.txt"    
##
##    testflag        = "ALL"         # valid inputs are "ALL", "LIMITED", "ET-ONLY" (ET-ONLY 25% less time than ALL)
##    recalc          = True          # recalc = True will prevent all 
##
##    crop            = "alfalfa"     # reference crop. possible values are "grass" , "alfalfa" 
##    timezone        = -5.0          #  -5 or -4 for Eeastern time depending on daylight savings
##
##    metric_py.run(workspace, landsat_files, landsat_meta, dem_path,
##                    hot_shp_path, cold_shp_path, weather_path, testflag,
##                    recalc, crop, timezone)
