from django.urls import path
from . import views

urlpatterns = [
    path('files/upload/', views.upload_file, name='upload_file'),
    path('files/', views.list_files, name='list_files'),
    path('files/<uuid:file_id>/', views.get_file_content, name='get_file_content'),
    path('files/<uuid:file_id>/progress/', views.get_file_progress, name='get_file_progress'),
    path('files/<uuid:file_id>/delete/', views.delete_file, name='delete_file'),
]

