from metric_model_code import metric

# an arc tool something like this needs to be created.

workspace =     r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev_2\Models\Mid_Atlantic_test2"

landsat_files =[r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\Final_MidAtl\final_clip2.tif",
                r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\Final_MidAtl\final_clip3.tif",
                r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\Final_MidAtl\final_clip4.tif",
                r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\Final_MidAtl\final_clip5.tif",
                r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\Final_MidAtl\final_clip6.tif",
                r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\Final_MidAtl\final_clip7.tif",
                r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\Final_MidAtl\final_clip10.tif",
                r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\Final_MidAtl\final_clip11.tif"]

landsat_meta    = r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\Final_MidAtl\NC_metadata.txt"
dem_path        = r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\DEM_NC_Subset\grdn37ww78_13_UTM_Subset.tif"
hot_shp_path    = r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\Final_MidAtl\nonirrigated_hot.shp"
cold_shp_path   = r"C:\Users\ksparrow\Desktop\eclipse\workspace\metric_dev\Models\Mid_Atlantic_orig\Final_MidAtl\irrigated_cool.shp"
testflag        = "ALL"
recalc          = True

crop            = "alfalfa"     # reference crop. possible values are "grass" , "alfalfa" 
timezone        = -4.0          #  -5 EST w/ DST

metric.main(workspace, landsat_files, landsat_meta, dem_path, hot_shp_path, cold_shp_path, testflag, recalc, crop, timezone)


 


        
