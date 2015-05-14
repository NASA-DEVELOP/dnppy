from dnppy import download
import os

# read in the test_dir filepath
from dnppy import test
test_dir = test.test_dir()

# test downloading from filelist
filelist_txt    = "reverb_filelist.txt"
output_dir      = os.path.join(test_dir, "reverb_download")

print("Testing download on May 2013 MODIS MYD11A1 data!")
download.download_filelist(filelist_txt, 'hdf', output_dir)

