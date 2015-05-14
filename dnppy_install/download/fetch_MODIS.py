__author__ = 'jwely'


from dnppy import core

from .list_ftp import list_ftp
from .list_http import list_http
from .download_url import download_url

import os
from datetime import datetime


def MODIS(product, version, tiles, outdir, years, j_days=False):

    """
    Fetch MODIS Land products from one of two servers

       http://e4ftl01.cr.usgs.gov
       ftp://n5eil01u.ecs.nsidc.org

     Inputs:
       product     MODIS product to download such as 'MOD10A1' or 'MYD11A1'
       version     version number, usually '004' or '041' or '005'
       tiles       list of tiles to grab such as ['h11v12','h11v11']
       outdir      output directory to save downloaded files
       years       list of years to grab such as range(2001,2014)
       j_days      list of days to grab such as range(31:60). Defaults to all days in year
    """

    def Find_MODIS_Product(product, version):
        """
        Subfunction to determine  server properties for MODIS data product. returns ftp handles

        the two current servers where aqua/terra MODIS data can be downloaded are
            site1='http://e4ftl01.cr.usgs.gov'
            site2='n5eil01u.ecs.nsidc.org'

        Inputs:
           product     modis product such as 'MOD10A1'
           versions    modis version, usually '005', '004', or '041'

        Outputs:
           site        server address where data can be found
           ftp         ftp handle for open ftp session
           Dir         subdirectory of server to further search for files of input product.
        """

        sat_designation = product[0:3]
        prod_ID = product[3:]

        site1 = 'http://e4ftl01.cr.usgs.gov/'
        site2 = 'n5eil01u.ecs.nsidc.org'

        isftp = False
        Dir = False

        # refine the address of the desired data product
        if '10' in prod_ID:
            isftp = True
            site  = site2

        elif sat_designation == 'MOD':
            if isftp:
                Dir = 'DP1/MOST/' + product + '.' + version
            else:
                site = site1+'MOLT/' + product + '.' + version

        elif sat_designation == 'MYD':
            if isftp:
                Dir = 'DP1/MOSA/' + product + '.' + version
            else:
                site = site1+'MOLA/' + product+'.' + version

        elif sat_designation == 'MCD':
            site = site1+'MOTA/' + product + '.' + version

        else:
            print('No such MODIS product is available for download with this script!')
            site = "None"

        return site, isftp, Dir


    # check formats
    tiles = core.enf_list(tiles)
    years = core.enf_list(years)
    years = [str(year) for year in years]

    if isinstance(j_days, list):
        js = [str(j_day).zfill(3) for j_day in j_days]
    elif isinstance(j_days, int):
        js = [str(j_days)]
    else:
        js = range(367)

    # do a quick input tile check for 6 characters.
    for tile in tiles:
        if not len(tile) == 6:
            print("Warning! your tiles appear to be invalid!")
            print("Warning! make sure they are in format 'h##v##")

    # create output directories
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    print 'Connecting to servers!'

    # obtain the web address, protocol information, and subdirectory where
    # this tpe of MODIS data can be found.
    site, ftp, Dir = Find_MODIS_Product(product,version)

    # Depending on the type of connection (ftp vs http) populate the file list
    try:
        if ftp:
            dates,_ = list_ftp(site, Dir)
        else:
            dates   = list_http(site)
    except:
        print 'Could not connect to site! check inputs!'

    # refine contents down to just addresses of valid year and j_day
    good_dates=[]
    for date in dates:
        try:
            j_day = datetime.srptime(date, "%Y.%m.%d").strftime("%j").zfill(3)
            year  = datetime.strptime(date, "%Y").strftime("%Y")

            if year and year in years:
                good_dates.append(date)

                if j_days:
                    if j_day not in js:
                        good_dates.remove(date)
        except: pass

    print 'Found ' + str(len(good_dates)) + ' days within range'

    # for all folders within the desired date range,  map the subfolder contents.
    for good_date in good_dates:

        if ftp: files,_ = list_ftp(site,Dir+'/'+good_date)
        else:   files   = list_http(site+'/'+good_date)

        for afile in files:
            # only list files with desired tilenames and not preview jpgs
            if not '.jpg' in afile:
                for tile in tiles:
                    if tile in afile:
                        # assemble the address
                        if ftp: address='/'.join(['ftp://'+site,Dir,good_date,afile])
                        else:   address='/'.join([site,good_date,afile])
                        print 'Downloading MODIS ' + address

                        #download the file
                        outname = os.path.join(outdir,afile)
                        download_url(address,outname)

    print 'Finished retrieving MOIDS data!'
    return