import arcpy
from arcpy import env
import math
if arcpy.CheckExtension("Spatial")== "Available":
    arcpy.CheckOutExtension("Spatial")
    from arcpy.sa import *
else:
    arcpy.AddError("You do not have the Spatial Analyst Extension, and therefore cannot use this tool.")
arcpy.env.overwriteOutput = True

from time_series import time_series

##################
#Make sure to float rasters!!!!!!
##################

#Convert date to JD
#creating conversion tool for julian day
#calculating solar declination angle

def date_to_jd(year, month, day):
    """
    Convert a date to Julian Day.

    Algorithm from 'Practical Astronomy with your Calculator or Spreadsheet',
        4th ed., Duffet-Smith and Zwart, 2011.

    Parameters
    ----------
    year : int
        Year as integer. Years preceding 1 A.D. should be 0 or negative.
        The year before 1 A.D. is 0, 10 B.C. is year -9.

    month : int
        Month as integer, Jan = 1, Feb. = 2, etc.

    day : float
        Day, may contain fractional part.

    Returns
    -------
    jd : float
        Julian Day

    Examples
    --------
    Convert 6 a.m., February 17, 1985 to Julian Day

    >>> date_to_jd(1985,2,17.25)
    2446113.75

    PLANNED IMPROVEMENT: this could be drastically simplified with datetime module
    """
    if month == 1 or month == 2:
        yearp = year - 1
        monthp = month + 12
    else:
        yearp = year
        monthp = month

    # this checks where we are in relation to October 15, 1582, the beginning
    # of the Gregorian calendar.
    if ((year < 1582) or
        (year == 1582 and month < 10) or
        (year == 1582 and month == 10 and day < 15)):
        # before start of Gregorian calendar
        B = 0
    else:
        # after start of Gregorian calendar
        A = math.trunc(yearp / 100.)
        B = 2 - A + math.trunc(A / 4.)

    if yearp < 0:
        C = math.trunc((365.25 * yearp) - 0.75)
    else:
        C = math.trunc(365.25 * yearp)

    D = math.trunc(30.6001 * (monthp + 1))

    jd = B + C + D + day + 1720994.5

    return jd

def Dec(DOY):
    declin = ((23.5*math.pi)/180) * math.cos((((2 * math.pi)* (DOY - 173)/365)))
    return declin

def Hour_Angle(lon, d_time):
    ha = (2*math.pi)*d_time + lon - (math.pi)
    return ha

def Hour_Angle2(lonm, d_time, DOY, tzo):
    #lonm: longitude of measurement location in positive degrees west
    #d_time: UTC time in decimal hours
    #DOY: day-of-year, integer number of days from beginning of given year
    #tzo: time_zone_offset for local time in decimal days
    l_time = d_time - tzo
    bee = 2*math.pi * (DOY - 81) / 364
    #Seasonal Correction for Solar Time
    SCorr = 0.1645 * math.sin(2 * bee) - 0.1255 * math.cos(bee) \
            - 0.025 * math.sin(bee)
    #Longitude of center of time zone in positive degrees west
    lonz = tzo * 15.0
    ha = (math.pi / 12) * ((l_time + 0.06667 * (lonz - lonm) + SCorr) - 12)
    return ha

def Sunset_Hour_Angle(lat, declin):
    #lat: latitude in radians
    #declin: solar declination in radians
    ha_ss = math.acos(-math.tan(lat) * math.tan(declin))
    return ha_ss

def XTerr_Radiation_Day(lat, declin, ha_ss, d_r):
    #Extraterrestrial Radiation for Hourly or Shorter Periods
    #xterr_rad, MJ*m^-2*hour^-1
    #lat: latitude in radians
    #declin: solar declination in radians
    #ha_ss: hour angle at sunset
    #d_r: relative earth-sun distance scaled to mean distance
    #G_sc, solar constant = 0.0820 MJ*m^-2*min^-1
    G_sc = 0.0820
    xterr_rad = (24 * 60 / math.pi) * G_sc * d_r * ((ha_ss *
                math.sin(lat) * math.sin(declin)) + (math.cos(lat) *
                math.cos(declin)*math.sin(ha_ss)))
    return xterr_rad

def XTerr_Radiation_Period(lat, declin, ha1, ha2, d_r):
    #Extraterrestrial Radiation for Hourly or Shorter Periods
    #xterr_rad, MJ*m^-2*hour^-1
    #lat: latitude in radians
    #declin: solar declination in radians
    #ha1: hour angle at beginning of period in radians
    #ha2: hour angle at end of period in radians
    #d_r: relative earth-sun distance scaled to mean distance
    #G_sc, solar constant = 0.0820 MJ*m^-2*min^-1
    G_sc = 0.0820
    xterr_rad = (12 * 60 / math.pi) * G_sc * d_r * (((ha2 - ha1) *
                math.sin(lat) * math.sin(declin)) + (math.cos(lat) *
                math.cos(declin)*(math.sin(ha2) - math.sin(ha1))))
    return xterr_rad

def Daylight_Hours(sunset_hour_angle):
    Nhours = (24 / math.pi) * sunset_hour_angle
    return Nhours

def Solar_Radiation(a_s, b_s, sunhr, dayhr, xterr_rad):
    #sol_rad, MJ*m^-2*hour^-1
    #a_s, fraction of radiation reaching Earth on overcast day
    #b_s, additional fraction of radiation reaching Earth on clear day
    #sunhr, sunshine hours
    #dayhr, daylight hours
    #xterr_rad, extraterrestrial radiation
    sol_rad = (a_s + b_s * (sunhr / dayhr)) * xterr_rad
    return sol_rad

