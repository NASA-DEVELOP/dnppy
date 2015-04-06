import arcpy
from arcpy.arcobjects.arcobjects import Extent
from arcpy.sa.Functions import CreateConstantRaster
from datetime import datetime
import math
import os
import time
import shutil
from dnppy_limited import landsat

import function_bank as DM


        
class MetricModel:


    def __init__(self, working_directory, saveflag, recalc):
        """
        Initializes the new metric model workspace

        for best results, 'working_directory' should be a NEW folder or a previously
        created METRIC model folder.
        """ 

        self.saveflag   = saveflag
        self.recalc     = recalc
        
        # copy the empty metric model template into the newly created working directory
        print("Initializing: Preparing a fresh workspace for METRIC")
        if not os.path.exists(working_directory):
            # get the absolute path of the empty metric model template directory
            live_path = os.path.realpath(__file__)
            head, tail = os.path.split(live_path)
            template_path = os.path.join(head, "Empty_Metric_Model")
            shutil.copytree(template_path, working_directory)
        
        #Set up directories and filepaths
        self.out_dir        = os.path.join(working_directory,"output")
        self.middle_dir     = os.path.join(working_directory,"intermediate_calculations")
        self.ref_pixel_dir  = os.path.join(working_directory,"input_ref_pixels")
        self.landsat_dir    = os.path.join(working_directory,"input_landsat")
        self.weather_dir    = os.path.join(working_directory,"input_weather")
        self.dem_dir        = os.path.join(working_directory,"input_dem")
        self.geodatabase    = os.path.join(working_directory,"default.mdb" )

        arcpy.env.workspace         = self.out_dir
        arcpy.env.scratchWorkspace  = self.geodatabase
        arcpy.env.overwriteOutput   = True

        self.net_radiation          = 0
        self.soil_heat_flux         = 0
        self.sensible_heat_flux     = 0
        self.latent_energy          = 0
        self.evapotranspiration     = 0
        return


    def check_saveflag(self, object_name):
        """
        Central function for managing saving of intermediate data products

        depending on the value of self.saveflag, it will compare the input
        variable "flag_name" to a list of objects for which to save outputs.
        if the input object name is found in that list of variables to save,
        this function returns True, otherwise returns False.
        """

        ETO =      [ "net_rad",     # net radiation from incoming and outgoing
                     "H",           # sensible heat flux convected to the air
                     "LE",          # latent energy
                     "LH_vapor",
                     "ET_inst",     # instantaneous evapotranspiration
                     "ET_inst2",
                     "ET_frac2",
                     "ET_frac",     # reference evapotranspiration fraction
                     "ET_24hr",     # 24 hour ET estimate
                     "ET_24hr2",
                     "LS_ref"]      # landsat reflectance bands

        LIM = ETO+ [ "savi",        # soil adjusted vegetation index
                     "ndvi",        # normalized difference vegetation index
                     "lai"]         # leaf area index
                     
                                        
        ALL = LIM+ [ "slope",       # slope of the dem
                     "aspect",      # aspect of the dem
                     "sia",         # cosine of solar incidence angle
                     "bbse",        # broadband sufrace emissivity
                     "nbe",         # narrow band emissivity
                     "therm_rad10", # initial thermal radiance band 10
                     "therm_rad11", # initial thermal radiance band 11
                     "corr_rad10",  # corrected thermal radiance band 10
                     "corr_rad11",  # corrected thermal radiance band 11
                     "sfcTemp",     # surface temperature
                     "p",           # atmospheric pressure
                     "w",           # water in the atmosphere
                     "entisr",      # effective narrow band transmittance for incoming solar radiation
                     "entsrrs",     # effective narrow band transmittance for shortwave radiation reflected from surface
                     "pr",          # path reflectance
                     "bbat",        # broad-band atmospheric transmissivity
                     "ibbswr",      # incoming broad band short wave radiation
                     "asr",         # at-surface reflectance
                     "bsa",         # broadband surface albedo
                     "eae",         # effective atmospheric transmissivity
                     "g_ratio",     # soil heat flux to net radiation ratio
                     "zom",         # momentum rougness length
                     "ilwr",        # incoming long wave radiation
                     "olwr",        # outgoing long wave radiation
                     "soil_hf",     # soil heat flux.
                     "wcoeff",      # wind speed weighting coefficient
                     "T_s_datum",   # TS datum
                     "ws_200m",     # wind speed at assumed blending height of 200m
                     "fric_vel",    # friction velocity
                     "aero_res",    # aerodynamic resistance
                     "L",           # Monin-Obukhov length (height at which buoyancy and mechanical mixing balance
                     "psi",         # stability corrections for momentum transport at various atmospheric layers  
                     "dT"]          # sensible heat flux         
        
        if self.saveflag == "ALL":
            save_list = ALL
        elif self.saveflag == "LIMITED":
            save_list = LIM
        elif self.saveflag == "ET-ONLY":
            save_list = ETO
        else:
            raise Exception("invalid saveflag!, must be 'ALL', 'LIMITED', or 'ET-ONLY'")

        if object_name in save_list:
            return True
        else:
            return False
        
        
    def ingest_all_data(self, landsat_filepath_list, landsat_metapath,
                     dem_path, hot_shape_path, cold_shape_path):
        """
        Primary functin for loading data into the main metric workspace.
        useful for arcpy tool creation
        
        landsat_filepath_list:  list of landsat band tiff filepaths, MUST be in order [2,3,4,5,6,7,10,11]
        landsat_metapath:       filepath to the landsat metadata
        dem_path:               filepath to the digital elevation model
        hot_shape_path:         filepath to the shapefile outlining the hot pixels
        cold_shape_path:        filepath to the shapefile outlining the cold pixels
        """ 

        self.ingest_landsat_data(landsat_filepath_list, landsat_metapath)
        self.ingest_dem(dem_path) 
        self.ingest_ref_pixels(hot_shape_path, cold_shape_path)
        return


    def ingest_landsat_data(self, band_filepaths, metadata_path):
            """
            Ingests landsat data into the METRIC model by creating object attributes
            
            The list of filepaths in band_filepahts MUST contain filepaths to each
            of the following bands in ascending order. [2,3,4,5,6,7,10,11].
            """

            self.metadata_path  = metadata_path
            self.landsat_meta   = landsat.Grab_Meta(metadata_path) #dnppy function
            
            band_names          = [2,3,4,5,6,7,10,11]
            new_band_filepaths  = []

            # copy all the landsat bands into the workspace if they aren't there.
            for band_filepath in band_filepaths:

                path, name  = os.path.split(band_filepath)
                destination = os.path.join(self.landsat_dir,name)

                new_band_filepaths.append(destination)

                if not path == self.landsat_dir:
                    shutil.copy(band_filepath, destination)
                    shutil.copy(band_filepath.replace('tif','tfw'), destination.replace('tif','tfw'))

            # fill the landsat object with the raster attributes

            self.landsat_bands = []  # legacy. list of landsat band objects
            
            for i,band_filepath in enumerate(band_filepaths):
                path_attr_name = 'B{0}_path'.format(band_names[i])
                rast_attr_name = 'B{0}_rast'.format(band_names[i])
                
                setattr(self, path_attr_name, band_filepath)
                setattr(self, rast_attr_name, arcpy.Raster(getattr(self, path_attr_name)))
                
                self.landsat_bands.append(getattr(self, rast_attr_name))

            return


    def ingest_dem(self, dem_filepath):
        """ ingests the DEM into the metric model workspace """ 

        # copy the input dem filepath into the workspace if it isnt already there
        path, name  = os.path.split(dem_filepath)
        destination = os.path.join(self.dem_dir,name)

        if not path == self.dem_dir:
            shutil.copy(dem_filepath, destination)
            shutil.copy(dem_filepath.replace('tif','tfw'), destination.replace('tif','tfw'))
            
        self.dem_path = destination
        self.dem_file = arcpy.Raster(destination)
        return


    def ingest_ref_pixels(self, hot_shape_path, cold_shape_path):
        """ ingests the reference pixels into the metric model workspace"""

        # copy the input hot shape into workspace if it isnt already there
        path, name          = os.path.split(hot_shape_path)
        destination         = os.path.join(self.ref_pixel_dir, name)
        self.hot_shape_path = destination

        if not path == self.ref_pixel_dir:
            shutil.copy(hot_shape_path, destination)
            shutil.copy(hot_shape_path.replace('tif','tfw'), destination.replace('tif','tfw'))

        # copy the input cold shape into workspace if it isnt already there
        path, name          = os.path.split(cold_shape_path)
        destination         = os.path.join(self.ref_pixel_dir, name)
        self.cold_shape_path= destination

        if not path == self.ref_pixel_dir:
            shutil.copy(cold_shape_path, destination)
            shutil.copy(cold_shape_path.replace('tif','tfw'), destination.replace('tif','tfw'))

        # these hot/cold pixel tables are empty template dbfs included in empty METRIC
        self.hot_pixel_table = os.path.join(self.ref_pixel_dir,"pixel_hot_stats.dbf")
        self.cold_pixel_table = os.path.join(self.ref_pixel_dir,"pixel_cold_stats.dbf")
        return

    def get_timezone(self):
        """Gets timezone from test_mid_atlantic"""
        

    def get_date(self):
        """ Turns data into julian_day"""
        return self.landsat_meta.j_day


    def get_time(self):
        """ Output time array is of format [hours, minutes, seconds, decimal_time]""" 
        time = map(float,self.landsat_meta.SCENE_CENTER_TIME.split(".")[0].split(":"))
        print time
        decimal_time = float(((time[1] * 60 + time[2]) / 3600) + time[0])
        decimal_time = float(decimal_time / 24)
        print decimal_time
        time.append(decimal_time)
        return time


    def get_longitude(self):
        lon_UL = float(self.landsat_meta.CORNER_UL_LON_PRODUCT)
        lon_UR = float(self.landsat_meta.CORNER_UR_LON_PRODUCT)
        lon_LL = float(self.landsat_meta.CORNER_LL_LON_PRODUCT)
        lon_LR = float(self.landsat_meta.CORNER_LR_LON_PRODUCT)

        lon = (lon_UL + lon_UR + lon_LL + lon_LR) / 4
        self.lon = lon * math.pi / 180
        return self.lon


    def get_lattitude(self):
        lat_UL = float(self.landsat_meta.CORNER_UL_LAT_PRODUCT)
        lat_UR = float(self.landsat_meta.CORNER_UL_LAT_PRODUCT)
        lat_LL = float(self.landsat_meta.CORNER_UL_LAT_PRODUCT)
        lat_LR = float(self.landsat_meta.CORNER_UL_LAT_PRODUCT)

        lat = (lat_UL + lat_UR + lat_LL + lat_LR) / 4
        self.lat = lat * math.pi / 180
        return self.lat


    def get_earth_sun_distance(self):
        return float(self.landsat_meta.EARTH_SUN_DISTANCE)


    def get_cloud_cover(self):
        return float(self.landsat_meta.CLOUD_COVER)


    def get_solar_declination_angle(self, doy):
        return DM.Dec(doy)


    def get_sunset_angle(self, lat, declination):
        sunset_hour_angle = math.acos(-math.tan(lat) * math.tan(declination))
        return sunset_hour_angle


    def get_daily_extraterrestrial_radiation(self, lat, declination, sunset_hour_angle, earth_sun_distance):
        G_sc = 0.0820
        self.xterr_rad = (24 * 60 / math.pi) * G_sc * earth_sun_distance * ((sunset_hour_angle *
                math.sin(lat) * math.sin(declination)) + (math.cos(lat) *
                math.cos(declination)*math.sin(sunset_hour_angle)))
        return self.xterr_rad


    def get_slope(self):
        """ calculates a slope raster from the DEM"""
        
        sfname = "slope.tif"
        sfpath = os.path.join(self.middle_dir, sfname)
        
        if os.path.isfile(sfpath) and not self.recalc:
            print "Reading previously estimated slopes... "
            slope = arcpy.Raster(sfpath)
        else:
            print "Calculating elevation derivatives... "
            slope = arcpy.sa.Slope(self.dem_file)
            
            # cap slopes at 30 degrees to reduce DEM artifacts
            slope = arcpy.sa.Con(slope, slope, 30, "VALUE < 30")
            
            # convert degrees to radians
            slope = slope * math.pi / 180
            
            if self.check_saveflag("slope"):
                slope.save(sfpath)
                
        return slope


    def get_aspect(self):
        """ calculates the aspect raster from the DEM"""
        
        afname = "aspect.tif"
        afpath = os.path.join(self.middle_dir, afname)
        
        if os.path.isfile(afpath) and not self.recalc:
            print "Reading previously estimated aspects... "
            aspect = arcpy.Raster(afpath)
        else:
            
            aspect = arcpy.sa.Aspect(self.dem_file)
            # get rid of -1 "slope 0" flag
            aspect = arcpy.sa.Con(aspect, aspect, math.pi, "VALUE > -1")
            
            # convert degrees to radians and rotate half turn to put 0 aspect to south
            aspect = (aspect * math.pi / 180) - math.pi

            if self.check_saveflag("aspect"):
                aspect.save(afpath)
            
        return aspect


    def get_solar_zenith_angle(self, declination, lat, hour_angle):
        return DM.Num8(declination, lat, hour_angle)


    def get_vapor_pressure(self, dewp_C):
        e_a = DM.Saturation_Vapor_Pressure(dewp_C)
        return e_a


    def get_cosine_of_solar_incidence_angle(self, declination, lat, slope, aspect, hour_angle):
        """ calculate the cosine of solar incidence angle from sceen geometry"""

        siname = "sia_output.tif"
        sipath = os.path.join(self.middle_dir, siname)
        
        if os.path.isfile(sipath) and not self.recalc:
            print "Reading previously estimated cosine of solar incidence angles... "
            sia = arcpy.Raster(sipath)
        else:
            print "Calculating cosine of solar incidence angles... "
            sia, sia1, sia2, sia3, sia4, sia5 = DM.Num7(declination, lat, slope, aspect, hour_angle)

            if self.check_saveflag("sia"):
                sia.save(sipath)
        return sia


    def get_reflectance_band(self, cos_sia):                    ### dnppy_flag
        """ converts landsat bands to reflectance """ 
        
        refl_bands = []
        for i in xrange(len(self.landsat_bands)):
            landsat_band_file = "LS_ref{0}.tif".format(str(i+2))
            landsat_band_path = os.path.join(self.middle_dir, landsat_band_file)
            
            if os.path.isfile(landsat_band_path) and not self.recalc:
                reflectance_band = arcpy.Raster(landsat_band_path)
                refl_bands.append(reflectance_band)
            else:
                reflectance_band = DM.Num10(self.landsat_bands[i], cos_sia)
                refl_bands.append(landsat_band_path)

                if self.check_saveflag("LS_ref"):
                    reflectance_band.save(landsat_band_path)
                
        return refl_bands


    def get_SAVI(self, refl_band5, refl_band4):
        """ calculates soil adjusted vegetation index"""
       # L=0.1 for SAVI_idaho or L=0.5 for common SAVI 
        L = 0.5
        svname = "savi_output.tif"
        svpath = os.path.join(self.out_dir, svname)
        
        if os.path.isfile(svpath) and not self.recalc:
            savi = arcpy.Raster(svpath)
        else:
            savi = DM.Num19(refl_band5, refl_band4, L)

            if self.check_saveflag("savi"):
                savi.save(svpath)
        return savi


    def get_NDVI(self, refl_band5, refl_band4):
        """ calculates normalized difference vegetation index"""
        
        ndname = "ndvi_output.tif"
        ndpath = os.path.join(self.out_dir, ndname)
        
        if os.path.isfile(ndpath)and not self.recalc:
            ndvi = arcpy.Raster(ndpath)
        else:
            ndvi = DM.Num23(refl_band5, refl_band4)

            if self.check_saveflag("ndvi"):
                ndvi.save(ndpath)
        return ndvi


    def get_LAI(self, savi):
        """ calculates leaf area index"""
        
        laname = "lai_output.tif"
        lapath = os.path.join(self.out_dir, laname)
        
        if os.path.isfile(lapath) and not self.recalc:
            lai = arcpy.Raster(lapath)
        else:
            lai = DM.Num18(savi)

            if self.check_saveflag("lai"):
                lai.save(lapath)
        return lai


    def get_broadband_surface_emissivity(self, lai):
        bbse_name = "bbse_output.tif"
        bbse_path = os.path.join(self.middle_dir, bbse_name)
        
        if os.path.isfile(bbse_path) and not self.recalc:
            bbse = arcpy.Raster(bbse_path)
        else:
            bbse = DM.Num17(lai)

            if self.check_saveflag("bbse"):
                bbse.save(bbse_path)
        return bbse


    def get_narrow_band_emissivity(self, lai):
        nbe_name = "nbe_output.tif"
        nbe_path = os.path.join(self.middle_dir, nbe_name)
        
        if os.path.isfile(nbe_path)and not self.recalc:
            nbe = arcpy.Raster(nbe_path)
        else:
            nbe = DM.Num22(lai)

            if self.check_saveflag("nbe"):
                nbe.save(nbe_path)
        return nbe

    def _get_initial_thermal_radiances(self):
        
        #Landsat Thermal Band 10
        thrad10_name = "thermRad10_output.tif"
        thrad10_path = os.path.join(self.middle_dir, thrad10_name)
        
        if os.path.isfile(thrad10_path)and not self.recalc:
            therm_rad10 = arcpy.Raster(thrad10_path)
        else:
            therm_rad10 = DM.L8_Thermal_Radiance(self.B10_rast)

            if self.check_saveflag("therm_rad10"):
                therm_rad10.save(thrad10_path)

        #Landsat Thermal Band 11
        thrad11_name = "thermRad11_output.tif"
        thrad11_path = os.path.join(self.middle_dir, thrad11_name)
        
        if os.path.isfile(thrad11_path) and not self.recalc:
            therm_rad11 = arcpy.Raster(thrad11_path)
        else:
            therm_rad11 = DM.L8_Thermal_Radiance(self.B11_rast)

            if self.check_saveflag("therm_rad11"):
                therm_rad11.save(thrad11_path)

        return [therm_rad10, therm_rad11]


    def _get_corrected_thermal_radiances(self, nbe):
        """@param nbe: found in get_narrow_band_emissivity (Ln262)"""
        
        initial_thermal_radiances = self._get_initial_thermal_radiances()
        therm_rad10 = initial_thermal_radiances[0]
        therm_rad11 = initial_thermal_radiances[1]

        path_rad = 0.91
        nbt = 0.866
        sky_rad = 1.32
        
        #Corrections Thermal Band 10
        corr10_name = "corrRad10_output.tif"
        corr10_path = os.path.join(self.middle_dir, corr10_name)
        
        if os.path.isfile(corr10_path)and not self.recalc:
            corr_rad10 = arcpy.Raster(corr10_path)
        else:
            corr_rad10 = DM.Num21(therm_rad10, path_rad, nbt, nbe, sky_rad)

            if self.check_saveflag("corr_rad10"):
                corr_rad10.save(corr10_path)

        #Corrections Thermal Band 11
        corr11_name = "corrRad11_output.tif"
        corr11_path = os.path.join(self.middle_dir, corr11_name)
        
        if os.path.isfile(corr11_path) and not self.recalc:
            corr_rad11 = arcpy.Raster(corr11_path)
        else:
            corr_rad11 = DM.Num21(therm_rad11, path_rad, nbt, nbe, sky_rad)

            if self.check_saveflag("corr_rad11"):
                corr_rad11.save(corr11_path)

        return [corr_rad10, corr_rad11]


    def get_surface_temperature(self, nbe):
        """@param nbe: found in get_narrow_band_emissivity (Ln262)"""
        
        lst_name = "sfcTemp_output.tif"
        lst_path = os.path.join(self.middle_dir, lst_name)
        
        if os.path.isfile(lst_path) and not self.recalc:
            sfcTemp = arcpy.Raster(lst_path)
        else:
            corrected_thermal_radiances = self._get_corrected_thermal_radiances(nbe)
            corr_rad10 = corrected_thermal_radiances[0]
            corr_rad11 = corrected_thermal_radiances[1]

            sfcTemp10 = DM.Num20(corr_rad10, nbe, 774.89, 1321.08)
            sfcTemp11 = DM.Num20(corr_rad11, nbe, 480.89, 1201.14)
            sfcTemp = (sfcTemp10 + sfcTemp11) / 2

            if self.check_saveflag("sfcTemp"):
                sfcTemp.save(lst_path)
        return sfcTemp


    def get_atmospheric_pressure(self):
        p_name = "p_output.tif"
        p_path = os.path.join(self.middle_dir, p_name)
        
        if os.path.isfile(p_path) and not self.recalc:
            p = arcpy.Raster(p_path)
        else:
            p = DM.Num5(self.dem_file)

            if self.check_saveflag("p"):
                p.save(p_path)
        return p


    def get_water_in_the_atmosphere(self, e_a, p, P_air):
        """
        @param e_a: found in get_vapor_pressure (ln181)
        @param p: found in get_atmospheric_pressure (ln344)
        """
        
        w_name = "w_output.tif"
        w_path = os.path.join(self.middle_dir, w_name)
        
        if os.path.isfile(w_path) and not self.recalc:
            w = arcpy.Raster(w_path)
        else:
            w = DM.Num6(e_a, p)

            if self.check_saveflag("w"):
                w.save(w_path)
        return w


    def get_effective_narrowband_trasmittance1(self, p, w, cth):
        """
        @param p: found in get_atmospheric_pressure (ln344)
        @param w: found in get_water_in_the_atmosphere (ln358)
        @param cth: found in get_solar_zenith_angle (ln178)
        """
        
        kt = 1.0
        constants = [[0.987, -0.00071, 0.000036, 0.0880, 0.0789],
                     [2.319, -0.00016, 0.000105, 0.0437, -1.2697],
                     [0.951, -0.00033, 0.000280, 0.0875, 0.1014],
                     [0.375, -0.00048, 0.005018, 0.1355, 0.6621],
                     [0.234, -0.00101, 0.004336, 0.0560, 0.7757],
                     [0.365, -0.00097, 0.004296, 0.0155, 0.6390]]
        entirs_bands = []
        for i in xrange(6):
            ent_name = 'entisrBnd0' + str(i+1) + '_output.tif'
            ent_path = os.path.join(self.middle_dir, ent_name)
            
            if os.path.isfile(ent_path) and not self.recalc:
                raster = arcpy.Raster(ent_path)
            else:
                raster = DM.Num12(p, w, cth, kt, constants[i][0], constants[i][1],
                                  constants[i][2], constants[i][3], constants[i][4])
                
                if self.check_saveflag("entisr"):
                    raster.save(ent_path)
                    
            entirs_bands.append(raster)
        return entirs_bands


    def get_effective_narrowband_transmittance2(self, p, w):
        """
        param p: found in get_atmospheric_pressure (ln344)
        @param w: found in get_water_in_the_atmosphere (ln358)
        """
        
        kt = 1.0
        cos_n = 1
        constants = [[0.987, -0.00071, 0.000036, 0.0880, 0.0789],
                     [2.319, -0.00016, 0.000105, 0.0437, -1.2697],
                     [0.951, -0.00033, 0.000280, 0.0875, 0.1014],
                     [0.375, -0.00048, 0.005018, 0.1355, 0.6621],
                     [0.234, -0.00101, 0.004336, 0.0560, 0.7757],
                     [0.365, -0.00097, 0.004296, 0.0155, 0.6390]]
        entsrrs_bands = []
        for i in xrange(6):
            ent2_name = 'entsrrsBnd0' + str(i+1) + '_output.tif'
            ent2_path = os.path.join(self.middle_dir, ent2_name)
            
            if os.path.isfile(ent2_path) and not self.recalc:
                raster = arcpy.Raster(ent2_path)
            else:
                raster = DM.Num13(p, w, cos_n, kt, constants[i][0], constants[i][1],
                                  constants[i][2], constants[i][3], constants[i][4])
                
                if self.check_saveflag("entsrrs"):
                    raster.save(ent2_path)
                
            entsrrs_bands.append(raster)
        return entsrrs_bands


    def get_per_band_path_reflectance(self, entisr_bands):
        """@param entisr_bands: found in get_effective_narrowband_trasmittance1 (ln373)"""
        
        pr_bands = []
        constants = [0.254, 0.149, 0.147, 0.311, 0.103, 0.036]
        for i in xrange(6):
            pr_name = 'prBnd0' + str(i+1) + '_output.tif'
            pr_path = os.path.join(self.middle_dir, pr_name)
            
            if os.path.isfile(pr_path) and not self.recalc:
                raster = arcpy.Raster(pr_path)
            else:
                raster = DM.Num14(entisr_bands[i], constants[i])

                if self.check_saveflag("pr"):
                    raster.save(pr_path)
                    
            pr_bands.append(raster)
        return pr_bands


    def get_broad_band_atmospheric_transmissivity(self, p, w, cth):
        """
        @param p: found in get_atmospheric_pressure (ln344)
        @param w: found in get_water_in_the_atmosphere (ln358)
        @param cth: found in get_solar_zenith_angle (ln178)
        """
        
        bbat_name = "bbat_output.tif"
        bbat_path = os.path.join(self.middle_dir, bbat_name)
        
        if os.path.isfile(bbat_path) and not self.recalc:
            bbat = arcpy.Raster(bbat_path)
        else:
            kt = 1.0
            bbat = DM.Num4(p, w, cth, kt)

            if self.check_saveflag("bbat"):
                bbat.save(bbat_path)
        return bbat


    def get_incoming_broad_band_short_wave_radiation(self, sia, bbat, earth_sun_distance):
        """
        @param sia: found in get_cosine_of_solar_incidence_angle (ln185)
        @param bbat: found in get_broad_band_atmospheric_transmissivity (ln440)
        """
        ibbswr_name = "ibbswr_output.tif"
        ibbswr_path = os.path.join(self.middle_dir, ibbswr_name)
        
        if os.path.isfile(ibbswr_path) and not self.recalc:
            ibbswr = arcpy.Raster(ibbswr_path)
        else:
            ibbswr = DM.Num3(sia, bbat, earth_sun_distance)

            if self.check_saveflag("ibbswr"):
                ibbswr.save(ibbswr_path)
        return ibbswr


    def get_at_surface_reflectance(self, refl_bands, entisr_bands, entsrrs_bands, pr_bands):
        """
        @param refl_bands: found in get_reflectance_band
        @param entisr_bands: found in get_effective_narrowband_trasmittance1 (ln373)
        @param entsrrs_bands: found in get_effective_narrowband_transmittance2 (ln397)
        @param pr_bands: found in get_per_band_path_reflectance (ln421)
        """
        
        asr_bands = []
        for i in xrange(6):
            raster = DM.Num11(refl_bands[i], entisr_bands[i], entsrrs_bands[i], pr_bands[i])
            asr_bands.append(raster)

            if self.check_saveflag("asr"):
                raster.save()
        return asr_bands


    def get_broadband_surface_albedo(self, asr_bands):
        """@param asr_bands: found in get_at_surface_reflectance (ln471)"""

        bsa_name = "bsa_output.tif"
        bsa_path = os.path.join(self.middle_dir, bsa_name)
        
        if os.path.isfile(bsa_path) and not self.recalc:
            bsa = arcpy.Raster(bsa_path)
        else:
            bsa = DM.Num15(asr_bands)

            if self.check_saveflag("bsa"):
                bsa.save(bsa_path)
        return bsa


    def get_effective_atmospheric_transmissivity(self, bbat):
        """@param bbat: found in get_broad_band_atmospheric_transmissivity (ln440)"""
        
        eae_name = 'eae_output.tif'
        eae_path = os.path.join(self.middle_dir, eae_name)
        
        if os.path.isfile(eae_path) and not self.recalc:
            eae = arcpy.Raster(eae_path)
        else:
            eae = DM.Num25(bbat)
            if self.check_saveflag("eae"):
                eae.save(eae_path)
        return eae


    def get_soil_heat_flux_to_net_radiation_ratio(self, bsa, sfc_temp, ndvi):
        """
        @param bsa: found in get_broadband_surface_albedo (ln482)
        @param sfc_temp: found in get_surface_temperature (ln328)
        @param ndvi: found in get_NDVI
        """
        
        grat_name = "g_ratio_output.tif"
        grat_path = os.path.join(self.middle_dir, grat_name)
        
        if os.path.isfile(grat_path) and not self.recalc:
            g_ratio = arcpy.Raster(grat_path)
        else:
            g_ratio = DM.Num26(bsa, sfc_temp, ndvi)

            if self.check_saveflag("g_ratio"):
                g_ratio.save(grat_path)
        return g_ratio


    def get_momentum_roughness_length(self, lai):
        """@param lai: found in get_LAI"""
        
        zom = DM.Num33(lai)

        if self.check_saveflag("zom"):
            zom.save('zom_output.tif')
        return zom


    def get_incoming_long_wave_radiation(self, eae, temp_C_mid):
        """@param eae: found in get_effective_atmospheric_transmissivity (ln495)"""

        ilwr_name = "ilwr_output.tif"
        ilwr_path = os.path.join(self.middle_dir, ilwr_name)
        
        if os.path.isfile(ilwr_path) and not self.recalc:
            ilwr = arcpy.Raster(ilwr_path)
        else:
            ilwr = DM.Num24(eae, temp_C_mid + 273)
            if self.check_saveflag("ilwr"):
                ilwr.save(ilwr_path)
        return ilwr


    def get_outgoing_long_wave_radiation(self, bbse, sfc_temp):
        """
        @param bbse: found in get_broadband_surface_emissivity (ln252)
        @param sfc_temp: found in get_surface_temperature (ln328)
        """
        
        olwr_name = "olwr_output.tif"
        olwr_path = os.path.join(self.middle_dir, olwr_name)
        
        if os.path.isfile(olwr_path) and not self.recalc:
            olwr = arcpy.Raster(olwr_path)
        else:
            olwr = DM.Num16(bbse, sfc_temp)
            if self.check_saveflag("olwr"):
                olwr.save(olwr_path)
        return olwr

 
    def get_net_radiation(self, ibbswr, bsa, olwr, ilwr, bbse):
        """
        @param ibbswr: found in get_incoming_broad_band_short_wave_radiation
        @param bsa: found in get_broadband_surface_albedo (ln482)
        @param olwr: found in get_outgoing_long_wave_radiation (ln545)
        @param ilwr: found in get_incoming_long_wave_radiation (ln545)
        @param bbse: found in get_broadband_surface_emissivity (ln252)
        """
        
        netrad_name = "net_rad.tif"
        netrad_path = os.path.join(self.middle_dir, netrad_name)
        
        if os.path.isfile(netrad_path)and not self.recalc:
            self.net_radiation = arcpy.Raster(netrad_path)
        else:
            self.net_radiation = DM.Num2(ibbswr, bsa, olwr, ilwr, bbse)
            if self.check_saveflag("net_rad"):
                self.net_radiation.save(netrad_name)
        return self.net_radiation


    def get_soil_heat_flux(self, g_ratio):
        shflux_name = "soil_hf.tif"
        shflux_path = os.path.join(self.middle_dir, shflux_name)
        
        if os.path.isfile(shflux_path) and not self.recalc:
            self.soil_heat_flux = arcpy.Raster(shflux_path)
        else:
            self.soil_heat_flux = self.net_radiation * g_ratio
            if self.check_saveflag("soil_hf"):
                
                self.soil_heat_flux.save(shflux_path)
        return self.soil_heat_flux


    def get_wind_speed_weihting_coefficient(self):  # jeff flag
        elev_wx = float(1205)
        wcoeff = DM.Num36(self.dem_file, elev_wx)

        if self.check_saveflag("wcoeff"):
            wcoeff.save("wcoeff_output.tif")
        return wcoeff


    def get_T_s_datum(self, sfc_temp): # jeff flag
        elev_ts_datum = 2670
        T_s_datum_path = os.path.join(self.middle_dir, "T_s_datum.tif")
        T_s_datum = DM.Datum_Ref_Temp(sfc_temp, self.dem_file, elev_ts_datum)

        if self.check_saveflag("T_s_datum"):
            T_s_datum.save(T_s_datum_path)
        return T_s_datum


    def get_wind_speed_at_assumed_blending_height(self, wind_speed):
        lai_w = 0.764196 #PUT IN LAI FOR ID OR NC WX STATION !!!
        zom_w = 0.018 * lai_w
        ws_200m = DM.Num32(wind_speed, zom_w)
        return ws_200m


    def get_friction_velocity(self, ws_200m, zom):
        """
        @param ws_200m: found in get_wind_speed_at_assumed_blending_height (Ln594)
        @param zom: found in get_momentum_roughness_length (Ln523)
        """
        fric_vel_path = os.path.join(self.middle_dir, "fric_vel.tif")
        fric_vel = DM.Num31(ws_200m, zom)
        
        if self.check_saveflag("fric_vel"):
            fric_vel.save(fric_vel_path)
        return fric_vel


    def get_aerodynamic_resistance(self, fric_vel):
        """@param fric_vel: found in get_friction_velocity (Ln604)"""

        aero_res_path = os.path.join(self.middle_dir, "aero_res.tif")
        aero_res = DM.Num30(fric_vel)

        if self.check_saveflag("aero_res"):
            aero_res.save(aero_res_path)
        return aero_res

    def get_sensible_heat_flux(self, lai, wind_speed, p, sfc_temp, LEref): # jeff_flag
        """ itteratively solves for sensible heat flux"""
        
        zom = self.get_momentum_roughness_length(lai)

        ws_200m     = self.get_wind_speed_at_assumed_blending_height(wind_speed) ## ws_200m is a scalar float !!!
        T_s_datum   = self.get_T_s_datum(sfc_temp)
        fric_vel    = self.get_friction_velocity(wind_speed, zom)
        aero_res    = self.get_aerodynamic_resistance(fric_vel)
        dsc         = arcpy.Describe(zom)
        ext         = dsc.Extent
        dT          = aero_res * 0.0
        #dT          = CreateConstantRaster(0, "FLOAT", 30, Extent(ext.XMin, ext.YMin, ext.XMax, ext.YMax))
        dT_path     = os.path.join(self.middle_dir,"dT0.tif")
        
        if self.check_saveflag("dT"):
            dT.save(dT_path)
        
        self.sensible_heat_flux = aero_res * 0.0
        #self.sensible_heat_flux = CreateConstantRaster(0, "FLOAT", 30, Extent(ext.XMin, ext.YMin, ext.XMax, ext.YMax))
        
        rho_air = DM.Num37(p, sfc_temp, dT)
        rho_air.save(os.path.join(self.middle_dir, "rho_air.tif"))

        # we are assuming that 5 itterations is enough for convergence.
        for i in xrange(5):
            if i > 0:
               
               # equation 40-45b
                L_path = os.path.join(self.middle_dir, "L{0}.tif".format(i))
                L = DM.Num40(rho_air, fric_vel, sfc_temp, self.sensible_heat_flux)

                if self.check_saveflag("L"):
                    L.save(L_path)
                    
                # separate loop needed to filter L
                # jeff - what does this actually mean?
                psi_200_unstable_path   = os.path.join(self.middle_dir, "psi_200_unst{0}.tif".format(i))
                psi_200_stable_path     = os.path.join(self.middle_dir, "psi_200_stab{0}.tif".format(i))
                
                psi_200_unstable = DM.Num41(L)
                psi_200_stable = DM.Num44(L)

                if self.check_saveflag("psi"):
                    psi_200_unstable.save(psi_200_unstable_path)
                    psi_200_stable.save(psi_200_stable_path)

                psi_2_unstable = DM.Num42a(L)
                psi_2_stable = DM.Num45a(L)

                psi_1_unstable = DM.Num42b(L)
                psi_1_stable = DM.Num45b(L)
                
                #if arcpy.GetRasterProperties_management(L,"MINIMUM") < 0:
                psi_200 = arcpy.sa.Con(L, psi_200_unstable, L, "VALUE < 0")
                psi_2 = arcpy.sa.Con(L, psi_2_unstable, L, "VALUE < 0")
                psi_1 = arcpy.sa.Con(L, psi_1_unstable, L, "VALUE < 0")
                #if arcpy.GetRasterProperties_management(L,"MAXIMUM") > 0:
                psi_200 = arcpy.sa.Con(L, psi_200_stable, 0, "VALUE > 0")
                psi_2 = arcpy.sa.Con(L, psi_2_stable, 0, "VALUE > 0")
                psi_1 = arcpy.sa.Con(L, psi_1_stable, 0, "VALUE > 0")

                fric_vel = DM.Num38(ws_200m, zom, psi_200)
                aero_res = DM.Num39(psi_2, psi_1, fric_vel)
                
                print "fric_vel path =", fric_vel
                print "aero_res path = ", aero_res
                
            rho_air_hot = DM.meanFromRasterBySingleZone(rho_air, self.hot_shape_path, self.hot_pixel_table)
            net_rad_hot = DM.meanFromRasterBySingleZone(self.net_radiation, self.hot_shape_path, self.hot_pixel_table)
            
            G_hot = DM.meanFromRasterBySingleZone(self.soil_heat_flux, self.hot_shape_path, self.hot_pixel_table)
            aero_res_hot = DM.meanFromRasterBySingleZone(aero_res, self.hot_shape_path, self.hot_pixel_table)
            T_s_datum_hot = DM.meanFromRasterBySingleZone(T_s_datum, self.hot_shape_path, self.hot_pixel_table)
            dT_hot = DM.Num46(net_rad_hot, G_hot, aero_res_hot, rho_air_hot)  ## Why?

            rho_air_cold = DM.meanFromRasterBySingleZone(rho_air, self.cold_shape_path, self.cold_pixel_table)
            net_rad_cold = DM.meanFromRasterBySingleZone(self.net_radiation, self.cold_shape_path, self.cold_pixel_table)
            G_cold = DM.meanFromRasterBySingleZone(self.soil_heat_flux, self.cold_shape_path, self.cold_pixel_table)
            aero_res_cold = DM.meanFromRasterBySingleZone(aero_res, self.cold_shape_path, self.cold_pixel_table)
            T_s_datum_cold = DM.meanFromRasterBySingleZone(T_s_datum, self.cold_shape_path, self.cold_pixel_table)
            dT_cold = DM.Num49(net_rad_cold, G_cold, LEref, aero_res_cold, rho_air_cold)

            a = DM.Num50(dT_hot, dT_cold, T_s_datum_hot, T_s_datum_cold)
            b = DM.Num51(dT_hot, a, T_s_datum_hot)

            dT = DM.Num29(a, b, T_s_datum)
            print "dT path=", dT

            rhoair = DM.Num37(p, sfc_temp, dT)

            self.sensible_heat_flux = DM.Num28(rhoair, dT, aero_res)

            if self.check_saveflag("H"): 
                self.sensible_heat_flux.save("H" + str(i) + ".tif")

        return self.sensible_heat_flux

    def get_latent_energy_consumed_by_ET(self):
        self.latent_energy = DM.Num1(self.net_radiation, self.soil_heat_flux, self.sensible_heat_flux)

        if self.check_saveflag("LE"):
            self.latent_energy.save("LE.tif")
        return self.latent_energy

    def get_latent_heat_vaporization(self, sfcTemp):
        self.latent_heat = DM.Num53(sfcTemp)
        
        if self.check_saveflag("LH_vapor"):
            self.latent_heat.save("LH_vapor_output.tif")
        return self.latent_heat

    def get_instantaneous_evapotranspiration(self):
        self.evapotranspiration = self.latent_energy * 0.035 / 24

        if self.check_saveflag("ET_inst"):
            self.evapotranspiration.save("ET_inst.tif")
        return self.evapotranspiration
    
    def get_ETrF(self, ET_ref_hr):
        self.ET_rf = self.evapotranspiration/ET_ref_hr
        
        if self.check_saveflag("ET_frac"):
            self.ET_rf.save("ET_frac.tif")
        return self.ET_rf
        
    def get_daily_evapotranspiration(self, ET_ref_day):
        self.daily_evapotranspiration = self.ET_rf * ET_ref_day

        if self.check_saveflag("ET_24hr"):
            self.daily_evapotranspiration.save("ET_24hr.tif")
        return self.daily_evapotranspiration


    def get_evapotranspiration_instant(self):
        self.ETinstant = DM.Num52(self.latent_energy)

        if self.check_saveflag("ET_inst2"):
            self.ETinstant.save("ET_inst2.tif")
        return self.ETinstant

    def get_ET_fraction(self, ET_ref_hr):
        self.ET_fraction = DM.Num54(self.ETinstant, ET_ref_hr)
        
        if self.check_saveflag("ET_frac2"):
            self.ET_fraction.save("ET_frac2.tif")
        return self.ET_fraction
    
    def get_evapotranspiration_day(self, ET_ref_day):
        self.evapotranspiration_daily = DM.Num55(self.ET_fraction,ET_ref_day)

        if self.check_saveflag("ET_24hr2"):
            self.evapotranspiration_daily.save("ET_24hr2.tif")
        return self.evapotranspiration_daily
   
