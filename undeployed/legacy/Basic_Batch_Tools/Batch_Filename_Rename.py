#---------------------------------
#Name: String Replace
#Purpose: Rename filenames (i.e. remove special characters)
#Notes: Text that must be changed are those in all Caps.
    #AAA = file type extension (i.e ".tif")
    #BBB = characters to be replaced
    #CCC = new characters to replace BBB
#Created: 02/24/2014
#---------------------------------

arcpy.env.workspace = "INPUT FILE PATH TO DATA FOLDER HERE"
arcpy.env.overwriteOutput = True
Files = arcpy.ListFiles("*.AAA")

for filename in Files:
    if 'BBB' in filename:
        newfilename = string.replace(filename, 'BBB', 'CCC')
        print "Renaming", filename, "to", newfilename, "..."
        os.rename(filename, newfilename)
        

