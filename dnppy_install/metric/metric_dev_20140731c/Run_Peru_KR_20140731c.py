import os

#Set time zone offset for project
#Peru Time (PET) is 5 hours behind UTC
tzo = 5.0
#Set output directory (primary ArcGIS workspace)
outdir = "C:\\arcgis\\projects\\peru\\output"

#Test file connections if script is run from IDE or Python console
#read in Landsat
landsat_dir = "C:\\Users\\kwross\\Documents\\Work\\Peru\\metric_data\\landsat\\December_2013"

#Landsat 8 Filenames (Metadata, Bands 2-7, Bands 10-11, Weather Data)
f_meta = "LC80090652013357LGN00_MTL.txt"
f_band2 = "LC80090652013357LGN00_B2.tif"
f_band3 = "LC80090652013357LGN00_B3.tif"
f_band4 = "LC80090652013357LGN00_B4.tif"
f_band5 = "LC80090652013357LGN00_B5.tif"
f_band6 = "LC80090652013357LGN00_B6.tif"
f_band7 = "LC80090652013357LGN00_B7.tif"
f_band10 = "LC80090652013357LGN00_B10.tif"
f_band11 = "LC80090652013357LGN00_B11.tif"

#Landsat Fullpath Names
fmeta = os.path.join(landsat_dir, f_meta)
fb2 = os.path.join(landsat_dir, f_band2)
fb3 = os.path.join(landsat_dir, f_band3)
fb4 = os.path.join(landsat_dir, f_band4)
fb5 = os.path.join(landsat_dir, f_band5)
fb6 = os.path.join(landsat_dir, f_band6)
fb7 = os.path.join(landsat_dir, f_band7)
fb10 = os.path.join(landsat_dir, f_band10)
fb11 = os.path.join(landsat_dir, f_band11)

#Read in DEM
dem_dir = "C:\\Users\\kwross\\Documents\\Work\\Peru\\metric_data\\dem"
f_DEM = "projectedDEM1.tif"
fdem = os.path.join(dem_dir, f_DEM)

#Read in Weather
wx_dir = "C:\\Users\\kwross\\Documents\\Work\\Peru\\metric_data\\wx_data"
f_wx_data = "Dec2013.txt"
fwx = os.path.join(wx_dir, f_wx_data)

#Read in Reference Pixels
refpix_dir = "C:\\Users\\kwross\\Documents\\Work\\Peru\\metric_data\\refpix"
hotpix_shp = "ColdPixels.shp"
coldpix_shp = "HotPixels.shp"
fhpx = os.path.join(refpix_dir, hotpix_shp)
fcpx = os.path.join(refpix_dir, coldpix_shp)
fhtbl = os.path.join(refpix_dir, "hotstats.dbf")
fctbl = os.path.join(refpix_dir, "coldstats.dbf")

#Function for call from toolbox or otherwise
def DVLP_metric_run(fmeta, fb2, fb3, fb4, fb5, fb6, fb7, fb10, fb11, fdem,
                    wx_dir, fhpx, fcpx, fhtbl, fctbl, outdir, tzo):

    import arcpy

    from arcpy import env
    import math
    import os
    import string
    import Develop_Module_KR_20140731c as DM
##    arcpy.env.workspace = "C:\\arcgis\\projects\\peru\\output" EDITED 7/27/2014
##    outdir = "C:\\arcgis\\projects\\peru\\output" EDITED 7/28/2014
    arcpy.env.workspace = outdir
    arcpy.env.scratchWorkspace = "C:\\arcgis\\scratch\\scratch.gdb"
    arcpy.env.overwriteOutput= True
    #Set Pixel Sizes by Landsat 8
    arcpy.env.cellSize = fb2
    arcpy.env.snapRaster = fb2

    landsat_dir = os.path.dirname(fmeta)
    landsat_base = os.path.basename(fmeta)
    landsat_root = os.path.splitext(landsat_base)[0]
    print "Landsat 8 pathname: ", landsat_dir
    print "Landsat 8 metadata file: ", fmeta