def Net_Solar_Radiation(albedo, sol_rad):
    net_sol_rad = (1 - albedo) * sol_rad
    return net_sol_rad

def Net_Longwave_Radiation(Tmax, Tmin, svp_act, sol_rad, csky_rad):
    #Tmax: daily max temperature, C
    #Tmin: daily min temperature, C
    #svp_act: actual vapor pressure, kPa
    #sol_rad: solar radiation, MJ*m^-2*hour^-1
    #csky_rad: clear-sky radiation, MJ*m^-2*hour^-1
    ## radiation per day or hour is okay b/c they are in a ratio
    #Stefan-Boltzmann constant, 4.093 10^-9 MJ*K^-4*m^-2*day^-1
    sig_SB = 4.903e-9
    #Convert Celsius temps to Kelvin
    TmaxK = Tmax + 273.16
    TminK = Tmin + 273.16
    net_lw_rad = sig_SB * ((TmaxK ** 4 + TminK ** 4) / 2) * (0.34 - 0.14 *
                 math.sqrt(svp_act)) * (1.35 * (sol_rad / csky_rad) - 0.35)
    return net_lw_rad

def Reference_ET_day(Del, R_n, G_shf, gam, T_C, u2, e_s, e_a, crop):
    #Function to Calculate Reference Evapotranspiration (ET_r or ET_o)
    #ET_Ref
    #Del: slope vapor pressure curve, kPa*C^-1
    #R_n: net radiation at the crop surface, MJ*m^-2*day^-1
    #G_shf: soil heat flux density, MJ*m^-2*day^-1
    #T_C: air temperature at 2 m height, C
    #u2: wind spead at 2 m height, m*s^-1
    #e_s: saturation vapor pressure, kPa
    #e_a: actual vapor pressure, kPa
    #gam: pyschometric constant, kPa*C^-1
    #Cn: numerator constant for reference type and calculation time step (Book:the ASCE Standardized Reference ET Equation)
    #Cd: denominator constant for reference type and calculation time step (Book:the ASCE Standardized Reference ET Equation)
    
    if crop == "grass":
        Cn = 900
        Cd = 0.34
    if crop == "alfalfa":
        Cn = 1600
        Cd = 0.38
        
    ET_ref = (0.408 * Del * (R_n - G_shf)) + (gam * (Cn / (T_C + 273.16)) *
                 u2 * (e_s - e_a)) / (Del + gam * (1 + Cd * u2))
    return ET_ref

def Reference_ET_hr(Del, R_n, G_shf, gam, T_C, u2, e_s, e_a, crop):
    #Function to Calculate Reference Evapotranspiration (ET_r or ET_o)
    #ET_Ref
    #Del: slope vapor pressure curve, kPa*C^-1
    #R_n: net radiation at the crop surface, MJ*m^-2*day^-1
    #G_shf: soil heat flux density, MJ*m^-2*day^-1
    #T_C: air temperature at 2 m height, C
    #u2: wind spead at 2 m height, m*s^-1
    #e_s: saturation vapor pressure, kPa
    #e_a: actual vapor pressure, kPa
    #gam: pyschometric constant, kPa*C^-1
    #Cn: numerator constant for reference type and calculation time step (Book:the ASCE Standardized Reference ET Equation)
    #Cd: denominator constant for reference type and calculation time step (Book:the ASCE Standardized Reference ET Equation)
    if crop == "grass":
        Cn = 37
        Cd = 0.24
    if crop == "alfalfa":
        Cn = 66
        Cd = 0.25
    
    ET_ref = (0.408 * Del * (R_n - G_shf)) + (gam * (Cn / (T_C + 273.16)) *
                 u2 * (e_s - e_a)) / (Del + gam * (1 + Cd * u2))
    return ET_ref

def Latent_Heat_Flux_PM(Del, R_n, G_shf, gam, e_s, e_a, rho_air, r_s, r_a):
    #Function to Calculate Reference Evapotranspiration (ET_r or ET_o)
    #ET_Ref
    #Del: slope vapor pressure curve, kPa*C^-1
    #R_n: net radiation at the crop surface, MJ*m^-2*day^-1
    #G_shf: soil heat flux density, MJ*m^-2*day^-1
    #e_s: saturation vapor pressure, kPa
    #e_a: actual vapor pressure, kPa
    #gam: pyschometric constant, kPa*C^-1
    #r_s: bulk surface resistance, s*m^-1
    #r_a: aerodynamic resistance, s*m^-1
    #rho_air: mean density of air at constant pressure
    #specific heat at constant pressure, 1.013*10^-3 MJ*kg^-1*C^-1
    cp_air= 0.001013
    lamda_ET = (Del * (R_n - G_shf) + (rho_air * cp_air * ((e_s - e_a) / r_a)) /
               (Del + (gam * (1 + (r_s / r_a)))))
    return lamda_ET

def L8_Thermal_Radiance(L8Bnd):
    #Assign variables
    M_L= float(0.0003342)
    A_L= float(0.1)
    #Set inactive areas to null
    conBnd = Con(L8Bnd, L8Bnd, "", "VALUE >= 1")
    #Calculate radiance
    thermRad = (conBnd * M_L) + A_L
    return thermRad

