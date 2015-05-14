from dnppy import download

# read in the test_dir filepath
from dnppy import test
test.setup()
test_dir = test.test_dir()

# test ftp
ftp_add     = "trmmopen.gsfc.nasa.gov"
name_paths  = download.list_ftp(ftp_add, 'anonymous')

for name_path in name_paths: print name_path

# test http
http_add = "http://e4ftl01.cr.usgs.gov"
files    = download.list_http(http_add)
print files

