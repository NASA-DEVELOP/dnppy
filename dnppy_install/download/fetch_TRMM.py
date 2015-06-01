__author__ = 'jwely'

# import modules
from ftplib import FTP
import os

def fetch_TRMM(years, months, days, product_string, outdir):

    """
    Fetches TRMM data from an FTP server.

       ftp://trmmopen.gsfc.nasa.gov/trmmdata/ByDate/V07/

     Input:
       year        year of desired satellite observation (int or str)
       month       month of desired satellite observation (int)
       day         day of the month of desired satellite observation (int)
       outdir      output directory where files should be saved (str)
    """

    # set up connection and empty structure
    failed = []
    ftp = FTP('trmmopen.gsfc.nasa.gov')
    ftp.login('anonymous')

    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    for year in years:
        for month in months:
            for day in days:

                # navigate to path of desired year/month/day
                workdir = '/'.join(['trmmdata','ByDate','V07',
                        str(year),str(month).zfill(2),str(day).zfill(2)])

                try:
                    ftp.cwd(workdir)
                except:
                    break

                # create a filelist of the directory.
                filenames = ftp.nlst()
                for filename in filenames:
                    if not product_string in filename:
                        filenames.remove(filename)

                print('Found {0} total files!'.format(len(filenames)))

                for filename in filenames:
                    # define local filename and write file to local hard drive
                    try:
                        print("downloading {0}".format(filename))
                        local_filename = os.path.join(outdir,filename)
                        afile = open(local_filename,'wb')
                        ftp.retrbinary('RETR '+filename, file.write)
                        afile.close()
                    except:
                        failed.append(filename)

    # close the fpt session, print status and finish up.
    ftp.quit()
    print('Finished downloading TRMM files!: {0} failures!'.format(len(failed)))

    return failed