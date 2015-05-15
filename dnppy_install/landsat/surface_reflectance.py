
#standard imports
from .grab_meta import *
from dnppy import solar
import arcpy
import datetime
import numpy as np
import math
import os
arcpy.CheckOutExtension("Spatial")


__all__=['surf_reflectance']      # planned development


def surface_reflectance(meta_path, toa_folder, dem_path, dew_point, outdir, kt = 1):

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
        if "\\" in meta_path:
                name = meta_path.split("\\")[-1]
                tilename = name.replace("_MTL.txt", "")
        elif "//" in meta_path:
                name = meta_path.split("//")[-1]
                tilename = name.replace("_MTL.txt", "")

        #construct the list of TOA reflectance band tiffs and populate it based on the above definitions
        toa_list = []
        out_list = []
        i = 1
        for file in os.listdir(toa_folder):
                if ("TOA_Ref" in file) and (".tif" in file) and (".tif." not in file):
                        if "LC8" in meta_path:
                                tile = "{0}_B{1}".format(tilename, i)
                                if tile in file and str(i) in OLI_bands:
                                        path = "{0}\\{1}".format(toa_folder, file)
                                        out_file = file.replace("TOA", "Surf")
                                        toa_list.append(path)
                                        out_list.append(out_file)
                                i = i + 1
                        elif ("LE7" in file) or ("LT5" in file) or ("LT4"in file):
                                tile = "{0}_B{1}".format(tilename, j)
                                if path in file and str(i) in TM_ETM_bands:
                                        path = "{0}\\{1}".format(toa_folder, file)
                                        out_file = file.replace("TOA", "Surf")
                                        toa_list.append(file)
                                        out_list.append(out_file)
                                i = i + 1
        
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
        ap = 101.3 * ((( 293 - (0.0065 * DEM))/293 ) ** 5.26)
        
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
        for i in xrange(6):
                pr = pr_constants[i] * (1 - entisr_bands[i])
                pr_bands.append(pr)

        #At Surface Reflectance
        for i in xrange(6):
                asr_path = "{0}\\{1}".format(outdir, out_list[i])
                refl_surf = (toa_list[i] - pr_bands[i])/(entisr_bands[i] * entsrrs_bands[i])
                refl_surf.save(asr_path)

        return