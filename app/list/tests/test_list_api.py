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
    }
    defaults.update(params)
    entry = Entry.objects.create(
        album=album,
        owner_list=list,
        **params,
        )

    return entry


class PublicListAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.test_user = get_user_model().objects.create_user(
            'user1@example.com'
            'testpass1234'
        )

    def test_auth_required(self):
        """Test auth is required to call API."""
        query_params = {
            'public': True
        }
        res = self.client.get(LISTS_URL, query_params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_list(self):
        """Test retrieving a public list."""
        album1 = create_album()
        list1 = create_list(user=self.test_user, public=False)
        create_entry(album1, list1)
        query_params = {
            'public': True
        }

        res = self.client.get(LISTS_URL, query_params)

        lists = List.objects.filter(public=True).order_by('id')
        serializer = ListSerializer(lists, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)


class PrivateListAPITests(TestCase):
    """Test authenticated user API requests."""
    def setUp(self):
        self.client = APIClient()
        self.user2 = get_user_model().objects.create_user(
            'user2@example.com'
            'testpass1234'
        )
        self.user = get_user_model().objects.create_user(
            'user1@example.com'
            'testpass1234'
        )
        self.client.force_authenticate(self.user)

    def test_regular_user_retrieve_list(self):
        """Test retrieving a private list as a regular user."""
        album1 = create_album()
        list1 = create_list(user=self.user2, public=True, label='label2')
        list2 = create_list(user=self.user2, public=False, label='label1')

        create_entry(album1, list1)
        create_entry(album1, list2)
        query_params = {
            'public': True
        }

        res = self.client.get(LISTS_URL, query_params)

        lists = List.objects.filter(public=True).order_by('-id')
        serializer = ListSerializer(lists, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    def test_list_limited_to_user(self):
        """Test lists returned are limited ot user."""
        create_list(user=self.user2)
        create_list(user=self.user)

        res = self.client.get(LISTS_URL)

        lists = List.objects.filter(user=self.user)
        serializer = ListSerializer(lists, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    def test_create_list_with_items(self):
        """Test creating a list with items."""
        album1 = create_album()
        payload = {
            'label': 'Test List',
            'albums': [
                {
                    'album': {
                        'id': album1.id
                    },
                    'description': 'Sample Description',
                }
            ]
        }
        res = self.client.post(LISTS_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        lists = List.objects.filter(user=self.user)
        self.assertEqual(lists.count(), 1)
        list = lists[0]
        self.assertEqual(list.entries.count(), 1)