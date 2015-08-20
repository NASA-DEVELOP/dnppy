####Download files via ftp ####

#1) Click on the "Packages" tab at the top of your window 
#   ->  Click on the "Install package(s)..." -> Select "USA(TN)" and press OK
  
#2) Click on the "Packages" tab at the top of your window 
#   ->  Click on the "Load Package..." -> Select "RCurl" and press OK


##Please change the year and the path in the following script before you run it (look for the # sign to see where)
# Once you change all the years and path copy the entire script and paste it into your R Console window and let it run


library(RCurl)
url <- "ftp://data.ncdc.noaa.gov/cdr/persiann/files/1983/" ### change according to the year you want###
filenames <- getURL(url, dirlistonly = TRUE) 
fn <- unlist(strsplit(filenames, "\r\n")) 

# To download the files 
destdir <- "C:/Users/jessica.sutton/Documents/DATA/Precipitation/PERSIANN/1983/"  # Adapt to your system 
lapply(fn, function(x) download.file(paste0(url, x), paste0(destdir, x)))




url <- "ftp://data.ncdc.noaa.gov/cdr/persiann/files/1984/"  ### change according to the year you want###
filenames <- getURL(url, dirlistonly = TRUE) 
fn <- unlist(strsplit(filenames, "\r\n")) 

# To download the files 
destdir <- "C:/Users/jessica.sutton/Documents/DATA/Precipitation/PERSIANN/1984/"  # Adapt to your system 
lapply(fn, function(x) download.file(paste0(url, x), paste0(destdir, x)))
library(RCurl)



url <- "ftp://data.ncdc.noaa.gov/cdr/persiann/files/1985/" ### change according to the year you want###
filenames <- getURL(url, dirlistonly = TRUE) 
fn <- unlist(strsplit(filenames, "\r\n")) 

# To download the files 
destdir <- "C:/Users/jessica.sutton/Documents/DATA/Precipitation/PERSIANN/1985/"  # Adapt to your system 
lapply(fn, function(x) download.file(paste0(url, x), paste0(destdir, x)))




url <- "ftp://data.ncdc.noaa.gov/cdr/persiann/files/1986/" ### change according to the year you want###
filenames <- getURL(url, dirlistonly = TRUE) 
fn <- unlist(strsplit(filenames, "\r\n")) 

# To download the files 
destdir <- "C:/Users/jessica.sutton/Documents/DATA/Precipitation/PERSIANN/1986/"  # Adapt to your system 
lapply(fn, function(x) download.file(paste0(url, x), paste0(destdir, x)))




url <- "ftp://data.ncdc.noaa.gov/cdr/persiann/files/1987/" ### change according to the year you want###
filenames <- getURL(url, dirlistonly = TRUE) 
fn <- unlist(strsplit(filenames, "\r\n")) 

# To download the files 
destdir <- "C:/Users/jessica.sutton/Documents/DATA/Precipitation/PERSIANN/1987/"  # Adapt to your system 
lapply(fn, function(x) download.file(paste0(url, x), paste0(destdir, x)))



url <- "ftp://data.ncdc.noaa.gov/cdr/persiann/files/1988/" ### change according to the year you want###
filenames <- getURL(url, dirlistonly = TRUE) 
fn <- unlist(strsplit(filenames, "\r\n")) 

# To download the files 
destdir <- "C:/Users/jessica.sutton/Documents/DATA/Precipitation/PERSIANN/1988/"  # Adapt to your system 
lapply(fn, function(x) download.file(paste0(url, x), paste0(destdir, x)))




url <- "ftp://data.ncdc.noaa.gov/cdr/persiann/files/1989/" ### change according to the year you want###
filenames <- getURL(url, dirlistonly = TRUE) 
fn <- unlist(strsplit(filenames, "\r\n")) 

# To download the files 
destdir <- "C:/Users/jessica.sutton/Documents/DATA/Precipitation/PERSIANN/1989/"  # Adapt to your system 
lapply(fn, function(x) download.file(paste0(url, x), paste0(destdir, x)))



url <- "ftp://data.ncdc.noaa.gov/cdr/persiann/files/1990/" ### change according to the year you want###
filenames <- getURL(url, dirlistonly = TRUE) 
fn <- unlist(strsplit(filenames, "\r\n")) 

# To download the files 
destdir <- "C:/Users/jessica.sutton/Documents/DATA/Precipitation/PERSIANN/1990/"  # Adapt to your system 
lapply(fn, function(x) download.file(paste0(url, x), paste0(destdir, x)))



url <- "ftp://data.ncdc.noaa.gov/cdr/persiann/files/1991/" ### change according to the year you want###
filenames <- getURL(url, dirlistonly = TRUE) 
fn <- unlist(strsplit(filenames, "\r\n")) 

# To download the files 
destdir <- "C:/Users/jessica.sutton/Documents/DATA/Precipitation/PERSIANN/1991/"  # Adapt to your system 
lapply(fn, function(x) download.file(paste0(url, x), paste0(destdir, x)))




url <- "ftp://data.ncdc.noaa.gov/cdr/persiann/files/1992/" ### change according to the year you want###
filenames <- getURL(url, dirlistonly = TRUE) 
fn <- unlist(strsplit(filenames, "\r\n")) 

# To download the files 
destdir <- "C:/Users/jessica.sutton/Documents/DATA/Precipitation/PERSIANN/1992/"  # Adapt to your system 
lapply(fn, function(x) download.file(paste0(url, x), paste0(destdir, x)))




url <- "ftp://data.ncdc.noaa.gov/cdr/persiann/files/1993/" ### change according to the year you want###
filenames <- getURL(url, dirlistonly = TRUE) 
fn <- unlist(strsplit(filenames, "\r\n")) 

# To download the files 
destdir <- "C:/Users/jessica.sutton/Documents/DATA/Precipitation/PERSIANN/1993/"  # Adapt to your system 
lapply(fn, function(x) download.file(paste0(url, x), paste0(destdir, x)))
