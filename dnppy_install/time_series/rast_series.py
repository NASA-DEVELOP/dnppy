
# local imports
from dnppy import core
from dnppy import raster
from time_series import time_series

# standard imports
import os
from datetime import datetime, timedelta
from calendar import monthrange, isleap
import matplotlib.pyplot as plt


__author__ = ["Jeffry Ely, Jeff.ely.08@gmail.com"]


class raster_series(time_series):
    """
    This is an extension of the time_series class

    It is built to handle just like a time_series object, with
    the simplification that the "row_data" attribute, is comprised
    of nothing more than filepaths and filenames. All attributes
    for tracking the time domain are the same.

    some time_series methods for manipulating and viewing text data
    will not apply to raster_series
    """
        
    def from_directory(self, directory, fmt, fmt_unmask = False):
        """
        creates a list of all rasters in a directory, then
        passes this list to self.from_rastlist
        """

        filepaths = core.list_files(False, directory, ".tif")
        filepaths = raster.enf_rastlist(filepaths)
        
        self.from_rastlist(filepaths, fmt, fmt_unmask)
        return

    
    def from_rastlist(self, filepaths, fmt, fmt_unmask = False):
        """
        loads up a list of filepaths as a time series
        if filenames contain variant characters that are not related
        to date, a "fmt_unmask" may be used to isolate the datestrings
        from the rest of the filenames by character index.

        for an example filename
            "MYD11A1.A2013001_day_clip_W05_C2014001_Avg_K_C_p_GSC.tif"
        we only want the part with the year and julian day in it
            "2013001"
        so we can use
            fmt        = "%Y%j"
            fmt_unmask = [10,11,12,13,14,15,16]
        to indicate that we only want the 10th through 16th characters
        """

        self.headers = ['filepaths','filenames','fmt_names']
        self.row_data = []

        for filepath in filepaths:
            head, filename = os.path.split(filepath)

            if fmt_unmask:
                fmt_name = ""
                for char_index in fmt_unmask:
                    fmt_name = fmt_name + filename[char_index]
            else:
                fmt_name = filename
            
            self.row_data.append([filepath, filename, fmt_name])

        self.build_col_data()
        self.define_time('fmt_names', fmt)

        print("Imported and interpreted {0} raster filepath datetimes!".format(len(self.row_data)))
        return
    

    def series_stats(self, outdir, saves = ['AVG','NUM','STD','SUM'],
                                        low_thresh = None, high_thresh = None):
        """
        Applies the dnppy.raster.many_stats() function to each
        of the lowest level subsets of this rast_series.

        arguments are the same as dnppy.raster.many_stats()
        """

        self.outdir = outdir
        self.saves  = saves
        
        # only at the lowest discretezation level should stats be taken.
        if self.subsetted:
            for subset in self.subsets:
                subset.series_stats(outdir, saves)

        else:
            raster.many_stats(self.col_data['filepaths'],
                              outdir, self.name, saves, low_thresh, high_thresh)
        return


    def make_subsets(self, subset_units, overlap_width = 0,
                           cust_center_time = False, discard_old = False):
        """
        splits the time series into individual time chunks

        used for taking advanced statistics, usually periodic
        in nature. Also usefull for exploiting temporal relationships
        in a dataset for a variety of purposes including data
        sanitation, periodic curve fitting, etc.

        subset_units
            subset_units follows convention of fmt. For example:
            %Y  groups files by year
            %m  groups files by month
            %j  groups file by julian day of year

        overlap_width
            this variable can be set to greater than 0
            to allow "window" type statistics, so each subset may contain 
            data points from adjacent subsets.
            
            overlap_width = 1 is like a window size of 3
            overlap_width = 2 is like a window size of 5

            WARNING: this function is imperfect for making subsets by months.
            the possible lengths of a month are extremely variant, so sometimes
            data points at the ends of a month will get placed in the adjacent
            month. If you absolutely require accurate month subsetting,
            you should use this function to subset by year, then use the
            "group_bins" function to bin each year by month. so,

            instead of
                ts.subset("%Y")
                ts.subset("%b")

            use
                ts.subset("%Y")
                ts.group_bins("%b")

        cust_center_time
            Allows a custom center time to be used! This was added so that
            days could be centered around a specific daily aquisition time.
            for example, its often usefull to define a day as
            satellite data aquisition time +/- 12 hours.
            if used, "cust_center_time" must be a datetime object!

        discard_old
            By default, performing a subsetting on a time series that already
            has subsets does not subset the master time series, but instead
            the lowest level subsets. Setting "discard_old" to "True" will
            discard all previous subsets of the time series and start subsetting
            from scratch.
        """

        if discard_old:
            self.subsetted = False
            self.subsets = []
        
        if self.subsetted:
            for subset in self.subsets:
                subset.make_subsets(subset_units, overlap_width)

        else:
            
            self.subsetted = True

            # sanitize overlap
            if overlap_width < 0:
                print("overlap_width must be 0 or more, setting it to 0!")
                overlap_width = 0

            # convert units into subset units and into terms of seconds
            # timedelta objecs can only have units of days or seconds, so we use seconds
            subset_units = self._fmt_to_units(subset_units)

            # initial step width
            step_width = self._units_to_seconds(subset_units)

            if subset_units not in ['year','month','day','minute']:
               raise Exception("Data is too high resolution to subset by {0}".format(subset_units))

            print("Subsetting data by {0}".format(subset_units))

            if self.time_dom == False:
                raise Exception("must call 'define_time' method before taking subsets!")
            
            # determine subset lists starting, end points and incriment
            time_s = self.time_dom[0]
            time_f = self.time_dom[-1]

            # set up starttime with custom center times.
            if cust_center_time:
                
                print("using custom center time")
                
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


            # Iterate through entire dataset one time step unit at a time.
            delta = uend - ustart
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
                    new_subset = raster_series(units = subset_units, parent = self)
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

        similarly to "make_subsets" the "overlap_width" variable can be
        set to greater than 1 to allow "window" type statistics, so
        each subset may contain data points from adjacent subsets.
        However, for group_bins, overlap_width must be an integer.

        "cyclical" of "True" will allow end points to be considered adjacent.
        So, for example, January will be considered adjacent to December,
        day 1 will be considered adjacent to day 365.
        """

        ow = int(overlap_width)
        
        if self.subsetted:
            for subset in self.subsets:
                subset.group_bins(fmt_units, overlap_width, cyclical)

        else:

            self.subsetted = True

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
                new_subset      = raster_series( units = subset_units, parent = self)

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


if __name__ == "__main__":

    rs = raster_series()
    
    indir   = r"C:\Users\jwely\Desktop\troubleshooting\test_in_MODIS"
    fmt     = "%Y%j"
    outdir  = r"C:\Users\jwely\Desktop\troubleshooting\test_out_MODIS"
    
    rs.from_directory(indir, fmt, range(9,16))
    rs.make_subsets("%m")
    rs.interogate()
    rs.series_stats(outdir, low_thresh = -10.0, high_thresh = 50.0)
