from csv_io import *
from time_series import *


def read_fixed_width(intxt, num_header_rows = 1):
    """
    designed to give a good initial stab at reading fixed width
    data from a text file by attempting csv format conversion.

    headder rows are assumed to contain header information, and will
    influence the way columns are split.
    """
    
    lines = []
    
    with open(intxt, 'r') as f:

        # read in headers
        if num_header_rows ==1:
            header = next(f)
            lines.insert(0, header)
            
        elif num_header_rows ==2:
            header1 = next(f).replace(' \n','')
            header2 = next(f).replace(' \n','')

            # combine headers
            header1_pos = []
            for i,h in enumerate(header1.split()):
                
                if i == 0:
                    header1_pos.append(header1.index(h + " "))
                if i == len(header1.split()):
                    header1_pos.append(header1.index(" " + h))
                else:
                    header1_pos.append(header1.index(h + " "))

                print i,h,header1_pos[-1]
                    
            print header1_pos
            print header1

        # read in data rows
        for i,line in enumerate(f):
            lines.append(line.replace(' \n',''))

        # insert the header at the top of the lines.
        lines.insert(0, header)
            
        # transpose data to columnar character stacks
        lines = zip(*lines)
        for i,col in enumerate(lines):

            if all([x == ' ' for x in col]):
                lines[i] = [',']*len(lines[i])

        # rever the data to row format with commas
        lines = zip(*lines)
        lines = ["".join(line) for line in lines]

        # remove double commas in a probably stupid way
        for i in range(5):
            lines = [line.replace(',,',',') for line in lines]
        lines = [line.split(',') for line in lines]

        # separate the header from the lines
        header = lines[0]
        header = [h.replace(' ','') for h in header]
        del lines[0]
        del lines[0]
        
        write_csv_rows(lines, header, intxt.replace(".txt",".csv"))

        return lines, header


if __name__ == "__main__":

    filepath = "9321966457550dat.txt"
    
    read_fixed_width(filepath, 2)
    t = time_series('poop')
    t.from_csv("9321966457550dat.csv")
    t.merge_cols("Date","HrMn")
    t.define_time("Date_HrMn","%Y%m%d%H%M")
