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

        self.label = "DEVELOP_METRIC" 
        self.alias = "DEVELOP_METRIC"

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

        
        param15 = arcpy.Parameter(
            displayName =   "Workspace to store intermediates and outputs (full path to a NEW directory)",
            name =          "workspace",
            datatype =      "GPString",
            parameterType = "Required",
            direction =     "Input")
        
        param0 = arcpy.Parameter(
            displayName =   "Landsat 8 Metadata filepath",
            name =          "l8_meta",
            datatype =      "DEFile",
            parameterType = "Required",
            direction =     "Input")
        param0.filter.list = ['txt']

        param1 = arcpy.Parameter(
            displayName =   "Landsat 8 Band 2 filepath (tif)",
            name =          "l8_b2",
            datatype =      "GPRasterLayer",
            parameterType = "Required",
            direction =     "Input",
            category =      "Landsat bands")

        param2 = arcpy.Parameter(
            displayName =   "Landsat 8 Band 3 filepath (tif)",
            name =          "l8_b3",
            datatype =      "GPRasterLayer",
            parameterType = "Required",
            direction =     "Input",
            category =      "Landsat bands")

        param3 = arcpy.Parameter(
            displayName =   "Landsat 8 Band 4 filepath (tif)",
            name =          "l8_b4",
            datatype =      "GPRasterLayer",
            parameterType = "Required",
            direction =     "Input",
            category =      "Landsat bands")

        param4 = arcpy.Parameter(
            displayName =   "Landsat 8 Band 5 filepath (tif)",
            name =          "l8_b5",
            datatype =      "GPRasterLayer",
            parameterType = "Required",
            direction =     "Input",
            category =      "Landsat bands")

        param5 = arcpy.Parameter(
            displayName =   "Landsat 8 Band 6 filepath (tif)",
            name =          "l8_b6",
            datatype =      "GPRasterLayer",
            parameterType = "Required",
            direction =     "Input",
            category =      "Landsat bands")

        param6 = arcpy.Parameter(
            displayName =   "Landsat 8 Band 7 filepath (tif)",
            name =          "l8_b7",
            datatype =      "GPRasterLayer",
            parameterType = "Required",
            direction =     "Input",
            category =      "Landsat bands")

        param7 = arcpy.Parameter(
            displayName =   "Landsat 8 Band 10 filepath (tif)",
            name =          "l8_b10",
            datatype =      "GPRasterLayer",
            parameterType = "Required",
            direction =     "Input",
            category =      "Landsat bands")

        param8 = arcpy.Parameter(
            displayName =   "Landsat 8 Band 11 filepath (tif)",
            name =          "l8_b11",
            datatype =      "GPRasterLayer",
            parameterType = "Required",
            direction =     "Input",
            category =      "Landsat bands")

        param9 = arcpy.Parameter(
            displayName =   "Digital Elevation Model raster (tif)",
            name =          "DEM",
            datatype =      "GPRasterLayer",
            parameterType = "Required",
            direction =     "Input")

        param10 = arcpy.Parameter(
            displayName =   "shapefile of hot pixels (non-irrigated)",
            name =          "hot_pix",
            datatype =      "DEShapefile",
            parameterType = "Required",
            direction =     "Input")
        
        param11 = arcpy.Parameter(
            displayName =   "shapefile of cold pixels (irrigated)",
            name =          "cold_pix",
            datatype =      "DEShapefile",
            parameterType = "Required",
            direction =     "Input")

        param12 = arcpy.Parameter(
            displayName =   "Weather data text file (txt)",
            name =          "wx_file",
            datatype =      "DEFile",
            parameterType = "Required",
            direction =     "Input")
        param12.filter.list = ['txt']
        
        param13 = arcpy.Parameter(
            displayName =   "Reference crop type",
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

        param16 = arcpy.Parameter(
            displayName =   "manual elevation of weather station (in meters)",
            name =          "wx_elevation",
            datatype =      "GPDouble",
            parameterType = "Optional",
            direction =     "Input")
            
        param17 = arcpy.Parameter(
            displayName =   "manual roughness length (zom) estimate at weather station location ",
            name =          "wx_zom",
            datatype =      "GPDouble",
            parameterType = "Optional",
            direction =     "Input")
            
        param18 = arcpy.Parameter(
            displayName =   "manual LE_cold calibration factor Usually 1.05",
            name =          "LE_cold_cal_factor",
            datatype =      "GPDouble",
            parameterType = "Optional",
            direction =     "Input")
        
        param19 = arcpy.Parameter(
            displayName =   "Mountainous terrain",
            name =          "mounts",
            datatype =      "GPBoolean",
            parameterType = "Optional",
            direction =     "Input")
        
        param20 = arcpy.Parameter(
            displayName =   "Save_flag (decides which variables to save to hard disk)",
            name =          "saveflag",
            datatype =      "GPString",
            parameterType = "Required",
            direction =     "Input")
        param20.filter.list = ["ALL", "LIMITED", "ET-ONLY"]

        param21 = arcpy.Parameter(
            displayName =   "Force Recalculation",
            name =          "recalc",
            datatype =      "GPBoolean",
            parameterType = "Required",
            direction =     "Input")
        
        params = [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9,
                  param10, param11, param12, param13, param14, param15, param16, param17, param18,
                  param19, param20, param21]
        
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

        try:    wx_elev = float(parameters[16].value)
        except: wx_elev = None
        try:    wx_zom  = float(parameters[17].value)
        except: wx_zom  = None
        try:    LE_ref  = float(parameters[18].value)
        except: LE_ref  = None
        try:    mounts  = bool(parameters[19].value)
        except: mounts  = None

        testflag        = str(parameters[20].value)
        recalc          = bool(parameters[21].value)

        # print parameters to screen
        for param in parameters:
            message = "{0} : {1}".format(str(param.name).ljust(12," "), param.value)
            print(message)
            arcpy.AddMessage(message)

        metric_py.run(metric_workspace, landsat_files, landsat_meta, dem_path,
                    hot_shp_path, cold_shp_path, weather_path, testflag,
                    recalc, crop, timezone, wx_elev, wx_zom, LE_ref, mounts)


# Manually run the metric model here
if __name__ == "__main__":

    tbx = Toolbox()
    tool = METRIC_run()

    workspace =     r"C:\Users\jwely\Desktop\metric_trub\model_run_NC_manual"

    landsat_files =[r"C:\Users\Jeff\Desktop\metric_testing\LC80440282015144LGN00\LC80440282015144LGN00_B2.TIF",
                    r"C:\Users\Jeff\Desktop\metric_testing\LC80440282015144LGN00\LC80440282015144LGN00_B3.TIF",
                    r"C:\Users\Jeff\Desktop\metric_testing\LC80440282015144LGN00\LC80440282015144LGN00_B4.TIF",
                    r"C:\Users\Jeff\Desktop\metric_testing\LC80440282015144LGN00\LC80440282015144LGN00_B5.TIF",
                    r"C:\Users\Jeff\Desktop\metric_testing\LC80440282015144LGN00\LC80440282015144LGN00_B6.TIF",
                    r"C:\Users\Jeff\Desktop\metric_testing\LC80440282015144LGN00\LC80440282015144LGN00_B7.TIF",
                    r"C:\Users\Jeff\Desktop\metric_testing\LC80440282015144LGN00\LC80440282015144LGN00_B10.TIF",
                    r"C:\Users\Jeff\Desktop\metric_testing\LC80440282015144LGN00\LC80440282015144LGN00_B11.TIF.tif"]

    landsat_meta    = r"C:\Users\Jeff\Desktop\metric_testing\LC80440282015144LGN00\LC80440282015144LGN00_MTL.txt"
    dem_path        = r"C:\Users\Jeff\Desktop\metric_testing\SRTM_mosaic.tif"
    hot_shp_path    = r"C:\Users\jwely\Desktop\metric_trub\test_inputs_NC\input_ref_pixels\nonirrigated_hot.shp"
    cold_shp_path   = r"C:\Users\jwely\Desktop\metric_trub\test_inputs_NC\input_ref_pixels\irrigated_cool.shp"''
    weather_path    = r"C:\Users\jwely\Desktop\metric_trub\test_inputs_NC\input_weather\6564006671082dat.txt"

    testflag        = "ALL"         # valid inputs are "ALL", "LIMITED", "ET-ONLY" (ET-ONLY 25% less time than ALL)
    recalc          = True          # recalc = True will prevent all

    crop            = "alfalfa"     # reference crop. possible values are "grass" , "alfalfa"
    timezone        = -5.0          #  -5 or -4 for Eeastern time depending on daylight savings

    wx_elev         = 1.000         # elevation of the weather station
    wx_zom          = 0.010         # estimated zom at weather station (temporary)
    LE_cold_cal_fac = 1.050         # LE calibration factor, should probably always be 1.05
    mountains       = True         # set true for mountainous regions

    metric_py.run(workspace, landsat_files, landsat_meta, dem_path,
                    hot_shp_path, cold_shp_path, weather_path, testflag,
                    recalc, crop, timezone, wx_elev, wx_zom, LE_cold_cal_fac, mountains)
