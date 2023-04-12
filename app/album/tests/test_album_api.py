"""
Tests for album APIs.
"""
from decimal import Decimal

import time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Album, Artist

from album.serializers import AlbumSerializer

from datetime import date


ALBUMS_URL = reverse('album:album-list')


def specific_album_url(album_id):
    """Create and return a specific album URL."""
    return reverse('album:album-detail', args=[album_id])


def create_artist(name='Sample Artist Name'):
    """Create and return a sample artist"""
    artist = Artist.objects.get_or_create(name=name)[0]
    return artist


def create_album(**params):
    """Create and return a sample album."""
    defaults = {
        'title': 'Sample Album title',
        'artist': create_artist(),
        'release_date': date.fromisoformat('2000-01-01'),
        'avg_rating': Decimal('1.00'),
        'rating_count': 1_000,
        'link': 'https://example.com/album_art',
    }
    defaults.update(params)

    album = Album.objects.create(**defaults)
    return album


class PublicAlbumAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """"Test auth is required to call API."""
        res = self.client.get(ALBUMS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAlbumApiTests(TestCase):
    """Test authentiated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_albums(self):
        """Test retrieving a list of albums."""
        create_album()
        create_album(title='Sample Album 2')

        res = self.client.get(ALBUMS_URL)

        albums = Album.objects.all().order_by('-id')
        serializer = AlbumSerializer(albums, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_album_with_new_artist(self):
        """Test creating an album"""
        payload = {
            'title': 'Sample Album Title',
            'artist': {'name': 'Sample Artist'},
            'release_date': date.fromisoformat('2001-01-01'),
            'avg_rating': Decimal('1.00'),
            'rating_count': 1
        }
        res = self.client.post(ALBUMS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        album = Album.objects.get(id=res.data['id'])
        for k, v in payload.items():
            if k == 'artist':
                artist = Artist.objects.get(name=payload['artist']['name'])
                self.assertEqual(getattr(album, k), artist)
            else:
                self.assertEqual(getattr(album, k), v)

    def test_create_album_with_existing_artist(self):
        """Test creating an album with an existing artist."""
        artist = create_artist(name='Sample Artist')
        payload = {
            'title': 'Sample Album',
            'artist': {'name': 'Sample Artist'},
            'release_date': date.fromisoformat('2000-01-01'),
            'avg_rating': Decimal('1.00'),
            'rating_count': 100,
        }
        res = self.client.post(ALBUMS_URL, payload, format='json')

        #self.assertEqual(res.data['artist']['name'], 'd')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        artists = Artist.objects.all()
        self.assertEqual(artists.count(), 1)
        albums = Album.objects.all()
        self.assertEqual(albums.count(), 1)
        album = albums[0]
        self.assertEqual(album.artist, artist)
        self.assertTrue(
            Artist.objects.filter(
            name=payload['artist']['name']
            ).exists()
        )

    def test_partial_update(self):
        """Test partial update of album."""
        original_title = 'Original Title'
        album = create_album(title=original_title, rating_count=1)

        payload = {'rating_count': 2}
        url = specific_album_url(album.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        album.refresh_from_db()
        self.assertEqual(album.rating_count, payload['rating_count'])
        self.assertEqual(album.title, original_title)

    def test_full_update(self):
        """Test full update of album."""
        album = {
            'title': 'Sample Album',
            'release_date': date.fromisoformat('2000-01-01'),
            'avg_rating': Decimal('1.00'),
            'rating_count': 100,
        }
        album = create_album(**album)

        payload = {
            'title': 'Sample Album 2',
            'artist': {'name': 'Sample Artist 2'},
            'release_date': date.fromisoformat('2000-02-02'),
            'avg_rating': Decimal('2.00'),
            'rating_count': 200,
        }
        url = specific_album_url(album.id)
        res = self.client.put(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        album.refresh_from_db()
        for k, v in payload.items():
            if k == 'artist':
                artist = Artist.objects.get(name=payload['artist']['name'])
                self.assertEqual(getattr(album, k), artist)
            else:
                self.assertEqual(getattr(album, k), v)