##    print "Landsat 8 meta filename: ", landsat_base
##    print "Landsat 8 meta root name: ", landsat_root
##    print os.listdir(landsat_dir)

    #Get Metadata File and Read in as String
    metadata = open(fmeta, 'r')
    meta_lines = metadata.read()

    #Landsat Metadata Parsing
    #Get Date
    Date = meta_lines.split("DATE_ACQUIRED = ")[1].split("\n")[0]
    year  = float(Date[0:4])
    month = float(Date[5:7])
    day   = float(Date[8:10])
    print "Day: ", day
    print "Month: ", month
    print "Year: ", year

    #Get Time
    Time = meta_lines.split("SCENE_CENTER_TIME = ")[1].split("\n")[0]
    hours   = float(Time[0:2])
    minutes = float(Time[3:5])
    seconds = float(Time[6:8])
    decimal_time = ((minutes * 60 + seconds) / 3600) + hours
    decimal_time = decimal_time / 24
    print "Hours: ", hours
    print "Minutes: ", minutes
    print "Seconds: ", seconds
    print "Decimal Time: ", decimal_time

    #Get Longitude
    lon_UL = float(meta_lines.split("CORNER_UL_LON_PRODUCT = ")[1].split("\n")[0])
    lon_UR = float(meta_lines.split("CORNER_UR_LON_PRODUCT = ")[1].split("\n")[0])
    lon_LL = float(meta_lines.split("CORNER_LL_LON_PRODUCT = ")[1].split("\n")[0])
    lon_LR = float(meta_lines.split("CORNER_LR_LON_PRODUCT = ")[1].split("\n")[0])

    lon = (lon_UL + lon_UR + lon_LL + lon_LR) / 4
    lon = lon * math.pi / 180
    print "Longitude: ", lon, "rad"

    #Get Latitude
    lat_UL = float(meta_lines.split("CORNER_UL_LAT_PRODUCT = ")[1].split("\n")[0])
    lat_UR = float(meta_lines.split("CORNER_UR_LAT_PRODUCT = ")[1].split("\n")[0])
    lat_LL = float(meta_lines.split("CORNER_LL_LAT_PRODUCT = ")[1].split("\n")[0])
    lat_LR = float(meta_lines.split("CORNER_LR_LAT_PRODUCT = ")[1].split("\n")[0])

    lat = (lat_UL + lat_UR + lat_LL + lat_LR) / 4
    lat = lat * math.pi / 180
    print "Latitude: ", lat, "rad"

    #Get Earth-Sun Distance
    earth_sun_distance = float(meta_lines.split("EARTH_SUN_DISTANCE = ")[1].split("\n")[0])
    print "Earth Sun Distance: ", earth_sun_distance

    #Get Cloud Cover
    cloud_cover = float(meta_lines.split("CLOUD_COVER = ")[1].split("\n")[0])
    print "Landsat Cloud Cover: ", cloud_cover, "%"

    #Find DOY
    jd_landsat = DM.date_to_jd(year,month,day)
    jd_january = DM.date_to_jd(year,1,1)
    DOY = jd_landsat - jd_january + 1
    print "Day Of Year: ", DOY

    #Calculate Solar Declination Angle
    declin = DM.Dec(DOY)
    print "Declination: ", declin, "rad"
    #Hour Angle (0 at noon, negative AM, positive PM
    hour_a = DM.Hour_Angle(lon, decimal_time)
    print "Hour Angle: ", hour_a, "rad"
    #Cosine of estimated solar zenith angle
    cth = DM.Num8(declin, lat, hour_a)
    print "Cosine of Theta Angle: ", cth, "<->"

    #Get Sun Elevation Angle (SEA)
    sea = float(meta_lines.split("SUN_ELEVATION = ")[1].split("\n")[0])
    print "SEA: ", sea, "deg"

    #Calculate Sine of SEA to Check with CTH
    sin_sea = math.sin(sea * math.pi / 180 )
    print "Sine of the Sun Elevation Angle: ", sin_sea, "<->"

    #Get Weather Data
    wx_return = DM.Wx_Data_Extract_PERU_WFP(fwx, year, month, day)

    #Unpack returned tuple
    temp_C_avg = wx_return[0]
    temp_C_min = wx_return[1]
    temp_C_max = wx_return[2]
    RH_mean = wx_return[3]
    precip = wx_return[4]
    wind_speed = wx_return[5]
    P_air = wx_return[6]
    temp_C_mid = wx_return[7]
    dewp_C = wx_return[8]

    #Check returned tuple
    print "Temperature Mean: ", temp_C_avg, "Celsius"
    print "Temperature Minimum: ", temp_C_min, "Celsius"
    print "Temperature Maximum: ", temp_C_max, "Celsius"
    print "Relative Humidity, Daily Mean: ", RH_mean, "%"
    print "Precipitation, Daily Total: ", precip, "mm"
    print "Wind Speed from Weather Data: ", wind_speed, "m/s"
    print "Air Pressure at Surface, Reference Daily Mean: ", P_air, "kPa"
    print "Temperature Mid-point (Max+Min)/2: ", temp_C_mid, "Celsius"
    print "Dewpoint: ", dewp_C, "Celsius"

    ##Initial weather & biophysical reference calcs
    #reference crop height (m) & albedo (unitless) *grass*
    crop_hgt = 0.12
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
    lon_alt = -lon * 180 / math.pi
    dtime_alt = decimal_time * 24
    ltime = dtime_alt - tzo
    print "Acquisition Time, Local: ", ltime, "Decimal Hours"
    ha_ref = DM.Hour_Angle2(lon_alt, dtime_alt, DOY, tzo)
    print "Hour Angle Alt: ", ha_ref, "rad"
    #hour angles bracketing one hour
    ha1 = DM.Hour_Angle2(lon_alt, (dtime_alt - 0.5), DOY, tzo)
    ha2 = DM.Hour_Angle2(lon_alt, (dtime_alt + 0.5), DOY, tzo)