def Datum_Ref_Temp(temp0, elev, elevRef):
    #Assign variables
    #Specific heat of air at constant pressure
    #J*kg^-1*K-1
    cp_air= float(1003.5)
    #gravity of Earth
    #m*s^-2
    gE= float(9.81)
    #calculate temperature difference relative to datum
    dTemp = -(gE / cp_air) * (elev - elevRef)
    #apply temperature difference relative to datum
    tempDatum = temp0 + dTemp
    return tempDatum

def Aerodynamic_Resistance(wind_speed, z_m, h_c):
    #height of wind measurements, m
    #z_m = 2 typically
    #crop height, m
    #h_c = 0.12 for *grass*
    #height of humidity measurement, m
    z_h = z_m
    #zero plane displacement height, m
    d_0 = 0.6667 * h_c
    #roughness length governing momentum transfer, m
    z_om = 0.123 * h_c
    #roughness length governing transfer of heat and vapor, m
    z_oh = 0.1 * z_om
    #von Karman's constant
    k_vK = 0.41
    #aerodynamic resistance, s*m^-1
    r_aero = ((math.log((z_m - d_0) / z_om) * math.log((z_m - d_0) / z_oh)) /
             ((k_vK ** 2) * wind_speed))
    return r_aero

def Surface_Resistance(LAI):
    #bulk stomatal resistance of the well illuminated leaf, s*m^-1
    r_leaf = float(100)
    #active (sunlit) leaf area index, m^2*m^-2
    LAI_active = 0.5 * LAI
    #bulk surface resistance
    r_surf = r_leaf / LAI_active
    return r_surf

def Saturation_Vapor_Pressure(T_Celcius):
    e_zero = 0.6108 * math.exp((17.27 * T_Celcius) / (T_Celcius + 237.3))
    return e_zero

def Saturation_Vapor_Pressure_Alt(T_Celcius):
    e_zero = 0.1 * ( 6.11 * 10 ** ( (7.5 * T_Celcius) / (237.3 + T_Celcius) ) )
    return e_zero

def Pyschometric_Constant(P_air):
    #specific heat at constant pressure, 1.013*10^-3 MJ*kg^-1*C^-1
    cp_air= float(0.001013)
    #latent heat of vaporization, 2.45 MJ*kg^-1
    lamda_lhv = float(2.45)
    #ratio molecular weight of water vapor/dry air, 0.622
    eps_ratio = float(0.622)
    #pychometric constant, kPa*C^-1
    gamma_pc = (cp_air * P_air) / (eps_ratio * lamda_lhv)
    return gamma_pc

def Slope_Saturation_Vapor_Pressure(T_Celsius):
    Delta_svp = 4098 * (0.6108 * math.exp((17.27 * T_Celsius) /
    (T_Celsius + 237.3))) / (T_Celsius + 237.3) ** 2
    return Delta_svp

"""
Weather data parsers are found below for various specific regions/formats
@param time: The time which the Landsat image was taken. Formatted as HHMM
@return: returns a list of weather variables: temperature, relative humidity, precipitation, air pressure,
wind speed, and dewpoint

These SHOULD return wx objects with attributes for each variable to make things neater.
"""

def Wx_Data_Extract(time_obj, wx_filepath):
    """
    This function was writen to reenstate wx file parsing for tha greed upon NOAA
    weather data format for any study area within the USA. This is THE function
    that should be used for reading weather data, the others will not be supported.
    """

    # format weather as a time series object from dnppy module
    wx_data = time_series("wx_data")

    wx_data.from_csv(wx_filepath)
    




    return [temp_C_min, temp_C_max, temp_C_mid, P_air, wind_speed, dewp_C]



def Wx_Data_Extract_Idaho(time, wx_filepath):
    IDWeather = wx_filepath
    weatherdata = open(IDWeather, 'r')
    rows = []
    for line in weatherdata:
        rows.append(line.split())
    difference = 100
    temp_C_min = 100
    temp_C_max = -100
    wx_datestruct = []
    for i in xrange(2, len(rows)):
        if abs(time - float(rows[i][6])) < difference and float(rows[i][12]) is not 999.9:
            difference = abs(time - float(rows[i][6]))
            wx_datestruct = rows[i]
        if float(rows[i][14]) < temp_C_min:
            temp_C_min = float(rows[i][14])
        elif float(rows[i][14]) > temp_C_max and float(rows[i][14]) != 999.9:
            temp_C_max = float(rows[i][14])

    temp_C_mid = (temp_C_max + temp_C_min) / 2.0

    #Temperature (C)
    temp_C = float(wx_datestruct[14])
    print "Temperature: ", temp_C, "C"

    #Daily Mean Relative Humidity (%)
    RH = float(wx_datestruct[122])
    print "Relative Humidity", RH, "%"

    #Mean Air Pressure at Surface (mb)
    P_air = float(wx_datestruct[84])
    print "Air Pressure at Surface: ", P_air, "mb"

    #Wind Speed (m/s), converted from mph
    wind_speed = float(wx_datestruct[12])
    print "Wind Speed: ", wind_speed, "m/s"

    #Dewpoint (C)
    dewp_C = float(wx_datestruct[16])
    print "Dewpoint: ", dewp_C, "Celsius"

    print (temp_C, RH, P_air, wind_speed, dewp_C)
    return [temp_C_min, temp_C_max, temp_C_mid, P_air, wind_speed, dewp_C]

