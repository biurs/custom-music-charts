"""
URLs for list APIs
"""

from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from list import views

router = DefaultRouter()
router.register('lists', views.ListViewSet)

app_name = 'list'

urlpatterns = [
    path('', include(router.urls))
]