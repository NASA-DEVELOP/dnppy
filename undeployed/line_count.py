
import os

def lines_in_py_package(dirname):

    python_filelist = []
    for r,d,f in os.walk(dirname):
        for afile in f:
            if afile.endswith(".py"):
                python_filelist.append(os.path.join(r, afile))

    line_total = 0

    for pyfile in python_filelist:
        lines = lines_in_file(pyfile)
        line_total += lines
        print("{0} {1}".format(pyfile.replace(dirname,"").ljust(90), lines))

    print("-"*98)
    print("{0} {1}".format("Total line count".ljust(90), line_total))
    return python_filelist
    
    
    

def lines_in_file(fname):
    """ returns number of lines for input filename """

    c = 0
    with open(fname) as f:
        for l in f:
            if len(l.replace(" ","")) > 3:
                c += 1
    return c



if __name__ == "__main__":
    files = lines_in_py_package(r"C:\Users\Jeff\Desktop\Github\dnppy")
    
    