## EDITED: Taken from paper, but gives oversized time-step
##    ha1 = ha_ref - math.pi * ltime / 24
##    ha2 = ha_ref + math.pi * ltime / 24
    print "Hour Angle Start: ", ha1, "rad"
    print "Hour Angle End: ", ha2, "rad"

    #Sunset Hour Angle
    ha_ss = DM.Sunset_Hour_Angle(lat, declin)
    print "Sunset Hour Angle: ", ha_ss, "rad"

    #Daily Extraterrestrial Radiation, R_a_day
    R_a_day = DM.XTerr_Radiation_Day(lat, declin, ha_ss, earth_sun_distance)
    print "**Daily Extraterrestrial Radiation: ", R_a_day, "MJ*m^-2*day^-1"

    #Hourly Extraterrestrial Radiation, R_a
    R_a_short = DM.XTerr_Radiation_Period(lat, declin, ha1, ha2, earth_sun_distance)
    print "**Hourly Extraterrestrial Radiation: ", R_a_short, "MJ*m^-2*hour^-1"
    R_a_hr = R_a_short * 24
    print "**Period Extraterrestrial Radiation: ", R_a_hr, "MJ*m^-2*day^-1"

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
    e_s = (e_zero_max + e_zero_min) / 2
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
    ET_ref_day = DM.Reference_ET(Delta_svp, R_n_day, G_day, gamma_pc, temp_C_mid,
                             wind_speed, e_s, e_a)
    ET_ref_hr = DM.Reference_ET(Delta_svp, R_n_hr, G_hr, gamma_pc, temp_C_mid,
                             wind_speed, e_s, e_a)
    ET_ref_hourly = ET_ref_hr / 24
    print "Reference Evapotranspiration, Daily Rate: ", ET_ref_day, "mm*day^-1"
    print "Reference Evapotranspiration, 1030 Rate: ", ET_ref_hr, "mm*day^-1"
    print "Reference Evapotranspiration, 1030 Hourly Rate: ", ET_ref_hourly, "mm*hour^-1"

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
    LE_ref = ET_ref_hr * 28.4
    print "Latent Heat Flux, LE, Reference, 1030: ", LE_ref, "W*m^-2"

