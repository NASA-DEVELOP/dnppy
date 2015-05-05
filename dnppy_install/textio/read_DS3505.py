
# local imports
from text_data_class import *

def read_DS3505(filepath, has_headers = True):
    """
    text reader for DS3505 data (space delimited) with some fixes
    
    Weather data downloaded from the following website has a peculiarity
    [http://gis.ncdc.noaa.gov/map/viewer/#app=cdo&cfg=cdo&theme=hourly&layers=1&node=gi]
    in that it has some upercase T's that are rarely needed, but ruin otherwise
    uniform space formatting.
    """
    
    with open(filepath,'r') as f:

        data = []

        if has_headers:
            headers = next(f).replace('\n','').split(' ')
            headers = [x for x in headers if x != ""]
        else:
            headers = None

        for line in f:
            entry = line.replace("T"," ").replace("\n","").split(' ')
            entry = [x for x in entry if x!= ""] # remove emptys
            data.append(entry)
        f.close()
            
    print("Loaded data from '{0}'".format(filepath))

    # assemble the text data object and return it
    tdo = text_data( text_filepath   = filepath,
                            headers         = headers,
                            row_data        = data)
    
    return tdo
