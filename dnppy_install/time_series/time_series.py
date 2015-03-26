
# modules
from datetime import datetime
import csv_io
import os

__author__ = "Jeffry Ely, Jeff.ely.08@gmail.com"


class time_series:
    """
    A subsetable and discretizable time series object

    The primary motivation for creating this object was to allow
    a time series to be discretized into any number of small chunks
    but retain the ability to process and interogate the time series
    at any level with the exact same external syntax.

    A time series object is comprised of a matrix of data, and may contain
    an object list of subset time_series objects. Potentially unlimited
    nesting of time series datasets is possible, for example: a years worth
    of hourly data may be discretized into 1-month time series, while each
    of those is in turn discretized into days. The highest level time series
    will still allow opperations to be performed upon it.

    All internal methods are built to handle this flexible definition of a
    time series, where the steps of the method depend on weather the time
    series is at its smallest subset or not.

    (it isn't quite finished yet)

    MEMORY WARNING. The entirety of the dataset is represented in every layer
    of discretization, so watch out for exploding memory consumption by
    excessive subsetting.

    PLANNED IMPROVEMENTS:
    this needs to be expanded to allow the "data" attribute to be lists of
    filepaths. this will allow advanced time series operations to be performed
    on raster datasets.

    this should allow far more elegant replacement of the follwing funtions
    within the dnppy module:

    "files_in_window"
    "rolling_window"
    "rolling_stats"
    "group_stats"
    """

    def __init__(self, name = "Nameless", units = False, discretized = False, disc_level = 0):
        """ initializes the time series """

        self.name           = name          # the name of this time series
        self.units          = units         # unit of time represented by subset if discretized
        self.discretized    = discretized   # does this time series have subsets?
        self.disc_level     = disc_level    # the subset level of this time_series

        self.rasterpaths    = False         # becomes true if time series is of raster data

        self.fmt            = False         # for interpreting timestrings to time objs
        self.headers        = []            # one header for each col in dataset

        self.time_col       = 0             # index of data column with time info
        self.time           = []            # separate copy of data[time_col]
        self.time_dom       = False         # self.time converted to list of datetime objs
        self.time_dec_days  = []            # self.time converted to mono rising decimal days

        self.subsets        = []            # object list containing constituent time_seires

        self.row_data       = []            # row wise dataset
        self.col_data       = []            # column wise dataset, built as dict

        self.bad_rows       = []            # subset from data attribute with "bad rows"
        return


    def __getitem__(self, arg):
        """
        allows subsets of the time series to be accessed as follows

        Time series whos first row is:
        ['20010101', '045316', '1', '20010101045316', 366]

        With no discretezation layers
        comand        : result
        ts[0]         : ['20010101', '045316', '1', '20010101045316', 366]
        ts[0][0]      : 20010101

        with one discretezation layer
        ts[0]         : <__main__.time_series instance at 0x00000000023CEB48>
        ts[0][0]      : ['20010101', '045316', '1', '20010101045316', 366]
        ts[0][0][0]   : 20010101

        with two discretezation layers
        ts[0]         : <__main__.time_series instance at 0x00000000023CEB48>
        ts[0][0]      : <__main__.time_series instance at 0x00000000023CCA48>
        ts[0][0][0]   : ['20010101', '045316', '1', '20010101045316', 366]
        ts[0][0][0][0]: 20010101
        """

        if isinstance(arg, slice):
            a = arg.start
            b = arg.stop

            if self.discretized:
                if b > len(self.subsets): b = len(self.subsets)
                return [self.subsets[x] for x in range(a,b)]

            else:
                if b > len(self.row_data): b = len(self.row_data)
                return [self.row_data[x] for x in range(a,b)]

        else:
            if self.discretized:
                return self.subsets[arg]

            else:
                return list(self.row_data[arg])



    def _get_atts_from(self, parent_time_series):
        """
        Allows bulk setting of attributes. usefull for allowing a subset to inherit
        information from its parent time_series

        internal use only
        """

        self.fmt            = parent_time_series.fmt
        self.headers        = parent_time_series.headers
        self.time_col       = parent_time_series.time_col
        self.time_header    = parent_time_series.time_header
        self.disc_level     = parent_time_series.disc_level + 1
        return


    def from_csv(self, csv_path):
        """ creates the time_series data from a csv"""

        if not self.discretized:
            self.row_data, self.headers = csv_io.read_csv_rows(csv_path)
            self.build_col_data()

        else:
            raise Warning("You may not import new data into \
                          an already discretized time series")
        return


    def to_csv(self, csv_path):
        """ simply write the data to a csv file"""

        print("Saved time series '{0}' with {1} rows and {2} columns".format(
                                    self.name, len(self.row_data), len(self.col_data)))

        csv_io.write_csv_rows(self.row_data, self.headers, csv_path)
        return


    def from_list(self, data, headers, time_header, fmt):
        """ creates the time series data from a list"""

        self.row_data = data
        self.headers  = headers

        # populates self.time with time series
        self.define_time(self.time_header, self.fmt)
        self.build_col_data()
        return


    def from_rasterlist(self, filepaths, fmt):
        """ loads up a list of filepaths as a time series """

        self.headers = ['filepaths','filenames']
        self.row_data = []

        for filepath in filepaths:
            head, filename = os.path.split(filepath)
            self.row_data.append([filepath, filename])

        self.build_col_data()
        self.define_time('filenames', fmt)

        # flags this time series as being comprised of rasterpaths
        self.rasterpaths  = True

        return


    def build_col_data(self):
        """ builds columnwise data matrix with an actual dict """

        temp_col = zip(*self.row_data)

        self.col_data = {}
        for i,col in enumerate(temp_col):
            self.col_data[self.headers[i]] = col
        return


    def clean(self, col_header):
        """ Removes rows where the specified column has an invalid number"""

        if not col_header in self.headers:
            raise LookupError("{0} header not in dataset!".format(col_header))

        col_index = self.headers.index(col_header)
        temp_data = self.row_data
        self.row_data = []

        for row in temp_data:

            try:
                test = float(row[col_index])
            except:
                self.bad_rows.append(row)
                continue

            self.row_data.append(row)

        print("Removed {0} rows with invalid '{1}'".format(len(self.bad_rows),col_header))
        print("Dataset now has {0} rows".format(len(self.row_data)))

        if self.discretized:
            for subset in self.subsets:
                subset.clean(col_header)
        return


    def add_row(self, row):
        """ simply adds a row to the time_series data"""

        self.row_data.append(list(row))
        return


    def rebuild(self, destroy_subsets = False):
        """ reconstructs the time series from its constituent subsets"""

        # handles time series with multiple levels of discretezation
        while self.subsets[0].discretized:
            for subset in self.subsets:
                subset.rebuild(destroy_subsets)

        else:
            if self.discretized:
                self.row_data = []
                for subset in self.subsets:
                    for row in subset.row_data:
                        self.row_data.append(row)

                self.define_time(self.time_header, self.fmt)

        if destroy_subsets:
            self.subsets = []
            self.discretized = False

        return


    def _extract_time(self, time_header):
        """
        special case of "extract_column" method for time domain

        internal use only
        """

        self.time_header = time_header
        self.build_col_data()

        if time_header in self.headers:
                self.time_col   = self.headers.index(time_header)
                self.time       = self.col_data[time_header]
        else:
            raise LookupError("Time header not in dataset!")

        if self.discretized:
            for subset in self.subsets:
                subset._extract_time(time_header)

        return self.time


    def merge_cols(self, header1, header2):
        """merges two columns together (string concatenation)"""

        new_header  = "_".join([header1, header2])

        for i, entry in enumerate(self.row_data):
                new_field   = "".join([self.col_data[header1][i], self.col_data[header2][i]])

                self.row_data[i].append(new_field)

        # updates column and row data
        self.headers.append(new_header)
        self.build_col_data()

        print("merged '{0}' and '{1}' columns into new column '{2}'".format(header1, header2, new_header))

        if self.discretized:
            for subset in self.subsets:
                subset.merge_cols(header1, header2)

        return



    def define_time(self, time_header, fmt, start_date = False):
        """
        Converts time strings into time objects for standardized processing

        for tips on how to use 'fmt' variable, see url below:
        https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior

        Creates two things:
            a converted list of time objects
            a new list of monotonically increasing decimal days
        """

        # populates self.time with time series
        self._extract_time(time_header)


        # use manual start date or set to begining of first day on record
        if start_date:
            start = datetime.strptime(start_date, fmt)

        else:
            earliest = datetime.strptime(self.time[0], fmt)
            start = datetime(earliest.year, earliest.month, earliest.day, 0,0,0,0)

        datestamp_list      = self.time
        self.fmt            = fmt

        self.time_dom       = []
        self.time_dec_days  = []

        for i,datestamp in enumerate(datestamp_list):

            # If error, give user information about the line on which the error occurs
            try:    t = datetime.strptime(datestamp, fmt)
            except: raise Exception("Input '{0}' in line {1} is not of format {2}".format(
                    datestamp, i+2 , fmt))

            self.time_dom.append(t)

            delta = t - start
            delta = float(delta.total_seconds()) / 86400
            self.time_dec_days.append(float(delta))

        if self.discretized:
            for subset in self.subsets:
                subset.define_time(time_header, fmt)

        return


    def discretize(self, fmt_units):
        """
        splits the time series into individual time chunks

        used for taking advanced statistics, usually periodic
        in nature. Also usefull for exploiting temporal relationships
        in a dataset for a variety of purposes including data
        sanitation, periodic curve fitting, etc.

        fmt_units follows convention of fmt. For example:
        %Y  groups files by year
        %m  groups files by month
        %j  groups file by julian day of year
        """

        # convert units into subset units (because these are the attribute names)
        subset_units = self._fmt_to_units(fmt_units)

        if self.discretized:

            for subset in self.subsets:
                subset.discretize(subset_units)

        else:

            print("Discretizing data by {0}".format(subset_units))

            if self.time_dom == False:
                raise Exception("must call 'define_time' method before discretization!")

            self.discretized = True

            # set up list by which to discretize
            disc_list   = [getattr(x, subset_units) for x in self.time_dom]

            # set up the first subset time_series object
            counter     = 0
            new_subset  = time_series(units = subset_units)

            new_subset._get_atts_from(self)

            # anywhere the subset_unit has changed make new subset time_series
            for i,t in enumerate(disc_list[:-1]):
                now     = disc_list[i]
                later   = disc_list[i+1]

                new_subset.add_row(self.row_data[i])

                if not now == later:
                    # name the current subset and add it to the parent time series
                    new_subset.define_time(self.time_header, self.fmt)
                    new_subset._name_as_subset()
                    self.subsets.append(new_subset)

                    # create new empty subset
                    counter += 1
                    new_subset  = time_series("temp_name", subset_units)

                    new_subset._get_atts_from(self)

            # handles the last group in the data
            new_subset.add_row(self.row_data[-1])
            new_subset.define_time(self.time_header, self.fmt)
            new_subset._name_as_subset()

            self.subsets.append(new_subset)

            # rebuild the time domain
            self.define_time(self.time_header, self.fmt)

        return

    def _name_as_subset(self):
        """
        generates a name string from a datetime object and units

        internal use only
        """

        # uses the time_series object units attribute and
        # first entry in its dataset to descriptively name itself

        subset_units = self.units
        datetime_obj = self.time_dom[0]

        if subset_units == "year" or subset_units == "%Y":
            self.name = datetime_obj.strftime("%Y")

        if subset_units == "month" or subset_units == "%m":
            self.name = datetime_obj.strftime("%Y-%b")

        if subset_units == "day" or subset_units == "%d":
            self.name = datetime_obj.strftime("%Y-%m-%d")

        if subset_units == "hour" or subset_units == "%H":
            self.name = datetime_obj.strftime("%Y-%m-%d-%H")

        if subset_units == "minute" or subset_units == "%M":
            self.name = datetime_obj.strftime("%Y-%m-%d-%H:%M")

        if subset_units == "second" or subset_units == "%S":
            self.name = datetime_obj.strftime("%Y-%m-%d-%H:%M:%S")

        return


    def column_stats(self, col_header):
        """
        takes statistics on a specific column of data

        creates object attributes according to the column name
        """

        #print("Stats for time_series '{0}'. Column '{1}'".format(self.name,col_header))

        # pull column data and find some stats
        import numpy as np

        col_data = map(float, self.col_data[col_header])

        # build array of stats
        stats = [max(col_data),
                 min(col_data),
                 col_data.index(max(col_data)),
                 col_data.index(min(col_data)),
                 np.mean(col_data),
                 np.std(col_data)]

        # build array of names
        names = ["{0}_max_v".format(col_header),
                 "{0}_min_v".format(col_header),
                 "{0}_max_i".format(col_header),
                 "{0}_min_i".format(col_header),
                 "{0}_avg".format(col_header),
                 "{0}_std".format(col_header)]

        # set attributes for names and stats
        for i,stat in enumerate(stats):
            setattr(self, names[i], stats[i])
            #print("{0} \t {1}".format(names[i], stats[i]))

        if self.discretized:
            for subset in self.subsets:
                subset.column_stats(col_header)
        return


    def normalize(col):
        """ used to normalize specific columns in the time series"""

        raise Exception("This 'normalize' function isnt finished!")

        return


    def group_bins(self, fmt_units):
        """
        sorts the time series into time chunks by common bin_unit

        used for grouping data rows together. For example, if one used
        this function on a 5 year dataset with a bin_unit of month,
        then the time_series would be subseted into 12 sets (1 for each
        month), which each set containing all entries for that month,
        regardless of what year they occurred in

        fmt_units follows convention of fmt. For example:
        %Y  groups files by year
        %m  groups files by month
        %j  groups file by julian day of year
        """

        self.discretized = True

        # ensure proper unit format is present
        fmt_units = self._units_to_fmt(fmt_units)

        grouping = [int(obj.strftime(fmt_units)) for obj in self.time_dom]

        for i in range(min(grouping),max(grouping)):

            subset_units    = self._fmt_to_units(fmt_units)
            new_subset      = time_series("temp_name", subset_units)

            new_subset._get_atts_from(self)

            subset_rows = [j for j,e in enumerate(grouping) if e == i]
            subset_data = [self.row_data[row] for row in subset_rows]

            new_subset.from_list(subset_data, self.headers, self.time_header, self.fmt)
            new_subset.define_time(self.time_header, self.fmt)
            new_subset._name_as_subset()

            self.subsets.append(new_subset)
        return


    def _fmt_to_units(self, fmt):
        """ converts fmt strings to unit names of associated datetime attributes """

        fmtlist =  ["%Y", "%m", "%b", "%d", "%j", "%H", "%M", "%S"]
        unitlist = ["year","month","month","day","day","hour","minute","second"]

        if fmt in fmtlist:
            unit = unitlist[fmtlist.index(fmt)]
            return unit

        if fmt in unitlist:
            return fmt


    def _units_to_fmt(self, units):
        """ converts unit names to fmt strings used by datetime.stftime """

        fmtlist  = ["%Y", "%m", "%b", "%d", "%j", "%H", "%M", "%S"]
        unitlist = ["year","month","month","day","day","hour","minute","second"]

        if units in unitlist:
            fmt = fmtlist[unitlist.index(units)]
            return fmt

        if units in fmtlist:
            return units


    def add_mono_time(self):
        """Adds a monotonically increasing time column with units of decimal days"""

        self.row_data = zip(*self.row_data)
        self.row_data.insert(int(self.time_col) + 1, self.time_dec_days)
        self.row_data = zip(*self.row_data)

        if "decimal_days" not in self.headers:
            self.headers.insert(int(self.time_col) + 1, "decimal_days")

        if self.discretized:
            for subset in self.subsets:
                subset.add_mono_time()

        return self.row_data


    def interogate(self):
        """ prints a heads up stats table of all subsets in this time_series """

        if self.disc_level == 0:
            print("")
            print("="*84)
            print("time_series name \t\t len \t start \t\t\t end")
            print("="*84)

        if self.discretized:

            # use leading and trailing spaces for visualizing discretization depth
            padded_name = self.disc_level * "   " + self.name
            print("{0} \t {1} \t {2} \t {3}".format(
                padded_name.ljust(28, " "),
                str(len(self.time)).ljust(5," "),
                self.time_dom[0],
                self.time_dom[-1]))

            for subset in self.subsets:
                subset.interogate()

        else:
            # use leading and trailing spaces for visualizing discretization depth
            padded_name = self.disc_level * "   " + self.name
            print("{0} \t {1} \t {2} \t {3}".format(
                padded_name.ljust(28, " "),
                str(len(self.time)).ljust(5," "),
                self.time_dom[0],
                self.time_dom[-1]))
        return