def Wx_Data_Extract_NC(time, wx_filepath):
    IDWeather = wx_filepath
    weatherdata = open(IDWeather, 'r')
    rows = []
    for line in weatherdata:
        rows.append(line.split())
    difference = 100
    temp_C_min = 100
    temp_C_max = -100
    wx_datestruct = []
    for i in xrange(1, len(rows)):
        if abs(time - float(rows[i][2])) < difference and float(rows[i][21]):
            differenct = abs(time - float(rows[i][6]))
            wx_datestruct = rows[i]

def Wx_Data_Extract_PERU_WFP(fwx, year, month, day):
    #Get Peru WFP Project Weather Data File and Read in as String
    weatherdata = open(fwx, 'r')
    wx_lines = weatherdata.read()

    #Weather Data Parsing
    #creates a tag for selecting correct line in weather data file
    wx_year = int(year)
    wx_month = int(month)
    wx_day = int(day)
## Renamed wx_delimiter to wx_datetag to be more descriptive
    wx_datetag = str(wx_year) + "-" + str(wx_month) + "-" + str(wx_day)
##    print "Weather File Date Tag: ", wx_datetag

    #unpack weather data for the day
    wx_dateline = wx_lines.split(wx_datetag)[1].split("\n")[0]
    wx_datestruct = wx_dateline.split()
    #Mean Temperature (C) from Weather Data
    temp_C_avg = float(wx_datestruct[0])
    #Min Temperature (C) from Weather Data
    temp_C_min = float(wx_datestruct[1])
    #Max Temperature (C) from Weather Data
    temp_C_max = float(wx_datestruct[2])
    #Daily Mean Relative Humidity (%) from Weather Data
    RH_mean = float(wx_datestruct[3])
    #Daily Total Precip (mm) from Weather Data
    precip = float(wx_datestruct[4])
    #Mean Air Pressure at Surface (mb) from Weather Data
    P_air_mb = float(wx_datestruct[5])
    P_air = P_air_mb * 0.1
    #Wind Speed (m/s) from Weather Data
    wind_speed = float(wx_datestruct[6])

    #calculated quantities
    #daily mid-Temp in Celsius
    temp_C_mid = (temp_C_max + temp_C_min) / 2
    #get dewpoint in Celsius
##    EDIT 7/25/2014 dewp_C changed - this was just a conversion from F to C ???
##    dewp_C = ( temp_C_avg - 32.0 ) * 5 / 9
##    print "Dewpoint: ", dewp_C1, "Celsius"
    dewp_C = temp_C_mid - ((100 - RH_mean) / 5)

    return [temp_C_avg, temp_C_min, temp_C_max, RH_mean,
            precip, P_air, wind_speed, temp_C_mid, dewp_C]

def Wx_Data_Extract_MID_ATLANTIC(fwx, year, month, day, hours, minutes, seconds):
    #Get Mid-Atlantic Project Weather Data File and Read in as String
    weatherdata = open(fwx, 'r')
    wx_lines = weatherdata.read()

    #Weather Data Parsing
    #creates a tag for selecting correct line in weather data file
    wx_day = int(day)
    wx_month = int(month)
    wx_year = int(year)
    wx_minutes = int(minutes) if seconds < 30 else int(minutes) + 1
    wx_hours = int(hours) if wx_minutes > 24 else int(hours) - 1
    wx_list = [wx_year, wx_month, wx_day, wx_hours]

    wx_datetag = ""
    for item in wx_list:
        if item < 10:
            it = "0" + str(item)
        else:
            it = str(item)
        wx_datetag += it
    print "Weather File Delimiter: ", wx_datetag

    #unpack weather data
    wx_dateline = wx_lines.split(wx_datetag)[1].split("\n")[0]
    wx_datestruct = wx_dateline.split()

    #Temperature (C)
    temp_C = float(wx_datestruct[18])
    print "Temperature: ", temp_C, "C"

    #Daily Mean Relative Humidity (%)
    RH = 0 # We do not have an RH value in our fwx

    #Daily Total Precip (mm), converted from inches
    precip = float(wx_datestruct[25]) * 25.4
    print "Precipitation: ", precip, "mm"

    #Mean Air Pressure at Surface (mb)
    P_air = float(wx_datestruct[22])
    print "Air Pressure at Surface: ", P_air, "mb"

    #Wind Speed (m/s), converted from mph
    wind_speed = float(wx_datestruct[6]) * 0.44704
    print "Wind Speed: ", wind_speed, "m/s"

    #Dewpoint (C)
    dewp_F = float(wx_datestruct[19])
    dewp_C = ( dewp_F - 32.0 ) * 5 / 9
    print "Dewpoint: ", dewp_C, "Celsius"

    return (temp_C, RH, precip, P_air, wind_speed, dewp_C)

def meanFromRasterBySingleZone(valRaster, polyShp, storeTbl):
    #Assumes single polygon shapefile with field named "Interior"
    #outStats = arcpy.sa.ZonalStatisticsAsTable(polyShp, "interior", valRaster,
    #                                        storeTbl, "NODATA", "MEAN")
    rows = arcpy.SearchCursor(storeTbl)
    row = rows.next()
    meanVal = row.getValue("MEAN")
    return meanVal

#Equation Number 1- Latent Energy Consumed by ET
def Num1(netRad, G, H):
    outMath = netRad - G - H
    return outMath