## Comment out from here down to turn off raster calcs
    #Cast Landsat 8 Bands to Raster
    L8Bnd02 = arcpy.Raster(fb2)
    L8Bnd03 = arcpy.Raster(fb3)
    L8Bnd04 = arcpy.Raster(fb4)
    L8Bnd05 = arcpy.Raster(fb5)
    L8Bnd06 = arcpy.Raster(fb6)
    L8Bnd07 = arcpy.Raster(fb7)
    L8Bnd10 = arcpy.Raster(fb10)
    L8Bnd11 = arcpy.Raster(fb11)

    #make DEM into Raster
    DEM = arcpy.sa.Float(fdem)

    #Calculate Slope
    sfname = "slope_temp.tif"
    sfpath = os.path.join(outdir, sfname)
    if os.path.isfile(sfpath):
        print "Reading previously estimated slopes... "
        slope = arcpy.Raster(sfpath)
    else:
        print "Calculating elevation derivatives... "
        slope = arcpy.sa.Slope(DEM)
        #cap slopes at 30 degrees to tamp down DEM artifacts
        slope = arcpy.sa.Con(slope, slope, 30, "VALUE < 30")
        #convert degrees to radians
        slope = slope * math.pi / 180
        slope.save(sfname)

    #Calculate Aspect
    afname = "aspect_temp.tif"
    afpath = os.path.join(outdir, afname)
    if os.path.isfile(afpath):
        print "Reading previously estimated aspects... "
        aspect = arcpy.Raster(afpath)
    else:
        aspect = arcpy.sa.Aspect(DEM)
        #get rid of -1 "slope 0" flag
        aspect = arcpy.sa.Con(aspect, aspect, math.pi, "VALUE > -1")
        #convert degrees to radians and rotate half turn to put 0 aspect to south
        aspect = ( aspect * math.pi / 180 ) - math.pi
        aspect.save(afname)

    #Calculate Cosine of Solar Incidence Angle
    siname = "sia_output.tif"
    sipath = os.path.join(outdir, siname)
    if os.path.isfile(sipath):
        print "Reading previously estimated cosine of solar incidence angles... "
        sia = arcpy.Raster(sipath)
    else:
        print "Calculating cosine of solar incidence angles... "
        sia = DM.Num7( declin, lat, slope, aspect, hour_a)
        sia.save(siname)

    #Calculate Reflectance for Landsat 8 bands 2-7
    print "Calculating per-band TOA reflectances... "

    #TOA reflectance Band 2
    rb02name = "Refl_Band_02.tif"
    rb02path = os.path.join(outdir, rb02name)
    if os.path.isfile(rb02path):
        ReflBnd02 = arcpy.Raster(rb02path)
    else:
        ReflBnd02 = DM.Num10(L8Bnd02, sia)
        ReflBnd02.save(rb02name)

    #TOA reflectance Band 3
    rb03name = "Refl_Band_03.tif"
    rb03path = os.path.join(outdir, rb03name)
    if os.path.isfile(rb03path):
        ReflBnd03 = arcpy.Raster(rb03path)
    else:
        ReflBnd03 = DM.Num10(L8Bnd03, sia)
        ReflBnd03.save(rb03name)

    #TOA reflectance Band 4
    rb04name = "Refl_Band_04.tif"
    rb04path = os.path.join(outdir, rb04name)
    if os.path.isfile(rb04path):
        ReflBnd04 = arcpy.Raster(rb04path)
    else:
        ReflBnd04 = DM.Num10(L8Bnd04, sia)
        ReflBnd04.save(rb04name)

    #TOA reflectance Band 5
    rb05name = "Refl_Band_05.tif"
    rb05path = os.path.join(outdir, rb05name)
    if os.path.isfile(rb05path):
        ReflBnd05 = arcpy.Raster(rb05path)
    else:
        ReflBnd05 = DM.Num10(L8Bnd05, sia)
        ReflBnd05.save(rb05name)

    #TOA reflectance Band 6
    rb06name = "Refl_Band_06.tif"
    rb06path = os.path.join(outdir, rb06name)
    if os.path.isfile(rb06path):
        ReflBnd06 = arcpy.Raster(rb06path)
    else:
        ReflBnd06 = DM.Num10(L8Bnd06, sia)
        ReflBnd06.save(rb06name)

    #TOA reflectance Band 7
    rb07name = "Refl_Band_07.tif"
    rb07path = os.path.join(outdir, rb07name)
    if os.path.isfile(rb07path):
        ReflBnd07 = arcpy.Raster(rb07path)
    else:
        ReflBnd07 = DM.Num10(L8Bnd07, sia)
        ReflBnd07.save(rb07name)

    #Calculating Num19: SAVI
    L = 0.1 #Assuming Climate/Elevation similar to that of Western U.S.
    print "Calculating SAVI assuming L = (", L, ")"
    svname = "savi_output.tif"
    svpath = os.path.join(outdir, svname)
    if os.path.isfile(svpath):
        savi = arcpy.Raster(svpath)
    else:
        savi = DM.Num19(ReflBnd05, ReflBnd04, L)
        savi.save(svname)
    print "SAVI [min, mean, max]: ", savi.minimum, savi.mean, \
                                     savi.maximum, "<->"

    #Calculating Num23: NDVI
    print "Calculating NDVI... "
    ndname = "ndvi_output.tif"
    ndpath = os.path.join(outdir, ndname)
    if os.path.isfile(ndpath):
        ndvi = arcpy.Raster(ndpath)
    else:
        ndvi = DM.Num23(ReflBnd05, ReflBnd04)
        ndvi.save(ndname)
    print "NDVI [min, mean, max]: ", ndvi.minimum, ndvi.mean, \
                                     ndvi.maximum, "<->"

    #Calculating Num18: LAI
    print "Calculating LAI... "
    laname = "lai_output.tif"
    lapath = os.path.join(outdir, laname)
    if os.path.isfile(lapath):
        lai = arcpy.Raster(lapath)
    else:
        lai = DM.Num18(savi)
        lai.save(laname)
    print "LAI [min, mean, max]: ", lai.minimum, lai.mean, \
                                     lai.maximum, "m^2*m^-2"

    #Calculating Num17: Broadband Surface Emissivity
    print "Calculating broadband surface emissivity... "
    bbse = DM.Num17(lai)
    bbse.save( "bbse_output.tif" )

    #Calculating Num22: Narrow Band Emissivity
    print "Calculating narrow band emissivity... "
    nbe = DM.Num22(lai)
    nbe.save( "nbe_output.tif" )

    #Calculate Initial Thermal Radiances
    print "Calculating thermal radiances... "
    thermRad10 = DM.L8_Thermal_Radiance(L8Bnd10)
    thermRad10.save( "thermRad10_output.tif" )
    thermRad11 = DM.L8_Thermal_Radiance(L8Bnd11)
    thermRad11.save( "thermRad11_output.tif" )

    #Assumed or estimated constants for Corrected Radiances
    #"No Correction" assumptions ... CHANGE IF BETTER VALUES KNOWN
    #Path Radiance
    pathRad = 0
    #Narrow Band Transmissivity
    nbt = 1
    #Narrow Band Downward Thermal Radiation from Clear Sky
    skyRad = 0

    ## METRIC Idaho estimates
    ## pathRad = 0.91
    ## nbt = 0.866
    ## skyRad = 1.32

    #calculate Num21: Corrected Thermal Radiances
    corrRad10 = DM.Num21(thermRad10, pathRad, nbt, nbe, skyRad)
    corrRad10.save( "corrRad10_output.tif" )
    corrRad11 = DM.Num21(thermRad11, pathRad, nbt, nbe, skyRad)
    corrRad11.save( "corrRad11_output.tif" )

    #calculate Num20: Surface Temperature
    #uses Landsat 7 values for K1, K2 and should be tweaked for Landsat 8
    print "Calculating surface temperatures... "
    sfcTemp10 = DM.Num20(corrRad10, nbe, 774.89, 1321.08)
    sfcTemp11 = DM.Num20(corrRad11, nbe, 480.89, 1201.14)
    sfcTemp = (sfcTemp10 + sfcTemp11) / 2
    sfcTemp.save( "sfcTemp_output.tif" )
    print "T_s [min, mean, max]: ", sfcTemp.minimum, sfcTemp.mean, \
                                    sfcTemp.maximum, "Kelvin"
    #Finds the Near-Surface Air Temperature for use in Num24
    temp_K_mid = temp_C_mid + 273.15
    print "Near Surface Air Temperature: ", temp_K_mid, "Kelvin"

    #calculate Num5: Atmospheric Pressure
    print "Calculating elevation-adjusted ""standard"" pressures... "
    p = DM.Num5(DEM)
    print "p [min, mean, max]: ", p.minimum, p.mean, p.maximum, "kPa"
    p.save( "p_output.tif" )
    print "Air Pressure at Surface, Reference Daily Mean: ", P_air, "kPa"

    #Calculate Num6: Water in the Atmosphere
    print "Calculating water in atmosphere... "
    w = DM.Num6(e_a, p)
    print "W [min, mean, max]: ", w.minimum, w.mean, w.maximum, "mm"
    w.save( "w_output.tif" )
    w_ref = DM.Num6(e_a, P_air)
    print "Water in Atmosphere, Reference, W: ", w_ref, "mm"

    #Calculates Num12: Effective Narrowband Transmittance
    #For Incoming Solar Radiation for each band 2-7;
    #Uses Landsat 7 constants for now but should use Landsat 8 ones instead
    print "Calculating effective narrowband transmittance for incoming... "
    kt = 1.0 #unitless turbidity coefficient, assuming clean air
    entisrBnd02 = DM.Num12(p, w, cth, kt, 0.987, -0.00071, 0.000036, 0.0880,  0.0789)
    entisrBnd02.save( "entisrBnd02_output.tif" )
    entisrBnd03 = DM.Num12(p, w, cth, kt, 2.319, -0.00016, 0.000105, 0.0437, -1.2697)
    entisrBnd03.save( "entisrBnd03_output.tif" )
    entisrBnd04 = DM.Num12(p, w, cth, kt, 0.951, -0.00033, 0.000280, 0.0875,  0.1014)
    entisrBnd04.save( "entisrBnd04_output.tif" )
    entisrBnd05 = DM.Num12(p, w, cth, kt, 0.375, -0.00048, 0.005018, 0.1355,  0.6621)
    entisrBnd05.save( "entisrBnd05_output.tif" )
    entisrBnd06 = DM.Num12(p, w, cth, kt, 0.234, -0.00101, 0.004336, 0.0560,  0.7757)
    entisrBnd06.save( "entisrBnd06_output.tif" )
    entisrBnd07 = DM.Num12(p, w, cth, kt, 0.365, -0.00097, 0.004296, 0.0155,  0.6390)
    entisrBnd07.save( "entisrBnd07_output.tif" )

    #Calculates Num13: Effective Narrowband Transmittance
    #For Shortwave Radiation Reflected From The Surface for each band 2-7;
    #Uses Landsat 7 constants for now but should use Landsat 8 ones instead
    print "Calculating effective narrowband transmittance for outbound... "
    cos_n = 1 #for Landsat, since Landsat has essentially a nadir view angle
    entsrrsBnd02 = DM.Num13(p, w, cos_n, kt, 0.987, -0.00071, 0.000036, 0.0880,  0.0789)
    entsrrsBnd02.save( "entsrrsBnd02_output.tif" )
    entsrrsBnd03 = DM.Num13(p, w, cos_n, kt, 2.319, -0.00016, 0.000105, 0.0437, -1.2697)
    entsrrsBnd03.save( "entsrrsBnd03_output.tif" )
    entsrrsBnd04 = DM.Num13(p, w, cos_n, kt, 0.951, -0.00033, 0.000280, 0.0875,  0.1014)
    entsrrsBnd04.save( "entsrrsBnd04_output.tif" )
    entsrrsBnd05 = DM.Num13(p, w, cos_n, kt, 0.375, -0.00048, 0.005018, 0.1355,  0.6621)
    entsrrsBnd05.save( "entsrrsBnd05_output.tif" )
    entsrrsBnd06 = DM.Num13(p, w, cos_n, kt, 0.234, -0.00101, 0.004336, 0.0560,  0.7757)
    entsrrsBnd06.save( "entsrrsBnd06_output.tif" )
    entsrrsBnd07 = DM.Num13(p, w, cos_n, kt, 0.365, -0.00097, 0.004296, 0.0155,  0.6390)
    entsrrsBnd07.save( "entsrrsBnd07_output.tif" )

    #Calculates Num14: Per Band Path Reflectance for each band 2-7
    #Uses Landsat 7 constants for now but should use Landsat 8 ones instead
    print "Calculating surface reflectance (METRIC Method)... "
    prBnd02 = DM.Num14(entisrBnd02, 0.254)
    prBnd02.save( "prBnd02_output.tif" )
    prBnd03 = DM.Num14(entisrBnd03, 0.149)
    prBnd03.save( "prBnd03_output.tif" )
    prBnd04 = DM.Num14(entisrBnd04, 0.147)
    prBnd04.save( "prBnd04_output.tif" )
    prBnd05 = DM.Num14(entisrBnd05, 0.311)
    prBnd05.save( "prBnd05_output.tif" )
    prBnd06 = DM.Num14(entisrBnd06, 0.103)
    prBnd06.save( "prBnd06_output.tif" )
    prBnd07 = DM.Num14(entisrBnd07, 0.036)
    prBnd07.save( "prBnd07_output.tif" )
    ## ACK! old version was all pointed at Band 2 ???
