
# local imports
#from dnppy import raster
from time_series import time_series


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

    def from_directory(self, directory, fmt):
        """
        creates a list of all rasters in a directory, then
        passes this list to self.from_rastlist
        """

        filepaths = core.list_files(False, directory, ".tif")
        self.from_rastlist(filepaths, fmt)
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

        # flags this time series as being comprised of is_rasterpath
        self.is_rasterpath  = True
        return
    

    def rast_stats(self, outdir, saves = ["AVG","STD","NUM"],
                                        low_thresh = False, high_thresh = False):
        """
        wraper for the "many_stats" function in the raster module

        performs the many_stats function on each of the lowest level
        subsets of this time_series object
        """
        
        from dnppy import raster

        self.outdir = outdir
        self.saves  = saves
        
        # only at the lowest discretezation level should stats be taken.
        if self.discretized:
            for subset in self.subsets:
                subset.rast_statistics(outdir, saves)

        else:
            raster.many_stats(self.col_data['filepaths'],
                              outdir, self.name, saves, low_thresh, high_thresh)
        return




if __name__ == "__main__":

    rs = raster_series()
    
