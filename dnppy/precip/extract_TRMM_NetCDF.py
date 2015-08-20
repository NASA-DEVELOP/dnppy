__author__ = ["jwely"]
__all__ = ["extract_TRMM_NetCDF"]

# dnppy imports
from dnppy import core

# arcpy imports
import arcpy
arcpy.env.overwriteOutput = True


def extract_TRMM_NetCDF(filelist, outdir):

    """
     Function converts NetCDFs to tiffs. Designed to work with TRMM data downloaded
     from GLOVIS

     inputs:
       filelist    list of '.nc' files to convert to tiffs.
       outdir      directory to which tif files should be saved

    returns an output filelist of local filepaths of extracted data.
    """

    # Set up initial parameters.
    arcpy.env.workspace = outdir
    filelist = core.enf_list(filelist)
    output_filelist = []

    # convert every file in the list "filelist"
    for infile in filelist:
        
        # use arcpy module to make raster layer from netcdf
        arcpy.MakeNetCDFRasterLayer_md(infile, "r", "longitude", "latitude", "r", "", "", "BY_VALUE")
        outname = core.create_outname(outdir, infile, "e", "tif")
        arcpy.CopyRaster_management("r", outname, "", "", "", "NONE", "NONE", "")
        output_filelist.append(outname)
        print('Converted netCDF file ' + outname + ' to Raster')

    return output_filelist


if __name__ == "__main__":
    afile = ""
    outdir = ""
    extract_TRMM_NetCDF(afile, outdir)
