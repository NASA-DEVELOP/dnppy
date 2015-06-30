library(chron)
library(RColorBrewer)
library(lattice)
library(ncdf)
library(ncdf4)
library(raster)

## For multiple files
## Input directory

files <- list.files(path="C:/Users/jessica.sutton/Documents/DATA/test_data/", pattern="*.nc", full.names=T, recursive=T)### recursive = T <-- loops through all subfolders 

## Output directory
dir.output <- 'C:/Users/jessica.sutton/Documents/DATA/Rasters/FullRasters/test/' ### change as needed to give output location
 
## For simplicity, I use "i" as the file name, you could change any name you want, "substr" is a good function to do this.
for (i in 1:length(files)) {
    a <- nc_open(files[i]) # load file
    p <- ncvar_get(nc=a,'precipitation') ### select the parameter you want to make into raster files
    e <- extent(0,360,-60,60) ### choose the extent based on the netcdf file info 
    r <- raster(p)
    re <- setExtent(r,e) ### set the extent to the raster
    projection(re) <- "+proj=longlat +datum=WGS84 +ellps=WGS84 +towgs84=0,0,0"
    
    writeRaster(re, paste(dir.output, basename(files[i]), sep = ''), format = 'GTiff', overwrite = T) ###the basename allows the file to be named the same as the original
}
 
## END

gc()


  final <- crop(re, extent(re,81,320,501,860)) ### crop down to the specific area you want ### add this to the above script if you want a cropped/clipped version