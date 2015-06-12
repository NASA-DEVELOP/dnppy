__author__ = 'jwely'


from dnppy import core

from list_ftp import list_ftp
from list_http import list_http
from download_url import download_url

import os
from datetime import datetime


def fetch_MODIS(product, version, tiles, outdir, start_dto, end_dto,
                                                force_overwrite = False):
    """
    Fetch MODIS Land products from one of two servers.

       http://e4ftl01.cr.usgs.gov
       ftp://n5eil01u.ecs.nsidc.org

    Inputs:
        product         MODIS product to download such as 'MOD10A1' or 'MYD11A1'
        version         version number, usually '004' or '041' or '005'
        tiles           list of tiles to grab such as ['h11v12','h11v11']
        outdir          output directory to save downloaded files
        start_dto       datetime object, the starting date of the range of data to download
        end_dto         datetime object, the ending date of the range of data to download
        force_overwrite will re-download files even if they already exist

    outputs:
        out_filepaths   list of filepaths to all files created by this function
    """

    out_filepaths = []

    # check formats
    tiles = core.enf_list(tiles)

    # do a quick input tile check for 6 characters.
    for tile in tiles:
        if not len(tile) == 6:
            print("Warning! your tiles appear to be invalid!")
            print("Warning! make sure they are in format 'h##v##")

    # create output directories
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    print("Connecting to servers!")

    # obtain the web address, protocol information, and subdirectory where
    # this tpe of MODIS data can be found.
    site, isftp, Dir = Find_MODIS_Product(product, version)

    if Dir:
        print("Connected to {0}/{1}".format(site, Dir))
    else:
        print("Connected to {0}".format(site))

    # Depending on the type of connection (ftp vs http) populate the file list
    try:
        if isftp:
            dates,_ = list_ftp(site, False, False, Dir)
        else:
            dates   = list_http(site)
    except:
        raise ValueError("Could not connect to {0}/{1}".format(site,Dir))

    print dates
    # refine contents down to just addresses of valid year and j_day
    good_dates = []
    for date in dates:
        try:
            date_dto = datetime.strptime(date, "%Y.%m.%d")
            if start_dto <= date_dto <= end_dto:
                good_dates.append(date)

        except:
            print("skipping non date folder name {0}".format(date))


    print('Found {0} days within range'.format(len(good_dates)))

    # for all folders within the desired date range,  map the subfolder contents.
    for good_date in good_dates:

        if isftp:
            files,_ = list_ftp(site, False, False, Dir + '/' + good_date)

        else:
            files   = list_http(site + '/' + good_date)

        for afile in files:

            # only list files with desired tile names and not preview jpgs
            if not '.jpg' in afile:
                for tile in tiles:
                    if tile in afile:

                        # assemble the address
                        if isftp:
                            address='/'.join(['ftp://'+site, Dir, good_date, afile])
                        else:
                            address='/'.join([site, good_date, afile])

                        #download the file
                        outname = os.path.join(outdir, afile)
                        out_filepaths.append(outname)
                        if not os.path.isfile(outname) and not force_overwrite:
                            download_url(address, outname)

                        print('Downloaded {0}'.format(address))

    print('Finished retrieving MODIS - {0} data!'.format(product))

    return out_filepaths



def Find_MODIS_Product(product, version):
    """
    Subfunction to determine  server properties for MODIS data product.
    returns http/ftp handles

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
    Dir   = False

    # refine the address of the desired data product
    if '10' in prod_ID:
        isftp = True
        site  = site2

    if sat_designation == 'MOD':
        if isftp:
            Dir = 'MOST/' + product + '.' + version
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



# testing area
if __name__ == "__main__":

    from datetime import datetime
    prod = "MOD10A1"
    vers = "005"
    tile = ["h11v05", "h12v05"]
    outd = r"C:\Users\jwely\Desktop\troubleshooting\test\MOD10A1"
    star  = datetime(2015,1,1)
    end    = datetime(2015,12,31)

    fetch_MODIS(prod, vers, tile, outd, star, end)