##    prBnd02 = DM.Num14(entisrBnd02, 0.254)
##    prBnd02.save( "prBnd02_output.tif" )
##    prBnd02 = DM.Num14(entisrBnd02, 0.149)
##    prBnd02.save( "prBnd03_output.tif" )
##    prBnd02 = DM.Num14(entisrBnd02, 0.147)
##    prBnd02.save( "prBnd04_output.tif" )
##    prBnd02 = DM.Num14(entisrBnd02, 0.311)
##    prBnd02.save( "prBnd05_output.tif" )
##    prBnd02 = DM.Num14(entisrBnd02, 0.103)
##    prBnd02.save( "prBnd06_output.tif" )
##    prBnd02 = DM.Num14(entisrBnd02, 0.036)
##    prBnd02.save( "prBnd07_output.tif" )

    #Calculates Num4: Broad-Band Atmospheric Transmissivity
    print "Calculating broad-band atmospheric tranmissivity... "
    bbat = DM.Num4(p, w, cth, kt)
    bbat.save( "bbat_output.tif" )
    bbat_ref = DM.Num4(P_air, w_ref, cth, kt)
    print "Broadband Atmospheric Transmissivity, Reference, tau_sw: ", bbat_ref, "<->"

    #Calculates Num3: Incoming Broad-Band Short-Wave Radiation
    print "Calculating downwelling broad-band shortwave radiantion, R_S_in... "
    ibbswr = DM.Num3(sia, bbat, earth_sun_distance)
    ibbswr.save( "ibbswr_output.tif" )
    ibbswr_ref = DM.Num3(cth, bbat_ref, earth_sun_distance)
    print "R_S_in [min, mean, max]: ", ibbswr.minimum, ibbswr.mean, \
                                       ibbswr.maximum, "W*m^-2"
    print "Incoming Broad-Band Shortwave Radiation, Reference, R_S_in: ", ibbswr_ref, "W*m^-2"

    #Calculates Num11: At-Surface Reflectance for each badn 2-7
    print "Calculating surface albedo, alpha... "
    asrBnd02 = DM.Num11(ReflBnd02, entisrBnd02, entsrrsBnd02, prBnd02)
    asrBnd02.save( "asrBnd02_output.tif" )
    asrBnd03 = DM.Num11(ReflBnd03, entisrBnd03, entsrrsBnd03, prBnd03)
    asrBnd03.save( "asrBnd03_output.tif" )
    asrBnd04 = DM.Num11(ReflBnd04, entisrBnd04, entsrrsBnd04, prBnd04)
    asrBnd04.save( "asrBnd04_output.tif" )
    asrBnd05 = DM.Num11(ReflBnd05, entisrBnd05, entsrrsBnd05, prBnd05)
    asrBnd05.save( "asrBnd05_output.tif" )
    asrBnd06 = DM.Num11(ReflBnd06, entisrBnd06, entsrrsBnd06, prBnd06)
    asrBnd06.save( "asrBnd06_output.tif" )
    asrBnd07 = DM.Num11(ReflBnd07, entisrBnd07, entsrrsBnd07, prBnd07)
    asrBnd07.save( "asrBnd07_output.tif" )
    ## ACK! More Band 2 pointing ???
