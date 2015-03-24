
from dnppy import test
test_dir = test.test_dir()

# test raster to numpy on an image
from dnppy.raster import raster

filepath        = r"F:\LaRC_Projects\Spring_2015_North_Carolina_Water\chlExt\A2004001172500.L2_LAC_OC.tif.lyr.tif"
image, metadata = raster.to_numpy(filepath)

