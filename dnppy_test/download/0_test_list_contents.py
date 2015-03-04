from dnppy.download import list_contents


print("===== Testing 'dnppy.download.list_contents module =====")


# test ftp
ftp_add      = "some address"
names, paths = list_contents.ftp(ftp_add)
print zip(filenames, filepaths)

# test http
http_add = "some address"
files    = list_contents.http(http_add)
print files