##    asrBnd02 = DM.Num11(ReflBnd02, entisrBnd02, entsrrsBnd02, prBnd02)
##    asrBnd02.save( "asrBnd02_output.tif" )
##    asrBnd03 = DM.Num11(ReflBnd02, entisrBnd02, entsrrsBnd02, prBnd02)
##    asrBnd03.save( "asrBnd03_output.tif" )
##    asrBnd04 = DM.Num11(ReflBnd02, entisrBnd02, entsrrsBnd02, prBnd02)
##    asrBnd04.save( "asrBnd04_output.tif" )
##    asrBnd05 = DM.Num11(ReflBnd02, entisrBnd02, entsrrsBnd02, prBnd02)
##    asrBnd05.save( "asrBnd05_output.tif" )
##    asrBnd06 = DM.Num11(ReflBnd02, entisrBnd02, entsrrsBnd02, prBnd02)
##    asrBnd06.save( "asrBnd06_output.tif" )
##    asrBnd07 = DM.Num11(ReflBnd02, entisrBnd02, entsrrsBnd02, prBnd02)
##    asrBnd07.save( "asrBnd07_output.tif" )

    #Calculates Num15:  Broadband Surface Albedo
    asr_list = [asrBnd02, asrBnd03, asrBnd04, asrBnd05, asrBnd06, asrBnd07]
    coefficient_list = [0.254, 0.149, 0.147, 0.311, 0.103, 0.036]
    alname = "bsa_output.tif"
    alpath = os.path.join(outdir, alname)
    bsa = DM.Num15(asr_list, coefficient_list)
    bsa.save(alname)
    ## CONDITIONAL VERSION OFF
