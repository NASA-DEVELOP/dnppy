
"""
=======================================================================================
                                    dnppy.log
=======================================================================================
 The "log.py" module is part of the "dnppy" package (develop national program py).
 This module houses just a few python functions for creating and using log files.

 If you wrote a function you think should be added to this module, or have an idea for one
 you wish was available, please email the Geoinformatics YP class or code it up yourself
 for future DEVELOP participants to use!

 see "log_example.py" for example usage of this simple module

"""
#--------------------------------------------------------------------------------------
#   function name       development notes
#--------------------------------------------------------------------------------------
__all__=['init',        # complete
         'entry',       # complete
         'close']       # complete

#======================================================================================
def init(directory,name):

    """Opens a log file and places header info. passes file handles"""
    
    import os,time
    fname=os.path.join(directory,'Log_'+name+'_'+time.strftime('%Y-%b-%d')+'.txt')
    if not os.path.isfile(os.path.join(directory,fname)):
       try:
          fhandle = open(fname, 'a')
          fhandle.write('-----------------------------------------------------\n')
          fhandle.write('Program initialized! on '+time.strftime('%Y-%b-%d')+'\n')
          fhandle.write('-----------------------------------------------------\n')
          print('======begin log!======')
          return(fhandle)
       except:
          print('Could not create Log file with name : '+
          ' Log_'+name+'_'+date.today().isoformat()+'.txt')
    else:
        fhandle=open(fname,'a')
        fhandle.write('-----------------------------------------------------\n')
        fhandle.write('Program initialized! on '+time.strftime('%Y-%b-%d')+'\n')
        fhandle.write('-----------------------------------------------------\n')
        print('======begin log!======')
        return(fhandle)

#====================================================================================== 
def entry(entry,fhandle):
    
    """creates an entry in log file opened with dnppy.log.init""" 

    import time
    timestamp = time.strftime('%H:%M:%S')
    print entry
    try:    fhandle.write('{0}: {1}\n'.format(timestamp, entry))
    except: print 'Log File Error: entry could not be logged'
    return

#======================================================================================
def close(fhandle):

    """Closes the logfile"""
    
    entry('Program terminated',fhandle)
    fhandle.close()
    return
