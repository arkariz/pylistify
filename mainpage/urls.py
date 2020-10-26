from os import name
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.log_out, name='logout'),
    path('mainpage/', views.mainPage, name='main'),
    ]