def rolling_stats(centers, windows, window_width, low_thresh, high_thresh, outdir,
                    NoData_Value, chunks=False, start_chunk=False, saves = ['AVG','NUM','STD']):
    """
    Takes rolling statistics on time series raster data.

     Similar to "raster.many_stats" but with optimization for statistics across many
     partially overlapping datasets and the ability to handle extremely large datasets.

     this function was built specifically for the Langley Northwest Agriculture team in
     Fall of 2014. It was designed to perform statistics on many raster blocks as output from
     the 'core.rolling_window' function, therefore its inputs include centers, windows, and window width.

     the function was used to take moving averages of MODIS land surface temperature data
     where efficiency could be gained by keeping data loaded for one window in memory for
     the next window, since 80% or more of each window overlaps with the previous one. This
     very significantly reduced processing time, but required chunking data to avoid hitting
     pythons 2GB memory limit (32 bit version).

     Inputs:
       centers         Array of filenames representing the center of each list in "windows".
       windows         2d array of filenames. window groupings as output from "core.rolling_window".
       window_width    Window width used to generate the windows in 2d array "windows" used
                       for naming.
       low_thresh      values below low_thresh are assumed erroneous and set to NoData.
       high_thresh     values above high_thresh are assumed erroneous and set to NoData.
       outdir          Directory where output should be stored.
       NoData_Value    Value representing NoData.
       chunks          The number of chunks to split processing into. Chunks are vertical
                       slices. leave blank or False to allow automatic determination of a
                       safe chunk value to limit matrix size to 3 million values at once.
       start_chunk     Value of chunk to start at. Used to get around the memory leak bug.
       saves           which statistics to save in a raster. Any of
                           AVG = rasters showing average value across all input rasters
                           NUM = rasters showing the number of good pixels which comprised AVG
                           STD = rasters showing the standard deviation of pixels
                       Defaults to all three ['AVG','NUM','STD'].

     Bugs:
       Some memory leaking appears to occur, this problem has not been solved, but using
       a 64 bit installation of python has been found to help by increasing memory headroom.
       If a memory error occurs when processing large datasets, users can input a value for
       "start_chunk" equal to the value of the active chunk at the time of error. This will
       allow memory to clear and pick up at the beginning of the chunk where the crash occurred.
    """

    saves = core.enf_list(saves)
    
    #creates output directory if not already there
    if not os.path.exists(outdir): os.makedirs(outdir)
    tempdir=os.path.join(outdir,'Chunks')
    if not os.path.exists(tempdir):os.makedirs(tempdir)

    #set up empty tracking lists
    chunk_average_list =[]
    chunk_count_list =[]
    chunk_std_list=[]
    ychunks=[]
    chunk_name_list=[]   
    
    # define sizes based on window size and dims of first image in window
    temp, meta  =to_numpy(windows[0][0])
    xs, ys      =temp.shape
    zs          =len(windows[0])
    xyzs        =xs*ys*zs

    # automatically determine number of chunks to use by limiting the size of
    # any given data brick to 3 million values
    if not chunks: chunks=xyzs/3000000+1

    # find the dimensions of the chunks for subprocessing of the data
    # data is split into chunks to avoid hitting memory limits. (2GB for 32 bit python)
    for sub in range(chunks):
        ychunks.append(range(((sub)*ys)/chunks, (((sub+1)*ys)/chunks)))
        chunk_name_list.append('Chnk'+str(sub))

    # find the maximum width of a chunk    
    width=len(max(ychunks,key=len))
    
    print('rolling stats has split data into ' + str(chunks) + ' chunks.')

    # process each chunk
    for chunkID,ychunk in enumerate(ychunks):
        if chunkID >= start_chunk:
            
            print 'Processing chunk number '+ str(chunkID) + ' with width '+ str(width)
            
            for j,window in enumerate(windows):
                filtered=0
                center=centers[j]
                print '{Rolling_Raster_Stats}  Window center : ' + center
                info=core.Grab_Data_Info(center,False,True)
                
                # Create_output_filenames based on the file representing the window center
                head,tail = os.path.split(center)
                chunk_average_name= os.path.join(tempdir,'.'.join(tail.split('.')[:-1])+
                    '_W'+str(window_width).zfill(2)+'_C'+info.year+info.j_day+'_Avg_Chnk'+str(chunkID)+'.tif')
                chunk_count_name= os.path.join(tempdir,'.'.join(tail.split('.')[:-1])+
                    '_W'+str(window_width).zfill(2)+'_C'+info.year+info.j_day+'_Num_Chnk'+str(chunkID)+'.tif')
                chunk_std_name= os.path.join(tempdir,'.'.join(tail.split('.')[:-1])+
                    '_W'+str(window_width).zfill(2)+'_C'+info.year+info.j_day+'_Std_Chnk'+str(chunkID)+'.tif')

                # clear existing rollover list and create a new one
                rollover_from=[]
                rollover_to=[]

                # if this is the first window we've examined, create empty numpy matrix
                # based on dimensions of the first file, and number of entries in the first window
                if j==0:
                    newmatrix = numpy.zeros((xs,width,len(window)))
                    oldmatrix = numpy.zeros((xs,width,len(window)))
                    newcount  = numpy.zeros((xs,width,len(window)))
                    oldcount  = numpy.zeros((xs,width,len(window)))
                    
                # if this is not the first window, check to see if any of the current files
                # were in the previous window
                elif j>0:
                    for filename in windows[j]:
                        if filename in windows[j-1]:
                            # track rollover locations, to and from, for shuffling data between windows
                            rollover_from.append(windows[j-1].index(filename))
                            rollover_to.append(windows[j].index(filename))
                            
                # for all files in the group, populate the newmatrix
                for i,item in enumerate(window):
                    path,name=os.path.split(item)
                    if i in rollover_to:
                        index=rollover_to.index(i)
                        newmatrix[:,:,i]=oldmatrix[:,:,rollover_from[index]]
                    else:
                        print '{Rolling_Raster_Stats} New file loaded: '+ name
                        tempmatrix,x,y,w,h,spat_ref = to_numpy(Raster)
                        try:
                            newmatrix[:,range(len(ychunk)),i]=tempmatrix[:,ychunk]
                            newmatrix[:,range(len(ychunk),width),i]=numpy.zeros((xs,width-len(ychunk)))+NoData_Value
                        except:
                            print 'Abnormal Image discovered! filling with nodata!'
                            newmatrix[:,range(width),i]=numpy.zeros((xs,width))+NoData_Value
                
                # examine each pixel, add pixels with good data to the count.
                print '{Rolling_Raster_Stats} Filtering bad values and calculating statistics!'

                # start by looking at layers. Skip layers which were rolled over and already processed
                for z in range(zs):

                    # only perform this data filtering if it hasn't already been done on this "z slice"
                    if not z in rollover_to:
                        for x in range(xs):
                            for y in range(width):

                                # if a pixel value is not 0 (NoData), add to the count
                                if not round(newmatrix[x,y,z]/NoData_Value,10)==1:
                                    newcount[x,y,z] = 1

                                    # filter data for potential errors
                                    # by threshold values
                                    if high_thresh and newmatrix[x,y,z]>=high_thresh:
                                        newmatrix[x,y,z]=NoData_Value
                                        filtered +=1
                                        newcount[x,y,z]= 0
                                        
                                    if low_thresh and newmatrix[x,y,z]<=low_thresh:
                                        newmatrix[x,y,z]=NoData_Value
                                        filtered +=1
                                        newcount[x,y,z]= 0
                                    
                    else: newcount[:,:,z]=oldcount[:,:,z]

                # total up all z-wise entries in the count matrix.
                del count
                count=numpy.sum(newcount,axis=2)
                
                # perform per-pixel data filtering by pulling out values greater than 3
                # standard deviations away from the mean value for that pixel.
                
                Std = numpy.zeros((xs,width))
                average = numpy.zeros((xs,width))
                
                for x in range(xs):
                    for y in range(width):
                        
                        # perform initial filtering of edge values.
                        pixels=newmatrix[x,y,:][newmatrix[x,y,:] !=NoData_Value]

                        if len(pixels)>=3:
                            pixel_avg=numpy.mean(pixels)
                            pixel_std=numpy.std(pixels)
                            high_tail=float(pixel_avg+3*pixel_std)
                            low_tail=float(pixel_avg-3*pixel_std)

                            for z,pixel in enumerate(pixels):
                                if pixel>=high_tail or pixel<=low_tail:
                                    pixels[z]=NoData_Value
                                    filtered   += 1
                                    count[x,y] -= 1

                        # perform the statistics now that outliers are removed           
                        pixels=pixels[pixels !=NoData_Value]

                        if len(pixels)>=3:
                            Std[x,y]= numpy.std(pixels)   
                            average[x,y]= numpy.mean(pixels)   
                        elif len(pixels)>=1:
                            average[x,y]= numpy.mean(pixels)
                            Std[x,y] = NoData_Value
                        else:
                            average[x,y]=NoData_Value
                            Std[x,y]=NoData_Value
                        del pixels
                                
                print '{Rolling_Raster_Stats}  filtered '+ str(filtered) + ' total pixel values'

                #write output to chunk file

                if 'AVG' in saves: 
                    to_numpy(average,x,y,w,h,spat_ref,chunk_average_name)
                    chunk_average_list.append(chunk_average_name)
                    
                if 'NUM' in saves:
                    to_numpy(count,x,y,w,h,spat_ref,chunk_average_name)
                    chunk_count_list.append(chunk_count_name)
                    
                if 'STD' in saves:
                    to_numpy(Std,x,y,w,h,spat_ref,chunk_average_name)
                    chunk_std_list.append(chunk_std_name)

                # clean up at the end of each window and set the newmatrix to the old one
                del rollover_from[:]
                del rollover_to[:]
                del Std
                del average
                
                oldmatrix=newmatrix
                oldcount=newcount