def reference_calculation(longitude, latitude, earth_sun_distance, cloud_cover,doy, solar_declination_angle, 
                          decimal_time, temp_C_min, temp_C_max, temp_C_mid, P_air, wind_speed, dewp_C, crop, timezone):
    # REFERENCE - Refactor to Function ???
#
#
#Set time zone offset for project
    """TIME ZONE OFFSET VALUE!!!"""
#    tzo = 6.0 ##Initial weather & biophysical reference calcs
    tzo = -timezone
#reference crop height (m) & albedo (unitless) alfalfa
#    crop_hgt = 0.5
#    crop_a = 0.23
    if crop == "grass":
        crop_hgt = 0.12
        crop_a = 0.23
    if crop == "alfalfa":
        crop_hgt = 0.5
        crop_a = 0.23
        
#wind speed measurement height, m
    z_m = 2
#aerodynamic resistance assuming 2m measure height, 0.12m crop height (grass)
    r_aero = DM.Aerodynamic_Resistance(wind_speed, z_m, crop_hgt)
    print "Aerodynamic Resistance: ", r_aero, "s/m"
#aerodynamic resistance assuming 2m measure height, 0.12m crop height (grass)
    LAI_ref = 24 * crop_hgt
    r_surf = DM.Surface_Resistance(LAI_ref)
    print "Surface Resistance: ", r_surf, "s/m"
