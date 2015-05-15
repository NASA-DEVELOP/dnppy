__author__ = 'jwely'

import os

def exists(location):
    """Ensures input location is either a file or a folder"""

    # if the object is neither a file or a location, return False.
    if not os.path.exists(location) and not os.path.isfile(location):
        print("{0} is not a valid file or folder!".format(location))
        return False

    else:
        return True

