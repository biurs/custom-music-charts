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


ARTISTS_URL = reverse('artist:artist-list')


def specific_artist_url(artist_id):
    """Create and return a specific artist URL."""
    return reverse('artist:artist-detail', args=[artist_id])


def create_artist(**params):
    """Create and return a sample artist"""
    defaults = {
        'name': 'Sample Artist Name',
        'origin_country': 'USA',
        'years_active': [{'start': 2000, 'end': 2010}, {'start': 2014, 'end': 2015}]
    }
    defaults.update(params)

    artist = Artist.objects.create(**defaults)
    return artist


class PublicArtistAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """"Test auth is required to call API."""
        res = self.client.get(ARTISTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateArtistApiTests(TestCase):
    """Test authenticated superuser API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_regular_user_retrieve_artists(self):
        """Test retrieving a list of artists as regular user."""
        create_artist()
        create_artist(name='Sample Artist 2')

        res = self.client.get(ARTISTS_URL)

        artists = Artist.objects.all().order_by('-id')
        serializer = ArtistSerializer(artists, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_regular_user_create_artist_fails(self):
        """Test creating an artist as a regular user fails."""
        payload = {
            'name': 'Sample Artist'
        }
        res = self.client.post(ARTISTS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Artist.objects.all().count(), 0)

    def test_regular_user_partial_update_artist_fails(self):
        """Test partially updating an artist as a regular user fails."""
        original_name = 'Sample Artist'
        original_country = 'USA'
        artist = create_artist(name=original_name, origin_country=original_country)

        payload = {'origin_country': 'CAN'}
        url = specific_artist_url(artist.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        artist.refresh_from_db()
        self.assertEqual(artist.name, original_name)
        self.assertEqual(artist.origin_country, original_country)

    def test_regular_user_full_update_artist_fails(self):
        """Test fully updating an artist as a regular user fails."""
        artist_dict = {
            'name': 'Sample Artist Name',
            'origin_country': 'USA',
            'years_active': [{'start': 1990, 'end': 1995}]
        }
        artist = create_artist(**artist_dict)

        payload = {
            'name': 'Sample Artist Name 2',
            'origin_country': 'CAN',
            'years_active': [{'start': 2000, 'end': 2005}]
        }
        url = specific_artist_url(artist.id)
        res = self.client.put(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        artist.refresh_from_db()
        for k, v in artist_dict.items():
                self.assertEqual(getattr(artist, k), v)

    def test_regular_user_delete_artist_fails(self):
        """Test deleting artist as a regular user fails."""
        artist = create_artist()

        url = specific_artist_url(artist.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Artist.objects.filter(id=artist.id).exists())


class PrivateArtistSuperuserApiTests(TestCase):
    """Test authenticated superuser API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            'user@example.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_artists(self):
        """Test retrieving a list of artists."""
        create_artist()
        create_artist(name='Sample Artist Name 2')

        res = self.client.get(ARTISTS_URL)

        artists = Artist.objects.all().order_by('-id')
        serializer = ArtistSerializer(artists, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_artist(self):
        """Test creating an artist"""
        payload = {
            'name': 'Sample Artist Name',
            'origin_country': 'USA',
            'years_active': [{'start': 2000, 'end': 2001}],
        }
        res = self.client.post(ARTISTS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        artist = Artist.objects.get(id=res.data['id'])
        for k, v in payload.items():
                self.assertEqual(getattr(artist, k), v)

    def test_partial_update_artist(self):
        """Test partial update of artist"""
        artist_name = 'Sample Artist Name'
        artist_country = 'CAN'
        artist = create_artist(name=artist_name, origin_country=artist_country)
        payload = {
            'name': 'New Artist Name'
        }

        url = specific_artist_url(artist.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        artist.refresh_from_db()
        self.assertEqual(artist.name, payload['name'])
        self.assertEqual(artist.origin_country, artist_country)

    def test_full_update_artist(self):
        """Test full update of artist"""
        artist = {
            'name': 'Sample Artist Name 1',
            'origin_country': 'USA',
            'years_active': [{'start': 2000, 'end': 2001}],
        }

        artist = create_artist(**artist)

        payload = {
            'name': 'Sample Artist Name 2',
            'origin_country': 'CAN',
            'years_active': [{'start': 2020, 'end': 2021}]
        }

        url = specific_artist_url(artist.id)
        res = self.client.put(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        artist.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(artist, k), v)

    def test_delete_artist(self):
        """Test deleting an artist."""
        artist = create_artist()

        url = specific_artist_url(artist.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Artist.objects.filter(id=artist.id).exists())