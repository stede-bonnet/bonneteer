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
    

    
    form = SearchForm()
    context['form'] = form

    return render(request,'bonneteer/index.html',context=context)





def about(request):
    context = {}    
    return render(request,'bonneteer/about.html',context=context)