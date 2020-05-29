#from fetcher.updateJsons import parseThread
import json
import requests
import threading
import time
import os
import sys
import pathlib
import datetime


# STATIC PATH FILE VARIABLES, SHOULD BE THE SAME THROUGHOUT BUT IF SOMETHIGN CHANGES JUST CHANGE IT HERE
SAVED_DIR= os.path.join(str(pathlib.Path().absolute()),"fetcher","saved")
MEGATHREAD_JSON = os.path.join(SAVED_DIR,"megaThread.json")
MEGATHREAD_TXT = os.path.join(SAVED_DIR,"megathread.txt")
QUERYFORMATS = os.path.join(SAVED_DIR,"queryFormat.txt")


#CHECK IF THERE IS AN INTERNET CONNECTION AVAILABLE
def checkInternet(times):

    #check i times
    for i in range(times):
        
        #ping google, always up
        r = requests.get("http://google.com")
        
        #if request good
        if r:
            return True
        
        #else wait 20 seconds and retry
        else:
            print("no internet detected, retrying in 20 seconds..")
            time.sleep(20)

    #bad request, return false
    print("request timed out")
    return False





#GET MEGA THREAD FOR R/PIRATEDGAMES
def getMegaThread():
    f = open(MEGATHREAD_TXT,"r")
    readToday = f.read().split()[0]
    
    if str(readToday) == str(datetime.datetime.now().date()):
        return
    
    print("writing to file")
    #if internet connection available
    if checkInternet(2):
        
        #get top posts from r/PiratedGames
        r = requests.get("https://www.reddit.com/r/PiratedGames/.json?count=2",headers={'User-agent':'myobot'})
        
        #for each of the posts
        for i in r.json()['data']['children']:

            #if post is mega thread
            if  "Mega Thread" in i['data']['title']:
                
                #open megathread.txt and write to it
                with open(MEGATHREAD_TXT,"w+") as f:
                    f.write(str(datetime.datetime.now().date()) + "\n")
                    f.write(i['data']['selftext'])






#GO THROUGH DOWNLOADED MEGATHREAD AND WRITE TO JSON
def parseThread():
    
    #initiate return dictionary 
    data ={}

    #open txt file with megathread donwloaded
    with open(MEGATHREAD_TXT) as f:
        
        #split into sections
        f = f.read().split("###")

        #parse sections
        for section in f[1::]:

            # s[0] title, s[1] data
            s = section.split(":",1)
            sectionTitle = s[0]
            data[sectionTitle] ={}
            
            #iterate over all the safe sites in section
            for line in s[1].split("\n"):
                site,url = grab(line)

                #if not empty
                if site != "":
                    data[sectionTitle][site] = url
    
    #write dictionary out to megathread json
    with open(MEGATHREAD_JSON,"w") as outfile:
        json.dump(data,outfile)









#GRAB LINKS FROM THE CHOSEN LINES,RETURNS --> SITE-NAME,URL
def grab(line):

    #remove all newlines 
    sline = line.strip()
    
    #check if there is a link in the line
    if "http" or "https" in sline:
        

        sline =sline.split("(")
        
        #if line has url and title
        if len(sline) == 2:
            
            #exception for empty lines
            try:
                name = sline[0].split("[")[1]
                url = sline[1].split(")")[0]
                return name[:len(name)-1:],url

            except IndexError:
                return "",""
    
    #if there's no site return empty
    return "",""








