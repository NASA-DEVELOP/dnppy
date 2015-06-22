import dnppy
from dnppy import core
import os
import requests
from bs4 import BeautifulSoup
import urllib2
p_url = r"http://water.weather.gov/precip/p_download_new/2005/"
url = r"http://water.weather.gov/precip/p_download_new/2005/02/"
url2 = r"http://water.weather.gov/precip/p_download_new/2005/02/02/"
r = requests.get(p_url)
data = r.text
soup = BeautifulSoup(data)
data = []

"""
def next_page(soup,data,cur_link,):
    print "Current Link: " + cur_link
    pop = soup.find_all('a')
    for i in pop:
        end = i.get('href')
        if len(end) == 3:
            new_link = cur_link + end
            print "Next Link: " + new_link
            new_soup = BeautifulSoup(urllib2.urlopen(new_link).read())
            data = next_page(new_soup,data,new_link)
            pop = new_soup.find_all('a')
            for x in pop:
                end = x.get('href')
                if 
                new_link = new_link + end
                print "Tar File: " + new_link
                full_url.append(new_link)
        
##Need to figure out how to skip the weird NQUE could just put another if statement. 
#def get_data(link):
#    page = urllib2.urlopen(link)
#    soup = BeautifulSoup(page)
#    return soup

#next_page(soup,data,url)
"""
#This part is continuing to build the folder pathnames
first_char = ['0','1','2','3']
for link in soup.find_all('a'):
    end = link.get('href')
    for i in first_char:
        if end[-1] == '/' and i in end[0]:
            print r'Folder: ' + p_url + end 
            new_url = url + end
            
    

# Below pulls out the files from folder with data the user is looking for in them. 
templist = []
Contains = ['nws_']
Contains = core.enf_list(Contains)
for link in soup.find_all('a'):
    end = link.get('href')
    for i in Contains:
        if i in end[:]:
            full_url = url2 + end
            templist.append(full_url)      
      
# Currently produces a list of urls at whatever directory you're at. 
# Need to: find a way to add a better filter to find_all.
# Can NOT reference two tags at the same time 


