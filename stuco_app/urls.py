# stuco_app/stuco_app_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("about/", views.about, name="about"),
]
