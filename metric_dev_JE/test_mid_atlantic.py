from metric import metric

# an arc tool something like this needs to be created.

workspace =     r"C:\Users\jwely\Desktop\trubshoot\version_JE\Test_NC_alfalfa"

landsat_files =[r"C:\Users\jwely\Desktop\trubshoot\test_inputs_NC\input_landsat\final_clip2.tif",
                r"C:\Users\jwely\Desktop\trubshoot\test_inputs_NC\input_landsat\final_clip3.tif",
                r"C:\Users\jwely\Desktop\trubshoot\test_inputs_NC\input_landsat\final_clip4.tif",
                r"C:\Users\jwely\Desktop\trubshoot\test_inputs_NC\input_landsat\final_clip5.tif",
                r"C:\Users\jwely\Desktop\trubshoot\test_inputs_NC\input_landsat\final_clip6.tif",
                r"C:\Users\jwely\Desktop\trubshoot\test_inputs_NC\input_landsat\final_clip7.tif",
                r"C:\Users\jwely\Desktop\trubshoot\test_inputs_NC\input_landsat\final_clip10.tif",
                r"C:\Users\jwely\Desktop\trubshoot\test_inputs_NC\input_landsat\final_clip11.tif"]

landsat_meta    = r"C:\Users\jwely\Desktop\trubshoot\test_inputs_NC\input_landsat\NC_metadata.txt"
dem_path        = r"C:\Users\jwely\Desktop\trubshoot\test_inputs_NC\input_dem\grdn37ww78_13_UTM_Subset.tif"
hot_shp_path    = r"C:\Users\jwely\Desktop\trubshoot\test_inputs_NC\input_ref_pixels\nonirrigated_hot.shp"
cold_shp_path   = r"C:\Users\jwely\Desktop\trubshoot\test_inputs_NC\input_ref_pixels\irrigated_cool.shp"
weather_path    = r"C:\Users\jwely\Desktop\trubshoot\test_inputs_NC\input_weather\6564006671082dat.txt"    

testflag        = "ALL"         # valid inputs are "ALL", "LIMITED", "ET-ONLY" (ET-ONLY cuts processing time by about 25% compared to ALL)
recalc          = True          # recalc = True will prevent all 

crop            = "alfalfa"     # reference crop. possible values are "grass" , "alfalfa" 
timezone        = -5.0          #  -5 or -4 for Eeastern time depending on daylight savings

metric.main(workspace, landsat_files, landsat_meta, dem_path, hot_shp_path, cold_shp_path, weather_path, testflag, recalc, crop, timezone)


 


        