#Equation Number 2- Net Radiation Flux at Surface
def Num2(ibbswr, bsa, olwr, ilwr, bbse):
    outMath = ibbswr - (bsa * ibbswr) + ilwr - olwr - (1 - bbse) * ilwr
    return outMath

#Equation Number 3- Incoming Shortwave Radiation
def Num3(sia, bbat, d):
    gsc = 1367 #solar constant
    outMath = ( gsc * sia * bbat ) / ( d**2 )
    return outMath

#Equation Number 4- Broad-Band Atmospheric Transmissivity
def Num4(p, w, cth, kt):
    outMath1 = 0.075 * ( w / cth ) ** 0.4
    outMath2 = ( -0.00146 * p ) / ( kt * cth )
    outMath3 = 0.35 + 0.627 * arcpy.sa.Exp( outMath2 - outMath1 )
    return outMath3

#Equation Number 5- Atmospheric Pressure
def Num5(Elevation):
    pressure = 101.3 * ( ( ( 293 - ( 0.0065 * Elevation ) ) / 293 ) ** 5.26 )
    return pressure

#Equation Number 6- Water in Atmosphere
def Num6(nsvp, p):
    w = ( 0.14 * nsvp * p ) + 2.1
    return w

#Use Num7 in Num10 versus Num8
#Equation Number 7- Cosine of Solar Incidence Angle
def Num7(delta, phi, s, gamma, omega):
    #===========================================================================
    # cos_theta_rel = ( math.sin(delta) * math.sin(phi) * arcpy.sa.Sin(s) )
    # - ( math.sin(delta) * math.cos(phi) * arcpy.sa.Sin(s) * arcpy.sa.Cos(gamma) )
    # + ( math.cos(delta) * math.cos(phi) * arcpy.sa.Cos(s) * math.cos(omega) )
    # + ( math.cos(delta) * math.sin(phi) * arcpy.sa.Sin(s) * arcpy.sa.Cos(gamma) * math.cos(omega) )
    # + ( math.cos(delta) * arcpy.sa.Sin(gamma) * arcpy.sa.Sin(s) * math.sin(omega) )
    #===========================================================================
    cos_theta1 = math.sin(delta) * math.sin(phi) * arcpy.sa.Cos(s)
    cos_theta2 = -( math.sin(delta) * math.cos(phi) * arcpy.sa.Sin(s) * arcpy.sa.Cos(gamma) )
    cos_theta3 = math.cos(delta) * math.cos(phi) * arcpy.sa.Cos(s) * math.cos(omega)
    cos_theta4 = math.cos(delta) * math.sin(phi) * arcpy.sa.Sin(s) * arcpy.sa.Cos(gamma) * math.cos(omega)
    cos_theta5 = math.cos(delta) * arcpy.sa.Sin(gamma) * arcpy.sa.Sin(s) * math.sin(omega)
    cos_theta_rel = cos_theta1 + cos_theta2 + cos_theta3 + cos_theta4 + cos_theta5
    return(cos_theta_rel, cos_theta1, cos_theta2, cos_theta3, cos_theta4, cos_theta5)
#cos_theta_rel =   ( math.sin(delta) * math.sin(phi) * arcpy.sa.Sin(s) )
#                - ( math.sin(delta) * math.cos(phi) * arcpy.sa.Sin(s) * arcpy.sa.Cos(gamma) )
#                + ( math.cos(delta) * math.cos(phi) * arcpy.sa.Cos(s) * math.cos(omega) )
#                + ( math.cos(delta) * math.sin(phi) * arcpy.sa.Sin(s) * arcpy.sa.Cos(gamma) * math.cos(omega) )
#                + ( math.cos(delta) * arcpy.sa.Sin(gamma) * arcpy.sa.Sin(s) * math.sin(omega) )

#Equation Number 8- Cosine of Solar Zenith Over Horizontal Surface
def Num8(delta, phi, omega):
    cos_theta_hor = ( math.sin(delta) * math.sin(phi) ) + ( math.cos(delta) * math.cos(phi) * math.cos(omega) )
    return cos_theta_hor
'''
#Equation Number 9 is not necessary for Landsat 8
#Equation Number 9- Square of Relative Earth-Sun Distance, d^2 #Completed by Scott
def Num9(files):
    return ( 1 / ( 1 + .033 * math.cos(int(files[13:16]) * 2 * math.pi / 365 ) ) )
'''
#Equation Number 10- Per Band "Top of Atmosphere" Bidirectional Reflectance
def Num10(l8raster, Num7):
    M_rho= float(0.00002)
    A_rho= float(-0.1)

    #Part one of calculation.
    outCon = arcpy.sa.Con(l8raster, l8raster,"", "VALUE >= 1")
    outTimes = (outCon * M_rho) + A_rho

    #Divide Part 2 from Part 1
    outDivide = outTimes / Num7
    return outDivide

#Equation Number 11- Per Band Surface Reflectance
def Num11(refl_toa, trans_in, trans_out, refl_path):
    refl_surf = ( refl_toa - refl_path ) / ( trans_in * trans_out )
    return refl_surf

#Equation Number 12- Effective Narrowband Transmittance For Incoming Solar Radiation
def Num12(p, w, cth, kt, c1, c2, c3, c4, c5):
    outMath = c1 * ((arcpy.sa.Exp((c2*p)/(kt*cth))) - (((c3*w)+c4)/cth)) + c5
    return outMath

