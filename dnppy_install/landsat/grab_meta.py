

def grab_meta(filename):
    """
    Parses the xml format landsat metadata "MTL.txt" file

     This function parses the xml format metadata file associated with landsat images.
     it outputs a class instance metadata object with all the attributes found in the MTL
     file for quick referencing by other landsat related functions.

     Inputs:
       filename    the filepath to a landsat MTL file.

     Returns:
       meta        class object with all metadata attributes
    """

    # if the "filename" input is actually already a metadata class object, return it back.
    import inspect
    if inspect.isclass(filename): return (filename)

    fields = []
    values = []

    class metadata_obj(object):pass
    meta = metadata_obj()

    if filename:
        metafile = open(filename,'r')
        metadata = metafile.readlines()

    for line in metadata:
        # skips lines that contain "bad flags" denoting useless data AND lines
        # greater than 1000 characters. 1000 character limit works around an odd LC5
        # issue where the metadata has 40,000+ erroneous characters of whitespace
        bad_flags = ["END","GROUP"]                 
        if not any(x in line for x in bad_flags) and len(line)<=1000:   
                line = line.replace("  ","")
                line = line.replace("\n","")
                field_name , field_value = line.split(' = ')
                fields.append(field_name)
                values.append(field_value)

    for i in range(len(fields)):
        
        #format fields without quotes,dates, or times in them as floats
        if not any(['"' in values[i],'DATE' in fields[i],'TIME' in fields[i]]):   
            setattr(meta,fields[i],float(values[i]))
        else:
            values[i] = values[i].replace('"','')
            setattr(meta,fields[i],values[i])   
        
    # print "{0} : {1}".format(fields[i],values[i])

    # Add a FILEPATH attribute for local filepath of MTL file.
    meta.FILEPATH = filename

    # only landsat 8 includes sun-earth-distance in MTL file, so calculate it for the others.
    # this equation is tuned to match [http://landsathandbook.gsfc.nasa.gov/data_prod/prog_sect11_3.html]
    # with a maximum error of 0.055%
    if not meta.SPACECRAFT_ID == "LANDSAT_8":
        j_day = int(meta.LANDSAT_SCENE_ID[13:16])
        ecc   = 0.01671123
        theta = j_day * (2 * math.pi / 369.7)    #see above url for why this number isn't 365.25
        sm_ax = 1.000002610
        meta.EARTH_SUN_DISTANCE = sm_ax*(1-(ecc*ecc))/(1+ecc*(math.cos(theta)))
        print("Calculated Earth to Sun distance as {0} AU".format(str(meta.EARTH_SUN_DISTANCE)))
        
    return(meta)
