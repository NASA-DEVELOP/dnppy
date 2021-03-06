

# local imports
from csv_io import *

# standard imports
import numpy
import os
from datetime import datetime, timedelta
from calendar import monthrange, isleap
import matplotlib.pyplot as plt


__author__ = ["Jeffry Ely, Jeff.ely.08@gmail.com"]


class time_series:
    """
    A subsetable and discretizable time series object

    The primary motivation for creating this object was to allow
    a time series to be discretized into any number of small chunks
    but retain the ability to process and interrogate the time series
    at any level with the exact same external syntax.

    A time series object is comprised of a matrix of data, and may contain
    an object list of subset time_series objects. Potentially unlimited
    nesting of time series datasets is possible, for example: a years worth
    of hourly data may be discretized into 1-month time series, while each    of those is in turn discretized into days. The highest level time series
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

    def __init__(self, name = "name", units = None, discretized = False, disc_level = 0, parent = None):
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
        self.time_seconds   = []            # self.time converted to mono rising seconds
        self.center_time    = []            # time around which data in a subset it centered
        self.start_dto      = []            # datetime_object that mono rising times start from

        self.subsets        = []            # object list containing constituent time_seires

        self.row_data       = []            # row wise dataset
        self.col_data       = []            # column wise dataset, built as dict

        self.bad_rows       = []            # subset from data attribute with "bad rows"

        self.infilepath     = []            # tracks filepath of input CSV. used to DISALLOW overwriting
                                            # source CSV with output CSV.

        # run some methods to build subset attributes
        if parent:
            self._get_atts_from(parent)
            
        return


    def __getitem__(self, arg):
        """
        allows subsets of the time series to be accessed as follows, for example:

        Time series whos first row is:
        ['20010101', '045316', '1', '20010101045316', 366]

        With no discretezation layers
        command       : result
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


        # allows finding a slice of subsets or rows from a subset.
        if isinstance(arg, slice):
            a = arg.start
            b = arg.stop

            if self.discretized:
                if b > len(self.subsets): b = len(self.subsets)
                return [self.subsets[x] for x in range(a,b)]

            else:
                if b > len(self.row_data): b = len(self.row_data)
                return [self.row_data[x] for x in range(a,b)]

        # allows finding subsets or rows by index.
        elif isinstance(arg, int):
            if self.discretized:
                return self.subsets[arg]

            else:
                return list(self.row_data[arg])

        # allows finding subsets by name.
        elif isinstance(arg, str):
            if self.discretized:
                for subset in self.subsets:
                    if subset.name == arg:
                        return subset
                    
                else:   raise Exception("no subset with name {0}".format(arg))
            else:       raise Exception("String input is allowed for discretized time_series only!")
        else:           raise Exception("Unrecognized argument type! use int, slice, or string!")


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


    def _fmt_to_units(self, fmt):
        """ converts fmt strings to unit names of associated datetime attributes """

        fmtlist =  ["%Y", "%m", "%b", "%d", "%j", "%H", "%M", "%S"]
        unitlist = ["year","month","month","day","day","hour","minute","second"]

        if fmt in fmtlist:
            unit = unitlist[fmtlist.index(fmt)]
            return unit

        if fmt in unitlist:
            return fmt
        else:
            raise Exception("'{0}' is an invalid unit or format!".format(fmt))


    def _units_to_fmt(self, units):
        """ converts unit names to fmt strings used by datetime.stftime. internal use"""

        fmtlist =  ["%Y", "%b", "%m", "%j", "%d", "%H", "%M", "%S"]
        unitlist = ["year","month","month","day","day","hour","minute","second"]

        if units in unitlist:
            fmt = fmtlist[unitlist.index(units)]
            return fmt
        
        if units == "%b":
            return "%m"
        
        if units in fmtlist:
            return units
        else:
            raise Exception("'{0}' is an invalid unit or format!".format(fmt))


    def _extract_time(self, time_header):
        """  special case of "extract_column" method for time domain. internal use """

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


    def _center_datetime(self, datetime_obj, units):
        """ returns datetime obj that is centered on the "unit" of the input datetime obj"""

        dto = datetime_obj
        
        if units == "day":
            return datetime(dto.year, dto.month, dto.day, 12)

        if units == "month":
            # we need to find the middle day of the month which could be 14 or 15
            middle = (monthrange(dto.year, dto.month)[1]) / 2
            
            return datetime(dto.year, dto.month, middle, 0)

        if units == "year":
            return datetime(dto.year, 7, 2, 0)


    def _units_to_seconds(self, units, dto = None):
        """ converts other time units to seconds. internal use only"""

        # ensure proper unit formatting
        units = self._fmt_to_units(units)

        if units == "second":   return 1.0
        if units == "minute":   return 60.0
        if units == "hour":     return 60.0 * 60.0
        if units == "day":      return 60.0 * 60.0 * 24.0
        
        if units == "month":
            if dto:
                return 60.0 * 60.0 * 24.0 * monthrange(dto.year, dto.month)[1]
            else:
                return 60.0 * 60.0 * 24.0 * (365.25/12)
            
        if units == "year":
            if dto:
                return 60.0 * 60.0 * 24.0 * (365 + isleap(dto.year) *1)
            else:
                return 60.0 * 60.0 * 24.0 * 365.25


    def _seconds_to_units(self, seconds, units):
        """ converts seconds to other time units. internal use only"""

        if units == "second":   return 1.0
        if units == "minute":   return seconds / (60.0)
        if units == "hour":     return seconds / (60.0 * 60.0)
        if units == "day":      return seconds / (60.0 * 60.0 * 24.0)
        if units == "month":    return seconds / (60.0 * 60.0 * 24.0 * (365.25 / 12.0))
        if units == "year":     return seconds / (60.0 * 60.0 * 24.0 * 365.25)

    
    def _name_as_subset(self, binned = False):
        """ uses time series object to descriptively name itself. internal use only"""

        subset_units = self.units
        
        if isinstance(self.center_time, datetime):
            datetime_obj = self.center_time
        else:
            datetime_obj = self.time_dom[0]

        if binned:
            self.name = datetime_obj.strftime(self._units_to_fmt(self.units))

        else:
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

    
    def from_csv(self, csv_path, has_headers = True, delim = ',', spec_format = False):
        """
        creates the time_series data from a csv.

        This simply wraps the read_csv_rows function in csv_io module.
        """

        self.infilepath = os.path.abspath(csv_path)

        if not self.discretized:
            self.row_data, self.headers = read_csv_rows(csv_path, has_headers, delim, spec_format)
            self.build_col_data()

        else:
            raise Warning("You may not import new data into \
                          an already discretized time series")
        return


    def to_csv(self, csv_path):
        """ simply write the data to a csv file"""

        # disallow overwriting the csv used as input. Added by request
        if os.path.abspath(self.infilepath) == os.path.abspath(csv_path):
            csv_path = csv_path.replace(".csv", "_out.csv")

        print("Saved time series '{0}' with {1} rows and {2} columns".format(
                                    self.name, len(self.row_data), len(self.col_data)))

        write_csv_rows(self.row_data, self.headers, csv_path)
        return


    def from_list(self, data, headers, time_header, fmt):
        """ creates the time series data from a list"""

        self.row_data = data
        self.headers  = headers

        # populates self.time with time series
        self.define_time(self.time_header, self.fmt)
        self.build_col_data()
        return


    def build_col_data(self):
        """ builds columnwise data matrix with an actual dict """

        temp_col = zip(*self.row_data)

        self.col_data = {}
        for i,col in enumerate(temp_col):
            self.col_data[self.headers[i]] = list(col)
        return


    def clean(self, col_header):
        """ Removes rows where the specified column has an invalid number"""


        # loop cleaning for multiple column header inputs
        if isinstance(col_header, list):
            for col_head in col_header:
                self.clean(col_head)
                
        # clean for just one input column header
        else:
            if not col_header in self.headers:
                raise LookupError("{0} header not in dataset!".format(col_header))

            col_index = self.headers.index(col_header)
            temp_data = self.row_data
            self.row_data = []

            bad_count = 0
            for row in temp_data:

                try:
                    test = float(row[col_index])
                    self.row_data.append(row)
                except:
                    bad_count += 1
                    self.bad_rows.append(row)
                    continue

            if bad_count >0:
                print("Removed {0} rows with invalid '{1}'".format(bad_count,col_header))
                print("Dataset now has {0} rows".format(len(self.row_data)))

            # since rows have been removed, we must redefine the time domain. (sloppy, but concise)
            self.define_time(self.time_header, self.fmt, self.start_dto)

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

        time header variable can be either the header string, or a column index num

        Creates two things:
            a converted list of time objects
            a new list of monotonically increasing decimal days
        """

        # allows column index integers as time_header inputs
        if isinstance(time_header, int):
            time_header = self.headers[time_header]

        # populates self.time with time series  
        self._extract_time(time_header)


        # use manual start date (str or dto) or set to begining of first day on record
        if isinstance(start_date, str):
            start = datetime.strptime(start_date, fmt)
            
        elif isinstance(start_date, datetime):
            start = start_date

        else:
            earliest = datetime.strptime(self.time[0], fmt)
            start = datetime(earliest.year, earliest.month, earliest.day, 0,0,0,0)

        self.start_dto = start

        datestamp_list      = self.time
        self.fmt            = fmt

        self.time_dom       = []
        self.time_dec_days  = []
        self.time_seconds   = []

        for i,datestamp in enumerate(datestamp_list):

            # If error, give user information about the line on which the error occurs
            try:
                t = datetime.strptime(datestamp, fmt)
            except:
                raise Exception("Input '{0}' in line {1} is not of format {2}".format(
                                datestamp, i+2 , fmt))

            self.time_dom.append(t)

            delta = t - start
            delta = float(delta.total_seconds())
            self.time_seconds.append(float(delta))
            self.time_dec_days.append(float(delta / 86400))

        # If the data was not already in ascending time order, fix it here #unfinished

    
        if self.discretized:
            for subset in self.subsets:
                subset.define_time(time_header, fmt)     

        return


    def sort_ascending(self):
        """ reorders the data in this time_series to be in ascending order by time"""

        sorted_cols = sorted(zip(*self.col_data))

        for i,header in enumerate(self.headers): pass
            
        return

        
    def discretize(self, subset_units, overlap_width = 0, cust_center_time = False):
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

        the "overlap_width" variable can be set to greater than 0
        to allow "window" type statistics, so each subset may contain 
        data points from adjacent subsets.
        
        overlap_width = 1 is like a window size of 3
        overlap_width = 2 is like a window size of 5

        WARNING: this function is imperfect for discretizing by months.
        the possible lengths of a month are extremely variant, so sometimes
        data points at the ends of a month will get placed in the adjacent
        month. If you absolutely require accurate month discretization,
        you should use this function to discretize by year, then use the
        "group_bins" function to bin each year by month. so,

        instead of
            ts.discretize("%Y")
            ts.discretize("%b")

        use
            ts.discretize("%Y")
            ts.group_bins("%b")

        Allows a custom center time to be used! This was added so that
        days could be centered around a specific daily aquisition time.
        for example, its often usefull to define a day as
        satellite data aquisition time +/- 12 hours.
        if used, "cust_center_time" must be a datetime object!
        """

        if self.discretized:

            for subset in self.subsets:
                subset.discretize(subset_units, overlap_width)

        else:
            
            self.discretized = True
            
            if overlap_width < 0:
                print("overlap_width must be 0 or more, setting it to 0!")
                overlap_width = 0

            # convert units into subset units and into terms of seconds
            # timedelta objecs can only have units of days or seconds, so we use seconds
            subset_units = self._fmt_to_units(subset_units)

            # initial step width
            step_width = self._units_to_seconds(subset_units)

            if subset_units not in ['year','month','day']:
               raise Exception("Data is too high resolution! try the 'discretize()' fn")

            print("Discretizing data by {0}".format(subset_units))

            if self.time_dom == False:
                raise Exception("must call 'define_time' method before discretization!")
            
            # determine subset lists starting, end points and incriment
            time_s = self.time_dom[0]
            time_f = self.time_dom[-1]

            # set up starttime with custom center times.
            if cust_center_time:
                if subset_units == "month":
                    ustart  = datetime(time_s.year, time_s.month,
                                       cust_center_time.day, cust_center_time.hour,
                                       cust_center_time.minute, cust_center_time.second,
                                       cust_center_time.microsecond)
                elif subset_units == "hour":
                    ustart  = datetime(time_s.year, time_s.month, time_s.day, time_s.hour,
                                       cust_center_time.minute, cust_center_time.second,
                                       cust_center_time.microsecond)
                elif subset_units == "minute":
                    ustart  = datetime(time_s.year, time_s.month, time_s.day, time_s.hour, time_s.minute,
                                       cust_center_time.second, cust_center_time.microsecond)
                else: #subset_units == "day":
                    ustart  = datetime(time_s.year, time_s.month, time_s.day,
                                       cust_center_time.hour, cust_center_time.minute,
                                       cust_center_time.second, cust_center_time.microsecond)

                td      = time_f - time_s
                uend    = cust_center_time + timedelta(seconds = td.total_seconds())

            # otherwise, set the centers with no offest.
            else:
                ustart  = self._center_datetime(time_s, subset_units)
                uend    = self._center_datetime(time_f, subset_units) + timedelta(seconds = step_width)

            delta = uend - ustart

            # Iterate through entire dataset one time step unit at a time.
            center_time = ustart
            while center_time < uend:
                
                step_width   = self._units_to_seconds(subset_units, center_time)
                wind_seconds = step_width * (overlap_width + 0.5)

                temp_data = []
                for j, current_time in enumerate(self.time_dom):
                    dt = abs(center_time - current_time)
                    
                    if dt.total_seconds() < wind_seconds:
                        temp_data.append(self.row_data[j])

                # create the subset only if some data was found to populate it
                if len(temp_data) > 0:
                    new_subset = time_series(units = subset_units, parent = self)
                    new_subset.center_time = center_time
                    new_subset.from_list(temp_data, self.headers, self.time_header, self.fmt)
                    new_subset.define_time(self.time_header, self.fmt)
                    new_subset._name_as_subset()
                    self.subsets.append(new_subset)

                center_time += timedelta(seconds = step_width)

        return


    def group_bins(self, fmt_units, overlap_width = 0, cyclical = True):
        """
        sorts the time series into time chunks by common bin_unit

        used for grouping data rows together. For example, if one used
        this function on a 5 year dataset with a bin_unit of month,
        then the time_series would be subseted into 12 sets (1 for each
        month), which each set containing all entries for that month,
        regardless of what year they occurred in.

        fmt_units follows convention of fmt. For example:
        %Y  groups files by year
        %m  groups files by month
        %j  groups file by julian day of year

        similarly to "discretize" the "overlap_width" variable can be
        set to greater than 1 to allow "window" type statistics, so
        each subset may contain data points from adjacent subsets.
        However, for group_bins, overlap_width must be an integer.

        "cyclical" of "True" will allow end points to be considered adjacent.
        So, for example, January will be considered adjacent to December,
        day 1 will be considered adjacent to day 365.
        """

        ow = int(overlap_width)
        
        if self.discretized:
            for subset in self.subsets:
                subset.group_bins(fmt_units, overlap_width, cyclical)

        else:

            self.discretized = True

            # ensure proper unit format is present
            fmt     = self._units_to_fmt(fmt_units)
            units   = self._fmt_to_units(fmt_units)

            # set up cyclical parameters
            if fmt == "%j": cylen = 365
            if fmt == "%d": cylen = 365
            if fmt == "%m": cylen = 12
            if fmt == "%b": cylen = 12

            # initialize a grouping array to idenfity row indices for each subset
            grouping  = [int(obj.strftime(fmt)) for obj in self.time_dom]
            
            for i in xrange(min(grouping),max(grouping) + 1):

                subset_units    = self._fmt_to_units(fmt)
                new_subset      = time_series( units = subset_units, parent = self)

                # only take rows whos grouping is within ow of i
                subset_rows = [j for j,g in enumerate(grouping) if g <= i+ow and g >=i-ow]

                # fix endpoints
                if cyclical:
                    if i <= ow:
                        subset_rows = subset_rows + [j for j,g in enumerate(grouping) if g-cylen <= i+ow and g-cylen >=i-ow]
                    elif i >= cylen - ow:
                        subset_rows = subset_rows + [j for j,g in enumerate(grouping) if g+cylen <= i+ow and g+cylen >=i-ow]

                # grab row indeces from parent matrix to put in the subset
                subset_data = [self.row_data[row] for row in subset_rows]

                # run naming methods and definitions on the new subset
                if not len(subset_data) == 0:
                    new_subset.from_list(subset_data, self.headers, self.time_header, self.fmt)
                    new_subset.define_time(self.time_header, self.fmt)
                    
                    new_subset.center_time = self.time_dom[grouping.index(i)]
                    new_subset._name_as_subset(binned = True)

                    self.subsets.append(new_subset)
        return

    
    def column_stats(self, col_header):
        """
        takes statistics on a specific column of data

        creates object attributes according to the column name
        """

        print("calculated stats for time_series '{0}', col '{1}'".format(self.name,col_header))

        # pull column data and find some stats
        import numpy as np

        self.clean(col_header)
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

        # set attributes for names and stats, also make dict for immediate return
        statistics = {}
        for i,stat in enumerate(stats):
            setattr(self, names[i], stats[i])
            statistics[names[i]] = stats[i]
            
        if self.discretized:
            for subset in self.subsets:
                subset.column_stats(col_header)
        
        return statistics
    

    def column_plot(self, col_header):
        """ plots a specific column """

        # clean columnar data of non-numeric elements
        self.clean(col_header)

        return


    def normalize(self, col_header):
        """ used to normalize specific columns in the time series"""
        
        # make sure data is cleaned for numerical formatting
        self.clean(col_header)
        temp_col = self.col_data[col_header]
        temp_col = map(float, temp_col)

        # perform normalization
        minval   = min(temp_col)
        maxval   = max(temp_col)

        c = self.headers.index(col_header)
        for i,row in enumerate(self.row_data):
            self.row_data[i][c] = (float(row[c]) - minval) / (maxval - minval)

        print("data in column '{0}' has been normalized!".format(col_header))

        if self.discretized:
            for subset in self.subsets:
                subset.normalize(col_header)
        return


    def add_mono_time(self):
        """Adds a monotonically increasing time column with units of decimal days"""

        # add an entry to every row item in row_data, then rebuild column data
        if "decimal_days" not in self.headers:
            self.headers.append("decimal_days")
            
            for i, row in enumerate(self.row_data):
                self.row_data[i].append(self.time_dec_days[i])

        self.build_col_data()

        if self.discretized:
            for subset in self.subsets:
                subset.add_mono_time() 

        return 


    def interp_col(self, time_obj, col_header):
        """
        for input column, interpolate values to estimate value at input time_obj.
        input time_obj may also be of datestring matching decared fmt
        """

        # start by cleaning data by input column
        self.clean(col_header)

        # x and y data for interpolation
        y = self.col_data[col_header]
        x = self.time_seconds

        if not isinstance(time_obj, datetime):
            time_obj = datetime.strptime(time_obj, self.fmt)

        delta = time_obj - self.start_dto

        interp_x = delta.total_seconds()
        interp_y = numpy.interp(interp_x, x, y)

        print("Val in '{0}' at time '{1}' is '{2}'".format(col_header, time_obj, interp_y))

        return interp_y
        
        
    def interogate(self):
        """ prints a heads up stats table of all subsets in this time_series """

        if self.disc_level == 0:
            print("")
            print("="*84)
            print("time_series name \t\t len \t start \t\t\t end")
            print("="*84)

        # use leading and trailing spaces for visualizing discretization depth
        padded_name = self.disc_level * "   " + self.name
        print("{0} \t {1} \t {2} \t {3}".format(
            padded_name.ljust(28, " "),
            str(len(self.time)).ljust(5," "),
            self.time_dom[0],
            self.time_dom[-1]))

        if self.discretized:
            for subset in self.subsets:
                subset.interrogate()
        return


    def from_rastlist(self, filepaths, fmt):
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
    

    def rast_stats(self, outdir, saves = ["AVG","STD","NUM"],
                                        low_thresh = False, high_thresh = False):
        """
        wraper for the "many_stats" function in the raster module

        performs the many_stats function on each of the lowest level
        subsets of this time_series object
        """

        self.outdir = outdir
        self.saves  = saves

        if not self.rasterpaths:
            raise Exception("this method is only for rasterlist time_series!")
        
        # only at the lowest discretezation level should stats be taken.
        if self.discretized:
            for subset in self.subsets:
                subset.rast_statistics(outdir, saves)

        else:
            raster.many_stats(self.col_data['filepaths'],
                              outdir, self.name, saves, low_thresh, high_thresh)
        return

            
# testing code
if __name__ == "__main__":

    filepath = r"test_data\two_years_daily_hourly_variation.csv"
    fmt = "%d/%m/%Y%H%M"
    start = "01/01/20000000"

##    filepath = r"test_data\separate_date_time.csv"
##    fmt = "%Y%m%d%H%M%S"
##    start = "20000101000000"
    # testing csv manipulations
    print(" \n\n testing csv manipulations \n\n")

    ts = time_series('Master_TS')
    ts.from_csv(filepath)
    ts.merge_cols("date", "time")
    ts.define_time("date_time", fmt, start)
    ts.add_mono_time()

    #ts.discretize('%Y')
    ts.discretize('%b', overlap_width = 2)
    ts.interogate()
    
    ts.to_csv(r"test_data\separate_date_time_disc.csv")

    # testing bining
    print(" \n\n testing bin function \n\n")
    
    ts = time_series('Master_TS')
    ts.from_csv(filepath)
    ts.merge_cols("date", "time")
    ts.define_time("date_time", fmt, start)
    ts.add_mono_time()

    #ts.discretize("%Y")
    ts.group_bins("%b", overlap_width = 2)
    ts.interogate()
    
    ts.to_csv(r"test_data\separate_date_time_bin.csv")





















