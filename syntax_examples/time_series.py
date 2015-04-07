
"""
This is an example of the proper syntax to create a time series object

it will NOT run
"""

__author__ = "Jeffry Ely, jeff.ely.08@gmail.com"


# create time series from a csv file, such as weather data
from dnppy import time_series

help(time_series)                               # shows help for all module functions

ts = time_series("name of time series")         # declares "ts" as a time series object
ts.from_csv("your filepath here")               # calls the "from_csv" method to load data

print ts.row_data[0]                            # shows you the first row of your csv
print ts.headers                                # shows you the headers of your data
print ts.col_data                               # shows a dict of columnwise data
print ts.col_data[ts.headers[0]]                # shows the first column of data

help(ts.define_time)                            # shows help for function below
ts.define_time("time", "%Y%m%d-%H%M%S")         # allows time series to interpret time column data
                                                # of format YYYYMMDD-HHMMSS

help(ts.discretize)                             # shows help for function below  (you get the point)               
ts.discretize("%b")                             # discretizes data by month (Jan, Feb, Mar,etc)
ts.discretize("%Y")                             # discretizes data by year
ts.group_bins("%b")                             # groups all data by month

ts.merge_columns(col1_header, col2_header)      # creates a new column from two others

ts.interogate()                                 # prints a quick report of the time series object
