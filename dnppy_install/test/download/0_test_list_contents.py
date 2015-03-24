from dnppy.download import list_contents

# read in the test_dir filepath
from dnppy import test
test.setup()
test_dir = test.test_dir()

# test ftp
ftp_add     = "trmmopen.gsfc.nasa.gov"
name_paths  = list_contents.ftp(ftp_add, 'anonymous')

for name_path in name_paths: print name_path

# test http
http_add = "http://e4ftl01.cr.usgs.gov"
files    = list_contents.http(http_add)
print files

