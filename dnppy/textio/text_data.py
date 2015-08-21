
__author__ = ["Jwely"]

import json


class text_data():
    """
    A text data object is a very simple template structure for passing
    text type data (usually lists of weather or climate data entries)
    around between functions.
    """

    def __init__(self, headers = None, row_data = None):

        self.headers        = headers           # headers   (1d list)
        self.row_data       = row_data          # data      (2d list)
        self.col_data       = {}                # column wise data (dict)

        if row_data is not None:
            self._build_col_data()


    def __getitem__(self, index):
        """ used to return row data when using __getitem__ on this object type """

        return self.row_data[index]


    @staticmethod
    def _enf_unique_headers(headers):
        """ Appends digits to duplicate items in a list. Used to ensure each
        header is a unique string so a column-wise dictionary can be built.

        """

        # build list of duplicate values
        duplicates = []
        for i,header in enumerate(headers):
            if i > 0  and header in headers[:(i-1)] and not header in duplicates:
                duplicates.append(header)

        # for each duplicate name, number each occurrence
        for dup in duplicates:
            count = 0
            for i,header in enumerate(headers):
                if header == dup:
                    headers[i] = header + (str(count))
                    count += 1
        return headers


    def _build_col_data(self):
        """
        Builds column wise data dictionary structure out of
        row_data. (row_data is a list of rows, where each row is a list, so
        row_data is a list of lists). Col data is a single dictionary, where
        the keys are the "headers" and the value is the list of all values
        in that column from the top down.
        """

        temp_col = zip(*self.row_data)

        self.col_data = {}
        for i, col in enumerate(temp_col):
            self.col_data[self.headers[i]] = list(col)
        return self.col_data


    def _build_row_data(self):
        """
        Builds row wise data from existing column data. The opposite of
        _build_col_data.
        """

        num_rows = len(self.col_data[self.headers[0]])

        temp_rows = []
        for i in range(num_rows):
            temp_rows.append([self.col_data[header][i] for header in self.headers])

        self.row_data = temp_rows


    def write_csv(self, text_filepath, delim = ','):
        """
        writes the contents of this text file object as a CSV

        :param text_filepath:   output filepath to write csv .txt
        :param delim:           delimiter to use. defaults to comma
        """

        # write the file as a csv
        with open(text_filepath, 'w+') as f:
            if self.headers:
                f.write(delim.join(self.headers) + '\n')

            for row in self.row_data:
                row = map(str,row)
                entry = delim.join(row) + '\n'
                f.write(entry)
            f.close()

        return


    def read_csv(self, text_filepath, delim = ',', has_headers = True):
        """
        simple default reader of a delimited file. Does not read fixed-width

        :param text_filepath:       csv filepath to read from
        :param delim:               delimiter to use, defaults to comma
        :param has_headers:         Set "False" if csv file has no headers
                                    (this is bad, you should give your file headers)
        """

        with open(text_filepath, 'r+') as f:

            self.row_data = []

            if has_headers:
                headers = next(f).replace('\n','').split(delim)
                headers = [x for x in headers if x != ""]
                self.headers = self._enf_unique_headers(headers)
            else:
                self.headers = None

            for line in f:
                # check for a delimiter in the line is used to prevent
                # blank rows from getting into the row_data.
                if delim in line:
                    entry = line.replace('\n','').split(delim)
                    self.row_data.append(entry)
        f.close()
        return


    def write_json(self, json_filepath, row_wise = None, col_wise = None):
        """
        Writes the contents of this text data object to a json file. Note that
        json format does `not` support complex numbers with imaginary components.
        Also note that json formats are dictionary like, in that they preserve
        relationships, but do not display the list of relationships in any particular
        order.

        :param json_filepath:   output filepath to write json
        :param row_wise:        set to TRUE to save each row as its own structure
        :param col_wise:        set to True to save each col as its own structure
        """

        # structures json data
        if row_wise:
            json_dict = [self.headers] + self.row_data
        elif col_wise:
            json_dict = self._build_col_data()
        else:
            raise ValueError("Either 'row_wise' or 'col_wise' args must be set to True!")

        # write the file as a json
        with open(json_filepath, 'w+') as f:
            f.write(json.dumps(json_dict, json_filepath, indent = 4))


    def read_json(self, json_filepath, row_wise = None, col_wise = None):
        """
        Reads the contents of this tdo from a json file created by the
        `` text_data.write_json()``  function. Please note that this text_data
        class is designed for use with tabular type data, so this should
        function will not read ALL json files in a satisfactory manner.
        Users wishing to read json files in a general sense should  simply
        use the ``json`` module and invoke ``json.loads`` and ``json.dumps``
        directly on their data.

        :param json_filepath:   json filepath to read from
        :param row_wise:        read json file objects in as rows
        :param col_wise:        read json file objects in as columns
        """

        json_data = open(json_filepath).read()
        data = json.loads(json_data)

        if row_wise:
            self.row_data = data[1:]
            self.headers = self._enf_unique_headers(data[0])
            self._build_col_data()
        if col_wise:
            self.col_data = data
            self.headers = self._enf_unique_headers([key for key in self.col_data])
            self._build_row_data()
        return



# testing
if __name__ == "__main__":


    wd = text_data()
    wd.read_csv("test_data/weather_example.csv")
    wd.write_csv("test_data/weather_test_out.csv")
    wd.write_json("test_data/weather_test_cols.json", col_wise = True)
    wd.write_json("test_data/weather_test_rows.json", row_wise = True)

    del wd
    wd = text_data()
    wd.read_json("test_data/weather_test_rows.json", row_wise = True)
    wd.write_csv("test_data/weather_test_rows.csv")

    del wd
    wd = text_data()
    wd.read_json("test_data/weather_test_cols.json", col_wise = True)
    wd.write_csv("test_data/weather_test_cols.csv")