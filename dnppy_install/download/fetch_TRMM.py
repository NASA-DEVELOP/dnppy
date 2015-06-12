__author__ = 'jwely'

# import modules
from download_url import download_url
from list_ftp import list_ftp
from datetime import datetime, timedelta
import os
import gzip

def fetch_TRMM(product_string, outdir, start_dto, end_dto):

    """
    Fetches TRMM data from an FTP server.

       ftp://trmmopen.gsfc.nasa.gov/trmmdata/ByDate/V07/

     Input:
       product_string   the string for the desired product, options include
                            1B11, 1B21, 1CTMI, 2A12, 2A21, 2A23, 2A25, 2B31, 3B42,
                            3G25, 3G31. The usual precip product of interest is the
                            famous 3B42 data product.
       outdir           output directory where files should be saved (str)
       start_dto        datetime object for start date of desired range
       end_dto          datetime object for end date of desired range

    outputs:
        output_files    a list of new filepaths created by this function
    """

    # set up empty structure
    dates = []
    output_files = []
    ftpsite =  "ftp://trmmopen.gsfc.nasa.gov"

    date_delta = end_dto - start_dto

    for i in range(date_delta.days +1):
        dates.append(start_dto + timedelta(days = i))

    for date in dates:

        # navigate to path of desired year/month/day
        workdir = '/'.join(['trmmdata','ByDate','V07',
                            str(date.year),
                            str(date.month).zfill(2),
                            str(date.day).zfill(2)])

        filenames, filepaths = list_ftp(site = ftpsite, dir = workdir)

        for filename in filenames:

            if product_string in filename:
                try:
                    outname = os.path.join(outdir, os.path.basename(filename))
                    download_url(ftpsite + filename, outname)
                    output_files.append(outname)

                    # now extract it out of its GZ format
                    with gzip.open(outname, 'rb') as gz:
                        with open(outname.replace(".gz",""), 'wb') as f:
                            content = gz.read()
                            f.write(content)

                    os.remove(outname)


                    print("downloaded and extracted {0}".format(os.path.basename(filename)))
                except:
                    print("failed to download {0}".format(os.path.basename(filename)))

    print("Finished downloading TRMM files!")

    return output_files


if __name__ == "__main__":

    start = datetime(2014,1,1)
    end   = datetime(2014,1,2)
    outfiles = fetch_TRMM("3B42", r"C:\Users\jwely\Desktop\troubleshooting\test", start, end)
