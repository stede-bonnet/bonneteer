from django.shortcuts import render
from django.http import HttpResponse

from fetcher.parseUrls import *


from bonneteer.forms import SearchForm


def index(request):
    context = {}
    if request.method == 'POST':

        form = SearchForm(request.POST)
        if form.is_valid():
            srch = search(form.cleaned_data['search'])
            
            context['results'] = srch
            if len(srch) == 0:
                context['message'] = 'sorry no torrents found'

    else:
        context['message'] = ''
    
    form = SearchForm()
    context['form'] = form


    return render(request,'bonneteer/index.html',context=context)





def about(request):
    data = fetch_data()
    
    torrentSites = data['Torrent Sites']
    directDownloads = data['Direct Download Sites']
    trustedRepacks = data['Repacks']


    context = {'Torrents':torrentSites,'DirectDownload':directDownloads,'Repackers':trustedRepacks}    
    return render(request,'bonneteer/about.html',context=context)