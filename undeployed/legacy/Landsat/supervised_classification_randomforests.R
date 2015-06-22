### ##########################################################################################
### Script for classification of satellite data - Myanmar workshop June 2013
### Dr. Ned Norning, Dr. Martin Wegmann
### www.remote-sensing-biodiversity.org
##############################################################################################

##############################################################################################
###	DOCUMENTATION
#####################################################################################
# The script reads a Shapefile holding the samples (defined by: attName).

# Raster image that contains environmental variables (continuous, categorical) (defined by: inImage). 

# For each sample the data values for that pixel are determied and these data are used to run 
# the model. 
#####################################################################################

###########################
###						###
###	Set variables				###
###						###
###########################

#-----------------------------------------------------------------------------------------------
# within the CIP pool install.packages() need to be done prior the library() function
# the following command is just a new defined command by you which checks if the package is installed and if not, it installs the package automatically
loadandinstall <- function(mypkg) {if (!is.element(mypkg, installed.packages()[,1])){install.packages(mypkg)}; library(mypkg, character.only=TRUE)  }

loadandinstall("maptools")
loadandinstall("sp")
loadandinstall("randomForest")
loadandinstall("raster")
loadandinstall("rgdal")
loadandinstall("mgcv")


#-----------------------------------------------------------------------------------------------

####### Start Classification ########


###########################
###				###
###	Set variables	###
###				###
###########################

# install QGIS, load the satellite data and define a cropping area and training data within this region
# think about a validation set

#  set main folder
#_____________________________________________________________________________

workingdir <- ("C:/Users/cdisla/Desktop/Rstuff")

setwd(workingdir)

#### path to the shape training data using the relative path
shapefile <- 'Training_Sites_2013-2013-07-11/Training Sites 2013/TrainingSites2013.shp'


### Number of samples per land cover class - number up to you and depending on study area size
numsamps <- 2500

### Name of the attribute that holds the integer land cover type identifyer (very important to consider when doing the training data sets)
attName <- 'TypeNum'

### Name and path of the output GeoTiff image - just a variable for later usage
outImage <- 'Results/ActualFinalFolder/Class2013Final.tif'

#################
#### settings set - finished ###
#################

# import data - several choices:
# import the whole stack of bands
#satImage <- brick("crop_p224r63_all_bands.tif")


# in case you have just one file with various bands:

#there should be a way to loop this and stack/brick at the same time...
rasterdem <- raster(paste(workingdir, "/2000_Image/dem_mask.tif", sep=""))
plot(rasterdem)
raster2 <- raster(paste(workingdir,"/Landsat_8_Geotiff-2013-07-11/Landsat 8 Geotiff/l84_16_13b2.tif", sep=""))
raster3 <- raster(paste(workingdir,"/Landsat_8_Geotiff-2013-07-11/Landsat 8 Geotiff/l84_16_13b3.tif", sep=""))
raster4 <- raster(paste(workingdir,"/Landsat_8_Geotiff-2013-07-11/Landsat 8 Geotiff/l84_16_13b4.tif", sep=""))
raster5 <- raster(paste(workingdir,"/Landsat_8_Geotiff-2013-07-11/Landsat 8 Geotiff/l84_16_13b5.tif", sep=""))
raster6 <- raster(paste(workingdir,"/Landsat_8_Geotiff-2013-07-11/Landsat 8 Geotiff/l84_16_13b6.tif", sep=""))
raster7 <- raster(paste(workingdir,"/Landsat_8_Geotiff-2013-07-11/Landsat 8 Geotiff/l84_16_13b7.tif", sep=""))
raster4_6 <- raster(paste(workingdir,"/Landsat_8_Geotiff-2013-07-11/Landsat 8 Geotiff/l8_4_6.tif", sep=""))
raster6_5 <- raster(paste(workingdir,"/Landsat_8_Geotiff-2013-07-11/Landsat 8 Geotiff/l8_6_5.tif", sep=""))
raster7_6 <- raster(paste(workingdir,"/Landsat_8_Geotiff-2013-07-11/Landsat 8 Geotiff/l8_7_6.tif", sep=""))


