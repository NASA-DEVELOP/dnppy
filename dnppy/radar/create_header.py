
__author__ = ["Daniel Jensen, danieljohnjensen@gmail.com",
                "Scott Baron"]

import os
import re

def create_header(folder):
    """
    Builds a header file for the input UAVSAR .grd file,
    allowing the data to be read as a raster dataset.

    Inputs:
        folder:   the folder containing the UAVSAR .grd and .ann files
    """

    os.chdir(folder)

    #Empty lists to put information that will be recalled later.
    Lines_list = list()
    Samples_list = list()
    Latitude_list = list()
    Longitude_list = list()
    Files_list = list()

    #Step 1: Look through folder and determine how many different flights there are by looking at the HDR files.
    for files in os.listdir(folder):
        if files [-4:] == ".grd":
            newfile = open(files[0:-4] + ".hdr", 'w')
            newfile.write("""ENVI
description = {
  DESCFIELD }
samples = NSAMP
lines   = NLINE
bands   = 1
header offset = 0
file type = ENVI Standard
data type = DATTYPE
interleave = bsq
sensor type = Unknown
byte order = 0
map info = {Geographic Lat/Lon, 1.5000, 1.5000, LONGITUDE, LATITUDE, 5.5560000000e-05, 5.5560000000e-05, WGS-84, units=Degrees}
coordinate system string = {GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]}
wavelength units = Unknown""")
            newfile.close()
            if files[0:18] not in Files_list:
                Files_list.append(files[0:18])

    #Variables used to recall indexed values.
    var1 = 0

    #Step 2: Look through the folder and locate the annotation file(s). These can be in either .txt or .ann file types.
    for files in os.listdir(folder):
        if Files_list[var1] and files[-4:] == ".txt" or files[-4:] == ".ann":
            #Step 3: Once located, find the info we are interested in and append it to the appropriate list. We limit the variables to <=1 so that they only return two values (one for each polarization of
            searchfile = open(files, "r")
            for line in searchfile:
                if "GRD Lines" in line:
                    Lines = line[55:60]
                    if Lines not in Lines_list:
                        Lines_list.append(Lines)

                elif "GRD Samples" in line:
                    Samples = line[55:60]
                    if Samples not in Samples_list:
                        Samples_list.append(Samples)

                elif "grd_mag.row_addr" in line:
                    Latitude = line.split()[3]
                    print Latitude
                    if Latitude not in Latitude_list:
                        Latitude_list.append(Latitude)

                elif "grd_mag.col_addr" in line:
                    Longitude = line.split()[3]
                    print Longitude
                    if Longitude not in Longitude_list:
                        Longitude_list.append(Longitude)
            #Reset the variables to zero for each different flight date.
            var1 = 0
            searchfile.close()

    var6 = 0
    #Step 3: Open HDR file and replace data.
    for files in os.listdir(folder):
        if files[-4:] == ".hdr":
            with open(files, "r") as sources:
                lines = sources.readlines()
            with open(files, "w") as sources:
                for line in lines:
                    if "data type = DATTYPE" in line:
                        sources.write(re.sub(line[12:19], "4", line))
                    elif "DESCFIELD" in line:
                        sources.write(re.sub(line[2:11], "File Imported into ENVI.", line))
                    elif "lines" in line:
                        sources.write(re.sub(line[10:15], Lines_list[Files_list.index(files[0:18])], line))
                    elif "samples" in line:
                        sources.write(re.sub(line[10:15], Samples_list[Files_list.index(files[0:18])], line))
                    elif "map info" in line:
                        sources.write(re.sub(line[47:66], Longitude_list[Files_list.index(files[0:18])] + ", " + Latitude_list[Files_list.index(files[0:18])], line))
                    else:
                        sources.write(re.sub(line, line, line))

    print "Finished creating hdrs"
    return