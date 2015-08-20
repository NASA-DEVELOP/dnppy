
import os, time

class logfile:
    """
    log files may be used to have your scripts print progress so they
    can be verified and troubleshooted

    this simple class has just three methods,
    __init__()  opens up or creates a new logfile.(automatic)
    entry()     addes entries to the logfile with datestamps
    close()     closes the logfile.
    """


    def __init__(self, logfile_path, overwrite = True):
        """ initializes the logfile with a header and correct writing mode"""

        if overwrite or not os.path.exists(logfile_path):
            fhandle = open(logfile_path, 'w+')
        else:
            fhandle = open(logfile_path, 'a')

        fhandle.write('-----------------------------------------------------\n')
        fhandle.write('Initialized: ' + time.strftime('%Y-%b-%d-%H:%M:%S')+'\n')
        fhandle.write('-----------------------------------------------------\n')


        self.fhandle = fhandle
        return

        
    def entry(self, entry):
        """ creates an entry in log file"""
        
        timestamp = time.strftime('%Y-%b-%d-%H:%M:%S')
        print(entry)
        self.fhandle.write('{0}: {1}\n'.format(timestamp, entry))
        return

    def close(self):
        """Closes the logfile"""
        
        self.entry("Program Terminated")
        self.fhandle.close()
        return