##    if os.path.isfile(alpath):
##        bsa = arcpy.Raster(alpath)
##    else:
##        bsa = DM.Num15(asr_list, coefficient_list)
##        bsa.save(alname)
    #albedo for *grass* reference
    print "Sfc. Albedo [min, mean, max]: ", bsa.minimum, bsa.mean, \
                                            bsa.maximum, "<->"
    bsa_ref = 0.23
    print "Broad-Band Surface Albedo, Reference: ", bsa_ref, "<->"

    #Calculates Num25: Effective Atmospheric Transmissivity (Dimensionless)
    eae = DM.Num25(bbat)
    eae.save( "eae_output.tif" )

    #Calculates Num26: Ratio of Soil Heat Flux to Net Radiation
    g_ratio = DM.Num26(bsa, sfcTemp, ndvi)
    g_ratio.save( "g_ratio_output.tif" )
    print "G/Rn [min, mean, max]: ", g_ratio.minimum, g_ratio.mean, \
                                     g_ratio.maximum, "<->"

    #Calculates Num33: Momentum Roughness Length in meteres
    zom = DM.Num33(lai)
    zom.save( "zom_output.tif" )
    print "z_om [min, mean, max]: ", zom.minimum, zom.mean, \
                                     zom.maximum, "m"

    #Calculates Num24: Incoming Long-Wave Radiation
    ##I feel like something is wrong here... BAD EXPONENT 7/29/2014
    ilwr = DM.Num24(eae, temp_K_mid)
    ilwr.save( "ilwr_output.tif" )
    print "R_L_in [min, mean, max]: ", ilwr.minimum, ilwr.mean, \
                                       ilwr.maximum, "W*m^-2"

    #Calculates Num16: Outgoing Long-Wave Radiation
    ##I feel like something is wrong here... BAD EXPONENT 7/29/2014
    olwr = DM.Num16(bbse, sfcTemp)
    olwr.save( "olwr_output.tif" )
    print "R_L_out [min, mean, max]: ", olwr.minimum, olwr.mean, \
                                        olwr.maximum, "W*m^-2"

    #Calculates Num2: Net Radiation
    ##I feel like something is wrong here... OK NOW I THINK
    netRad = DM.Num2(ibbswr, bsa, olwr, ilwr, bbse)
    netRad.save( "netRad_output.tif" )
    print "R_n [min, mean, max]: ", netRad.minimum, netRad.mean, \
                                    netRad.maximum, "W*m^-2"

    #Calculates Soil Heat Flux
    SoilHeatFlux = netRad * g_ratio
    SoilHeatFlux.save( "soilheatflux_output.tif" )
    print "G [min, mean, max]: ", SoilHeatFlux.minimum, SoilHeatFlux.mean, \
                                  SoilHeatFlux.maximum, "W*m^-2"

## DR ROSS ACTIVE EDIT LINE 7/29/2014 1133AM
##    #Calculates Num27a: Ratio of Soil Heat Flux to Net Radiation (Alt, Cond. A)
##    #LAI >= 0.5
##    g_ratio_alt_A = DM.Num27a(lai)
##    g_ratio_alt_A.save( "g_ratio_alt_A_output.tif" )
##
##    #Calculates Num27b: Ratio of Soil Heat Flux to Net Radiation (Alt, Cond. B)
##    #LAI < 0.5
##    g_ratio_alt_B = DM.Num27b(sfcTemp, netRad)
##    g_ratio_alt_B.save( "g_ratio_alt_B_output.tif" )
##
##    #Calculates Num37: Air Density
##    air_dens = DM.Num37(p, sfcTemp, dT)
##    air_dens.save( "air_density_output.tif" )
##    #NEED EQUATION 29
##
##    #Calculates Num28: Sensible Heat Flux
##    sens_heat_flux = DM.Num28(air_dens, C_p??, dT, r_ah)
##    sens_heat_flux.save( "sens_heat_flux_output.save" )
##    #NEED EQUATION 29, 30, AND C_p
##
    #Calculates Num35: Momentum Roughness Length for Mountainous Terrain
    zom_mtn = DM.Num35(zom, slope)
    zom_mtn.save( "zom_mtn_output.tif" )

    #Define Elevation_Station: Elevation where Wind Speed is Measured
    #Elevation Peru station
    elev_wx = float(1205)

    #Calculates Num36: Wind Speed Weighting Coefficient
    wcoeff = DM.Num36(DEM, elev_wx)
    wcoeff.save( "wcoeff_output.tif" )

    #Calculates T_s_datum
    #Peru reference elevation set to 2670
    elev_ts_datum = 2670
    T_s_datum = DM.Datum_Ref_Temp(sfcTemp, DEM, elev_ts_datum)
    T_s_datum.save( "t_s_datum_output.tif" )
##    #assumes that lapse rate is 10*C/km
##    t_s_datum = sfcTemp + ( 10 * DEM )
##
    #Calculate z_omw: Momentum Roughness Length at Weather Data
    lai_w = 0.764196 #found lai in arcgis for weather station location in Peru
    zom_w = 0.018 * lai_w

    #Calculates Num32: Wind Speed at Assumed Blending Height (200m) Above Weather Station
    ws_200m = DM.Num32(wind_speed, zom_w)
    print "Wind Speed from Weather Station at 200m Above Ground: ", ws_200m

    #Calculates Num31: Friction Velocity
    fric_vel = DM.Num31(ws_200m, zom)
    fric_vel.save( "fric_vel_output.tif" )

    #Calculates Num30: Aerodynamic Resistance
    aero_res = DM.Num30(fric_vel)
    aero_res.save( "aero_res_output.tif" )

    ## Initialize Loop
    dTo = 0

    ## ITERATION
    #Calculates Num37: Air Density
    rho_air = DM.Num37(p, sfcTemp, dTo)

    # Air Density for Hot Pixel
    airdens_hot = DM.meanFromRasterBySingleZone(rho_air, fhpx, fhtbl)

    # Air Density for Cold Pixel
    airdens_cold = DM.meanFromRasterBySingleZone(rho_air, fcpx, fctbl)

    #Value for Net Radiation for Hot Pixel
    netRadhot = DM.meanFromRasterBySingleZone(netRad, fhpx, fhtbl)
    #print "Net Radiation for Hot Pixel from Module: ", netRadhot_test
    print "Net Radiation for Hot Pixel: ", netRadhot

    #Value for Net Radiation for Cold Pixel
    netRadcold = DM.meanFromRasterBySingleZone(netRad, fcpx, fctbl)
    #print "Net Radiation for Cold Pixel from Module: ", netRadcold_test
    print "Net Radiation for Cold Pixel: ", netRadcold

    #Value for Soil Heat Flux for Hot Pixel
    Ghot = DM.meanFromRasterBySingleZone(SoilHeatFlux, fhpx, fhtbl)
    #print Ghot_test
    print "Soil Heat Flux for Hot Pixel: ", Ghot

    #Value for Soil Heat Flux for Cold Pixel
    Gcold = DM.meanFromRasterBySingleZone(SoilHeatFlux, fcpx, fctbl)
    #print Gcold_test
    print "Soil Heat Flux for Cold Pixel: ", Gcold

    #Value for Aerodynamic Resistance for Hot Pixel
    rahhot = DM.meanFromRasterBySingleZone(aero_res, fhpx, fhtbl)
    #print rahhot_test
    print "Aerodynamic Reistance for Hot Pixel: ", rahhot

    #Value for Aerodynamic Resistance for Cold Pixel
    rahcold = DM.meanFromRasterBySingleZone(aero_res, fcpx, fctbl)
    #print rahcold_test
    print "Aerodynamic Resistance for Cold Pixel: ", rahcold
