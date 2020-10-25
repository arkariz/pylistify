from os import name
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('addplaylist/', views.index, name='result'),
    path('mainpage/', views.mainPage, name='main'),
    ]