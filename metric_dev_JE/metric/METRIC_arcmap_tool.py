import arcpy
from arcpy import env
import math
import os
from metric_model_code import metric
arcpy.env.overwriteOutput= True

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Develop METRIC Toolbox"
        self.alias = "Develop METRIC Toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [METRIC_Run]

class METRIC_Run(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "METRIC_Run"
        self.description = "Tool description goes here"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        landsat_meta = arcpy.Parameter(
            displayName="Landsat 8, Metadata File",
            name="l8_meta",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")
        landsat_meta.filter.list = ['txt']

        landsat_b2 = arcpy.Parameter(
            displayName="Landsat 8, Band 2",
            name= "l8_b2",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")

        landsat_b3 = arcpy.Parameter(
            displayName="Landsat 8, Band 3",
            name= "l8_b3",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")

        landsat_b4 = arcpy.Parameter(
            displayName="Landsat 8, Band 4",
            name= "l8_b4",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")

        landsat_b5 = arcpy.Parameter(
            displayName="Landsat 8, Band 5",
            name= "l8_b5",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")

        landsat_b6 = arcpy.Parameter(
            displayName="Landsat 8, Band 6",
            name= "l8_b6",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")

        landsat_b7 = arcpy.Parameter(
            displayName="Landsat 8, Band 7",
            name= "l8_b7",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")

        landsat_b10 = arcpy.Parameter(
            displayName="Landsat 8, Band 10",
            name= "l8_b10",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")

        landsat_b11 = arcpy.Parameter(
            displayName="Landsat 8, Band 11",
            name= "l8_b11",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")

        dem_raster= arcpy.Parameter(
            displayName="DEM TIF File",
            name= "raster",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")

        wx_dir= arcpy.Parameter(
            displayName="Weather Folder",
            name="wx_dir",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")
        
        crop= arcpy.Parameter(
            displayName="Reference crop type",
            name="crop",
            datatype="GPString",
            parameterType="Required",
            direction="Input")        

        timezone= arcpy.Parameter(
            displayName="Time zone offset in decimal hours",
            name="timezone",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")        

##        out_dir= arcpy.Parameter(
##            displayName="Output Folder",
##            name="output_dir",
##            datatype="DEFolder",
##            parameterType="Required",
##            direction="Input")

        return [landsat_meta, landsat_b2, landsat_b3, landsat_b4, landsat_b5,
                landsat_b6, landsat_b7, landsat_b10, landsat_b11, landsat_bqa,
                dem_raster, wx_dir]

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
        """The source code of the tool."""


    dem_path        = 
    hot_shp_path    = 
    cold_shp_path   = 
    testflag        = 
    recalc          = True



'''
        landsat_meta= parameters[0].valueAsText
        landsat_b2= parameters[1].valueAsText
        landsat_b3= parameters[2].valueAsText
        landsat_b4= parameters[3].valueAsText
        landsat_b5= parameters[4].valueAsText
        landsat_b6= parameters[5].valueAsText
        landsat_b7= parameters[6].valueAsText
        landsat_b10= parameters[7].valueAsText
        landsat_b11= parameters[8].valueAsText
        landsat_bqa= parameters[9].valueAsText
     
        landsat_files =[r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\Final_MidAtl\final_clip2.tif",
                r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\Final_MidAtl\final_clip3.tif",
                r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\Final_MidAtl\final_clip4.tif",
                r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\Final_MidAtl\final_clip5.tif",
                r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\Final_MidAtl\final_clip6.tif",
                r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\Final_MidAtl\final_clip7.tif",
                r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\Final_MidAtl\final_clip10.tif",
                r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\Final_MidAtl\final_clip11.tif"]
'''
        landsat_meta    = parameters[0].valueAsText
        
        landsat_files= [(parameters[1].valueAsText), (parameters[2].valueAsText), (parameters[3].valueAsText), 
                        (parameters[4].valueAsText), (parameters[5].valueAsText), (parameters[6].valueAsText), 
                        (parameters[7].valueAsText), (parameters[8].valueAsText)]

        
        #dem_raster= parameters[10].valueAsText
        #dem_path        = r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\DEM_NC_Subset\grdn37ww78_13_UTM_Subset.tif"
        dem_path = parameters[9].valueAsText
        wx_dir= parameters[10].valueAsText

        crop= parameters[11].valueAsText # reference crop. possible values are "grass" , "alfalfa" 
        timezone= parameters[12].valueAsText


        metric.main(workspace, landsat_files, landsat_meta, dem_path, hot_shp_path,
                     cold_shp_path, testflag, recalc, crop, timezone)
