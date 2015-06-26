__author__ = ['Quinten Geddes', 'jwely']

def LLtoUTM(Lat, Long):
    """
    function converts lat/lon to UTM coordinates. Equations from USGS
    bulletin 1532. North, East positive.
    :param Lat:
    :param Long:
    :return:
    """
#This function converts lat/long to UTM coords.  Equations from USGS Bulletin 1532
#East Longitudes are positive, West longitudes are negative.
#North latitudes are positive, South latitudes are negative
#Lat and Long are in decimal degrees
#Function was written by Chuck Gantz- chuck.gantz@globalstar.com
#for WGS 84 ellipsoid
    _deg2rad = pi / 180.0
    _rad2deg = 180.0 / pi
    a = 6378137
    eccSquared = 0.00669438
    k0 = 0.9996

#Make sure the longitude is between -180.00 .. 179.9
    LongTemp = (Long+180)-int((Long+180)/360)*360-180 # -180.00 .. 179.9

    LatRad = Lat*_deg2rad
    LongRad = LongTemp*_deg2rad

    LongOrigin = (int(ZoneNumber) - 1)*6 - 180 + 3 #+3 puts origin in middle of zone
    LongOriginRad = LongOrigin * _deg2rad

    eccPrimeSquared = (eccSquared)/(1-eccSquared)
    N = a/sqrt(1-eccSquared*sin(LatRad)*sin(LatRad))
    T = tan(LatRad)*tan(LatRad)
    C = eccPrimeSquared*cos(LatRad)*cos(LatRad)
    A = cos(LatRad)*(LongRad-LongOriginRad)

    M = a*((1
            - eccSquared/4
            - 3*eccSquared*eccSquared/64
            - 5*eccSquared*eccSquared*eccSquared/256)*LatRad
           - (3*eccSquared/8
              + 3*eccSquared*eccSquared/32
              + 45*eccSquared*eccSquared*eccSquared/1024)*sin(2*LatRad)
           + (15*eccSquared*eccSquared/256 + 45*eccSquared*eccSquared*eccSquared/1024)*sin(4*LatRad)
           - (35*eccSquared*eccSquared*eccSquared/3072)*sin(6*LatRad))

    UTMEasting = (k0*N*(A+(1-T+C)*A*A*A/6
                        + (5-18*T+T*T+72*C-58*eccPrimeSquared)*A*A*A*A*A/120)
                  + 500000.0)

    UTMNorthing = (k0*(M+N*tan(LatRad)*(A*A/2+(5-T+9*C+4*C*C)*A*A*A*A/24
                                        + (61
                                           -58*T
                                           +T*T
                                           +600*C
                                           -330*eccPrimeSquared)*A*A*A*A*A*A/720)))

    if Hemisphere == "S":
        UTMNorthing += 10000000.0; #10000000 meter offset for southern hemisphere
    return (UTMNorthing, UTMEasting)