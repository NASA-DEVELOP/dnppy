


def filelist(ftptexts, filetypes = False, outdir = False):

    """
    Reads text file of download links, downloads them.

     This script reads a text file with urls such as those output from ECHO REVERB
     and outputs them to an output directory. It will retry failed links 20 times before
     giving up and outputing a warning to the user.

     Inputs:
       ftptexts        array of txt files ordered from reverb containing ftp links
       filetype        file extension of the desired files, leave blank or False to grab all
                       types.
       outdir          folder where files are to be placed after download
       
     Outputs:
       failed          list of files which failed to download after the end of the script.
    """

    # force inputs to take list format
    ftptexts = core.enf_list(ftptexts)
    if filetypes:
        filetypes = core.enf_list(filetypes)

    for ftptext in ftptexts:
        #verify that things exist.
        core.exists(ftptext)

        if not outdir:
            outdir,_ = os.path.split(ftptext)
        
        ftp     = open(ftptext,'r')
        sites   = ftp.readlines()
        
        print("Attempting to download {0} files!".format(len(sites)))
        print("Saving all files to {0}".format(outdir))

        # perform the first attempt
        failed = urls(sites, filetypes, outdir)

        # for 19 more times, if there are still items in the failed list, try again
        for i in range(1,19):
            if len(failed)>0:
                print("retry number {0} to grab {1} failed downloads!".format(i,len(failed)))
                time.sleep(60)
                failed = urls(failed, filetypes, outdir)

        # once all tries are complete, print a list of files which repeatedly failed
        if len(failed)>0:
            print('Files at the following URLs have failed 20 download attempts')
            print('Manually verify that these files exist on the server:')
            for i in failed:
                print(i)
        else:
            print('Finished with no errors!')
                
        # close the open text files and finish up
        ftp.close
        
    return (failed)


def urls(url_list, filetypes, outdir):

    """
    Downloads a list of files. Retries failed downloads

     This script downloads a list of files and places it in the output directory. It was
     built to be nested within "Download_filelist" to allow loops to continuously retry
     failed files until they are successful or a retry limit is reached.

     Inputs:
       url_list         array of urls, probably as read from a text file
       filetypes       list of filetypes to download. Usefull for excluding xmls or
                       unwanted metadata. Usually 'hdf' for MODIS files
       outdir          folder where files are to be placed after download

     Output:
       failed          list of files which failed download
    """

    failed   = []
    url_list = core.enf_list(url_list)

    # creates output folder at desired path if it doesn't already exist
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # establish a wait time that will increase when downloads fail. This helps to reduce
    # the frequency of REVERB server rejections for requesting too many downloads
    wait = 0

    for site in url_list:
        download = False
        url      = site.rstrip()
        sub      = url.split("/")
        leng     = len(sub)
        name     = sub[leng-1]
        
        # Determine wether or not to download the file based on filetype.
        if filetypes:
            for filetype in filetypes:
                if filetype in name[-4:]:
                    download = True
        else: download = True

        # attempt download of the file, or skip it.
        if download:
            
            try:
                # wait for the wait time before attempting writing a file
                time.sleep(wait)
                a_url(url, os.path.join(outdir,name))
                print("{0} is downloaded {1}".format(name, wait))

                # reduce the wait time when downloads succeed. 
                if wait >= 1:
                    wait = wait-1

            # add to the failcount if the download is unsuccessful and wait longer next time.
            except:
                print("{0} will be retried! {1}".format(sub[leng-1], wait))
                wait = wait+5
                failed.append(url)


    print("Finished downloading urls!")                
    return (failed)


def a_url(url, outname):
    """Download a single file. input source url and output filename"""

    writefile   = open(outname,'wb+')
    page        = urllib.urlopen(url).read()
    
    writefile.write(page)
    writefile.close()
    return

