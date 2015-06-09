__author__ = 'jwely'

import ftplib
import socket

def list_ftp(site, username = False , password = False, Dir = False):
    """
    lists contents of typical FTP download site

    Returns two lists, the first is of filenames, the second is of full filepaths
    (including filenames) that one could patch through to the "download_url" function.

    returns False if the server has rejected our connection
    """

    try:
        ftp = ftplib.FTP(site)
    except EOFError:
        return [], []

    except socket.gaierror:
        raise Exception("Socket.gaierror indicates this ftp address '{0}' does not exist".format(site))


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

if __name__ == "__main__":
    filenames,_ = list_ftp("n5eil01u.ecs.nsidc.org")

    for filename in filenames:
        print filename