"""
 the "download.py" module is part of the "dnppy" package (develop national program py)
 this module houses python functions for obtaining data from the internet in a systematic
 way.

 If you wrote a function you think should be added to this module, or have an idea for one
 you wish was available, please email the Geoinformatics YP class or code it up yourself
 for future DEVELOP participants to use!
"""

__author__ = ["Jeffry Ely, jeff.ely.08@gmail.com"]

__all__=['Filelist',    # complete
         'Urls',        # complete
         'Url']         # complete 


from . import core
import list_contents


def Filelist(ftptexts, filetypes = False, outdir = False, Quiet = False):

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
       Quiet           Set Quiet to 'True' if you don't want anything printed to screen.
                       Defaults to 'False' if left blank.
     Outputs:
       failed          list of files which failed to download after the end of the script.

     Authors: Fall2014: Jeffry Ely
    """

    # force inputs to take list format
    ftptexts=core.Enforce_List(ftptexts)
    if filetypes:
        filetypes = core.Enforce_List(filetypes)

    for ftptext in ftptexts:
        #verify that things exist.
        core.Exists(ftptext)

        if not outdir:
            outdir,_ =os.path.split(ftptext)
        
        ftp = open(ftptext,'r')
        sites =ftp.readlines()
        if not Quiet:
            print '{Download_filelist} Attempting to download : '+ str(len(sites)) +' files!'
            print '{Download_filelist} Saving all files to : [' + outdir + ']'

        # perform the first attempt
        failed = Urls(sites,filetypes,outdir,Quiet)

        # for 19 more times, if there are still items in the failed list, try again
        for i in range(1,19):
            if len(failed)>0:
                print 'Retry number '+ str(i) + ' to grab '+ str(len(failed)) + ' failed downloads : '
                time.sleep(60)
                failed = Urls(failed,filetypes,outdir)

        # once all tries are complete, print a list of files which repeatedly failed
        if not Quiet:
            if len(failed)>0:
                print 'Files at the following URLs have failed 20 download attempts'
                print 'Manually verify that these files exist on the server:'
                for i in failed:
                    print i
            else:
                print '{Download_filelist} Finished with no errors!'
                
        # close the open text files and finish up
        ftp.close
        
    return (failed)


def Urls(urls, filetypes, outdir, Quiet=False):

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

     Authors: Spring2014: Jeffry Ely
    """

    failed=[]
    urls = core.Enforce_List(urls)

    # creates output folder at desired path if it doesn't already exist
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # establish a wait time that will increase when downloads fail. This helps to reduce
    # the frequency of REVERB server rejections for requesting too many downloads
    wait=0

    for site in url_list:
        download = False
        url = site.rstrip()
        sub = url.split("/")
        leng = len(sub)
        name = sub[leng-1]
        
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
                Url(url,os.path.join(outdir,name))
                if not Quiet:
                    print name + " is downloaded (" + str(wait) + ")"

                # reduce the wait time when downloads succeed. 
                if wait>=1:
                    wait=wait-1

            # add to the failcount if the download is unsuccessful and wait longer next time.
            except:
                print sub[leng-1]+ " will be retried! (" + str(wait) + ")"
                wait = wait+5
                failed.append(url)


    if not Quiet: print '{download.Urls} Finished!'                
    return (failed)


def Url(url,outname):
    """Download a single file. input source url and output filename"""

    writefile=open(outname,'wb+')
    page= urllib.urlopen(url).read()
    writefile.write(page)
    writefile.close()
    return

