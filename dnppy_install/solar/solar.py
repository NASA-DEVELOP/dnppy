"""
solar object class, built in my spare time for a personal project.


Distributed with the dnppy module, with permission from its original
author, Jeff Ely.
"""


__author__ = ["Jeffry Ely, Jeff.ely.08@gmail.com"]


from datetime import datetime, timedelta
from numpy import radians, ndarray, sin, cos, degrees, arctan2, arcsin, tan, arccos

class solar:
    """
    Object class for handling solar calculations. Many equations are taken from the
    excel sheet at this url : [http://www.esrl.noaa.gov/gmd/grad/solcalc/calcdetails.html]

    It requires a physical location on the earth and a datetime object

    Inputs: 
        lat             decimal degrees latitude (float OR numpy array)
        lon             decimal degrees longitude (float OR numpy array)
        time_zone       float of time shift from GMT (such as "-5" for EST)
        date_time_obj   either a timestamp string following fmt or a datetime obj
        fmt             if date_time_obj is a string, fmt is required to interpret it
        slope           slope of land at lat,lon for solar energy calculations
        aspect          aspect of land at lat,lon for solar energy calculations

    An instance of this class may have the following atributes:
        lat                 latitude                                    (array)
        lon                 longitude                                   (array)
        tz                  time zone                                   (scalar)
        rdt                 reference datetime object (date_time_obj)   (scalar)
        ajd                 absolute julian day                         (scalar)
        ajc                 absolute julian century                     (scalar)
        geomean_long        geometric mean longitude of the sun         (scalar)
        geomean_anom        geometric mean longitude anomaly of the sun (scalar)
        earth_eccent        eccentricity of earths orbit                (scalar)
        sun_eq_of_center    the suns equation of center                 (scalar)
        true_long           true longitude of the sun                   (scalar)
        true_anom           true longitude anomaly of the sun           (scalar)
        app_long            the suns apparent longitude                 (scalar)
        oblique_mean_elip   earth oblique mean elipse                   (scalar)
        oblique_corr        correction to earths oblique elipse         (scalar)
        right_ascension     suns right ascension angle                  (scalar)
        declination         solar delination angle                      (scalar)
        equation_of_time    equation of time (minutes)                  (scalar)
        hour_angle_sunrise  the hour angle at sunrise                   (array)
        solar_noon          LST of solar noon                           (array)
        sunrise             LST of sunrise time                         (array)
        sunset              LST of sunset time                          (array)
        sunlight            LST fractional days of sunlight             (array)
        true_solar          LST for true solar time                     (array)
        hour_angle          total hour angle                            (array)
        zenith              zenith angle                                (array)
        elevation           elevation angle                             (array)
        azimuth             azimuthal angle                             (array)
        rad_vector          radiation vector (distance in AU)           (scalar)
        earth_distance      earths distance to sun in meters            (scalar)
        norm_irradiance     incident solar energy at earth distance     (scalar)


    Units used by this class unless otherwise labled:
        angle    = degrees
        distance = meters
        energy   = watts or joules
        time     = mostly in datetime objects.

    PLANNED IMPROVEMENT:
    1) DONE. Inputs of numpy arrays for lat and lon needs to be allowed.
    2) inputs of a numpy array DEM for slope/aspect effects on incident solar energy
        intensity need to be allowed.
    3) needs to be structured to allow optimization for extremely large input arrays.
       Presently, all variables are calculated and indefinitely kept in memory (12-15 arrays).
       There should be some kind of "large_dataset" setting that allows desired values
       to be saved to disk and then removed from memory, and other unneeded values to
       be skipped all together.

    Present performance:
    To process about one landsat tile (7300^2 matrix) requires 9GB of memory and takes
    45 seconds to process on a single 3.3GHz thread. It would be nice to get the same output
    to run on ~5GB of memory so a 8GB system could handle it.
    """
    

    def __init__(self, lat, lon, date_time_obj, time_zone = 0,
                         fmt = False, slope = None, aspect = None):
        """
        Initializes critical spatial and temporal information for solar object.
        """

        # empty list of class attributes
        self.ajc                = None          # abs julian century (defined on __init__)
        self.ajd                = None          # abs julian day (defined on __init__)
        self.app_long           = None
        self.atmo_refraction    = None
        self.azimuth            = None
        self.declination        = None 
        self.earth_distance     = None
        self.earth_eccent       = None
        self.elevation          = None
        self.elevation_noatmo   = None
        self.equation_of_time   = None
        self.frac_day           = None
        self.geomean_anom       = None
        self.geomean_long       = None
        self.hour_angle         = None
        self.hour_angle_sunrise = None
        self.lat                = lat           # lattitude (E positive)- float
        self.lat_r              = radians(lat)  # lattitude in radians
        self.lon                = lon           # longitude (N positive)- float
        self.lon_r              = radians(lon)  # longitude in radians
        self.norm_irradiance    = None
        self.oblique_corr       = None
        self.oblique_mean_elip  = None
        self.rad_vector         = None
        self.rdt                = None          # reference datetime (defined on __init__)
        self.right_ascension    = None
        self.solar_noon         = None
        self.solar_noon_time    = None
        self.sun_eq_of_center   = None
        self.sunlight           = None
        self.sunlight_time      = None
        self.sunrise            = None
        self.sunrise_time       = None
        self.sunset             = None
        self.sunset_time        = None
        self.true_anom          = None
        self.true_long          = None
        self.true_solar         = None
        self.true_solar_time    = None
        self.tz                 = None          # time zone (defined on __init__)
        self.zenith             = None

        
        # Constants as attributes
        self.sun_surf_rad       = 63156942.6    # radiation at suns surface (W/m^2)
        self.sun_radius         = 695800000.    # radius of the sun in meters
        self.orbital_period     = 365.2563630   # num of days it takes earth to revolve
        self.altitude           = -0.01448623   # altitude of center of solar disk


        # sets up the object with some subfunctions
        self._set_datetime(date_time_obj, fmt, GMT_hour_offset = time_zone)

        # specify if attributes are scalar floats or numpy array floats
        if isinstance(lat, ndarray) and isinstance(lon, ndarray):
            self.is_numpy   = True
        else:
            self.is_numpy   = False
        
        return
    

    def _set_datetime(self, date_time_obj, fmt = False, GMT_hour_offset = 0):
        """
        sets the critical time information including absolute julian day/century

        Accepts datetime objects or a datetime string with format
        """

        # if input is datetime_obj set it
        if isinstance(date_time_obj, datetime):
            self.rdt =      date_time_obj
            self.rdt +=     timedelta(hours = -GMT_hour_offset)

        elif isinstance(date_time_obj, str) and isinstance(fmt, str):
            self.rdt =      datetime.strptime(date_time_obj,fmt)
            self.rdt +=     timedelta(hours = -GMT_hour_offset)
        else:
            raise Exception("bad datetime!")

        self.tz = GMT_hour_offset


        # uses the reference day of january 1st 2000
        jan_1st_2000_jd   = 2451545
        jan_1st_2000      = datetime(2000,1,1,12,0,0)

        time_del = self.rdt - jan_1st_2000
        self.ajd = float(jan_1st_2000_jd) + float(time_del.total_seconds())/86400
        self.ajc = (self.ajd - 2451545)/36525.0
        
        return


    def get_geomean_long(self):
        """ calculates geometric mean longitude of the sun"""

        if not self.geomean_long == None:
            return self.geomean_long
            
        self.geomean_long = (280.46646 + self.ajc * (36000.76983 + self.ajc*0.0003032)) % 360
        return self.geomean_long


    def get_geomean_anom(self):
        """calculates the geometric mean anomoly of the sun"""

        if not self.geomean_anom == None:
            return self.geomean_anom

        self.geomean_anom = (357.52911 + self.ajc * (35999.05029 - 0.0001537 * self.ajc))
        return self.geomean_anom

    
    def get_earth_eccent(self):
        """
        Calculates the precise eccentricity of earths orbit at ref_datetime
        """

        if not self.earth_eccent == None:
            return self.earth_eccent
        
        self.earth_eccent = 0.016708634 - self.ajc * (4.2037e-5 + 1.267e-7 * self.ajc)
        
        return self.earth_eccent


    def get_sun_eq_of_center(self):
        """calculates the suns equation of center"""

        if not self.sun_eq_of_center == None:
            return self.sun_eq_of_center

        if self.geomean_anom == None:
            self.get_geomean_anom()
            
        ajc = self.ajc
        gma = radians(self.geomean_anom)

        self.sun_eq_of_center = sin(gma) * (1.914602 - ajc*(0.004817 + 0.000014 * ajc)) + \
                                sin(2*gma) * (0.019993 - 0.000101 * ajc) + \
                                sin(3*gma) * 0.000289

        return self.sun_eq_of_center


    def get_true_long(self):
        """ calculates the tru longitude of the sun"""

        if not self.true_long == None:
            return self.true_long
        
        if self.geomean_long == None:
            self.get_geomean_long()
            
        if self.sun_eq_of_center == None:
            self.get_sun_eq_of_center()

        self.true_long = self.geomean_long + self.sun_eq_of_center
        return self.true_long


    def get_true_anom(self):
        """ calculates the true anomoly of the sun"""

        if not self.true_anom == None:
            return self.true_anom
        
        if self.geomean_long == None:
            self.get_geomean_long()
            
        if self.sun_eq_of_center == None:
            self.get_sun_eq_of_center()
            
        self.true_anom = self.geomean_anom + self.sun_eq_of_center
        return self.true_anom

        
    def get_rad_vector(self):
        """ calculates incident radiation vector to surface at ref_datetime (AUs)"""

        if not self.rad_vector == None:
            return self.rad_vector
        
        if self.earth_eccent == None:
            self.get_earth_eccent()

        if self.true_anom == None:
            self.get_true_anom()
            
        ec = self.earth_eccent
        ta = radians(self.true_anom)
        
        self.rad_vector  = (1.000001018*(1 - ec**2)) / (1 + ec *cos(ta))
        return self.rad_vector


    def get_app_long(self):
        """ calculates apparent longitude of the sun"""

        if not self.app_long == None:
            return self.app_long
        
        if self.true_long == None:
            self.get_true_long()

        stl = self.true_long
        ajc = self.ajc

        self.app_long = stl - 0.00569 - 0.00478 * sin(radians(125.04 - 1934.136 * ajc))
        return self.app_long
        

    def get_oblique_mean_elip(self):
        """ calculates the oblique mean eliptic of earth orbit """

        if not self.oblique_mean_elip == None:
            return self.oblique_mean_elip
        
        ajc = self.ajc

        self.oblique_mean_elip = 23 + (26 + ((21.448 - ajc * (46.815 + ajc * (0.00059 - ajc * 0.001813))))/60)/60
        return self.oblique_mean_elip


    def get_oblique_corr(self):
        """ calculates the oblique correction """

        if not self.oblique_corr == None:
            return self.oblique_corr
        
        if self.oblique_mean_elip == None:
            self.get_oblique_mean_elip()
            
        ome = self.oblique_mean_elip
        ajc = self.ajc
        
        self.oblique_corr = ome + 0.00256 * cos(radians(125.04 - 1934.136 * ajc))
        return self.oblique_corr


    def get_right_ascension(self):
        """ calculates the suns right ascension angle """

        if not self.right_ascension == None:
            return self.right_ascension
        
        if self.app_long == None:
            self.get_app_long()

        if self.oblique_corr == None:
            self.get_oblique_corr()
            
        sal = radians(self.app_long)
        oc  = radians(self.oblique_corr)

        self.right_ascension = degrees(arctan2(cos(oc) * sin(sal), cos(sal)))
        return self.right_ascension
        
    
    def get_declination(self):
        """ solar declination angle at ref_datetime"""

        if not self.declination == None:
            return self.declination
        
        if self.app_long == None:
            self.get_app_long()

        if self.oblique_corr == None:
            self.get_oblique_corr()
            
        sal = radians(self.app_long)
        oc  = radians(self.oblique_corr)
        
        self.declination = degrees(arcsin((sin(oc) * sin(sal))))
        return self.declination

        pass


    def get_equation_of_time(self):
        """ calculates the equation of time in minutes """

        if not self.equation_of_time == None:
            return self.equation_of_time
        
        if self.oblique_corr == None:
            self.get_oblique_corr()

        if self.geomean_long == None:
            self.get_geomean_long()

        if self.geomean_anom == None:
            self.get_geomean_anom()

        if self.earth_eccent == None:
            self.get_earth_eccent()

        oc  = radians(self.oblique_corr)
        gml = radians(self.geomean_long)
        gma = radians(self.geomean_anom)
        ec  = self.earth_eccent

        vary = tan(oc/2)**2

        self.equation_of_time = 4 * degrees(vary * sin(2*gml) - 2 * ec * sin(gma) + \
                                4 * ec * vary * sin(gma) * cos(2 * gml) -           \
                                0.5 * vary * vary * sin(4 * gml) -                  \
                                1.25 * ec * ec * sin(2 * gma))
        
        return self.equation_of_time


    def get_hour_angle_sunrise(self):
        """ calculates the hour hangle of sunrise """

        if not self.hour_angle_sunrise == None:
            return self.hour_angle_sunrise
            
        if self.declination == None:
            self.get_declination()

        d   = radians(self.declination)
        lat = self.lat_r

        self.hour_angle_sunrise = degrees(arccos((cos(radians(90.833)) /      \
                                  (cos(lat) * cos(d)) - tan(lat) * tan(d))))

        return self.hour_angle_sunrise


    def get_solar_noon(self):
        """ calculats solar noon in (local sidereal time LST)"""

        if not self.solar_noon == None:
            return self.solar_noon
        
        if self.equation_of_time == None:
            self.get_equation_of_time()

        lat = self.lat
        lon = self.lon
        eot = self.equation_of_time
        tz  = self.tz

        self.solar_noon = (720 - 4 * lon - eot + tz * 60)/1440

        # format this as a time for display purposes (Hours:Minutes:Seconds)
        if self.is_numpy:
            self.solar_noon_time = timedelta(days = self.solar_noon.mean())
        else:
            self.solar_noon_time = timedelta(days = self.solar_noon)
        
        return self.solar_noon
    

    def get_sunrise(self):
        """ calculates the time of sunrise"""

        if not self.sunrise == None:
            return self.sunrise
        
        if self.solar_noon == None:
            self.get_solar_noon()

        if self.hour_angle_sunrise == None:
            self.get_hour_angle_sunrise()

        sn = self.solar_noon
        ha = self.hour_angle_sunrise

        self.sunrise = (sn * 1440 - ha * 4)/1440

        # format this as a time for display purposes (Hours:Minutes:Seconds)
        if self.is_numpy:
            self.sunrise_time = timedelta(days = self.sunrise.mean())
        else:
            self.sunrise_time = timedelta(days = self.sunrise)
        
        return self.sunrise


    def get_sunset(self):
        """ calculates the time of sunrise"""

        if not self.sunset == None:
            return self.sunset

        if self.solar_noon == None:
            self.get_solar_noon()

        if self.hour_angle_sunrise == None:
            self.get_hour_angle_sunrise()

        sn = self.solar_noon
        ha = self.hour_angle_sunrise

        
        self.sunset = (sn * 1440 + ha * 4)/1440

        # format this as a time for display purposes (Hours:Minutes:Seconds)
        if self.is_numpy:
            self.sunset_time = timedelta(days = self.sunset.mean())
        else:
            self.sunset_time = timedelta(days = self.sunset)

        return self.sunset


    def get_sunlight(self):
        """ calculates amount of daily sunlight in fractional days"""

        if not self.sunlight == None:
            return self.sunlight
        
        if self.hour_angle_sunrise == None:
            self.get_hour_angle_sunrise()
            
        self.sunlight = 8 * self.hour_angle_sunrise / (60 * 24)

        # format this as a time for display purposes (Hours:Minutes:Seconds)
        if self.is_numpy:
            self.sunlight_time = timedelta(days = self.sunlight.mean())
        else:
            self.sunlight_time = timedelta(days = self.sunlight)
        
        return self.sunlight

    
    def get_true_solar(self):
        """ calculates the true solar time at ref_datetime"""

        if not self.true_solar == None:
            return self.true_solar
        
        if self.equation_of_time == None:
            self.get_equation_of_time()
            
        lat = self.lat
        lon = self.lon
        eot = self.equation_of_time

        # turn reference datetime into fractional days
        frac_sec = (self.rdt - datetime(self.rdt.year, self.rdt.month, self.rdt.day)).total_seconds() 
        frac_hr  = frac_sec / (60 * 60) + self.tz
        frac_day = frac_hr / 24

        self.frac_day = frac_day

        # now get true solar time
        self.true_solar = (frac_day * 1440 + eot + 4 * lon - 60 * self.tz) % 1440

        # format this as a time for display purposes (Hours:Minutes:Seconds)
        if self.is_numpy:
            self.true_solar_time = timedelta(days = self.true_solar.mean() / (60*24))
        else:
            self.true_solar_time = timedelta(days = self.true_solar / (60*24))

        return self.true_solar
        

    def get_hour_angle(self):
        """ calculates the hour angle at ref_datetime"""

        if not self.hour_angle == None:
            return self.hour_angle
        
        if self.true_solar == None:
            self.get_true_solar()
            
        ts = self.true_solar

        # matrix hour_angle calculations
        if self.is_numpy:
            ha = ts
            ha[ha <= 0] = ha[ha <= 0]/4 + 180
            ha[ha >  0] = ha[ha >  0]/4 - 180
            self.hour_angle = ha

        # scalar hour_angle calculations
        else:
            if ts <= 0:
                self.hour_angle = ts/4 + 180
            else:
                self.hour_angle = ts/4 - 180

        return self.hour_angle
        
        
    def get_zenith(self):
        """ calculates solar zenith angle at ref_datetime"""

        if not self.zenith == None:
            return self.zenith
        
        if self.declination == None:
            self.get_declination()

        if self.hour_angle == None:
            self.get_hour_angle()

        d   = radians(self.declination)
        ha  = radians(self.hour_angle)
        lat = self.lat_r

        self.zenith = degrees(arccos(sin(lat) * sin(d) + \
                                    cos(lat) * cos(d) * cos(ha)))

        return self.zenith
    

    def get_elevation(self):
        """ calculates solar elevation angle at ref_datetime"""

        if not self.elevation == None:
            return self.elevation
        
        if self.zenith == None:
            self.get_zenith()
            
        # perform an approximate atmospheric refraction correction
        
        # matrix hour_angle calculations
        # these equations are hideous, but im not sure how to improve them without adding computational complexity
        if self.is_numpy:
            e = 90 - self.zenith
            ar = e * 0 

            ar[e >  85]                 = 0
            ar[(e > 5) & (e <=85)]      = 58.1 / tan(radians(e[(e > 5) & (e <=85)])) - \
                                          0.07 / tan(radians(e[(e > 5) & (e <=85)]))**3 + \
                                          0.000086 / tan(radians(e[(e > 5) & (e <=85)]))**5
            ar[(e > -0.575) & (e <= 5)] = 1735 + e[(e > -0.575) & (e <= 5)] * \
                                            (103.4 + e[(e > -0.575) & (e <= 5)] * (-12.79 + e[(e > -0.575) & (e <= 5)] * 0.711))
            ar[e <= -0.575]             = -20.772 / tan(radians(e[e <= -0.575]))

        # scalar hour_angle calculations
        else:
            e  = 90 - self.zenith
            er = radians(e)
            
            if   e > 85:        ar = 0
            elif e > 5:         ar = 58.1 / tan(er) - 0.07 / tan(er)**3 + 0.000086 / tan(er)**5  
            elif e > -0.575:    ar = 1735 + e * (103.4 + e * ( -12.79 + e * 0.711)) 
            else:               ar = -20.772 / tan(er)
            

        self.elevation_noatmo = e
        self.atmo_refraction  = ar / 3600
        self.elevation        = self.elevation_noatmo + self.atmo_refraction
        
        return self.elevation

    
    def get_azimuth(self):
        """ calculates solar azimuth angle at ref_datetime"""


        if not self.azimuth == None:
            return self.azimuth
        
        if self.declination == None:
            self.get_declination()

        if self.hour_angle == None:
            self.get_hour_angle()

        if self.zenith == None:
            self.get_zenith()
            
        lat = self.lat_r       
        d   = radians(self.declination)
        ha  = radians(self.hour_angle)                
        z   = radians(self.zenith)     

        # matrix azimuth calculations
        # these equations are hideous, but im not sure how to improve them without adding computational complexity
        if self.is_numpy:

            az = ha * 0

            az[ha > 0] = (degrees(arccos(((sin(lat[ha > 0]) * cos(z[ha > 0])) - sin(d)) / (cos(lat[ha > 0]) * sin(z[ha > 0])))) + 180) % 360
            az[ha <=0] = (540 - degrees(arccos(((sin(lat[ha <=0]) * cos(z[ha <=0])) -sin(d))/ (cos(lat[ha <=0]) * sin(z[ha <=0]))))) % 360

            self.azimuth = az

        else:  
            if ha > 0:
                self.azimuth = (degrees(arccos(((sin(lat) * cos(z)) - sin(d)) / (cos(lat) * sin(z)))) + 180) % 360
            else:
                self.azimuth = (540 - degrees(arccos(((sin(lat) * cos(z)) -sin(d))/ (cos(lat) * sin(z))))) % 360

        return self.azimuth


    def get_earth_distance(self):
        """ distance between the earth and the sun at ref_datetime"""

        if self.rad_vector == None:
            self.get_rad_vector()

            
        # convert rad_vector length from AU to meters
        self.earth_distance = self.rad_vector * 149597870700
        
        return self.earth_distance


    def get_norm_irradiance(self):
        """
        calculates incoming solar energy in W/m^2 to a surface normal to the sun

        inst_irradiance is calculated as 
            = sun_surf_radiance *(sun_radius / earth_distance)^2

        then corrected as a function of solar incidence angle
        """

        if not self.norm_irradiance == None:
            return self.norm_irradiance
        
        if self.earth_distance == None:
            self.get_earth_distance()
            
        ed = self.earth_distance

        # calculate irradiance to normal surface at earth distance
        self.norm_irradiance = self.sun_surf_rad * (self.sun_radius / ed)**2
        
        return self.norm_irradiance


    def get_inc_irradiance(self):
        """
        calculates the actual incident solar irradiance at a given lat,lon coordinate
        with adjustments for slope and aspect if they have been given.
        """

        print("this function is unfinished!")

        return


    def summarize(self):
        """ prints attribute list and coresponding values"""

        for key in sorted(self.__dict__.iterkeys()):
            print("{0} {1}".format(key.ljust(20),sc.__dict__[key]))

        return
    

    def compute_all(self):
        """ computes and prints all the attributes of this solar object"""

        print("="*50)
        print("Interogation of entire matrix of points.")
        print("Some values displayed below are spatial averages")
        print("="*50)
        
        if self.is_numpy: # print means of lat/lon arrays
            print("latitude, longitude \t{0}, {1}".format(self.lat.mean(), self.lon.mean()))
        else:
            print("latitude, longitude \t{0}, {1}".format(self.lat, self.lon))

        print("datetime \t\t{0} (GMT)".format(self.rdt))
        print("time zone \t\t{0} (GMT offset)".format(self.tz))
        print("")
        print("abs julian day \t\t{0}\t (day)".format(self.ajd))
        print("abs julian century \t{0}\t (cen)".format(self.ajc))
        print("suns geomean long \t{0}\t (deg)".format(self.get_geomean_long()))
        print("suns geomean anom \t{0}\t (deg)".format(self.get_geomean_anom()))
        print("earth eccentricity \t{0}".format(self.get_earth_eccent()))
        print("suns eq of center \t{0}".format(self.get_sun_eq_of_center()))
        print("suns true long \t\t{0}\t (deg)".format(self.get_true_long()))
        print("suns true anom \t\t{0}\t (deg)".format(self.get_true_anom()))
        print("suns apparent long \t{0}\t (deg)".format(self.get_app_long()))
        print("earth obliq mean elip \t{0}\t (deg)".format(self.get_oblique_mean_elip()))
        print("earth obliq correction\t{0}\t (deg)".format(self.get_oblique_corr()))
        print("sun right ascension \t{0}\t (deg)".format(self.get_right_ascension()))
        print("solar declination angle {0}\t (deg)".format(self.get_declination()))
        print("equation of time \t{0}\t (min)".format(self.get_equation_of_time()))
        
        if self.is_numpy: # print means of hour angle array
            print("hour angle sunrise\t{0}\t (deg)".format(self.get_hour_angle_sunrise().mean())) 
        else:
            print("hour angle sunrise\t{0}\t (deg)".format(self.get_hour_angle_sunrise()))    
            
        print("")
        self.get_solar_noon()
        print("solar noon \t\t{0}\t (HMS - LST)".format(self.solar_noon_time))
        self.get_sunrise()
        print("sunrise \t\t{0}\t (HMS - LST)".format(self.sunrise_time))
        self.get_sunset()
        print("sunset  \t\t{0}\t (HMS - LST)".format(self.sunset_time))
        self.get_sunlight()
        print("sunlight durration \t{0}\t (HMS)".format(self.sunlight_time))
        self.get_true_solar()
        print("true solar time \t{0}\t (HMS - LST)".format(self.true_solar_time))
        print("")

        if self.is_numpy: #print means of these array objects
            print("hour angle \t\t{0}\t (deg)".format(self.get_hour_angle().mean()))            
            print("solar zenith angle \t{0}\t (deg)".format(self.get_zenith().mean()))        
            print("solar elevation angle \t{0}\t (deg)".format(self.get_elevation().mean()))    
            print("solar azimuth angle \t{0}\t (deg)".format(self.get_azimuth().mean()))        
        else:
            print("hour angle \t\t{0}\t (deg)".format(self.get_hour_angle()))                  
            print("solar zenith angle \t{0}\t (deg)".format(self.get_zenith()))                 
            print("solar elevation angle \t{0}\t (deg)".format(self.get_elevation()))           
            print("solar azimuth angle \t{0}\t (deg)".format(self.get_azimuth()))               

        print("")
        print("radiation vector \t{0}\t (AU)".format(self.get_rad_vector()))                  
        print("earth sun distance \t{0}(m)".format(self.get_earth_distance()))             
        print("norm irradiance \t{0}\t (W/m*m)".format(self.get_norm_irradiance()))           
        print("="*50)


# testing
if __name__ == "__main__":

    
    # use the current time and my time zone
    datestamp   = "20150515-120000"     # date stamp
    fmt         = "%Y%m%d-%H%M%S"       # datestamp format
    tz          = -4                    # timezone (GMT/UTC) offset
    lat = 37                            # lat (N positive)
    lon = -76.4                         # lon (E positive)
    
    sc  = solar(lat, lon, datestamp, tz, fmt)
    sc.compute_all()
    sc.summarize()


##    # numpy array test
##    import numpy
##    lat = numpy.array([[36, 36],[38,38]])
##    lon = numpy.array([[-77.4,-75.4],[-77.4,-75.4]])
##    sm  = solar(lat, lon, datestamp, tz, fmt)
##    
##    sm.compute_all()
    







    
        
