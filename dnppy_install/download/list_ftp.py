__author__ = 'jwely'

import ftplib

def list_ftp(site, username = False , password = False, Dir = False):
    """
    lists contents of typical FTP download site

    Returns two lists, the first is of filenames, the second is of full filepaths
    (including filenames) that one could patch through to the "download_url" function.
    """

    ftp = ftplib.FTP(site)

    if username and password:
        ftp.login(username, password)
    elif username:
        ftp.login(username)
    else:
        ftp.login()

    if Dir:
        ftp.cwd(Dir)
    else:
        ftp.cwd("")
        Dir = ""

    rawdata = []
    ftp.dir(rawdata.append)
    filenames = [i.split()[-1] for i in rawdata[1:]]
    filepaths = ["ftp://"+"/".join([site,Dir,afile]).replace("//","/") for afile in filenames]

    ftp.quit()
    return filenames, filepaths