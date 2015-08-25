These sets of scripts access and organize weather station data.

***convert_dat_to)excel***

The Python Convert Dat to Excel is used to convert the station weather data
(.dat format) to .xlsx or .csv (commented out) for smoother geocoding in 
arcmap. Specify the folder in the command line arguement for this process.
It does not delete the .dat file. 

***rename_modis***

The Python Rename MODID Files is exactly that. The script takes the long name
of the downloaded MODIS imagery file and leaves with only the YEAR-MONTH-DAY.

***ecmwf_reanalysis***

This is a MATLAB script useful for geoprocessing files in arcmap, as some functions cannot operate with filenames over a certain character amount. 

% The following script plots ECMWF Reanalysis data for a range of days
% Once the appropriate data is loaded, modify the d1,d2, ind1, ind2 and
% varuse variables to created the desired plot 

European Center for Medium Range Weather Forecast Reanalysis Data Plotting

1. Load data, available in NETCDF files from http://apps.ecmwf.int/datasets/
It should be clipped (squeezed) to the following grid for best plotting solution. It
 will have to be converted within Matlab prior to loading.

latmaxq = 50;
latminq = 20;
lonmaxq = -140;
lonminq = -40;

2. Projection can be modified, although Mercator makes the contours smoother.

3. Adjust 'd1' and 'd2' to the date applicable to the data loaded. It is best to 
   load data one year at a time rather than for an entire decade.

4. The rest of the plotting script is mostly modifying the mapping format; Plotting 
   Range, contour color/thickness, and title.

***parse_script***

The parseScript takes a text file downloaded from the mesowest station_metadata
call and takes out the unwanted characters leaving only the station ids. The output file is used to append the stids to the end of a URL ran through MESOs API that can call specific wx attributes from list of stations (stids). 

***pull_mesostation***

This script downloads weather station data from the MesoWest API.