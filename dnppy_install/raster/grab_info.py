
# local imports
from dnppy import core



def grab_info(filepath, data_type = False, CustGroupings = False):

    """
    Extracts in-filename metadata from common NASA data products

     This function simply extracts relevant sorting information from a MODIS or Landsat
     filepath of any type or product and returns object properties relevant to that data.
     it will be expanded to include additional data products in the future.

     Inputs:
           filepath        Full or partial filepath to any modis product tile
           data_type       Manually tell the software what the data is.
           CustGroupings   User defined sorting by julian days of specified bin widths.
                           input of 5 for example will group January 1,2,3,4,5 in the first bin
                           and january 6,7,8,9,10 in the second bin, etc.

     Outputs:
           info            on object containing the attributes (product, year, day, tile)
                           retrieve these values by calling "info.product", "info.year" etc.

     Attributes by data type:
           All             type,year,j_day,month,day,season,CustGroupings,suffix

           MODIS           product,tile
           Landsat         sensor,satellite,WRSpath,WRSrow,groundstationID,Version,band

     Attribute descriptions:
           type            NASA data type, for exmaple 'MODIS' and 'Landsat'
           year            four digit year the data was taken
           j_day           julian day 1 to 365 or 366 for leap years
           month           three character month abbreviation
           day             day of the month
           season          'Winter','Spring','Summer', or 'Autumn'
           CustGroupings   bin number of data according to custom group value. sorted by
                           julian day
           suffix          Any additional trailing information in the filename. used to find
                           details about special

           product         usually a level 3 data product from sensor such as MOD11A1
           tile            MODIS sinusoidal tile h##v## format

           sensor          Landsat sensor
           satellite       usually 5,7, or 8 for the landsat satellite
           WRSpath         Landsat path designator
           WRSrow          Landsat row designator
           groundstationID ground station which recieved the data download fromt he satellite
           Version         Version of landsat data product
           band            band of landsat data product, usually 1 through 10 or 11.
    """

    
    # pull the filename and path apart 
    path,name = os.path.split(filepath)
    
    # create an info object class instance
    class info_object(object):pass
    info = info_object()

    # figure out what kind of data these files are. 
    if not data_type:
        data_type = identify(name)

    if data_type == 'MODIS':
        params  =['product','year','j_day','tile','type','version','tag','suffix']
        n       = name.split('.')
        end     = n[4]
        string  =[n[0],name[9:13],name[13:16],n[2],'MODIS',n[3],end[:13],end[13:]]

    if data_type == 'MODIS':
        params  =['product','year','j_day','tile','type','version','tag','suffix']
        n       = name.split('.')
        end     = n[4]
        string  =[n[0],name[9:13],name[13:16],n[2],'MODIS',n[3],end[:13],end[13:]]
            
    elif data_type =='Landsat':
        params  =['sensor','satellite','WRSpath','WRSrow','year','j_day','groundstationID',
                                                        'Version','band','type','suffix']
        n       = name.split('.')[0]
        string  =[n[1],n[2],n[3:6],n[6:9],n[9:13],n[13:16],n[16:19],
                n[19:21],n[23:].split('_')[0],'Landsat','_'.join(n[23:].split('_')[1:])]
            
    elif data_type == 'WELD_CONUS' or data_type == 'WELD_AK':
        params  = ['coverage','period','year','tile','start_day','end_day','type']
        n       = name.split('.')
        string  =[n[0],n[1],n[2],n[3],n[4][4:6],n[4][8:11],'WELD']
        # take everything after the first underscore as a suffix if onecore.exists.
        if '_' in name:
            params.append('suffix')
            string.append('_'.join(name.split('_')[1:]))
            
    elif data_type == 'ASTER':
        params  = ['product','N','W','type','period']
        n       = name.split('_')
        string  = [n[0],n[1][1:3],n[1][5:9],n[-1].split('.')[0],'none']
    
    elif data_type == 'TRMM':
        print '{Grab_Data_Info} no support for TRMM data yet! you could add it!'
        return(False)

    elif data_type == 'AMSR_E':
        print '{Grab_Data_Info} no support for AMSR_E data yet! you could add it!'
        return(False)

    elif data_type == 'AIRS':
        print '{Grab_Data_Info} no support for AIRS data yet! you could add it!'
        return(False)

    # if data doesnt look like anything!
    else:
        print 'Data type for file ['+name+'] could not be identified as any supported type'
        print 'improve this function by adding info for this datatype!'
        return(False)

    # Create atributes and assign parameter names and values
    for i in range(len(params)):
        setattr(info,params[i],string[i])
    
    # ................................................................................
    # perform additional data gathering only if data has no info.period atribute. Images with
    # this attribute represent data that is produced from many dates, not just one day.
    if not hasattr(info,'period'):
    # fill in date format values and custom grouping and season information based on julian day
    # many files are named according to julian day. we want the date info for these files.
        try:
            tempinfo    = datetime.datetime(int(info.year),1,1)+datetime.timedelta(int(int(info.j_day)-1))
            info.month  = tempinfo.strftime('%b')
            info.day    = tempinfo.day
            
        # some files are named according to date. we want the julian day info for these files
        except:
            fmt         = '%Y.%m.%d'
            tempinfo    = datetime.datetime.strptime('.'.join([info.year,info.month,info.day]),fmt)
            info.j_day  = tempinfo.strftime('%j')

    # fill in the seasons by checking the value of julian day
        if int(info.j_day) <=78 or int(info.j_day) >=355:
            info.season='Winter'
        elif int(info.j_day) <=171:
            info.season='Spring'
        elif int(info.j_day)<=265:
            info.season='Summer'
        elif int(info.j_day)<=354:
            info.season='Autumn'
        
    # bin by julian day if integer group width was input
    if CustGroupings:
        CustGroupings=core.enf_list(CustGroupings)
        for grouping in CustGroupings:
            if type(grouping)==int:
                groupname='custom' + str(grouping)
                setattr(info,groupname,1+(int(info.j_day)-1)/(grouping))
            else:
                print('{Grab_Data_Info} invalid custom grouping entered!')
                print('{Grab_Data_Info} [CustGrouping] must be one or more integers in a list')

    # make sure the filepath input actually leads to a real file, then give user the info
    if core.exists(filepath):
        if not Quiet:
            print '{Grab_Data_Info} '+ info.type + ' File ['+ name +'] has attributes '
            print vars(info)
        return(info)
    else:
        return(False)



