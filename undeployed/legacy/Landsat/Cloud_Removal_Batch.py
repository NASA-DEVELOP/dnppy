####################################################
############# Landsat Cloud Removal ################
# In order to run this script, you need to have    #
# all the Landsat bands in one folder, along with  #
# the MTL.txt files and the gdal_calc.py file.     #
####################################################


import os
import shutil

#Variables for this tool include three folder paths:
#folder_path is the name and location of the folder with all the Landsat data
folder_path= r"C:\Users\sbarron\Desktop\Test"
os.chdir(folder_path)

#fmask_path is the name and location of a folder containing only the Fmask application.
#This folder can, and is recommended to be, located in the folder_path folder.
fmask_path= folder_path + "/" + "Fmask"

#Output_folder is the name and location of the folder where your cloud free Landsat
#images will be placed. This folder should be empty except for the gdal_calc.py file.
Output_folder= folder_path + "/" + "Output"

#The first for loop will look through the folder_path, take one Landsat scene, move it into
#the fmask_path, run the Fmask tool, and then export that scene, which contains the
#locations of clouds, to the output folder.
for raster in os.listdir(folder_path):
    try:
        #Locate the MTL.txt file for the Landsat scene.
        if len(raster) > 27 and len(raster)< 30 and raster[-7:]== "MTL.txt":
            #Landsat 8
            if raster[2]== "8":
                os.chdir(folder_path)
                #Move the scene to the fmask folder.
                shutil.move(raster, fmask_path)
                shutil.move(raster[0:-7] + "B1.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B2.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B3.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B4.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B5.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B6.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B7.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B8.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B9.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B10.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B11.TIF", fmask_path)
                shutil.move(raster[0:-7] + "BQA.TIF", fmask_path)
                print "Rasters moved to Fmask folder."
                os.chdir(fmask_path)
                #Run the Fmask tool.
                os.system(fmask_path + "/" + 'Fmask')
                #Move the scene to the Output_folder.
                shutil.move(raster, Output_folder)
                shutil.move(raster[0:-7] + "B1.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B2.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B3.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B4.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B5.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B6.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B7.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B8.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B9.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B10.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B11.TIF", Output_folder)
                shutil.move(raster[0:-7] + "BQA.TIF", Output_folder)
                shutil.move(raster[0:-7] + "MTLFmask", Output_folder)
                shutil.move(raster[0:-7] + "MTLFmask.hdr", Output_folder)
                print "MTLFmask files generated, moved to Output Folder."
                #Convert the MTLFmask files to TIFFs by changing the name.
                os.chdir(Output_folder)
                os.rename(raster[0:-7] + "MTLFmask", raster[0:-7] + "MTLFmask" + ".TIF")
                
            #Landsat 7    
            elif raster[2]== "7":
                os.chdir(folder_path)
                #Move the scene to the fmask folder.
                shutil.move(raster, fmask_path)
                shutil.move(raster[0:-7] + "B1.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B2.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B3.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B4.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B5.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B6_VCID_1.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B6_VCID_2.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B7.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B8.TIF", fmask_path)
                print "Rasters moved to Fmask folder."
                os.chdir(fmask_path)
                #Run the Fmask tool.
                os.system(fmask_path + "/" + 'Fmask')
                #Move the scene to the Output_folder.
                shutil.move(raster, Output_folder)
                shutil.move(raster[0:-7] + "B1.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B2.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B3.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B4.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B5.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B6_VCID_1.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B6_VCID_2.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B7.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B8.TIF", Output_folder)
                shutil.move(raster[0:-7] + "MTLFmask", Output_folder)
                shutil.move(raster[0:-7] + "MTLFmask.hdr", Output_folder)
                print "MTLFmask files generated, moved to Output Folder."
                #Convert the MTLFmask files to TIFFs by changing the name.
                os.chdir(Output_folder)
                os.rename(raster[0:-7] + "MTLFmask", raster[0:-7] + "MTLFmask" + ".TIF")
                
            #Landsat 5
            elif raster[2]== "5":
                os.chdir(folder_path)
                #Move the scene to the fmask folder.
                shutil.move(raster, fmask_path)
                shutil.move(raster[0:-7] + "B1.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B2.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B3.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B4.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B5.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B6.TIF", fmask_path)
                shutil.move(raster[0:-7] + "B7.TIF", fmask_path)
                print "Rasters moved to Fmask folder."
                os.chdir(fmask_path)
                #Run the Fmask tool.
                os.system(fmask_path + "/" + 'Fmask')
                #Move the scene to the Output_folder.
                shutil.move(raster, Output_folder)
                shutil.move(raster[0:-7] + "B1.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B2.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B3.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B4.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B5.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B6.TIF", Output_folder)
                shutil.move(raster[0:-7] + "B7.TIF", Output_folder)
                shutil.move(raster[0:-7] + "MTLFmask", Output_folder)
                shutil.move(raster[0:-7] + "MTLFmask.hdr", Output_folder)
                print "MTLFmask files generated, moved to Output Folder."
                #Convert the MTLFmask files to TIFFs by changing the name.
                os.chdir(Output_folder)
                os.rename(raster[0:-7] + "MTLFmask", raster[0:-7] + "MTLFmask" + ".TIF")
                
    except:
        print "Well that didn't work..."
        
print "MTLFmask files converted to TIFFs."

#The second for loop will go through the Output_folder and, using the gdal_calc.py, remove
#pixels that contain clouds (the MTLFmask.tif files) from the original Landsat scene.
os.chdir(Output_folder)
for files in os.listdir(Output_folder):
    try:
        if len(files) > 27 and len(files)< 32:
            #Prevents the script from try to remove clouds from the BQA and MTL.txt files.
            if files[23] != "Q" and files[23] != "T":
                print files
                files2= files[:22] + "MTLFmask.TIF"
                outfile= "Delete_" + files
                outfile2= "CF_" + files
                #The first equation looks at the MTLFmask file, determines if a pixel has clouds (Value<2),
                #and if it doesn't, takes that pixel value from the original Landsat image. It also adds one
                #to the original landsat image, so that any pixel with a value of zero (which is assigned as
                #a default in areas with clouds) can be changed to NoData.
                os.system('gdal_calc.py -A%s -B%s --outfile=%s --calc="((A+1)*(B<2))" --type="Float32" --NoDataValue=0' % (files,files2,outfile))
                #The second equation subtracts one from the output of the first equation, to remove that
                #temporary addition of one and return the image to its original values.
                os.system('gdal_calc.py -A%s --outfile=%s --calc="A-1" --type="Float32"' % (outfile,outfile2))
                os.remove(outfile)
    except:
        print "Well that didn't work..."

print "Process Completed, check " + str(Output_folder) + " for the generated cloud free (CF) files."  
