
"""
quick landsat 8 surface temperature code, doesnt work yet
"""


def surface_temp():
    """
    calculates the surface temperature with a modified plank equation
    following Markham and Barker.

                       K2
    Ts =    ----------------------
            ln((enb * K1 / Rc) +1)

    where
        K1  = constant 1, landsat specific
        K2  = constant 2, landsat specific
        Rc  = corrected thermal radiance
        enb = narrow band emissivity for thermal sensor wavelength band

    and

                Lt6 - Rp (tnb)
        Rc =    --------------  - (1 - enb) * Rsky
                     tnb

    where
        Lt6 = spectral radience of landsat band 6
        Rp  = path radiance in the 10.4 to 12.5 um band
        Rsky= narrow band downward thermal radiation from clear sky
        tnb = narrow band transmissivity of air (10.4 to 12.5 um range)
    """

    correct_rad = ((therm_rad - path_rad) / nbt) - ((1-nbe) * sky_rad)

    surface_temp = (K2 / (math.ln(((nbe * K1) / correct_rad) + 1 )))
    return
