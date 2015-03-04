"""
Fetches a variety of data products from various ftp and http servers
"""

__all__=['GPM',               # halted development
         'TRMM',              # active development
         'Landsat_WELD',      # complete
         'MODIS']             # complete


from . import core
import download
import list_contents

def GPM(year, month, day, product, outdir, Quiet=False):

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

     Output:
       failed      list of files which failed download

     Authors: Fall2014: Jeffry Ely
    """

    # import modules
    from ftplib import FTP

    # initialize empty tracking list
    failed=[]

    # open the ftp server and log into it with Jeffs information because who cares.
    ftp=FTP('arthurhou.pps.eosdis.nasa.gov')
    ftp.login('jeff.ely.08@gmail.com','jeff.ely.08@gmail.com')

    # navigate to path of desired year/month/day
    try: 
        workdir= '/'.join(['gpmdata',str(year),str(month).zfill(2),str(day).zfill(2),product])
        ftp.cwd(workdir)
    except:
        print '{Fetch_GPM} location does not exist on server: '+ workdir
        sys.exit()
    
    # create a filelist of the directory.
    filenames = ftp.nlst()
    if not Quiet:
        print '{Fetch_GPM} Found '+ str(len(filenames)) + ' total files!'

    # download all the GPM data in that folder (until we figure out the difference between
    # everything
    for filename in filenames:
        # create output path based on input year month day and ensure folder exists
        tempout=os.path.join(outdir,'_'.join([str(year),str(month).zfill(2),str(day).zfill(2)]))
        if not os.path.isdir(tempout): os.makedirs(tempout)

        # define local filename and write file to local hard drive
        try:
            if not Quiet:
                print '{Fetch_GPM} downloading ' + filename
            local_filename = os.path.join(tempout,filename)
            file = open(local_filename,'wb')
            ftp.retrbinary('RETR '+ filename, file.write)
            file.close()

        except:
            failed.append(filename)

    # close the fpt session, print status and finish up.
    ftp.quit()
    if not Quiet:
        print '{Fetch_GPM} Finished downloading all files!: '+ str(len(failed)) +' failures!'
    
    return(failed)


#=======================================================================================
def TRMM_1(years, months, days, product_string, outdir, Quiet=False):

    """
    Fetches TRMM data from an FTP server.

       ftp://trmmopen.gsfc.nasa.gov/trmmdata/ByDate/V07/

     Input:
       year        year of desired satellite observation (int or str)
       month       month of desired satellite observation (int)
       day         day of the month of desired satellite observation (int)
       outdir      output directory where files should be saved (str)

     Output:
       failed      list of files which failed download

     Authors: Fall2014: Jeffry Ely
    """

    # import modules
    from ftplib import FTP
    
    # set up connection and empty structure
    failed=[]
    ftp = FTP('trmmopen.gsfc.nasa.gov')
    ftp.login('anonymous')
    if not os.path.isdir(outdir): os.makedirs(outdir)

    for year in years:
        for month in months:
            for day in days:
                # navigate to path of desired year/month/day
                try:
                    workdir= '/'.join(['trmmdata','ByDate','V07',
                                       str(year),str(month).zfill(2),str(day).zfill(2)])
                    ftp.cwd(workdir)
                except: break
                
                # create a filelist of the directory.
                filenames = ftp.nlst()
                for filename in filenames:
                    if not product_string in filename:
                        filenames.remove(filename)
                        
                if not Quiet: print '{Fetch_TRMM} Found '+ str(len(filenames)) + ' total files!'

                for filename in filenames:
                    # define local filename and write file to local hard drive
                    try:
                        if not Quiet: print '{Fetch_TRMM} downloading ' + filename
                        local_filename = os.path.join(outdir,filename)
                        afile = open(local_filename,'wb')
                        ftp.retrbinary('RETR '+filename, file.write)
                        afile.close()
                    except:
                        failed.append(filename)

    # close the fpt session, print status and finish up.
    ftp.quit()
    if not Quiet:
        print '{Fetch_GPM} Finished downloading all files!: '+ str(len(failed)) +' failures!'
    
    return(failed)


#=======================================================================================
def Landsat_WELD(product, tiles, years, outdir, Quiet=False):

    """
     Fetch WELD data from the server at [http://e4ftl01.cr.usgs.gov/WELD]

     Weld data is corrected and processed Landsat 5 and 7 data that is distributed in the
     MODIS sinusoidal projection and grid format. Read more about WELD data.
       https://landsat.usgs.gov/WELD.php
       http://globalmonitoring.sdstate.edu/projects/weldglobal/

     Inputs:
       product     WELD product to download such as 'USWK','USMO','USYR'
       tiles       list of tiles to grab such as ['h11v12','h11v11']
       years       list of years to grab such as range(2001,2014)
       outdir      output directory to save downloaded files

     Outputs: NONE

     Authors: Fall2014: Jeffry Ely
    """

    # check formats
    tiles = core.Enforce_List(tiles)
    years = core.Enforce_List(years)
    years = [str(year) for year in years]

    # create output directories
    for tile in tiles:
        if not os.path.exists(os.path.join(outdir,tile)):
            os.makedirs(os.path.join(outdir,tile))
            
    if not Quiet: print '{Fetch_Landsat_WELD} Connecting to servers!'
    
    # Map the contents of the directory
    site= 'http://e4ftl01.cr.usgs.gov/WELD/WELD'+product+'.001'
    try:    dates = list_contents.http(site)
    except: print '{Fetch_Landsat_WELD} Could not connect to site! check inputs!'
    
    # find just the folders within the desired year range.
    good_dates=[]
    for date in dates:
        try:
            y,m,d = date.split(".")
            if y in years:
                good_dates.append(date)
        except: pass
        
    if not Quiet:
        print '{Fetch_Landsat_WELD} Found ' + str(len(good_dates)) + ' days within year range'

    # for all folders within the desired date range,  map the subfolder contents.
    for good_date in good_dates:
        
        files=List_http_contents(site+'/'+good_date)

        for afile in files:
            # only list files with desired tilenames and not preview jpgs
            if not '.jpg' in afile:
                for tile in tiles:
                    if tile in afile:
                        
                        # assemble the address
                        address='/'.join([site,good_date,afile])
                        if not Quiet: print '{Fetch_Landsat_WELD} Downloading' + address

                        #download the file.
                        outname=os.path.join(outdir,tile,afile)
                        download.Url(address,outname)
    return

    
#======================================================================================-
def MODIS(product, version, tiles, outdir, years, j_days=False, Quiet=False):

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

     Outputs: NONE

     Authors: Fall2014: Jeffry Ely
    """

    def Find_MODIS_Product(product,version):
        """
        Subfunction to determine  server properties for MODIS data product. returns ftp handles

        the two current servers where aqua/terra MODIS data can be downloaded are
            site1='http://e4ftl01.cr.usgs.gov'
            site2='n5eil01u.ecs.nsidc.org'

        Inputs:
           product     modis product such as 'MOD10A1'
           verions     modis version, usually '005', '004', or '041'

        Outputs:
           site        server address where data can be found
           ftp         ftp handle for open ftp session
           Dir         subdirectory of server to further search for files of input product.
        """
        
        sat_designation = product[0:3]
        prod_ID = product[3:]

        site1='http://e4ftl01.cr.usgs.gov/'
        site2='n5eil01u.ecs.nsidc.org'

        ftp=False
        Dir=False
        
        # refine the address of the desired data product
        if '10' in prod_ID:
            ftp = True
            site= site2
            
        if sat_designation=='MOD':
            if ftp: Dir = 'DP1/MOST/' + product + '.' + version
            else:   site = site1+'MOLT/' + product + '.' + version

        elif sat_designation=='MYD':
            if ftp: Dir = 'DP1/MOSA/' + product + '.' + version
            else:   site = site1+'MOLA/' + product+'.' + version
            
        elif sat_designation=='MCD':
            site = site1+'MOTA/' + product + '.' + version
            
        else:
            print '{Find_MODIS_Product} No such MODIS product is availble for download with this script!'
        
        return site, ftp, Dir


    # check formats
    tiles = core.Enforce_List(tiles)
    years = core.Enforce_List(years)
    years = [str(year) for year in years]
    if isinstance(j_days,list):
            js = [str(j_day).zfill(3) for j_day in j_days]
    elif isinstance(j_days,int):
        js = [str(j_day)]
    else:
        js = range(367)
    
    # do a quick input tile check for 6 characters.
    for tile in tiles:
        if not len(tile) == 6:
            print "{Fetch_MODIS} Warning! your tiles appear to be invalid!"
            print "{Fetch_MODIS} Warning! make sure they are in format 'h##v##"

    # create output directories
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    if not Quiet: print '{Fetch_MODIS} Connecting to servers!'
    
    # obtain the web address, protocol information, and subdirectory where
    # this tpe of MODIS data can be found.
    site, ftp, Dir = Find_MODIS_Product(product,version)

    # Depending on the type of connection (ftp vs http) populate the file list
    try:
        if ftp: dates,_ = list_contents.ftp(site, Dir)
        else:   dates   = list_contents.http(site)
    except: print '{Fetch_MODIS} Could not connect to site! check inputs!'
    
    # refine contents down to just addresses of valid year and j_day
    good_dates=[]
    for date in dates:
        try:
            y,m,d = date.split(".")
            j_day = core.Date_to_Julian(y,m,d).zfill(3)
            
            if y and y in years:
                good_dates.append(date)

                if j_days:
                    if j_day not in js:
                        good_dates.remove(date)
        except: pass

    if not Quiet:
        print '{Fetch_MODIS} Found ' + str(len(good_dates)) + ' days within range'

    # for all folders within the desired date range,  map the subfolder contents.
    for good_date in good_dates:
        
        if ftp: files,_ = list_contents.ftp(site,Dir+'/'+good_date)
        else:   files   = list_contents.http(site+'/'+good_date)

        for afile in files:
            # only list files with desired tilenames and not preview jpgs
            if not '.jpg' in afile:
                for tile in tiles:
                    if tile in afile:
                        # assemble the address
                        if ftp: address='/'.join(['ftp://'+site,Dir,good_date,afile])
                        else:   address='/'.join([site,good_date,afile])
                        if not Quiet:
                            print '{Fetch_MODIS} Downloading  ' + address

                        #download the file
                        outname = os.path.join(outdir,afile)
                        download.Url(address,outname)

    if not Quiet: print '{Fetch_MODIS} Finished! \n'
    return