def identify(name):

    """
    Compare filename against known NASA data file naming conventions to raster.identify it

     Nested within the raster.grab_info function

     Inputs:
       name        any filename of a file which is suspected to be a satellite data product

     Outputs:
       data_type   If the file is found to be of a specific data type, output a string
                   designating that type. The options are as follows, with urls for reference                          

     data_types:
           MODIS       https://lpdaac.usgs.gov/products/modis_products_table/modis_overview
           Landsat     http://landsat.usgs.gov/naming_conventions_scene_identifiers.php
           TRMM        http://disc.sci.gsfc.nasa.gov/precipitation/documentation/TRMM_README/
           AMSR_E      http://nsidc.org/data/docs/daac/ae_ocean_products.gd.html
           ASTER       http://mapaspects.org/article/matching-aster-granule-id-filenames
           AIRS        http://csyotc.cira.colostate.edu/documentation/AIRS/AIRS_V5_Data_Product_Description.pdf
           False       if no other types appear to be correct.
    """

    if  any( x==name[0:2] for x in ['LC','LO','LT','LE','LM']):
        return('Landsat')
    elif any( x==name[0:3] for x in ['MCD','MOD','MYD']):
        return('MODIS')
    elif any( x==name[0:4] for x in ['3A11','3A12','3A25','3A26','3B31','3A46','3B42','3B43']):
        return('TRMM')
    elif name[0:5]=='CONUS':
        return('WELD_CONUS')
    elif name[0:6]=='Alaska':
        return('WELD_AK')
    elif name[0:6]=='AMSR_E':
        return('AMSR_E')
    elif name[0:3]=='AST':
        return('ASTER')
    elif name[0:3]=='AIR':
        return('AIRS')

    
    else:
        return(False)
