
#standard imports
import os
import arcpy
if arcpy.CheckExtension('Spatial')=='Available':
    arcpy.CheckOutExtension('Spatial')
    arcpy.env.overwriteOutput = True

__all__=['ndvi_8',                  # complete
         'ndvi_457']                # complete


def ndvi_8(Band5, Band4, outdir = None):
    """
    Simple calculator of Normalized difference vegetation index on some Landsat 8 OLI
    data. Output file will have same name as inputs with "NDVI" in place of "B5", so
    inputs of files "LC80140342014347LGN00_B5.tif" and "LC80140342014347LGN00_B4.tif"
    will generate a file named "LC80140342014347LGN00_NDVI.tif"

    :param Band5:   The full filepath to the band 5 tiff file, the OLI NIR band
    :param Band4:   The full filepath to the band 4 tiff file, the OLI Visible Red band
    :param outdir:  directory to store output "NDVI" tiff

    :return ndvi8:  Name of output file created by this function
    """

    Band4 = os.path.abspath(Band4)
    Band5 = os.path.abspath(Band5)

    #Set the input bands to float
    Red = arcpy.sa.Float(Band4)
    NIR = arcpy.sa.Float(Band5)

    #Calculate the NDVI
    L8_NDVI = (NIR - Red)/(NIR + Red)

    # find output directory
    tail = os.path.basename(Band5).replace("_B5", "_NDVI")
    if outdir is None:
        head = os.path.dirname(Band5)
        ndvi8 = os.path.join(head, tail)
    else:
        ndvi8 = os.path.join(outdir, tail)

    L8_NDVI.save(ndvi8)
        
    print("saved ndvi_8 at {0}".format(ndvi8))
    return ndvi8


def ndvi_457(Band4, Band3, outdir = None):
    """
    Simple calculator of Normalized difference vegetation index on some Landsat 4/5/7 TM/ETM+
    data. Output file will have same name as inputs with "NDVI" in place of "B5", so
    inputs of files "LC70140342014347LGN00_B4.tif" and "LC70140342014347LGN00_B3.tif"
    will generate a file named "LC70140342014347LGN00_NDVI.tif"

    :param Band4:   The full filepath to the band 4 tiff file, the TM/ETM+ NIR band
    :param Band3:   The full filepath to the band 3 tiff file, the TM/ETM+ Visible Red band
    :param outdir:  directory to store output "NDVI" tiff

    :return ndvi457:  Name of output file created by this function
    """

    Band3 = os.path.abspath(Band3)
    Band4 = os.path.abspath(Band4)

    #Set the input bands to float
    Red = arcpy.sa.Float(Band3)
    NIR = arcpy.sa.Float(Band4)

    #Calculate the NDVI
    L457_NDVI = (NIR - Red)/(NIR + Red)

    # find output directory
    tail = os.path.basename(Band3).replace("_B3", "_NDVI")
    if outdir is None:
        head = os.path.dirname(Band3)
        ndvi457 = os.path.join(head, tail)
    else:
        ndvi457 = os.path.join(outdir, tail)

    L457_NDVI.save(ndvi457)

    print("saved ndvi_457 at {0}".format(ndvi457))
    return ndvi457
