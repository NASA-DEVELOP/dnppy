__author__ = ['Quinten Geddes', 'jwely']
__all__ = ["LLtoUTM"]

import numpy as np

def LLtoUTM(lat, lon, utm_zone, hemisphere):
    """
    Function converts lat/lon to UTM zone coordinates. Equations from USGS
    bulletin 1532. East and North are positive, South and West are negative.

    :param lat:             latitude value in degrees (East is positive)
    :param lon:             longitude value in degrees (North is positive)
    :param utm_zone:        UTM zone number as an integer, without the "S" or "N"
    :param hemisphere:      hemisphere for UTM zone, either "S", or "N"

    :return:                UTM_northing, UTM_easting
    """
    a      = 6378137
    eccSq  = 0.00669438         # ECC squared
    k0     = 0.9996

    # Make sure the longitude is between -180.00 .. 179.9
    LongTemp = (lon + 180) - int((lon + 180) / 360) * 360 - 180

    # convert to radians
    LatRad   = lat * np.pi / 180.0
    LongRad  = LongTemp * np.pi / 180.0

    # find the origin of longitude in radians
    LongOrigin = (int(utm_zone) - 1) * 6 - 180 + 3      # +3 puts origin in middle of zone
    LongOriginRad = LongOrigin * np.pi / 180.0

    # find set of coefficients
    eccPrSq = eccSq / (1 - eccSq)       # ECC prime squared
    N = a / np.sqrt(1 - eccSq * np.sin(LatRad) * np.sin( LatRad))
    T = np.tan(LatRad) * np.tan(LatRad)
    C = eccPrSq * np.cos(LatRad) * np.cos(LatRad)
    A = np.cos(LatRad) * (LongRad-LongOriginRad)

    # generate M
    M = a * ((1
            - eccSq / 4
            - 3 * eccSq * eccSq / 64
            - 5 * eccSq * eccSq * eccSq / 256) * LatRad
            - (3 * eccSq / 8
                + 3 * eccSq * eccSq / 32
                + 45 * eccSq * eccSq * eccSq / 1024) * np.sin(2 * LatRad)
            + (15 * eccSq * eccSq / 256 + 45 * eccSq * eccSq * eccSq / 1024) * np.sin(4 * LatRad)
            - (35 * eccSq * eccSq * eccSq / 3072) * np.sin(6 * LatRad))


    # calculate UTM coordinates for input lat/lon
    UTM_easting = (k0 * N * (A + (1 - T + C) * (A ** 3) / 6
                  + (5 - 18 * T + T * T + 72 * C - 58 * eccPrSq) * (A ** 5) / 120)
                  + 500000.0)

    UTM_northing = (k0 * (M + N * np.tan(LatRad) * ((A * A / 2) + (5 - T + (9 * (C + 4)) * (C ** 2)) * ((A ** 4) / 24)
                                        + (61 -58 * T + (T * T) + (600 * C) - (330 * eccPrSq)) * (A ** 6) / 720)))

    # apply a 10000000 meter offset for southern hemisphere
    if hemisphere == "S":
        UTM_northing += 10000000.0

    return UTM_northing, UTM_easting