#Hour Angle2
#Hour angle2 requires longitude in positive degrees west
    lon_alt = -longitude * 180 / math.pi
    dtime_alt = decimal_time * 24
    ltime = dtime_alt - tzo
    print "Acquisition Time, Local: ", ltime, "Decimal Hours"
    ha_ref = DM.Hour_Angle2(lon_alt, dtime_alt, doy, tzo)
    print "Hour Angle Alt: ", ha_ref, "rad"
#hour angles bracketing one hour
    ha1 = DM.Hour_Angle2(lon_alt, (dtime_alt - 0.5), doy, tzo)
    ha2 = DM.Hour_Angle2(lon_alt, (dtime_alt + 0.5), doy, tzo)
## EDITED: Taken from paper, but gives oversized time-step
##    ha1 = ha_ref - math.pi * ltime / 24
##    ha2 = ha_ref + math.pi * ltime / 24
    print "Hour Angle Start: ", ha1, "rad"
    print "Hour Angle End: ", ha2, "rad"
#Sunset Hour Angle
    ha_ss = DM.Sunset_Hour_Angle(latitude, solar_declination_angle)
    print "Sunset Hour Angle: ", ha_ss, "rad"
#Daily Extraterrestrial Radiation, R_a_day
    R_a_day = DM.XTerr_Radiation_Day(latitude, solar_declination_angle, ha_ss, earth_sun_distance)
    print "**Daily Extraterrestrial Radiation: ", R_a_day, "MJ*m^-2*day^-1"
