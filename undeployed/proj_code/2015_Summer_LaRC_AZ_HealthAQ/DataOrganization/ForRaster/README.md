All of these files were used to download, extract, clip, and separate the MODIS images used for analysis. These are python scripts using dnppy and arcpy. There are files for both Terra and Aqua satellites that follow the same set of directions, just with different input parameters.

Use:
1.use the "download_modis" file to access MODIS hdf files from the LPDAAC ftp server. This specifically downloads set months for every year rather than every month in each year. "download_terra" does the same thing for Terra data specifically. These use dnppy.
2. Use "extract_modis" to convert the Aqua downloaded files into tif files. This also uses dnppy.
3. Use "clip_modis" to clip the tif file to the study area using a shapefile. This uses dnppy and arcpy.
4. Use "modis_by_dates" to delete all MODIS files that are not located in a csv list of good dates. Good dates represent the files we want, where a max temperature on a day is above 104F and those dates were found using a separate script on downloaded weather data. This removes both day and night files with dates not in the csv list.

The resulting tif files are then used by scripts in the Analysis folder. 