#Equation Number 13- Effective Narrowband Transmittance For Shortwave Radiation Reflected From Surface
def Num13(p, w, cos_n, kt, c1, c2, c3, c4, c5):
    outMath = c1 * ((arcpy.sa.Exp((c2*p)/(kt*cos_n))) - (((c3*w)+c4)/cos_n)) + c5
    return outMath

#Equation Number 14- Per Band Path Reflectance
def Num14(tin, cb):
    outMath = cb * (1 - tin)
    return outMath

#Equation Number 15- Broad-Band Surface Albedo
def Num15(asr_list):
    surface_albedo = 0
    COEFFICIENT_LIST = [0.254, 0.149, 0.147, 0.311, 0.103, 0.036]
    for i in xrange(len(asr_list)):
        surface_albedo += asr_list[i] * COEFFICIENT_LIST[i]
    return surface_albedo

#Equation Number 16- Outgoing Longwave Radiation #Completed by Scott
def Num16(eps_bb, sfcTemp):
##    sigma = 5.67 * 10 ** -8
    sigma = 5.67e-8
    R_L_out = eps_bb * sigma * sfcTemp ** 4
    return R_L_out

#Equation Number 17- Broad Band Surface Emissivity #Completed by Scott
def Num17(Num18):
    outCon1= Con(Num18, Num18, 9999, "VALUE <= 3")
    outMath= 0.95 + (0.01 * outCon1)
    outCon2= Con(outMath, outMath, .98, "Value <= 50")
    return outCon2

#Equation Number 18- Leaf Area Index
def Num18(Num19):
    #assigns LAI for 0.1 <= SAVI <= 0.687
    outMath = ( (arcpy.sa.Ln( (.69 - Num19) / .59) ) / ( -0.91 ) )
    #assigns LAI for SAVI >= 0.687
    outCon1 = Con(Num19, outMath, 6, "VALUE <= 0.687")
    #assigns LAI for SAVI <= 0.1
    outCon2 = Con(Num19, outCon1, 0, "VALUE >= 0.1")
    return outCon2

#Equation Number 19- Soil Adjusted Vegetation Index #Completed by Scott
def Num19(Band5, Band4, L):
    outFloat5 = Float(Band5)
    outFloat4 = Float(Band4)
    outMath = ((1 + L) * (outFloat5 - outFloat4)) / (L + (Plus(outFloat5, outFloat4)))
    return outMath

#Equation 20 - Surface Temperature, Landsat 8, Band 10
def Num20(corrRad10, nbe, K1, K2):
    sfcTemp = (K2 / (arcpy.sa.Ln(((nbe * K1) / corrRad10) + 1)))
    return sfcTemp

#Equation Number 21- Corrected Thermal Radiance  #completed by Dr. Ross
def Num21(thermRad, pathRad, nbt, nbe, skyRad):
    corrRad = ((thermRad - pathRad) / nbt) - ((1 - nbe) * skyRad )
    return corrRad

#Equation Number 22- Narrow Band Emissivity
def Num22(Num18):
    outCon = Con(Num18, 0.97 + (0.0033 * Num18), 0.98, "VALUE <= 3")
    return outCon

#Equation Number 23- Normalized Difference Vegetation Index #Completed by Scott
def Num23(Band5, Band4):
    #Float rasters to make sure we get a range of values between -1 and 1
    outFloat5 = Float(Band5)
    outFloat4 = Float(Band4)
    outMath = (outFloat5 - outFloat4)/(Plus(outFloat5, outFloat4))
    return outMath

#Equation Number 24- Incoming Longwave Radiation
def Num24(eps_a, temp):
##    sigma = 5.67 * 10 ** -8
    sigma = 5.67e-8
    ## EDIT added temperature exponent (to the 4th)
    R_L_in = eps_a * sigma * temp ** 4
    return R_L_in

#Equation Number 25- Effective Atmospheric Emissivity
def Num25(t_sw):
    eps_a = 0.85 * (( - arcpy.sa.Ln(t_sw) ) ** 0.09)
    return eps_a

#Equation Number 26- Ratio of Soil Heat Flux to Net Radiation
def Num26(bsa, sfcTemp, ndvi):
    g2rn_ratio = (sfcTemp - 273.15) * (0.0038 + 0.0074 * bsa) * (1 - 0.98 * (ndvi ** 4))
    return g2rn_ratio
'''
#Equation Number 27a- Ratio of Soil Heat Flux to Net Radiation (Alt, Cond. A)
def Num27a(Num18):
    outMath = 0.05 + 0.18 * math.exp( -0.521 * (Num18) )
    return outMath #LAI >= 0.5
    #ERROR: A FLOAT IS REQUIRED
'''
#Equation Number 27b- Ratio of Soil Heat Flux to Net Radiation (Alt, Cond. B)
def Num27b(Num20, Num2):
    outMath = 1.80 * ( Num20 - 273.15 ) / Num2 + 0.084
    return outMath #LAI < 0.5

#Equation Number 28- Sensible Heat Flux
def Num28(Num37, Num29, Num30):
    outMath = Num37 * 1000 * ( Num29 / Num30 )
    return outMath

#Equation Number 29- Near Surface Temperature Difference, z1 to z2
def Num29(a, b, tsdatum):
    outMath = a + ( b * tsdatum )
    return outMath

