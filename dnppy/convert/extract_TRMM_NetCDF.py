
# dnppy imports
from dnppy import core

# arcpy imports
import arcpy
if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    arcpy.env.overwriteOutput = True


def TRMM_NetCDF(filelist, outdir):
    """
    Function converts NetCDFs to tiffs. Designed to work with TRMM data
    downloaded from GLOVIS

    :param filelist:            list of '.nc' files to convert to tifs.
    :param outdir:              directory to which tif files should be saved

    :return output_filelist:    list of local filepaths of extracted data.
    """

    # Set up initial parameters.
    arcpy.env.workspace = outdir
    filelist = core.enf_list(filelist)
    output_filelist = []

    # convert every file in the list "filelist"
    for infile in filelist:
        
        # use arcpy module to make raster layer from netcdf
        arcpy.MakeNetCDFRasterLayer_md(infile, "r", "longitude", "latitude", "r", "", "", "BY_VALUE")
        arcpy.CopyRaster_management("r", infile[:-3] + ".tif", "", "", "", "NONE", "NONE", "")
        output_filelist.append(infile[:-3] + ".tif")
        print('Converted netCDF file ' + infile + ' to Raster')

    return output_filelist

if __name__ == "__main__":
    afile = ""
    outdir = ""
    TRMM_NetCDF(afile, outdir)
