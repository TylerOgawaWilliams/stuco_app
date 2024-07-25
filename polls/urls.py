# urls.py
from django.contrib import admin
from django.urls import path

from polls import views as polls_views

urlpatterns = [
    path('', polls_views.list, name='list'),
    path('create/', polls_views.create, name='create'),
    path('results/<poll_id>/', polls_views.results, name='results'),
    path('vote/<poll_id>/', polls_views.vote, name='vote'),
]
