"""
Referenced by time_series module

quick dirty script for simple read and write of csv files

It contains some information about special formats that may be
frequently used by DEVELOP participants

"""

__author__ = ["Jeffry Ely, jeff.ely.08@gmail.com"]


def read_csv_rows(filepath, has_headers = True, delim = ',', spec_format = False):
    """
    import csv data as standard rows

    It allows some custom spec_format flags to be used for very special
    case datasets:

    spec_format:
        DS3505
            data downloaded from the following website has a peculiarity
            [http://gis.ncdc.noaa.gov/map/viewer/#app=cdo&cfg=cdo&theme=hourly&layers=1&node=gi]
            in that it has some upercase T's that are rarely needed, but ruin otherwise
            uniform space formatting.
        """
    
    with open(filepath,'r') as f:

        data = []

        if has_headers:
            headers = next(f).replace('\n','').split(delim)
            headers = [x for x in headers if x != ""] # remove emptys
        else:
            headers = False

        for line in f:
            
            if spec_format == "DS3505":
                entry = line.replace("T"," ").replace("\n","").split(delim)
            else:
                entry = line.replace("\n","").split(delim)
                
            entry = [x for x in entry if x!= ""] # remove emptys
            data.append(entry)
        f.close()
            
    print("Loaded data from '{0}'".format(filepath))
    return data, headers


def read_csv_cols(filepath, has_headers = True, delim = ','):
    """import csv data in columnwise format (transposed)"""

    data, headers = read_csv_rows(filepath, has_headers, delim)
    return zip(*data), headers


def write_csv_rows(data, headers, filepath):
    """ writes some row wise data structure to a csv file"""

    with open(filepath,'w+') as f:

        if headers:
            f.write(','.join(headers) + '\n')

        for row in data:
            row = map(str,row)
            entry = ','.join(row) + '\n'
            f.write(entry)
        f.close()
        
    print("Saved data to '{0}'".format(filepath))
    return


def write_csv_cols(data, headers, filepath):
    """ writes some column wise data structure to a csv file"""

    data = zip(*data)
    write_csv_rows(data, headers, filepath)
    return