#Equation 30- Aerodynamic Transport, z1 to z2
def Num30(Num31):
    #z_2 = 2m
    #z_1 = 0.1m
    #k = 0.41
    outMath = Ln( 2 / 0.1 ) / ( Num31 * 0.41 )
    return outMath

#Equation 31- Friction Velocity
def Num31(Num32, Num33):
    outMath = ( 0.41 * Num32 ) / ( Ln( float(200) / Num33 ) )
    return outMath

#Equation 32- Wind Speed at an Assumed Blending Height (200m) above Weather Station
def Num32(ws, zomw):
    ws200 = ( ws * Ln( 200 / zomw ) ) / ( Ln( 2 / zomw ) )
    return ws200

#Equation 33- Momentum Roughness Length, Option A
def Num33(lai):
    zom0 = 0.018 * lai
    zom = Con(zom0, zom0, 0.005, "VALUE >= 0.005")
    return zom

## Equation 34 zom options not used 7/29/2014
###Equation 34a- Momentum Roughness Length, Option B
##def Num34a():
##    pass
##
###Equation 34b- Momentum Roughness Length, Option C
##def Num34b():
##    pass

#Equation 35- Momentum Roughness Length for Mountainous Terrain
def Num35(Num33, s):
    outMath = Num33 * ( 1 + ( (180 / math.pi ) * s - 5 ) / 20 )
    return outMath

#Equation 36- Wind Speed Weighting Coefficient
def Num36(elevation, elevation_wx):
    outMath = 1 + 0.1 * ( ( elevation - elevation_wx ) / 1000 )
    return outMath

#Equation 37- Air Density
#R = 287 J kg^-1 K^-1 (specific gas constant)
R = 287
def Num37(p, Ts, dT ):
    rho_air = ( 1000 * p) / ( 1.01 * (Ts - dT) * R )
    return rho_air

#Equation 37c- Air Density for Cold Pixel
def Num37c():
    outMath = ( 1000 * 73.354539 ) / ( 1.01 * (296.067017) * 287 )
    return outMath

#Equation 37h- Air Density for Hot Pixel
def Num37h():
    outMath = ( 1000 * 73.381848 ) / ( 1.01 * (304.48149 - 2) * 287 )
    return outMath


#Equation 38- Friction Velocity (Corrected)
def Num38(Num32, Num33, Num41):
    return (Num32 * .041) / (arcpy.sa.Ln(200/Num33) - Num41)

#Equation 39- Aerodynamic Resistance
def Num39(Num45a, Num45b, Num38):
    return (arcpy.sa.Ln(2/.1) - Num45a + Num45b) / (Num38 * 0.41)

#Equation 40- Stability Conditions of the Atmoshphere, the Height at Which
#Forces of Bouyancy (or Stability) and Mechanical Mixing are Equal
def Num40(Num37, Num38, Num20, Num28):
#     if Num28 == 0.0:  # !!! THIS IF STATEMENT THROWS AN ERROR. CAN'T DO WITH RASTER !!!
#         mo_length = 0.0
#     else:
    mo_length = -(Num37 * 1006.1 * Num38 **3 *Num20) / (0.41 * 9.807 * Num28)
    return mo_length

#Equation 41- Stability Correction for Momentum Transport at 200m when L<0
def Num41(L):
    return 2 * arcpy.sa.Ln((2 + Num43a(L)) + arcpy.sa.Ln((1 + Num43a(L) ** 2) / 2) - (2 * ATan(Num43a(L)) + 5*(math.pi)))

#Equation 42a- Stability Correction for Heat Transport at 2m when L<0
def Num42a(L):
    return 2 * arcpy.sa.Ln((1 + Num43b(L)**2) / 2)

#Equation 42b- Stability Correction for Heat Transport at 0.1m when L<0
def Num42b(L):
    return 2 * arcpy.sa.Ln((1 + Num43c(L)**2) / 2)

#Equation 43a- Definition??
def Num43a(Num40):
    return (1 - 16 * (200 / Num40)) **.25

#Equation 43b- Definition??
def Num43b(Num40):
    return(1 - 16 * (2 / Num40)) ** .25

#Equation 43c- Definition??
def Num43c(Num40):
    return(1 - 16 * 0.1 / Num40) ** .25

#Equation 44- Integrated Stability Correction for Momentum Transport at 200m when L>0
def Num44(Num40):
    return -5 * (2 / Num40)

#Equation 45a- Integrated Stability Correction for Heat Transport at 2m when L>0
def Num45a(Num40):
    return -5 * (2 / Num40)

#Equation 45b- Integrated Stability Correction for Heat Transport at 0.1 m when L>0
def Num45b(Num40):
    return -5 * (0.1 / Num40)

#Equation 46- Change in Temperature for a Hot Pixel, or the Near-Surface
#Temperature Gradient over the Hot Pixel
def Num46(netRadhot, Ghot, rahhot, rhohot):
    #J*kg^-1*K-1
    cp_air= 1003.5
    dThot = ( (netRadhot - Ghot) * rahhot ) / ( rhohot * cp_air )
    return dThot

'''
#Equation 47- Sensible Heat Flux at the Hot Pixel
def Num47(netRadhot, Ghot, LEhot):
    pass

#Equation 48- Sensible Heat Flux at the Cold Pixel
def Num48(netRadcold, Gcold, LEcold):
    pass
'''

