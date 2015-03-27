

__all__=['ndvi_8',                  # complete
         'ndvi_457']                # complete



def ndvi_8(B5, B4, outdir = False):
    """
    calculates a normalized difference vegetation index on Landsat 8 OLI data.

    To be performed on raw or processed Landsat 8 OLI data.

    Inputs:
      B5          The full filepath to the band 5 tiff file, the OLI NIR band
      B4          The full filepath to the band 4 tiff file, the OLI Visible Red band
      outdir      Output directory to save NDVI tifs
    """

    Red = Float(B4)
    NIR = Float(B5)

    L8_NDVI = (NIR - Red)/(NIR + Red)

    band_path   = B4.replace("_B4","")        
    outname     = core.create_outname(outdir, band_path, "NDVI", "tif")
    
    L8_NDVI.save(outname)
        
    print("saved ndvi_8 at {0}".format(outname))
        


def ndvi_457(B4, B3, outdir = False):
    """
    calculates a normalized difference vegetation index on Landsat 4/5/7 TM/ETM+ data.

    To be performed on raw or processed Landsat 4/5/7/ TM/ETM+ data.

    Inputs:
      B4          The full filepath to the band 4 tiff file, the TM/ETM+ NIR band
      B3          The full filepath to the band 3 tiff file, the TM/ETM+ Visible Red band
      outdir      Output directory to save NDVI tifs
    """
   
    Red = Float(B3)
    NIR = Float(B4)

    L457_NDVI = (NIR - Red)/(NIR + Red)

    band_path   = B3.replace("_B3","")        
    outname     = core.create_outname(outdir, band_path, "NDVI", "tif")
    
    L457_NDVI.save(outname)
        
    print("saved ndvi_457 at {0}".format(outname))