#EXTRACT QUERY FORMATS FROM SAVED/ QUERYFORMATS
def get_query_formats():

    #initiate return dictionary
    searchQueries = {}

    #open queryformats file
    with open(QUERYFORMATS) as f:

        #iterate over each query format
        for line in f:

            #strip and split lines
            line = line.strip()
            line = line.split("|")
            
            #if there are multiple pages on website
            if line[1].endswith("1/") or line[1].endswith("1") or "/1/" in line[1]:
                
                #list of all pages
                allPages = []

                #check if ends with /1/ or /1

                if line[1][-1::] == "/":
                    for i in range(1,7):
                        allPages.append(line[1][:-2:]+str(i)+"/")
                    
                elif line[1][-1::]=="1":
                    for i in range(1,7):
                        allPages.append(line[1][:-1:]+str(i))
                elif "/1/" in line[1]:

                    splitLine = line[1].split("/1/")

                    for i in range(1,7):

                        allPages.append(splitLine[0] + "/{}/".format(str(i))+splitLine[1])
                searchQueries[line[0]] = allPages
            
            
            else:
                searchQueries[line[0]] = line[1]

    
    return searchQueries







# CHECK IF TRUSTED REPACKERS ARE IN THE REQUESTS
def is_available(trusted,reqs):
    
    #for each request made
    for requestMade in reqs:

        #for each line in html request
        for sliceofhtml in str(requestMade.text).lower().split():
            
            #if trusted repacker, in slice, return true
            if trusted.lower() in sliceofhtml:
                return [True,requestMade.url]

    return [False]






# CLASS VISITOR CLASS 
class siteVisitor(threading.Thread):

    siteUp = False
    request = None

    def __init__(self,target,site,url,searchUrl):
        threading.Thread.__init__(self)
        self.target = target
        self.site = site
        self.url = url
        self.searchUrl = searchUrl

    def run(self):
        self.test_url()

    def test_url(self):
        if self.searchUrl != "":
            r = False

            try:
                reqs = []
                if type(self.searchUrl) == list:
                    for searchPage in self.searchUrl:
                        r = requests.get(searchPage.format(self.target),headers={'User-agent':'searchbot'},timeout=4)
                        reqs.append(r)
                else:
                    r = requests.get(self.searchUrl.format(self.target),headers={'User-agent':'searchbot'},timeout=4)
                    reqs.append(r)

            except requests.exceptions.ConnectTimeout:
                return
            except requests.exceptions.ConnectionError:
                return
            except requests.exceptions.ReadTimeout:
                return
            finally:

                if r:
                    self.siteUp = True
                    self.reqs = reqs

            






#main function to return searches

def search(target):

    repackersAvailable = {}
    
    #get date to check if it is time to update the megathread
    day = datetime.datetime.now().day
    #day=7

    #if a week has passes since last update
    if day % 7 == 0:
        getMegaThread()


    #extract data from thread
    if "megaThread.json" not in os.listdir(SAVED_DIR):    
        parseThread()


    #get extracted data
    f = open(MEGATHREAD_JSON)
    data = json.load(f)


    #extract data to variables
    torrentSites = data['Torrent Sites']
    directDownloads = data['Direct Download Sites']
    trustedRepacks = list(data['Repacks'].keys())
    queriesFormats = get_query_formats()



    #list of threads for each site
    sites = []


    #initiate torrent sites
    for site,url in torrentSites.items():
        siteObj = siteVisitor(target,site,url,queriesFormats[url])
        sites.append(siteObj)
    

    ##initiate direct download sites
    for site,url in directDownloads.items():
        siteObj = siteVisitor(target,site,url,queriesFormats[url])
        sites.append(siteObj)


    #run each search on the sites
    for thread in sites:
        thread.start()


    #wait for threads to finish, timeout set to 5 seconds
    for thread in sites:
        thread.join()


    
    #for each site
    for thread in sites:

        #if the site is up
        if thread.siteUp:

            #iterate over each repackers
            for repacker in trustedRepacks:

                #if repacker in request
                result = is_available(repacker,thread.reqs)
                if result[0]:
                    #if not already gotten, add site
                    if repacker not in repackersAvailable:
                        repackersAvailable[repacker] = [[thread.site,result[1]]]
                    
                    #if already gotten add to dictionary
                    else:
                        repackersAvailable[repacker].append([thread.site,result[1]])

    return repackersAvailable

