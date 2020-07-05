from django.shortcuts import render
from django.http import HttpResponse

from fetcher.parseUrls import *
from random import randint

from bonneteer.forms import SearchForm
from bonneteer.models import Searches


def index(request,*args):
    context = {}
    if request.method == 'POST':

        if len(args) == 1:
            print(args)
        
        
        if "rnd_search" in request.POST:
            
            # log random search count
            dbSearches = Searches.objects.get(name="randomSearch")
            dbSearches.searches += 1
            dbSearches.save()
            context['message'] = "Sorry, having some problems with getting latest titles for random search"
            try:
                data = fetch_releases()
                data = data[:30:]
                randomTitle = data[randint(0,len(data))]
            except IndexError:
                data = []
            srch = search(randomTitle)

            context['results'] = srch
            context['head'] = randomTitle


            if len(srch) == 0:
                context['message'] = 'sorry no results for: {}'.format(randomTitle)
            

        else:
            form = SearchForm(request.POST)
            if form.is_valid():
                dbSearches = Searches.objects.get(name="standardSearch")
                dbSearches.searches += 1
                dbSearches.save()
                srch = search(form.cleaned_data['search'])
                context['results'] = srch
                context['head'] = form.cleaned_data['search']
                
                if len(srch) == 0:
                    context['message'] = 'sorry no results for: {}'.format(form.cleaned_data['search'])

    else:
        context['message'] = ''
        context['head'] = "Bonnet search"
    

    form = SearchForm()
    context['form'] = form
    context['showButtons'] = True

    return render(request,'bonneteer/index.html',context=context)


def releases(request):
    data = fetch_releases()
    context = {}
    context['tripleA']= data[:30:]
    context['indie'] = data[30:len(data):]
    return render(request,'bonneteer/releases.html',context=context)


def about(request):
    data = fetch_data()
    
    torrentSites = data['Torrent Sites']
    directDownloads = data['Direct Download Sites']
    trustedRepacks = data['Repacks']


    context = {'Torrents':torrentSites,'DirectDownload':directDownloads,'Repackers':trustedRepacks}    
    return render(request,'bonneteer/about.html',context=context)

def searchRelease(request,index):
    context = {}
    data = fetch_releases()
    releaseName = data[int(index)]
    
    srch = search(releaseName)

    context['results'] = srch
    context['head'] = releaseName

    if len(srch) == 0:
        context['message'] = 'sorry no results for: {}'.format(releaseName)

    context['showButtons'] = False
    return render(request,'bonneteer/index.html',context=context)