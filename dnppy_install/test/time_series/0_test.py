from dnppy.time_series import time_series

csv_path    = ""
time_header = ""
fmt         = ""
csv_outpath = ""

ts = time_series("lake_height_measurements")
ts.from_csv(csv_path)
ts.define_time(time_header, fmt)
ts.add_mono_time()
ts.to_csv(csv_outpath)


