__author__ = 'jwely'

import ftplib
import socket

def list_ftp(site, username = None , password = None, dir = None):
    """
    lists contents of typical FTP download site

    Returns two lists, the first is of filenames, the second is of full filepaths
    (including filenames) that one could patch through to the "download_url" function.

    returns False if the server has rejected our connection
    """

    # ftplib does not like the ftp address out front for some reason
    if "ftp://" in site:
        site = site.replace("ftp://", "")

    try:
        ftp = ftplib.FTP(site)
    except EOFError:
        return [], []

    except socket.gaierror:
        raise Exception("Socket.gaierror indicates this ftp address '{0}' does not exist".format(site))


    if username is not None and password is not None:
        ftp.login(username, password)
    elif username is not None:
        ftp.login(username)
    else:
        ftp.login()

    if dir is not None:
        ftp.cwd(dir)
    else:
        ftp.cwd("")
        dir = ""

    rawdata = []
    ftp.dir(rawdata.append)
    filenames = [i.split()[-1] for i in rawdata]
    filepaths = ["ftp://"+"/".join([site, dir, afile]).replace("//","/") for afile in filenames]
    ftp.quit()

    return filenames, filepaths


# testin area
if __name__ == "__main__":
    filenames, filepaths = list_ftp("n5eil01u.ecs.nsidc.org")

    for filename in filenames:
        print filename