"""
Tests for List APIs.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import List, Album, Artist, Entry

from list.serializers import ListSerializer

from decimal import Decimal

from datetime import date

LISTS_URL = reverse('list:list-list')


def specific_list_url(list_id):
    """Create and return a specific list URL."""
    return reverse('list:list-detail', args=[list_id])

def create_list(user, **params):
    """Create and return a sample list"""
    defaults = {
        'label': 'Sample List label',
    }
    defaults.update(params)

    list = List.objects.create(user=user, **defaults)
    return list

def create_artist(name='Sample Artist Name'):
    """Create and return a sample artist"""
    artist = Artist.objects.get_or_create(name=name, start_year=2000)[0]
    return artist

def create_album(**params):
    """Create and return a sample album."""
    defaults = {
        'title': 'Sample Album title',
        'release_date': date.fromisoformat('2000-01-01'),
        'avg_rating': Decimal('1.00'),
        'rating_count': 1_000,
        'link': 'https://example.com/album_art',
    }
    defaults.update(params)

    album = Album.objects.create(**defaults)
    album.artist.add(create_artist())
    album.save()

    return album

def create_entry(album, list, **params):
    """Create and return sample Entry"""
    defaults = {
        'description': 'Sample Entry Description',
        'album': album,
        'list': list,
    }
    defaults.update(params)
    entry = Entry.objects.create(**params)

    return entry

class PublicListAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        query_params = {
            'public': True
        }
        res = self.client.get(LISTS_URL, query_params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
