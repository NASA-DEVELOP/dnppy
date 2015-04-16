
# local imports
from text_data_object import *



def read_csv(filepath, has_headers = True, delim = ','):
    """ simple reader of a delimited file. Does not read fixed-width """
    
    with open(filepath,'r') as f:

        data = []

        if has_headers:
            headers = next(f).replace('\n','').split(delim)
        else:
            headers = None

        for line in f:
            entry = line.replace("\n","").split(delim)
            data.append(entry)
            
        f.close()
            
    print("Loaded data from '{0}'".format(filepath))

    # assemble the text data object and return it
    tdo = text_data_object( text_filepath   = filepath
                            headers         = headers
                            row_data        = data)
    
    return tdo
