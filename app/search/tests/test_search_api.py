"""
Tests for artist APIs.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Artist

from artist.serializers import ArtistSerializer


SEARCH_URL = reverse('search:search')


def create_artist(**params):
    """Create and return a sample artist"""
    defaults = {
        'name': 'Sample Artist Name',
        'origin_country': 'USA',
        'start_year': 2000,
    }
    defaults.update(params)

    artist = Artist.objects.create(**defaults)
    return artist

class PublicArtistAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_search(self):
        """"Test unauth can get artist list."""
        art1 = create_artist(name='abcde 123')
        art2 = create_artist(name='bcd 123')
        art4 = create_artist(name='abc 1')
        art3 = create_artist(name='zyx 123')
        art5 = create_artist(name='zyx 987')

        artists = Artist.objects.all().order_by('-id')
        serializer = Artist.s

        res = self.client.get(SEARCH_URL)
        query_params = {
            'term': 'abcde 123'
        }

        self.assertEqual(res.status_code, status.HTTP_200_OK)