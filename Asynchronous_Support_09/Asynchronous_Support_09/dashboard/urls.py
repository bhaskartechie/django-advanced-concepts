# asyncdemo/urls.py

from django.urls import path
from dashboard.views import AsyncPhotoView, photo_view

urlpatterns = [
    path("photos/", AsyncPhotoView.as_view(), name="async_photos"), # This is the asynchronous version
    # Uncomment the line below to use the synchronous version
    path("photos/", photo_view, name="async_photos"), # This is the synchronous version
]
