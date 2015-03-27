

__all__=['cloud_mask_8',            # complete
         'cloud_mask_457']          # planned development (to include slc-off band gaps)



def cloud_mask_8(band_nums, BQA_path, outdir = False):
    """
    Removal of cloud-covered pixels in raw Landsat 8 bands using the BQA file included.

    To be performed on raw Landsat 8 level 1 data.

    Inputs:
      band_nums   A list of desired band numbers such as [3 4 5]
      BQA_path    The full filepath to the BQA file for the Landsat 8 dataset
      outdir      Output directory to save cloudless band tifs and the cloud mask
    """

    #enforce the input band numbers as a list of strings
    band_nums = core.Enforce_List(band_nums)
    band_nums = map(str, band_nums)

    #define the range of values in the BQA file to be reclassified as cloud (0) or not cloud (1)
    outReclass = Reclassify(BQA_path, "Value", RemapRange([[50000,65000,0],[28670,32000,0],[2,28669,1],[32001,49999,1],[1,1,"NoData"]]))

    #set the name and save the binary cloud mask tiff file
    Mask_name = BQA_path.replace("_BQA", "")  
    CloudMask_path = core.create_outname(outdir, Mask_name, "Mask", "tif")   
    outReclass.save(CloudMask_path)

    #for each band listed in band_nums, apply the Con tool to erase cloud pixels and save each band as a new tiff
    for band_num in band_nums:      
      band_path = BQA_path.replace("BQA.tif", "B{0}.tif".format(band_num))            
      outname   = core.create_outname(outdir, band_path, "NoClds", "tif")
      outCon    = Con(outReclass, band_path, "", "VALUE = 1")
      outCon.save(outname)                 

    return



def cloud_mask_457(band_nums, BQA_path, outdir = False):
    """
    Removal of cloud-covered pixels in raw Landsat 4, 5, and 7 bands.

    To be performed on raw Landsat 8 level 1 data.

    Inputs:
      band_nums   A list of desired band numbers such as [3 4 5]
      BQA_path    The full filepath to the BQA file for the Landsat 8 dataset
      outdir      Output directory to save cloudless band tifs and the cloud mask
    """
    pass
