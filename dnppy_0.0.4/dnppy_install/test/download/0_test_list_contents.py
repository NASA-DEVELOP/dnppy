from dnppy.download import list_contents

# read in the test_dir filepath
from dnppy import test
test_dir = test.test_dir()

# test ftp
ftp_add      = "some address"
names, paths = list_contents.ftp(ftp_add)
print zip(filenames, filepaths)

# test http
http_add = "some address"
files    = list_contents.http(http_add)
print files
