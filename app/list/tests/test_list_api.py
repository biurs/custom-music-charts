"""
Tests for List APIs.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import List, Album, Artist, Entry

from list.serializers import ListDetailSerializer, ListSerializer

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

    def test_retrieve_specific_list(self):
        """Test retrieving detail view of specific list."""
        album1 = create_album()
        list1 = create_list(user=self.test_user, public=True)
        create_entry(album1, list1)
        query_params = {
            'public': True
        }

        specific_url = specific_list_url(list1.id)

        res = self.client.get(specific_url, query_params)

        serializer = ListDetailSerializer(list1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


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
        serializer = ListDetailSerializer(lists, many=True)
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
        album2 = create_album(title='title2')
        payload = {
            'label': 'Test List',
            'albums': [
                {
                    'album':  album1.id,
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

    def test_delete_list(self):
        """Test deleting a list"""
        list1 = create_list(user=self.user)
        url = specific_list_url(list1.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(List.objects.filter(id=list1.id).exists())

    def test_delete_other_user_list(self):
        """Test deleting another users list fails."""
        list1 = create_list(user=self.user2, public=True)
        url = specific_list_url(list1.id)
        query_params = {
            'Public': True
        }

        res = self.client.delete(url, query_params)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_list_with_entries(self):
        """Test deleting a list with entries."""
        list1 = create_list(user=self.user)
        album1 = create_album()
        entry1 = create_entry(album1, list1)

        url = specific_list_url(list1.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(List.objects.filter(id=list1.id).exists())
        self.assertFalse(Entry.objects.filter(id=entry1.id).exists())
        self.assertTrue(Album.objects.filter(id=album1.id).exists())

    def test_patch_list(self):
        """Test patching a list"""
        list1 = create_list(user=self.user)
        album1 = create_album()
        album2 = create_album(title='Album 2')
        create_entry(album1, list1)
        new_description = 'New Description'
        new_label = 'New List Label'

        payload = {
            'label': new_label,
            'albums': [
                {
                    'album': album2.id,
                    'description': new_description,
                }
            ]
        }

        url = specific_list_url(list1.id)
        res = self.client.patch(url, payload, format='json')
        updated_list = List.objects.get(id=list1.id)
        updated_list.albums.all()[0].id
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(album2.id, updated_list.albums.all()[0].id)
        self.assertEqual(new_description, updated_list.entries.all()[0].description)
        self.assertEqual(new_label, updated_list.label)

    def test_delete_list_with_entries(self):
        """Test deleting a list with entries"""
        list1 = create_list(user=self.user)
        album1 = create_album()
        entry1 = create_entry(album1, list1)

        url = specific_list_url(list1.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Entry.objects.filter(id=entry1.id).exists())
        self.assertTrue(Album.objects.filter(id=album1.id).exists())
        self.assertFalse(List.objects.filter(id=list1.id).exists())