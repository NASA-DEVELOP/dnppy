from landsat_metadata import landsat_metadata

def grab_meta(filename):
    """
    Legacy metadata function simply wraps the newer landsat_metadata class.
    You should use ``landsat_metadata`` instead of this function, and can
    refer to that class for further explanation.

    :param filename:            filepath to an MTL file
    :return landsat_metadata:   metadata object with MTL attributes.
    """

    return landsat_metadata(filename)


if __name__ == "__main__":
    m = grab_meta("metadata/LT50140342011307EDC00_MTL.txt")
    m2 = grab_meta("metadata/LC80140342014347LGN00_MTL.txt")

    from pprint import pprint
    pprint(vars(m))