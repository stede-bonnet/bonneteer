from django.contrib import admin
from django.urls import path
from django.urls import include
from bonneteer import views


app_name = 'bonneteer'
urlpatterns = [
    path('home',views.index,name='index'),
    path("about",views.about,name="about"),
    path("releases",views.releases,name="releases"),
    path("release-search/<slug:index>/",views.searchRelease,name="searchRel")
]