"""
Tests for artist APIs.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import List, Entry, Artist, Album

from list.serializers import ListSerializer

from datetime import date

from decimal import Decimal


LISTS_URL = reverse('list:list-list')


def specific_list_url(list_id):
    """Create and return a specific list URL."""
    return reverse('artist:artist-detail', args=[list_id])


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


def create_list(owner, **params):
    """Create and return a sample list"""
    defaults = {
        'name': 'Sample List Name',
        'description': 'Sample List Description',
        'is_public': True
    }
    defaults.update(params)

    list = List.objects.create(owner=owner, **defaults)
    return list


def create_entry(album, list, **params):
    """Create and return a sample entry."""
    defaults = {
        'album_description': 'Sample Album Description'
    }
    defaults.update(params)

    entry = Entry.objects.create(
        album=album,
        list=list,
        **params
        )
    return entry





class PublicListAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """"Test auth is required to call API."""
        res = self.client.get(LISTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateListApiTests(TestCase):
    """Test authenticated user API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_regular_user_retrieve_list(self):
        """Test retrieving a list as regular user."""
        album1 = create_album()
        list1 = create_list(owner=self.user)
        create_entry(album=album1, list=list1, album_description="Sample Desciption.")

        res = self.client.get(LISTS_URL)

        lists = List.objects.all().order_by('-id')
        serializer = ListSerializer(lists, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

#     def test_regular_user_create_artist_fails(self):
#         """Test creating an artist as a regular user fails."""
#         payload = {
#             'name': 'Sample Artist',
#             'start_year': 2000,
#         }
#         res = self.client.post(ARTISTS_URL, payload, format='json')

#         self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual(Artist.objects.all().count(), 0)

#     def test_regular_user_partial_update_artist_fails(self):
#         """Test partially updating an artist as a regular user fails."""
#         original_name = 'Sample Artist'
#         original_country = 'USA'
#         artist = create_artist(name=original_name, origin_country=original_country)

#         payload = {'origin_country': 'CAN'}
#         url = specific_artist_url(artist.id)
#         res = self.client.patch(url, payload)

#         self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
#         artist.refresh_from_db()
#         self.assertEqual(artist.name, original_name)
#         self.assertEqual(artist.origin_country, original_country)

#     def test_regular_user_full_update_artist_fails(self):
#         """Test fully updating an artist as a regular user fails."""
#         artist_dict = {
#             'name': 'Sample Artist Name',
#             'origin_country': 'USA',
#             'start_year': 2000,
#         }
#         artist = create_artist(**artist_dict)

#         payload = {
#             'name': 'Sample Artist Name 2',
#             'origin_country': 'CAN',
#             'start_year': 2001
#         }
#         url = specific_artist_url(artist.id)
#         res = self.client.put(url, payload, format='json')

#         self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
#         artist.refresh_from_db()
#         for k, v in artist_dict.items():
#                 self.assertEqual(getattr(artist, k), v)

#     def test_regular_user_delete_artist_fails(self):
#         """Test deleting artist as a regular user fails."""
#         artist = create_artist()

#         url = specific_artist_url(artist.id)
#         res = self.client.delete(url)

#         self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertTrue(Artist.objects.filter(id=artist.id).exists())