#Hourly Extraterrestrial Radiation, R_a
    R_a_hr = DM.XTerr_Radiation_Period(latitude, solar_declination_angle, ha1, ha2, earth_sun_distance)
    print "**Hourly Extraterrestrial Radiation: ", R_a_hr, "MJ*m^-2*hour^-1"
    '''
    R_a_hr = R_a_short
    print "**Period Extraterrestrial Radiation: ", R_a_hr, "MJ*m^-2*day^-1"
    '''
#Daylight Hours
    Nhours = DM.Daylight_Hours(ha_ss)
    print "Daylight Hours: ", Nhours, "hours"
#Sunshine Hours
    nnhours = Nhours * (1 - (cloud_cover / 100))
    print "Sunshine Hours: ", nnhours, "hours"
#Solar Radiation
#assume Angstrom values, a_s & b_s
#a_s, fraction of radiation reaching Earth on overcast days, assume 0.25
    a_s = 0.25
#b_s, additional fraction reaching Earth on clear days, assume 0.5
    b_s = 0.5
    R_s_day = DM.Solar_Radiation(a_s, b_s, nnhours, Nhours, R_a_day)
    R_s_hr = DM.Solar_Radiation(a_s, b_s, nnhours, Nhours, R_a_hr)
    print "Solar Radiation, Day: ", R_s_day, "MJ*m^-2*day^-1"
    print "Solar Radiation, 1030: ", R_s_hr, "MJ*m^-2*day^-1"
