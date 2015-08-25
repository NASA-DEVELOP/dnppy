__author__ = 'jwely'

import urllib
import ftplib
import os

__all__ = ["download_url"]


def download_url(url, outname, username = None, password = None, force_overwrite = False):
    """
    Download a single file. input source url and output filename

    :param url:             a string url to file for download
    :param outname:         filepath to write location of file
    :param username:        use if url leads to file on ftp server with username
    :param password:        use if url leads to file on ftp server with password
    :param force_overwrite: by default, this function will not overwrite existing files
                            on drive. This is to avoid accidental overwrite of critical
                            files as well as repeated download of the same files.

    :return outname:    returns filepath to locally created file after download
    """

    # if output file already exists, do not download a file there.
    if os.path.isfile(os.path.abspath(outname)) and not force_overwrite:
        return outname

    head, tail = os.path.split(outname)
    if not os.path.exists(head) and head is not "":
        os.makedirs(head)

    if "http" in url[:4]:
        connection  = urllib.urlopen(url)
        page        = connection.read()

        # escapes in the event of a 404 not found
        if "404 Not Found" in page:
            return None

        writefile   = open(outname, 'wb+')
        writefile.write(page)
        writefile.close()
        del connection
        return outname

    elif "ftp:" in url[:4]:
        filename = os.path.basename(url)
        server   = url.split("/")[2]
        path     = "/".join(url.split("/")[3:-1])

        ftp = ftplib.FTP(server)

        # log in to the server with user specified username and password
        if username is not None and password is not None:
            ftp.login(username, password)
        elif username is not None:
            ftp.login(username)
        else:
            ftp.login()

        ftp.cwd(path)
        ftp.retrbinary("RETR " + filename, open(outname, 'wb').write)
        ftp.quit()
        return outname

    else:
        raise Exception("Unknown url protocol type, must be http or ftp")




if __name__ == "__main__":

    url = "http://water.weather.gov/precip/p_download_new/2002/01/05/nws_precip_conus_20020105.nc"
    outpath = r"C:\Users\jwely\Desktop\troubleshooting\test.nc"
    download_url(url, outpath)
