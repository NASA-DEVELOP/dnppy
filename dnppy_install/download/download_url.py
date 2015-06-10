__author__ = 'jwely'

import urllib
import ftplib
import os


def download_url(url, outname, username = False, password = False):
    """Download a single file. input source url and output filename"""

    head, tail = os.path.split(outname)
    if not os.path.exists(head) and head is not "":
        os.makedirs(head)

    if "http" in url[:4]:
        writefile   = open(outname, 'wb+')
        connection  = urllib.urlopen(url)
        page        = connection.read()

        writefile.write(page)
        writefile.close()
        del connection

    elif "ftp:" in url[:4]:
        filename = os.path.basename(url)
        server   = url.split("/")[2]
        path     = "/".join(url.split("/")[3:-1])

        ftp = ftplib.FTP(server)

        # log in to the server with user specified username and password
        if username and password:
            ftp.login(username, password)
        elif username:
            ftp.login(username)
        else:
            ftp.login()

        ftp.cwd(path)
        ftp.retrbinary("RETR " + filename, open(outname, 'wb').write)
        ftp.quit()

    else:
        print("Unknown url protocol type, must be http or ftp")


    return