#Clear Sky Solar Radiation
    R_so_day = DM.Solar_Radiation(a_s, b_s, Nhours, Nhours, R_a_day)
    R_so_hr = DM.Solar_Radiation(a_s, b_s, Nhours, Nhours, R_a_hr)
    print "Clear-Sky Solar Radiation, Day: ", R_so_day, "MJ*m^-2*day^-1"
    print "Clear-Sky Solar Radiation, 1030: ", R_so_hr, "MJ*m^-2*day^-1"
#Net Solar Radiation
    R_ns_day = DM.Net_Solar_Radiation(crop_a, R_s_day)
    R_ns_hr = DM.Net_Solar_Radiation(crop_a, R_s_hr)
    print "Net Solar Radiation, Day: ", R_ns_day, "MJ*m^-2*day^-1"
    print "Net Solar Radiation, 1030: ", R_ns_hr, "MJ*m^-2*day^-1"
#mean saturation vapor pressure, e_s
    e_zero_max = DM.Saturation_Vapor_Pressure(temp_C_max)
    e_zero_min = DM.Saturation_Vapor_Pressure(temp_C_min)
    e_s = (e_zero_max + e_zero_min) / 2 #MAYBE A BETTER WAY FOR USA WX DATA
    print "Mean Saturation Pressure, e_s: ", e_s, "kPa"