# testing
if __name__ == "__main__":

    # testing csv manipulations
    ts = time_series('Master_TS')
    ts.from_csv("separate_date_time.csv")
    ts.merge_cols("date", "time")
    ts.define_time("date_time", "%Y%m%d%H%M%S", "20000101000000")
    ts.add_mono_time()

    print("time series with no subsets")
    print "ts[0]         :", ts[0]
    print "ts[0][0]      :", ts[0][0]


    ts.discretize('%d')
    print("time series with one subset layer")
    print "ts[0]         :", ts[0]
    print "ts[0][0]      :", ts[0][0]
    print "ts[0][0][0]   :", ts[0][0][0]


    ts.discretize('%H')
    print("time series with two subset layers")
    print "ts[0]         :", ts[0]
    print "ts[0][0]      :", ts[0][0]
    print "ts[0][0][0]   :", ts[0][0][0]
    print "ts[0][0][0][0]:", ts[0][0][0][0]

    ts.interogate()

    # testing bining
    ts = time_series('Master_TS')
    ts.from_csv("separate_date_time.csv")
    ts.merge_cols("date", "time")
    ts.define_time("date_time", "%Y%m%d%H%M%S", "20000101000000")
    ts.add_mono_time()

    ts.group_bins("%d")
    ts.interogate()
