raster.list<-c(rasterdem, raster2, raster3, raster4, raster5, raster6, raster7, raster4_6, raster6_5, raster7_6)
i<-1
for (i in 1:length(raster.list))
{
  raster.i<-raster.list[i]
  print(raster.i)
}
#for faster processing and to explain code, I will jsut use the first 4 bands. For full RF, use all bands
#When trying to stack all 7 bands, the last band has a slightly different extent, this will be an issue when stacking
#also, your bands lack a coordinate system, you need to define the projection. 

# or if you just want to import some bands in a big stack of bands:
# raster1 <- raster("raster_data/crop_p224p63.tif",band=1)
# raster2 <- raster("raster_data/crop_p224p63.tif",band=2)
# raster3 <- raster("raster_data/crop_p224p63.tif",band=3)
# raster4 <- raster("raster_data/crop_p224p63.tif",band=4)
# otherwise skip the "band=.." part and just add the correct file name for each band.

# stack the bands together (layer stacking)
# if more than 4 raster are imported, add another file name
satImage <- stack(rasterdem, raster2, raster3, raster4, raster5, raster6, raster7, raster4_6, raster6_5, raster7_6)


#-----------------------------------------------------------------------------------------------

###################################
###				###
###	Start processing	###
###				###
###################################


################
#
# Read the Shapefile
#using the link defined above

vec <- readShapePoly(paste(workingdir, "/",shapefile, sep="")) 
plot(vec)
vec #also not projected 

###############
#
# Create vector of unique land cover attribute values

allAtt <- slot(vec, "data")
tabAtt <-table(allAtt[[attName]])
uniqueAtt <-as.numeric(names(tabAtt))

### Create input data from a Shapefile with training data and the image ("generation points for Regions of Interest")
for (x in 1:length(uniqueAtt)) {
  # Create a mask for cover type 1 (an integer attribute)
  class_data <- vec[vec[[attName]]==uniqueAtt[x],]
  # Get random points for the class
  classpts <- spsample(class_data, type="random", n=numsamps) 
  #Append data for all but the first run
  if (x == 1) { 
    xy <- classpts
  } else {
    xy <- rbind(xy, classpts)		 
  }
}

head(xy)
head(vec)
vec$TypeNum
vec[,3]
head(allAtt)
allAtt[1,3]
allAtt[1,]
allAtt[,3]
# # # for testing if you want
# summary(xy)
# plot(xy)
# image(raster1)
# plot(xy, add=TRUE)



### plot the random generated points on one of the rasters - for visual checking only
pdf("C:/Users/cdisla/Desktop/Rstuff/randompoints2000.pdf")
plot(satImage,2)
points(xy)
dev.off()
# !!! resulting image NOT in the plot window but in a pdf outside your R session - see settings on top about location of results

##############
#
# Get class number for each sample point

temp <- overlay(vec, xy)
summary(temp)

#############
#
# Create the responce input for randomForest

response <- factor(temp[[attName]]) 
response
#############

trainvals <- cbind(response, extract(satImage, xy)) #what is behind certain values (1-water and the value for each band)

# check for consistency
head(trainvals)

#############
#
# Run Random Forest
# think about different methods (SVM, BRT, GLM, ...)
# compare the results


print("Starting to calculate random forest object") 
?randomForest
randfor <- randomForest(as.factor(response) ~. , #glm, car, gam, any statistics you want..
		    data=trainvals, 		#a tree gives all breaking point (how to split table) ##library(tree), cmd: #tree()
		    na.action=na.omit, 		# if pixels with no values exist
		    confusion=T,		# first info how good your classification performed
        ntree=2500)
                        

randfor #to look at results (confusion matrix: 100 good, all class A points are within class A)

# ### further settings which can be defined - see: randomForest manual
# model_1 <-randomForest(x=input,
#                        ntree=Treesize, 
#                        nodesize=Nodesize,  
#                        importance=TRUE, 
#                        proximity=FALSE, 
#                        mtry=Feature_OOB, 
#                       confusion=TRUE,
#                        do.trace=TRUE,
#                        norm.votes=TRUE)
# 
# ### other method could be applied and compared like glm(), gam(), SVM, tree etc.

#############
#
# Start predictions

print("Starting predictions")
predict(satImage, randfor, filename=paste(workingdir,"/",outImage, sep=""), progress='text', format='GTiff', datatype='INT1U', type='response', overwrite=TRUE)


####### End of Classification ########
