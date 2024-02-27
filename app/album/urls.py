"""
URL mappings for the album app.
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from album import views


router = DefaultRouter()
router.register('genres', views.GenreViewSet)
router.register('', views.AlbumViewSet)

app_name = 'album'

urlpatterns = [
    path('', include(router.urls)),
]