## Removed from Run version, but put in Module as Saturation_Vapor_Pressure_Alt
##    nsvp1 = 0.1 * ( 6.11 * 10 ** ( (7.5 * dewp_C) / (237.3 + dewp_C) ) )
##    print "Near-Surface Vapor Pressure (1): ", nsvp1, "kPa"
## Alternate Version from reference less preferred
##    nsvp3 = (RH_mean / 100) * satvp_mean
##    print "Near-Surface Vapor Pressure (3): ", nsvp3, "kPa"
#get actual (near-surface) vapor pressure, e_a
    e_a = DM.Saturation_Vapor_Pressure(dewp_C)
    print "Near-Surface Vapor Pressure: ", e_a, "kPa"
#Pyschometric constant
    gamma_pc = DM.Pyschometric_Constant(P_air)
    print "Pychometric constant: ", gamma_pc, "kPa*C^-1"
#Slope of saturation vapor pressure
    Delta_svp = DM.Slope_Saturation_Vapor_Pressure(temp_C_mid)
    print "Slope of saturation vapor pressure curve: ", Delta_svp, "kPa*C^-1"
#Net Longwave Radiation
    R_nl_day = DM.Net_Longwave_Radiation(temp_C_max, temp_C_min, e_a, R_s_day, R_so_day)
    R_nl_hr = DM.Net_Longwave_Radiation(temp_C_max, temp_C_min, e_a, R_s_hr, R_so_hr)
    print "Net Longwave Radiation: ", R_nl_day, "MJ*m^-2*day^-1"
    print "**Net Longwave Radiation: ", R_nl_hr, "MJ*m^-2*day^-1"
