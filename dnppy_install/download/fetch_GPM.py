__author__ = ['jeff.ely.08@gmail.com']

from ftplib import FTP
import sys, os

def fetch_GPM(year, month, day, product, outdir):

    """
    Fetches GPM data from an FTP server.

     The data is very preliminary, so it
     presently just grabs all the data for a given date (usually about 40 GB worth!)

       http://pps.gsfc.nasa.gov/Documents/GPM_Data_Info_140616.pdf

     Input:
       year        year of desired satellite observation (int or str)
       month       month of desired satellite observation (int)
       day         day of the month of desired satellite observation (int)
       outdir      output directory where files should be saved (str)
    """

    # initialize empty tracking list
    failed = []

    # open the ftp server and log into it with Jeffs information because who cares.
    ftp = FTP('arthurhou.pps.eosdis.nasa.gov')
    ftp.login('jeff.ely.08@gmail.com', 'jeff.ely.08@gmail.com')

    # navigate to path of desired year/month/day
    workdir = '/'.join(['gpmdata',str(year),str(month).zfill(2),str(day).zfill(2),product])
    try:
        ftp.cwd(workdir)
    except:
        print 'location does not exist on server: '+ workdir
        sys.exit()

    # create a filelist of the directory.
    filenames = ftp.nlst()
    print('Found {0} total files!'.format(len(filenames)))

    # download all the GPM data in that folder (until we figure out the difference between
    # everything
    for filename in filenames:
        # create output path based on input year month day and ensure folder exists
        tempout=os.path.join(outdir,'_'.join([str(year),str(month).zfill(2),str(day).zfill(2)]))
        if not os.path.isdir(tempout): os.makedirs(tempout)

        # define local filename and write file to local hard drive
        try:
            print('downloading {0}'.format(filename))
            local_filename = os.path.join(tempout,filename)
            wfile = open(local_filename,'wb')
            ftp.retrbinary('RETR '+ filename, wfile.write)
            wfile.close()

        except:
            failed.append(filename)

    # close the ftp session, print status and finish up.
    ftp.quit()
    print('Finished downloading GPM files!: {0} failures'.format(len(failed)))

    return failed


if __name__ == "__main__":
    pass