
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
    but retain the ability to process and interogate the time seriese
    at any level with the exact same external syntax.

    A time series object is either itself comprised of a matrix of data,
    or is comprised of many time series objects. Potentially unlimited
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

    def __init__(self, name = "Nameless", units = False):
        """initializes the time series"""

        self.rasterpaths    = False # becomes true if time series is of raster data
        
        self.name           = name  # the name of this time series
        self.units          = units # unit of time represented by subset if discretized
        self.fmt            = False # for interpreting timestrings to time objs
        self.headers        = []    # one header for each col in dataset
        self.time_col       = 0     # index of data column with time info
        self.time           = []    # separate copy of data[time_col]
        self.time_dom       = False # self.time converted to list of datetime objs
        self.time_dec_days  = []    # self.time converted to mono rising decimal days

        self.discretized    = False # does this time series have constituents?
        self.subsets        = []    # object list containing constituent time_seires
        self.row_data       = []    # row wise dataset
        self.col_data       = []    # column wise dataset, built as dict

        self.bad_rows       = []    # subset from data attribute with "bad rows"
        return

    
    def get_atts_from(self, parent_time_series):
        """
        Allows bulk setting of attributes. usefull for allowing a subset to inherit
        information from its parent time_series
        """
        
        self.fmt        = parent_time_series.fmt
        self.headers    = parent_time_series.headers
        self.time_col   = parent_time_series.time_col
        self.time_header= parent_time_series.time_header
        return
    
    
    def from_csv(self, csv_path):
        """ creates the time_series data from a csv"""

        if not self.discretized:
            self.row_data, self.headers = csv_io.read_csv_rows(csv_path)
            self.build_col_data()
            
        else:
            raise Warning("poop")
        return


    def to_csv(self, csv_path):
        """ simply write the data to a file"""
        
        print("Time series has {0} rows".format(len(self.row_data)))
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
        """ builds columnwise data matrix with an actual dict"""

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
        
        self.row_data.append(row)
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


    def extract_time(self, time_header):
        """ special case of "extract_column" method for time domain"""

        self.time_header = time_header
        self.build_col_data()
        
        if time_header in self.headers:
                self.time_col   = self.headers.index(time_header)
                self.time       = self.col_data[time_header]
        else:
            raise LookupError("Time header not in dataset!")
        
        if self.discretized:
            for subset in self.subsets:
                subset.extract_time(time_header)
                
        return self.time


    def merge_cols(self, header1, header2):
        """merges two columns together (string concatenation)"""

        new_header  = "_".join([header1, header2])
        
        for i, entry in enumerate(self.col_data):
                new_field   = "".join([self.col_data[header1][i], self.col_data[header2][i]])
                
                self.row_data.append(new_entry)

        # updates column and row data
        self.headers.append(new_header)
        self.build_col_data()
        
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
        self.extract_time(time_header)
            

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

    
    def discretize(self, subset_units):
        """
        splits the time series into individual time chunks

        used for taking advanced statistics, usually periodic
        in nature. Also usefull for exploiting temporal relationships
        in a dataset for a variety of purposes including data
        sanitation, periodic curve fitting, etc.

        supported discretizations are as follows: 
        "year", "month", "day", "hour", "minute", and "second".
        """

        if self.time_dom == False:
            raise Exception("must call 'define_time' method before discretization!")

        self.discretized = True
        
        # set up list by which to discretize
        disc_list   = [getattr(x, subset_units) for x in self.time_dom]

        # set up the first subset time_series object
        counter     = 0
        subset_name = "{0}_{1}".format(subset_units, counter)
        new_subset  = time_series(subset_name, subset_units)
        
        new_subset.get_atts_from(self)

        # anywhere the subset_unit has changed make new subset time_series
        for i,t in enumerate(disc_list[:-1]):
            now     = disc_list[i]
            later   = disc_list[i+1]

            new_subset.add_row(self.row_data[i])

            if not now == later:
                # add the old subset
                self.subsets.append(new_subset)

                # create new empty subset
                counter += 1
                subset_name = "{0}_{1}".format(subset_units, counter)
                new_subset  = time_series(subset_name, subset_units)
                
                new_subset.get_atts_from(self)

        # handles the last group in the data
        new_subset.add_row(self.row_data[-1])
        self.subsets.append(new_subset)

        self.define_time(self.time_header, self.fmt)
        print("Finished discretizing data by {0}".format(subset_units))
        
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
        pass

    
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

        grouping = [int(obj.strftime(fmt_units)) for obj in self.time_dom]

        for i in range(min(grouping),max(grouping)):

            subset_units    = fmt_units.replace('%','')
            subset_name     = "{0}_{1}".format(subset_units, i)
            new_subset      = time_series(subset_name, subset_units)
            
            new_subset.get_atts_from(self)

            subset_rows = [j for j,e in enumerate(grouping) if e == i]
            subset_data = [self.row_data[row] for row in subset_rows]
            new_subset.from_list(subset_data, self.headers, self.time_header, self.fmt)

            self.subsets.append(new_subset)
        return


    def interogate(self):

        if self.discretized:
             print("Interogation of subsets!")
             for subset in self.subsets:
                 subset.interogate()

        else:
            print("name: {0}, len: {1}, s: {2} e: {3}".format(
                self.name,
                len(self.time),
                self.time[0],
                self.time[-1]))
            

    def add_mono_time(self):
        """ ammends the data structure to add goodies"""

        self.row_data = zip(*self.row_data)
        self.row_data.insert(int(self.time_col) + 1, self.time_dec_days)
        self.row_data = zip(*self.row_data)

        if "decimal_days" not in self.headers:
            self.headers.insert(int(self.time_col) + 1, "decimal_days")

        if self.discretized:
            for subset in self.subsets:
                subset.add_mono_time()
        
        return self.row_data


# other testing

if __name__ == "__main__":
    ts = time_series('test')
    ts.from_csv("separate_date_time.csv")
    #ts.merge_cols("date","time")
    ts.define_time("date_time","%Y%m%d%H%M%S")


        






























    
