"""
URL mappings for the list app.
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from list import views


router = DefaultRouter()
router.register('', views.ListViewSet)

app_name = 'list'

urlpatterns = [
    path('', include(router.urls)),
]