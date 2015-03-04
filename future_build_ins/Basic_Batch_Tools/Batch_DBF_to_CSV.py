#---------------------------------------------
#Name: DBF to CSV Conversion
#Purpose: Convert DBF files into CSV's to enable merging and other processes
#Notes: Utilizes dbfpy module, download here - http://dbfpy.sourceforge.net/
        Fill in text where denoted by all Caps 
#Created: 02/24/2014
#---------------------------------------------
import csv, arcpy, sys, os
from dbfpy import dbf
from arcpy import env
from arcpy.sa import *

###############################################
#Input user parameters
arcpy.env.workspace = "INSERT PATH TO DBF FOLDER"
path = "INSERT PATH TO DBF FOLDER"
###############################################

arcpy.env.overwriteOutput = True

DBFfiles = arcpy.ListFiles("*.dbf")

for filename in DBFfiles:
    print ("Converting DBF file: " + filename + " to CSV")
    inDBFfiles = arcpy.env.workspace + "/" + filename
    fileroot = filename[0:(len(filename)-4)]
    csv_fn = fileroot + ".csv"
    with open(csv_fn,'wb') as csvfile:
        in_db = dbf.Dbf(inDBFfiles)
        out_csv = csv.writer(csvfile)
        names = []
        for field in in_db.header.fields:
            names.append(field.name)
        out_csv.writerow(names)
        for rec in in_db:
            out_csv.writerow(rec.fieldData)
        in_db.close()

print "DONE"