#Net Radiation
    R_n_day = R_ns_day - R_nl_day
    R_n_hr = R_ns_hr - R_nl_hr
    print "Net Radiation, Day: ", R_n_day, "MJ*m^-2*day^-1"
    print "Net Radiation, 1030: ", R_n_hr, "MJ*m^-2*day^-1"
#Soil Heat Flux
#Daily assumption
    G_day = 0.0
#Hourly assumptions
    G_hr = 0.1 * R_n_hr
    print "Soil Heat Flux, Day: ", G_day, "MJ*m^-2*day^-1"
    print "Soil Heat Flux, 1030: ", G_hr, "MJ*m^-2*day^-1"
#Reference Evapotranspiration
    ET_ref_day = DM.Reference_ET_day(Delta_svp, R_n_day, G_day, gamma_pc, temp_C_mid, 
        wind_speed, e_s, e_a, crop)
    ET_ref_hr = DM.Reference_ET_hr(Delta_svp, R_n_hr, G_hr, gamma_pc, temp_C_mid, 
        wind_speed, e_s, e_a, crop)
    print "Reference Evapotranspiration, Daily Rate: ", ET_ref_day, "mm*day^-1"
    print "Reference Evapotranspiration, 1030 Rate: ", ET_ref_hr, "mm*hour^-1"
#Air Density, Reference
    rho_air_ref = DM.Num37(P_air, temp_C_mid, 0)
    print "Air Density, Reference: ", rho_air_ref, "kg*m^-3"
#Latent Heat Flux, Reference
## Didn't seem quite right ... simple 28.4 conversion made sense, 7/31/2014
##    LE_ref1a = DM.Latent_Heat_Flux_PM(Delta_svp, R_n_hr, G_hr, gamma_pc, e_s, e_a,
##                                    rho_air_ref, r_surf, r_aero)
##    print "Latent Heat Flux, LE, Penman Monteith Form, 1030: ", LE_ref1a, "MJ*m^-2*day^-1"
##    LE_ref1 = LE_ref1a * 11.6
##    print "Latent Heat Flux, LE, Penman Monteith Form, 1030: ", LE_ref1, "W*m^-2"
    LE_reference = ET_ref_hr * 28.4 #jeff flag
    print "Latent Heat Flux, LE, Reference, 1030: ", LE_reference, "W*m^-2"
    return LE_reference, ET_ref_day, ET_ref_hr


