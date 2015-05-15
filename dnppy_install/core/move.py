__author__ = 'jwely'

import os, shutil

def move(source, destination):
    """Moves a file"""

    dest_path, name = os.path.split(destination)

    # create that directory if it doesnt already exist
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    try:
        shutil.move(source, destination)
        print('moved file from {0} to {1}'.format(source, destination))
    except:
        print("failed to move file from {0}".format(source))

    return dest_path