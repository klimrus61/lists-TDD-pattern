from django.contrib import admin
from django.urls import path, include
from lists import views

urlpatterns = [
    path('<int:list_id>/', views.view_list, name='view_list'),
    path('new', views.new_list, name='new_list'),
    
]
