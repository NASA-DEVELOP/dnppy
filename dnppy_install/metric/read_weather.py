from csv_io import *
from time_series import time_series
from datetime import datetime
#from function_bank import *

time        = "empty"
wx_filepath = "Sparrow_Kent_KEWN_Daily_July2013.txt"

def Wx_Data_Extract(time_obj, wx_daypath, wx_hourpath):
    """
    This function was writen to reenstate wx file parsing for tha greed upon NOAA
    weather data format for any study area within the USA. This is THE function
    that should be used for reading weather data, the others will not be supported.

    Author: Jeffry Ely
    """

    # datetime , num ,max_temp (F) , min_temp (F), max_dew_pt (F), min_dew_pt (F), average_P (kpa), reference_ET (in)
    
    # format weather (daily and hourly) as a time series object from dnppy module
    wx_day = time_series("wx_daily_data")
    wx_day.from_csv(wx_daypath)
    wx_day.define_time(0, "%m/%d/%Y", "01/01/2000")

##    wx_hour = time_series("wx_hourly_data")
##    wx.hour.from_csv(wx_hourpath)
##    wx_hour.define_time(0, "%m/%d/%Y", "01/01/2000")

    return wx_day
    return [temp_C_min, temp_C_max, temp_C_mid, P_air, wind_speed, dewp_C]


w = Wx_Data_Extract(time, wx_filepath, "poop")
w.interp_col(datetime(2013,7,1,12),w.headers[2])