def main(workspace, landsat_filepath_list, landsat_metapath,
                     dem_path, hot_shape_path, cold_shape_path, saveflag, recalc, crop, timezone):
    """
    main function for calling and executing the metric model

    workspace:              fresh folder to populate with the many metric model files and parameters
    saveflag:               parameter string to regulate intermediate output file generation
                                possible values include "ALL" , "LIMITED", "ET_ONLY"
    landsat_filepath_list:  list of landsat band tiff filepaths, MUST be in order [2,3,4,5,6,7,10,11]
    landsat_metapath:       filepath to the landsat metadata
    dem_path:               filepath to the digital elevation model
    hot_shape_path:         filepath to the shapefile outlining the hot pixels
    cold_shape_path:        filepath to the shapefile outlining the cold pixels
    """

    # initialize MetricModel objecet named "mike"
    mike = MetricModel(workspace, saveflag, recalc)
    mike.ingest_all_data(landsat_filepath_list, landsat_metapath, dem_path, hot_shape_path, cold_shape_path)
        
    time = mike.get_time()
    longitude = mike.get_longitude()
    latitude = mike.get_lattitude()
    earth_sun_distance = mike.get_earth_sun_distance()
    cloud_cover = mike.get_cloud_cover() # NEEDED FOR REFERENCE
    doy = mike.get_date()
    solar_declination_angle = mike.get_solar_declination_angle(doy)
    decimal_time = time[3]
    hour_angle = DM.Hour_Angle(longitude, decimal_time)

    temp_C_min = 24.4444    # NEEDED FOR REFERENCE
    temp_C_max = 32.7778    # NEEDED FOR REFERENCE
    temp_C_mid = 28.6111
    P_air = 1019.5
    wind_speed = 3.12928
    dewp_C = 21.6667

    LE_reference, ET_ref_day, ET_ref_hr = reference_calculation(longitude, latitude, earth_sun_distance, cloud_cover, doy, 
                                                                solar_declination_angle, decimal_time, temp_C_min, temp_C_max, 
                                                                temp_C_mid, P_air, wind_speed, dewp_C, crop, timezone)
    
    # Calculate net radiation
    slope = mike.get_slope()
    aspect = mike.get_aspect()
    solar_incidence_angle = mike.get_cosine_of_solar_incidence_angle(solar_declination_angle, latitude, slope, aspect, hour_angle)
    del slope
    del aspect
    del latitude
    del solar_declination_angle
    
    reflectance_bands = mike.get_reflectance_band(solar_incidence_angle)
    ####### For Band # use reflectance_bands[#-2] - see line 207
    SAVI = mike.get_SAVI(reflectance_bands[3], reflectance_bands[2])
    NDVI = mike.get_NDVI(reflectance_bands[3], reflectance_bands[2])
    LAI = mike.get_LAI(SAVI)
    del SAVI
    print "LAI Done"
    broad_band_surface_emissivity = mike.get_broadband_surface_emissivity(LAI)
    print "Broad band surface emissivity done"
    narrow_band_emissivity = mike.get_narrow_band_emissivity(LAI)
    print "narrow band emissivity done"
    atmospheric_pressure = mike.get_atmospheric_pressure()
    print "atmospheric pressure done"
    vapor_pressure = mike.get_vapor_pressure(dewp_C)
    del dewp_C
    print "vapor pressure done"
    water_in_atmosphere = mike.get_water_in_the_atmosphere(vapor_pressure, atmospheric_pressure, P_air)
    del vapor_pressure
    del P_air
    print "water in atmosphere is done"
    entisr_bands = mike.get_effective_narrowband_trasmittance1(atmospheric_pressure, water_in_atmosphere,
                                                               solar_incidence_angle)
    print "entisr bands are done"
    entsrrs_bands = mike.get_effective_narrowband_transmittance2(atmospheric_pressure, water_in_atmosphere)
    print "entsrrs bands are done"
    pr_bands = mike.get_per_band_path_reflectance(entisr_bands)
    print "pr bands are done"
    bbat = mike.get_broad_band_atmospheric_transmissivity(atmospheric_pressure, water_in_atmosphere,
                                                          solar_incidence_angle)
    del water_in_atmosphere
    print "broad band atmospheric trasmissivity is done"
    ibbswr = mike.get_incoming_broad_band_short_wave_radiation(solar_incidence_angle, bbat, earth_sun_distance)
    del solar_incidence_angle
    del earth_sun_distance
    print "incoming broad band short wave radiation"
    asr_bands = mike.get_at_surface_reflectance(reflectance_bands, entisr_bands, entsrrs_bands, pr_bands)
    del pr_bands
    del entsrrs_bands
    del entisr_bands
    del reflectance_bands
    print 'asr bands are done'
    bsa = mike.get_broadband_surface_albedo(asr_bands)
    del asr_bands
    print 'broadband surface albedo is done'
    eae = mike.get_effective_atmospheric_transmissivity(bbat)
    del bbat
    print 'effective effective atmospheric transmissivty is done'
    surface_temperature = mike.get_surface_temperature(narrow_band_emissivity)
    del narrow_band_emissivity
    print 'surface temperature is done'
    ilwr = mike.get_incoming_long_wave_radiation(eae, temp_C_mid)
    del eae
    del temp_C_mid
    print 'incoming long wave radtion is done'
    olwr = mike.get_outgoing_long_wave_radiation(broad_band_surface_emissivity, surface_temperature)
    print 'outgoing long wave radiation is done'
    mike.get_net_radiation(ibbswr, bsa, olwr, ilwr, broad_band_surface_emissivity)
    del olwr
    del ilwr
    del ibbswr
    del broad_band_surface_emissivity
    print 'net radiation is done'

    # Calculate soil heat flux
    g_ratio = mike.get_soil_heat_flux_to_net_radiation_ratio(bsa, surface_temperature, NDVI)
    del bsa
    del NDVI
    print 'soil heat flux to net radiation ratio is done'
    mike.get_soil_heat_flux(g_ratio)
    del g_ratio
    print 'soil heat flux is done'

    # Calculate sensible heat flux
    mike.get_sensible_heat_flux(LAI, wind_speed, atmospheric_pressure, surface_temperature, LE_reference)
    mike.get_latent_heat_vaporization(surface_temperature)
    del surface_temperature
    del atmospheric_pressure
    del wind_speed
    del LAI
    print 'sensible heat flux is done'

    # Calculate LE
    mike.get_latent_energy_consumed_by_ET()
    print 'latent energy is done'
    
    mike.get_instantaneous_evapotranspiration()
    mike.get_ETrF(ET_ref_hr)
    mike.get_daily_evapotranspiration(ET_ref_day)
    print 'ET 1 is done'

    mike.get_evapotranspiration_instant()
    mike.get_ET_fraction(ET_ref_hr)
    mike.get_evapotranspiration_day(ET_ref_day)
    del ET_ref_day
    del ET_ref_hr
    print 'ET 2 is done'

    return mike

class Timer:
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start

if __name__ == "__main__":
    with Timer() as t:
        main()

    print('Time elapsed %0.3f sec' % t.interval)
