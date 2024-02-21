"""
Tests for artist APIs.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Artist

from search.serializers import SearchSerializer



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
        """Test search returns artist with matching name."""
        art1 = create_artist(name='abcde 123')
        query_params = {
            'term': 'abcd 123'
        }
        res = self.client.get(SEARCH_URL, query_params)

        serial_res = SearchSerializer(art1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'][0], serial_res.data)

    def test_search_order_priority(self):
        """"Test artist list returned in correct order by similarity."""
        art1 = create_artist(name='abcde 123')
        art3 = create_artist(name='zyx 123')
        art2 = create_artist(name='bcd 123')

        query_params = {
            'term': 'abcd 123'
        }
        res = self.client.get(SEARCH_URL, query_params)

        serial_res = SearchSerializer([art1, art2, art3], many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serial_res.data)

    def test_search_with_no_results(self):
        """Test results when no matching query."""
        art1 = create_artist(name='abcde 123')
        query_params = {
            'term': 'zyx'
        }
        res = self.client.get(SEARCH_URL, query_params)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 0)



