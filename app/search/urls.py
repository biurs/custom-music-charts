"""
URLs for Search API.
"""

from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from search import views

router = DefaultRouter()
router.register('', views.SearchArtist)

app_name = 'search'

urlpatterns = [
    path('', include(router.urls))
]