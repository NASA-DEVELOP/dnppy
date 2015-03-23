
def read_csv_rows(filepath):
    """import csv data as standard rows"""
    
    with open(filepath,'r') as f:

        data = []
        headers = next(f).replace('\n','').split(',')

        for line in f:
            entry = line.replace('\n','').split(',')
            data.append(entry)
        f.close()
            
    print("Loaded data from {0}".format(filepath))
    return data, headers


def read_csv_cols(filepath):
    """import csv data in columnwise format (transposed)"""

    data, headers = read_csv_rows(filepath)
    return zip(*data), headers


def write_csv_rows(data, headers, filepath):
    """ writes some row wise data structure to a csv file"""

    with open(filepath,'w+') as f:
        f.write(','.join(headers) + '\n')

        for row in data:
            row = map(str,row)
            entry = ','.join(row) + '\n'
            f.write(entry)
        f.close()
        
    print("Saved data to {0}".format(filepath))
    return


def write_csv_cols(data, headers, filepath):
    """ writes some column wise data structure to a csv file"""

    data = zip(*data)

    write_csv_rows(data, headers, filepath)
    return




