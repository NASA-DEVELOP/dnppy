import os, shutil
from dnppy import core

def sort(filelist, delim = "_", recursive = False):
    """
    Simple function to sort files into folders based on common leading
    strings in the filenames

    use a custom delimiter by setting "delim", and set "recursive" to True
    if you need to do many directories deep and do not mind renaming files
    """

    for filename in filelist:
        head,tail = os.path.split(filename)

        tail_list = tail.split(delim)
        move_dir = os.path.join(head, tail_list[0])

        if not os.path.exists(move_dir):
            os.makedirs(move_dir)

        if recursive:
            shutil.move(filename, os.path.join(move_dir, "_".join(tail_list[1:])))
        else:
            shutil.move(filename, os.path.join(move_dir, "_".join(tail_list)))
        print("Moved file '{0}' ".format(filename))

    print("Moved all files!")
    return


if __name__ == "__main__":
    
    filelist = core.list_files(False, r"C:\Users\jwely\Desktop\troubleshooting\lauren_organize")
    sort(filelist)
    
    
        