#.......................................................................................
    print 'Finished processing chunks! Stitching them back together!'
    # at the end of each chunk processing, begin rejoining the output slices
    out_Avg = numpy.zeros((xs,ys))
    out_Num = numpy.zeros((xs,ys))
    out_Std = numpy.zeros((xs,ys))

    # assemble all chunks
    for centerID,center in enumerate(centers):
        print center

        # Create_output_filenames of completely assembled chunks.
        head,tail = os.path.split(center)
        info=core.Grab_Data_Info(center,False,True)
        average_name= os.path.join(outdir,'.'.join(tail.split('.')[:-1])+
            '_W'+str(window_width).zfill(2)+'_C'+info.year+info.j_day+'_Avg.tif')
        count_name= os.path.join(outdir,'.'.join(tail.split('.')[:-1])+
            '_W'+str(window_width).zfill(2)+'_C'+info.year+info.j_day+'_Num.tif')
        std_name= os.path.join(outdir,'.'.join(tail.split('.')[:-1])+
            '_W'+str(window_width).zfill(2)+'_Ce'+info.year+info.j_day+'_Std.tif')

         # look for these filenames and fill in the final output matrices
        if 'AVG' in saves:
            for chunkID,ychunk in enumerate(ychunks):
                Avg_chunk= os.path.join(tempdir,'.'.join(tail.split('.')[:-1])+
                    '_W'+str(window_width).zfill(2)+'_C'+info.year+info.j_day+'_Avg_Chnk'+str(chunkID)+'.tif')       

                temp,x,y,w,h,spat_ref = to_numpy(Avg_chunk)
                out_Avg[:,ychunk]=temp[:,range(len(ychunk))]
                
            raster.from_numpy(out_Avg,x,y,w,h,spat_ref,average_name)
            
        if 'NUM' in saves:
            for chunkID,ychunk in enumerate(ychunks):
                Num_chunk= os.path.join(tempdir,'.'.join(tail.split('.')[:-1])+
                    '_W'+str(window_width).zfill(2)+'_C'+info.year+info.j_day+'_Num_Chnk'+str(chunkID)+'.tif')      

                temp,x,y,w,h,spat_ref = to_numpy(Num_chunk)
                out_Num[:,ychunk]=temp[:,range(len(ychunk))]
            
            raster.from_numpy(out_Num,x,y,w,h,spat_ref,count_name)
            
        if 'STD' in saves:
            for chunkID,ychunk in enumerate(ychunks):
                Std_chunk= os.path.join(tempdir,'.'.join(tail.split('.')[:-1])+
                    '_W'+str(window_width).zfill(2)+'_C'+info.year+info.j_day+'_Std_Chnk'+str(chunkID)+'.tif')       
                
                temp,x,y,w,h,spat_ref = to_numpy(Std_chunk)
                out_Std[:,ychunk]=temp[:,range(len(ychunk))]

            raster.from_numpy(out_Std,x,y,w,h,spat_ref,std_name)
            
    print '{Rolling_Raster_Stats} Finished with all processing!'
    
    return
