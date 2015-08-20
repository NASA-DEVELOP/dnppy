library(chron)
library(RColorBrewer)
library(lattice)
library(ncdf)
library(ncdf4)

getwd()
workdir <- "C:/Users/jessica.sutton/Documents/DATA/Precipitation/1984_2014/1984"
setwd(workdir)

ncname <- "PERSIANN-CDR_v01r01_19840101_c20140523"
ncfname <- paste(ncname, ".nc", sep = "")

# open a NetCDF file
ncin <- nc_open(ncfname) ### open the netcdf 
### look at the metadata to determine the extent, cell size, resolution, etc. 
data <- ncvar_get( ncin, 'precipitation') ## get the precipitation layer out of the netcdf


library(raster)

# create a new (not projected) RasterLayer with cellnumbers as values
e <- extent(0, 360, -60,60) ### define the extent of the data <- this is the original extent, not the cropped version
r <- raster(data) ### change the precipitation layer into a raster

r4 <- setExtent(r, e) ### set the extent of the raster
print(r4) ### check to make sure the extent, number of cells, etc. is all correct
final <- crop(r4, extent(r4,81,320,501,860))### crop the raster for the location you want <-- based on the cell locations not lat and long


projection(final) <- "+proj=utm +datum=WGS84" ### assign the raster a projection


writeRaster(final,"C:/Users/jessica.sutton/Documents/DATA/test.tif",overwrite=TRUE) ### save the raster as a tif 



