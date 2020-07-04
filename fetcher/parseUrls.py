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
RELEASE_TXT = os.path.join(SAVED_DIR,"releases.txt")

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
    if ("http" or "https") in sline and len(sline) != 0:
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
    else: 
        if "-" in sline:
            sline = clean_line(sline)
            return sline.split("-")[1],""
    #if there's no site return empty
    return "",""



#cleans spaces in lines
def clean_line(line):
    illegal = [" "]
    new = []
    for letter in line:
        if letter not in illegal:
            new.append(letter)
    return "".join(new)









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

                #check if ends with /1/,/1 or /1/ 
                #if it does make a list of alternate pages

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

    #return list of queries
    return searchQueries







# CHECK IF TRUSTED REPACKERS ARE IN THE REQUESTS
def is_available(trusted,reqs):
    
    tempCandidate = ""
    #for each request made
    for requestMade in reqs:

        #for each line in html request
        for sliceofhtml in str(requestMade.text).lower().split():
            
            #if trusted repacker, in slice, return true
            if trusted.lower() in sliceofhtml:
                if "href" in sliceofhtml:
                    return [True,requestMade.url,sliceofhtml]
                
                else:
                    tempCandidate = requestMade.url
                
    #return false
    if tempCandidate != "":
        return [True,tempCandidate]

    return [False]






# CLASS VISITOR CLASS 
class siteVisitor(threading.Thread):

    #initiate variables
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



    #function to run searches
    def test_url(self):

        #if object is set up
        if self.searchUrl != "":
            
            #initiate request
            r = False

            #tru requests on each of the urls setup
            try:
                reqs = []
                if type(self.searchUrl) == list:
                    for searchPage in self.searchUrl:
                        r = requests.get(searchPage.format(self.target),headers={'User-agent':'searchbot'},timeout=5)
                        reqs.append(r)
                else:
                    r = requests.get(self.searchUrl.format(self.target),headers={'User-agent':'searchbot'},timeout=5)
                    reqs.append(r)



            #unhandled exeptions
            except requests.exceptions.ConnectTimeout:
                return
            except requests.exceptions.ConnectionError:
                return
            except requests.exceptions.ReadTimeout:
                return
            finally:    

                #if request is valid store and return 
                if r:
                    self.siteUp = True
                    self.reqs = reqs

            


#fetch json data in stored
def fetch_data():
    with(open(MEGATHREAD_JSON)) as f:
        return json.load(f)

def get_releases():

    req1 = requests.get("https://api.crackwatch.com/api/games",params={"is_aaa":"true","is_cracked":"true"}).text
    req2 = requests.get("https://api.crackwatch.com/api/games",params={"is_aaa":"false","is_cracked":"true"}).text
    
    d = json.loads(req1)
    d2 = json.loads(req2)


    
    with open(RELEASE_TXT,"w+") as f:
        for aTitle in d:
            f.write(aTitle['title']+"\n")
        for indie in d2:
            try:
                f.write(indie['title']+"\n")
            except UnicodeEncodeError:
                continue

def fetch_releases():
    gs = []
    with open(RELEASE_TXT,"r") as f:
        for line in f:
            gs.append(line.strip())




    return gs

#main function to return searches
def search(target):

    repackersAvailable = {}
    
    #get date to check if it is time to update the megathread
    day = datetime.datetime.now().day
    #day=7

    #if a week has passes since last update
    if day % 7 == 0:
        getMegaThread()
        #get_releases()


    #extract data from thread
    if "megaThread.json" not in os.listdir(SAVED_DIR):    
        parseThread()


    #get extracted data
    data = fetch_data()


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
                    finalUrl = ""

                    
                    
                    ##if there is a direct link
                    if len(result) == 3:
                        
                        #if it's an extension to the base, add to base
                        if "http" not in result[2] and "https" not in result[2]:
                            
                            if thread.url == "https://rarbg.to/":
                                finalUrl = "https://rargb.to/"+ result[2].split("\"")[1][1:]
                            else:
                                finalUrl = thread.url + result[2].split("\"")[1][1:]
                            
                        #if its the full url
                        else:
                            try:
                                finalUrl = result[2].split("=")[1]
                            except IndexError:
                                return
                    else: 
                        finalUrl = result[1]    
                    
                    #if repacker not already in the dictionary
                    if repacker not in repackersAvailable:
                        repackersAvailable[repacker] = [[thread.site,finalUrl]]
                    
                    #if already gotten add to dictionary
                    else:
                        repackersAvailable[repacker].append([thread.site,finalUrl])

    return repackersAvailable
