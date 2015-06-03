
#standard imports
from grab_meta import grab_meta
from dnppy import solar
import arcpy
import datetime
import numpy as np
import math
import os
if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckOutExtension("Spatial")
else:
        raise LicenseError


__all__ = ['surface_reflectance']      # complete


def surface_reflectance(meta_path, toa_folder, dem_path, dew_point, outdir = False, kt = 1.0):
        """
        This function will calculate surface reflectance for Landsat 4 TM, 5 TM, 7 ETM+, or 8 OLI data.
        
        *Note this function will calculate surface reflectance for Landsat 4, 5, and 7
         bands 1, 2, 3, 4, 5, and 7 or Landsat 8 bands 2, 3, 4, 5, 6, and 7. All 6 bands should be in the
         toa_folder and have "TOA_Ref" in their filenames as per the landsat.toa_reflectance convention.
         
        *The Landsat 8 Coastal Aerosol band (1) and Cirrus band (9) will not be calculated as they do not
         have a corresponding band in TM or ETM+.

        To be performed on Top-of-Atmosphere Reflectance data processed with the landsat.toa_reflectance_457
        or the landsat.toa_reflectance_8 function.

        Resources:
                DEM:
                -NASA Shuttle Radar Topography Mission (SRTM):
                        http://www2.jpl.nasa.gov/srtm/cbanddataproducts.html
                        *SRTM version 2 has a 30m resolution, but contains some gaps
                -NASA Advanced Spaceborne Thermal Emission and Reflection Radiometer (ASTER)
                 Global Digital Elevation Model (GDEM):
                        http://asterweb.jpl.nasa.gov/gdem.asp
                -USGS National Elevation Dataset (NED):
                        http://nationalmap.gov/elevation.html
                        *downloadable in 30 meter resolution through The National Map Viewer

                Dew Point:
                -NOAA Daily Observational Data: Global Summary of the Day (GSOD) - GIS Data Locator
                        http://gis.ncdc.noaa.gov/map/viewer/#app=clim&cfg=cdo&theme=daily&layers=0001&node=gis
                        *Select a weather station within the Landsat scene's extent, follow the link,
                         and enter the scene's acquisition date. This will output a text file, with
                         dew point under DEWP.
                        *More NOAA climatic data available at https://www.climate.gov/data/maps-and-data
                        
        Inputs:
                meta_path       The full filepath to the metadata file (ending in MTL.txt) for the dataset
                toa_folder      The filepath to the folder containing the TOA_Ref tiffs to be processed
                dem_path        The full filepath to a DEM tif that covers the desired Landsat scene
                                  *Note that the DEM should be resampled to the Landsat bands' resolution (30m)
                                   and pixel alignment. Also ensure there are no gaps in the dataset.
                dew_point       The number (e.g. 57.7) for the dew point at the time and place of scene acquisition
                outdir          Output directory to save converted files. If left False it will save
                                   output files in the toa_folder directory.
                kt              Unitless turbidity coefficient. Default set at 1.0 for clean air.
                                  *Set at 0.5 for extremeley turbid, dusty, or polluted air
        """

        outlist = []

        #define the list of constants for effective narrowband transmissivity for incoming solar radiation 
        constants_enbt1 = [[0.987, -0.00071, 0.000036, 0.0880, 0.0789],
                             [2.319, -0.00016, 0.000105, 0.0437, -1.2697],
                             [0.951, -0.00033, 0.000280, 0.0875, 0.1014],
                             [0.375, -0.00048, 0.005018, 0.1355, 0.6621],
                             [0.234, -0.00101, 0.004336, 0.0560, 0.7757],
                             [0.365, -0.00097, 0.004296, 0.0155, 0.6390]]

        #define the list of constants for effective narrowband transmissivity for shortwave radiation
        #reflected from the surface
        constants_enbt2 = [[0.987, -0.00071, 0.000036, 0.0880, 0.0789],
                             [2.319, -0.00016, 0.000105, 0.0437, -1.2697],
                             [0.951, -0.00033, 0.000280, 0.0875, 0.1014],
                             [0.375, -0.00048, 0.005018, 0.1355, 0.6621],
                             [0.234, -0.00101, 0.004336, 0.0560, 0.7757],
                             [0.365, -0.00097, 0.004296, 0.0155, 0.6390]]

        #enforce the list of band numbers, grab metadata from the MTL file, and define the band numbers needed from each sensor
        meta = grab_meta(meta_path)
        OLI_bands = ['2','3','4','5','6','7']
        TM_ETM_bands = ['1','2','3','4','5','7']

        #define the tile name for the landsat scene based on the metadata file's name

        #Open the metadata text file and read to set the scene's tilename
        f = open(meta_path)
        MText = f.read()

        if "PRODUCT_CREATION_TIME" in MText:
                tilename = getattr(meta, "BAND1_FILE_NAME")
        else:
                tilename = getattr(meta, "LANDSAT_SCENE_ID")

        #construct the list of TOA reflectance band tiffs and populate it based on the above definitions
        toa_list = []
        out_list = []
        n = 0
        for file in os.listdir(toa_folder):
                if ("TOA_Ref" in file) and (".tif" in file) and (".tif." not in file):
                        if "LC8" in meta_path:
                                tile = "{0}_B{1}".format(tilename, OLI_bands[n])
                                if tile in file:
                                        path = "{0}\\{1}".format(toa_folder, file)
                                        out_file = file.replace("TOA", "Surf")
                                        toa_list.append(path)
                                        out_list.append(out_file)
                                        n = n + 1
                                        if n > 5:
                                                break
                        elif ("LE7" in file) or ("LT5" in file) or ("LT4" in file):
                                tile = "{0}_B{1}".format(tilename, TM_ETM_bands[n])
                                if tile in file:
                                        path = "{0}\\{1}".format(toa_folder, file)
                                        out_file = file.replace("TOA", "Surf")
                                        toa_list.append(path)
                                        out_list.append(out_file)
                                        n = n + 1
                                        if n > 5:
                                                break

        #grab the corner lat/lon coordinates to calculate the approximate scene center lat/lon       
        ul_lat = getattr(meta, "CORNER_UL_LAT_PRODUCT")
        ul_lon = getattr(meta, "CORNER_UL_LON_PRODUCT")
        ur_lat = getattr(meta, "CORNER_UR_LAT_PRODUCT")
        ur_lon = getattr(meta, "CORNER_UR_LON_PRODUCT")
        ll_lat = getattr(meta, "CORNER_LL_LAT_PRODUCT")
        ll_lon = getattr(meta, "CORNER_LL_LON_PRODUCT")
        lr_lat = getattr(meta, "CORNER_LR_LAT_PRODUCT")
        lr_lon = getattr(meta, "CORNER_LR_LON_PRODUCT")

        u_lon_avg = np.mean([ul_lon, ur_lon])
        l_lon_avg = np.mean([ll_lon, lr_lon])
        l_lat_avg = np.mean([ul_lat, ll_lat])
        r_lat_avg = np.mean([ur_lat, lr_lat])
        
        center_lat = np.mean([l_lat_avg, r_lat_avg])
        center_lon = np.mean([u_lon_avg, l_lon_avg])

        #construct the datetime object from the date acquired and scene center time attributes      
        date = getattr(meta, "DATE_ACQUIRED")
        dl = date.split("-")
        time = getattr(meta, "SCENE_CENTER_TIME")
        tl = time.split(":")

        dt = datetime.datetime(int(dl[0]), int(dl[1]), int(dl[2]), int(tl[0]), int(tl[1]), int(tl[2][0:2]))

        #use the dnppy.solar module to calculate the solar characteristics at the scene center at the time of acquisition
        sc = solar.solar(center_lat, center_lon, dt, 0)
        sc.compute_all()

        #Cosine of Solar Zenith over horizontal surface
        declination = math.degrees(sc.get_declination())
        hour_angle = math.degrees(sc.get_hour_angle())
        lat = math.degrees(center_lat)

        cth = (math.sin(declination) * math.sin(lat)) + (math.cos(declination) * math.cos(center_lat) * math.cos(hour_angle))

        #Saturation Vapor Pressure
        svp = 0.6108 * math.exp((17.27 * dew_point) / (dew_point + 237.3))

        #Atmospheric Pressure
        DEM = arcpy.sa.Raster(dem_path)
        ap = 101.3 * ((( 293 - (0.0065 * DEM))/ 293) ** 5.26)
        
        #Water in Atmosphere
        wia = (0.14 * svp * ap) + 2.1

        #Effective Narrowband Transmittance for incoming solar radiation
        entisr_bands = []
        for i in xrange(6):
                c1 = constants_enbt1[i][0]
                c2 = constants_enbt1[i][1]
                c3 = constants_enbt1[i][2]
                c4 = constants_enbt1[i][3]
                c5 = constants_enbt1[i][4]
                enbt1 = c1 * ((arcpy.sa.Exp((c2 * ap)/(kt * cth))) - (((c3 * wia) + c4)/cth)) + c5
                entisr_bands.append(enbt1)

        #Effective Narrowband Transmittance for shortwave radiation reflected from surface
        entsrrs_bands = []
        
        #cos_n always 1 for sensor pointing straight nadir
        cos_n = 1
        
        for i in xrange(6):
                c1 = constants_enbt2[i][0]
                c2 = constants_enbt2[i][1]
                c3 = constants_enbt2[i][2]
                c4 = constants_enbt2[i][3]
                c5 = constants_enbt2[i][4]
                enbt2 = c1 * ((arcpy.sa.Exp((c2 * ap)/(kt * cos_n))) - (((c3 * wia) + c4))) + c5
                entsrrs_bands.append(enbt2)

        #Per Band Path Reflectance
        pr_bands = []
        pr_constants = [0.254, 0.149, 0.147, 0.311, 0.103, 0.036]
        for j in xrange(6):
                pr = pr_constants[j] * (1 - entisr_bands[j])
                pr_bands.append(pr)

        #Calculate and save At-Surface Reflectance band tiffs
        for k in xrange(6):
                if outdir:
                        asr_path = "{0}\\{1}".format(outdir, out_list[k])
                else:
                        asr_path = "{0}\\{1}".format(toa_folder, out_list[k])
                refl_surf = (toa_list[k] - pr_bands[k])/(entisr_bands[k] * entsrrs_bands[k])
                refl_surf.save(asr_path)
                outlist.append(asr_path)

        return outlist