#Equation 49- Near-Surface Temperature Gradient Over the Cold Pixel
def Num49(netRadcold, Gcold, LE_ref, rahcold, rhocold):
    #J*kg^-1*K-1
    cp_air= 1003.5
    dTcold = ( (netRadcold - Gcold - LE_ref) * rahcold ) / ( rhocold * cp_air )
    return dTcold

#Equation 50- Coefficient A
def Num50(dThot, dTcold, tsdhot, tsdcold):
    outMath = ( dThot - dTcold ) / ( tsdhot - tsdcold )
    return outMath

#Equation 51- Coefficient B
def Num51(dThot, a, tsdhot):
    outMath = (dThot - a ) / tsdhot
    return outMath

#Equation 52- Instantaneous Evapotranspiration (at Instant of Satellite Image)
def Num52(LE):
    ET_inst = (0.001469)* LE
    #ET_inst = (12.96) * ( LE / ( 2.45 * 1000 ) )
    return ET_inst

#Equation 53- Latent Heat of Vaporization
def Num53(sfcTemp):
    outMath = (2.501 - 0.00236 * ( sfcTemp - 273.15 )) 
    return outMath

#Equation 54- Reference Evapotranspiration Fraction
def Num54(ET_inst, ET_ref_hourly):
    ETrF = ET_inst/ET_ref_hourly
    return ETrF

#Equation 55- Evapotranspiration for a Specific MM/DD
def Num55(ETrF, ET_ref_day):
    C_rad=1 #Assuming horizontal sfc 
    ET_day = C_rad * ETrF * ET_ref_day 
    return ET_day

'''
#Equation 56- Correction Term Used in Sloping Terrain to Correct for Variation in 24 hour
#Versus Instantaneous Energy Availability, Calculated for Each Image and Pixel
def Num56():
    pass

#Equation 57- Instantaneous Clear-Sky Solar Radiation for 24 hour Horizontal Surfaces and Sloping Pixels
def Num57():
    pass

#Equation 58- Evapotranspiration of a Given Period (Examples: Month, Season, Year)
def Num58():
    pass

#Equation 59- Average Reference Evapotranspiration Fraction Over a Given Period():
def Num59():
    pass


#Extra Definitions:

def Brightness_Temperature(files):
    #Assign Variables
    M_L= float(0.0003342)
    A_L= float(0.1)
    K1a= float(774.89)
    K2a= float(1321.08)
    K1b= float(480.89)
    K2b= float(1201.14)
    print files
    outCon = Con(files, files, "", "VALUE >= 1")
    #Raster Calculator 1
    outTimes= (outCon * M_L) + A_L
    #Raster Calculator 2
     #If the file is Band 10:
    if files[22:25]== "B10":
        outDivide = K2a / (Ln((K1a / outTimes) + 1))
        outDivide.save("Brightness_Temperature_" + files)
    #If the file is Band 11:
    elif files[22:25]== "B11":
        outDivide = K2b / (Ln((K1b / OutPlus) + 1))
        outDivide.save("Brightness_Temperature_" + files)

def Reflectance(raster, MTL):
    #Get SEA from MTL file
     meta8=['LANDSAT_SCENE_ID = "','DATE_ACQUIRED = ',"SUN_ELEVATION = ",
                    "RADIANCE_MAXIMUM_BAND_{0} = ","RADIANCE_MINIMUM_BAND_{0} = ",
                    "QUANTIZE_CAL_MAX_BAND_{0} = ","QUANTIZE_CAL_MIN_BAND_{0} = ",
                    "REFLECTANCE_MULT_BAND_{0} = ","REFLECTANCE_ADD_BAND_{0} = "]

    meta7=['LANDSAT_SCENE_ID = "','DATE_ACQUIRED = ',"SUN_ELEVATION = ",
                    "RADIANCE_MAXIMUM_BAND_{0} = ","RADIANCE_MINIMUM_BAND_{0} = ",
                    "QUANTIZE_CAL_MAX_BAND_{0} = ","QUANTIZE_CAL_MIN_BAND_{0} = "]

    meta45=['BAND1_FILE_NAME = "',"ACQUISITION_DATE = ","SUN_ELEVATION = ",
                    "LMAX_BAND{0} = ","LMIN_BAND{0} = ",
                    "QCALMAX_BAND{0} = ","QCALMIN_BAND{0} = "]
    if MTL[2]== "8":
        x= meta8
    elif MTL[2]== "7":
        x= meta7
    elif MTL[2]== "4" or MTL== "5":
        x= meta45
    else:
        print """You have entered a dataset that does not have the correct Landsat naming
                conventions. Please restart the script with only Landsat 4,5,7 or 8 files,
                whose names are unchanged from their original versions."""

    fmeta= open(MTL)
    MTLtxt= fmeta.read()
    SEA= float(MTLtxt.split(x[2])[1].split("\n")[0])

    #Assign variables.
    M_rho= float(0.00002)
    A_rho= float(-0.1)
    SEA= float(54.42501009)
    print raster
    #Part one of calculation.
    outCon = Con(raster, raster, "", "VALUE >= 1")
    outTimes = (outCon * M_rho) + A_rho
    #Part two of calculation
    Part2= math.sin(SEA * (math.pi/180))
    #Divide Part 2 from Part 1
    outDivide = outTimes / Part2
    outDivide.save("Reflectance_" + raster)
'''

def Sensible_Heat_Function():
    # equations 28-51
    # start with equations 30-33
    # Num
    # Num31
    # Num30
    # while H doesn't change
        # Num37
        # Num40
    pass