##
##    ##Value for Air Density at Hot Pixel
##    #rhohot = 0.836925056643
##    #print "Air Density at Hot Pixel: ", rhohot
##
##    #Value for Air Density at Cold Pixel
##    #rhocold = 0.854739340835
##    #print "Air Density at Cold Pixel: ", rhocold

    #Value for T_s_datum for Hot Pixel:
    tsdhot = DM.meanFromRasterBySingleZone(T_s_datum, fhpx, fhtbl)
    #print tsdhot_test
    #tsdhot = 304.481049
    print "T_s_datum for Hot Pixel: ", tsdhot

    #Value for T_s_datum for Cold Pixel:
    tsdcold = DM.meanFromRasterBySingleZone(T_s_datum, fcpx, fctbl)
    #print tsdcold_test
    #tsdcold = 296.065796
    print "T_s_datum for Cold Pixel: ", tsdcold

    #Calculates Num46: Near-Surface Temperature Gradient for the Hot Pixel
    dThot = DM.Num46(netRadhot, Ghot, rahhot, airdens_hot)
    print "Near-Surface Temperature Gradient for the Hot Pixel, dT(hot)", dThot

    #Calculates Num49: Near-Surface Temperature Gradient for the Cold Pixel
    dTcold = DM.Num49(netRadcold, Gcold, LE_ref, rahcold, airdens_cold)
    print "Near-Surface Temperature Gradient for the Cold Pixel, dT(cold)", dTcold

    #Calculates Num50: Coefficient a
    a = DM.Num50(dThot, dTcold, tsdhot, tsdcold)
    print "Coefficient a: ", a

    #Calculates Num51: Coefficient b
    b = DM.Num51(dThot, a, tsdhot)
    print "Coefficient b: ", b

    #Calculates Num29: Near Surface Temperature Difference, z1 to z2
    dT = DM.Num29(a, b, T_s_datum)
    dT.save( "dT_output.tif" )

    #Calculates Num37: Air Density
    rhoair = DM.Num37(p, sfcTemp, dT)
    rhoair.save( "rhoair_output.tif" )

    #Calcualtes Num28: Sensible Heat Flux
    H = DM.Num28(rhoair, dT, aero_res)
    H.save( "H_output.tif" )

    #Calculates Num1: Latent Energy Consumed by ET
    LE = DM.Num1(netRad, SoilHeatFlux, H)
    LE.save( "LE_output.tif" )

    #Calculates Num53: Latent Heat of Vaporization
    gamma = DM.Num53(sfcTemp)
    gamma.save( "gamma_output.tif" )

##    #Calculates Num52: Instantaneous Evapotranspiration (at Instant of Satellite Image)
##    ET_inst = DM.Num52(LE, gamma)
##    ET_inst.save( "ET_inst_output.tif" )
## ABOVB CONVERSTION SEEMS WRONG ... PULLED CONVERSION BELOW FROM URL
## (http://www.fao.org/docrep/x0490e/x0490e07.htm)
    ET_inst = LE * 0.035 / 60
    ET_inst.save( "ET_inst_output.tif" )

## ONLY UNCOMMENT THIS IF YOU HAVE 20 EXTRA MINUTES
##    #Build Image Pyramids for Outputs
##    includedir = "INCLUDE_SUBDIRECTORIES"
##    buildpy = "BUILD_PYRAMIDS"
##    calcstats = "CALCULATE_STATISTICS"
##    buildsource = "NONE"
##    blockfield = "#"
##    estimatemd = "#"
##    skipx = "3"
##    skipy = "3"
##    ignoreval = "#"
##    pylevel = "-1"
##    skipfirst = "NONE"
##    resample = "BILINEAR"
##    compress = "#"
##    quality = "80"
##    skipexist = "SKIP_EXISTING"
##
##    arcpy.BuildPyramidsandStatistics_management(
##         outdir, includedir, buildpy, calcstats, buildsource, blockfield,
##         estimatemd, skipx, skipy, ignoreval, pylevel, skipfirst,
##         resample, compress, quality, skipexist)

    print "Tasks complete!"

DVLP_metric_run(fmeta, fb2, fb3, fb4, fb5, fb6, fb7, fb10, fb11, fdem,
                wx_dir, fhpx, fcpx, fhtbl, fctbl, outdir, tzo)



