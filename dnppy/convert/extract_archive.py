__author__ = 'jwely'

import os
import tarfile
import gzip
import zipfile
from dnppy import core

__all__ = ["extract_archive"]

def extract_archive(filepaths, delete_originals = False):
    """
    Input list of filepaths OR a directory path with compressed
    files in it. Attempts to decompress the following formats

    Support formats include ``.tar.gz``, ``.tar``, ``.gz``, ``.zip``.

    :param filepaths:           list of filepaths to archives for extraction
    :param delete_originals:    Set to "True" if archives may be deleted after
                                their contents is successful extracted.
    """

    filepaths = core.enf_filelist(filepaths)

    for filepath in filepaths:

        head,tail = os.path.split(filepath)

        if filepath.endswith(".tar.gz"):
            with tarfile.open(filepath, 'r:gz') as tfile:
                outdir = os.path.join(head, tail.replace(".tar.gz",""))
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(tfile, outdir)

        # gzip only compresses single files
        elif filepath.endswith(".gz"):
            with gzip.open(filepath, 'rb') as gzfile:
                outfile = os.path.join(head, tail.replace(".gz",""))
                content = gzfile.read()
                with open(outfile, 'wb') as of:
                    of.write(content)

        elif filepath.endswith(".tar"):
            with tarfile.open(filepath, 'r') as tfile:
                outdir = os.path.join(head, tail.replace(".tar",""))
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(tfile, outdir)

        elif filepath.endswith(".zip"):
            with zipfile.ZipFile(filepath, "r") as zipf:
                outdir = os.path.join(head, tail.replace(".zip",""))
                zipf.extractall(outdir)

        else: return

        print("Extracted {0}".format(filepath))

        if delete_originals:
            os.remove(filepath)

    return


#testing area
if __name__ == "__main__":
    formats = [r"C:\Users\jwely\Desktop\troubleshooting\zip_tests\MOD09A1.A2015033.h11v05.005.2015044233105_1_tar.tar",
               r"C:\Users\jwely\Desktop\troubleshooting\zip_tests\MOD09A1.A2015033.h11v05.005.2015044233105_1_targz.tar.gz",
               r"C:\Users\jwely\Desktop\troubleshooting\zip_tests\MOD09A1.A2015033.h11v05.005.2015044233105_1.tif.gz",
               r"C:\Users\jwely\Desktop\troubleshooting\zip_tests\MOD09A1.A2015033.h11v05.005.2015044233105_1_zip.zip"]

    for format in formats:
        extract_archive(format)
