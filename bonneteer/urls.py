from django.contrib import admin
from django.urls import path
from django.urls import include
from bonneteer import views


app_name = 'bonneteer'
urlpatterns = [
    path('',views.index,name='index'),
    path("bonneteer",views.index,name="index"),
    path("about",views.about,name="about")
]