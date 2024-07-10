from django.urls import path
from . import views

urlpatterns = [
    path('demo/', views.demo, name='upload_files_demo'),
    path('edit/<str:pk>/', views.edit, name='edit_file'),
    path('create/', views.file_upload, kwargs={"max_files": 3}, name='upload_files'),
    path('upload_modal/', views.file_upload_modal, kwargs={"max_files": 3}, name='upload_files_modal'),
    path('delete/<str:pk>/', views.delete, name='delete_file'),
    path('file_list_modal', views.IndexView.as_view(modal=True), name='file_list_modal'),
    path('', views.IndexView.as_view(), name='list_files'),
]
