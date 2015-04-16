

def text_data_object():
    """
    a text data object is a very simple template structure
    for passing text type data (usually lists of data entries)
    between other functions in dnppy
    """

    def __init__(self, text_filepath = None, headers = None, row_data = None):

        self.text_filepath  = text_filepath     # filepath  (string)
        self.headers        = headers           # headers   (1d list)
        self.row_data       = row_data          # data      (2d list)
        return


    def write_csv(self, text_filepath = None):
        """ writes the contents of this text file object as a CSV """

        # allow input filepath to overwrite any existing path
        if not text_filepath == None:
            self.text_filepath = text_filepath
            
        if self.text_filepath == None:
            raise Exception("you must provide a filepath to write this data!")

        # write the file as a csv
        with open(text_filepath,'w+') as f:
            if headers:
                f.write(','.join(headers) + '\n')

            for row in data:
                row = map(str,row)
                entry = ','.join(row) + '\n'
                f.write(entry)
            f.close()
            
        print("Saved data to '{0}'".format(filepath))
        return
