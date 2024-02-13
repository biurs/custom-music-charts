"""
Tests for album APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Album, Artist, Genre

from album.serializers import AlbumSerializer

from datetime import date


ALBUMS_URL = reverse('album:album-list')


def specific_album_url(album_id):
    """Create and return a specific album URL."""
    return reverse('album:album-detail', args=[album_id])


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


class PublicAlbumAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """"Test auth is required to call API."""
        res = self.client.get(ALBUMS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)


class PrivateAlbumApiTests(TestCase):
    """Test authenticated user API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_regular_user_retrieve_albums(self):
        """Test retrieving a list of albums as regular user."""
        create_album()
        create_album(title='Sample Album 2')

        res = self.client.get(ALBUMS_URL)

        albums = Album.objects.all().order_by('id')
        serializer = AlbumSerializer(albums, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    def test_regular_user_retrieve_albums_pagination(self):
        """Test retrieving a large list of albums as regular user."""
        for i in range(52):
            create_album(title=i)


        res1 = self.client.get(ALBUMS_URL)
        res2 = self.client.get(ALBUMS_URL, {'page':2})
        res3 = self.client.get(ALBUMS_URL, {'page':3})


        albums_page1 = Album.objects.all().order_by('id')[:25]
        albums_page2 = Album.objects.all().order_by('id')[25:50]
        albums_page3 = Album.objects.all().order_by('id')[50:52]

        serializer1 = AlbumSerializer(albums_page1, many=True)
        serializer2 = AlbumSerializer(albums_page2, many=True)
        serializer3 = AlbumSerializer(albums_page3, many=True)

        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        self.assertEqual(res1.data['results'], serializer1.data)
        self.assertEqual(res2.data['results'], serializer2.data)
        self.assertEqual(res3.data['results'], serializer3.data)


    def test_regular_user_create_album_fails(self):
        """Test creating an album as a regular user fails."""
        payload = {
            'title': 'Sample Album Title',
            'artist': [{'name': 'Sample Artist'}],
            'release_date': date.fromisoformat('2001-01-01'),
            'avg_rating': Decimal('1.00'),
            'rating_count': 1
        }
        res = self.client.post(ALBUMS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Album.objects.all().count(), 0)

    def test_regular_user_partial_update_album_fails(self):
        """Test partially updating an album as a regular user fails."""
        original_title = 'Original Title'
        original_rating_count = 1
        album = create_album(title=original_title, rating_count=original_rating_count)

        payload = {'rating_count': 2}
        url = specific_album_url(album.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        album.refresh_from_db()
        self.assertEqual(album.rating_count, original_rating_count)
        self.assertEqual(album.title, original_title)

    def test_regular_user_full_update_album_fails(self):
        """Test fully updating an album as a regular user fails."""
        album_dict = {
            'title': 'Sample Album',
            'release_date': date.fromisoformat('2000-01-01'),
            'avg_rating': Decimal('1.00'),
            'rating_count': 100,
        }
        album = create_album(**album_dict)

        payload = {
            'title': 'Sample Album 2',
            'artist': [{'name': 'Sample Artist 2'}],
            'release_date': date.fromisoformat('2000-02-02'),
            'avg_rating': Decimal('2.00'),
            'rating_count': 200,
        }
        url = specific_album_url(album.id)
        res = self.client.put(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        album.refresh_from_db()
        for k, v in album_dict.items():
            if k == 'artist':
                artist = Artist.objects.get(name=album['artist']['name'])
                self.assertEqual(getattr(album, k), artist)
            else:
                self.assertEqual(getattr(album, k), v)

    def test_regular_user_delete_album_fails(self):
        """Test deleting album as a regular user fails."""
        album = create_album()

        url = specific_album_url(album.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Album.objects.filter(id=album.id).exists())


class PrivateAlbumSuperuserApiTests(TestCase):
    """Test authenticated superuser API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            'user@example.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_albums(self):
        """Test retrieving a list of albums."""
        create_album()
        create_album(title='Sample Album 2')

        res = self.client.get(ALBUMS_URL)

        albums = Album.objects.all().order_by('id')
        serializer = AlbumSerializer(albums, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    def test_create_album_with_new_artist(self):
        """Test creating an album"""
        payload = {
            'title': 'Sample Album Title',
            'artist': [{'name': 'Sample Artist'}],
            'release_date': date.fromisoformat('2001-01-01'),
            'avg_rating': Decimal('1.00'),
            'rating_count': 1
        }
        res = self.client.post(ALBUMS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        album = Album.objects.get(id=res.data['id'])
        for k, v in payload.items():
            if k == 'artist':
                artist = Artist.objects.get(name=payload['artist'][0]['name'])
                self.assertIn(artist, album.artist.all())
            else:
                self.assertEqual(getattr(album, k), v)

    def test_create_album_with_existing_artist(self):
        """Test creating an album with an existing artist."""
        artist = create_artist(name='Sample Artist')
        payload = {
            'title': 'Sample Album',
            'artist': [{'name': 'Sample Artist'}],
            'release_date': date.fromisoformat('2000-01-01'),
            'avg_rating': Decimal('1.00'),
            'rating_count': 100,
        }
        res = self.client.post(ALBUMS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        artists = Artist.objects.all()
        self.assertEqual(artists.count(), 1)
        albums = Album.objects.all()
        self.assertEqual(albums.count(), 1)
        album = albums[0]
        self.assertIn(artist, album.artist.all())
        for artist in payload['artist']:
            self.assertTrue(
                Artist.objects.filter(
                name=artist['name']
                ).exists()
            )

    def test_create_album_with_no_artist_fail(self):
        """Test creating album with no artist fails."""
        payload = {
            'title': 'Sample Album',
            'release_date': date.fromisoformat('2000-01-01'),
            'avg_rating': Decimal('1.00'),
            'rating_count': 100,
        }
        res = self.client.post(ALBUMS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Album.objects.all().count(), 0)

    def test_create_album_multiple_artists(self):
        """Test creating an album with multiple artists."""
        payload = {
            'title': 'Sample Album',
            'artist': [{'name': 'Sample Artist'}, {'name': 'Sample Artist 2'}],
            'release_date': date.fromisoformat('2000-01-01'),
            'avg_rating': Decimal('1.00'),
            'rating_count': 100,
        }

        res = self.client.post(ALBUMS_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Artist.objects.all().count(), 2)

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
            'artist': [{'name': 'Sample Artist 2'}],
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
                artist = Artist.objects.get(name=payload['artist'][0]['name'])
                self.assertIn(artist, album.artist.all())
            else:
                self.assertEqual(getattr(album, k), v)

    def test_delete_album(self):
        """Test deleting an album."""
        album = create_album()

        url = specific_album_url(album.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Album.objects.filter(id=album.id).exists())

    def test_create_album_with_new_genres(self):
        """Test creating album with new genres."""
        payload = {
            'title': 'Sample Album Name',
            'artist': [{'name': 'Test Artist'}],
            'release_date': date.fromisoformat('2000-01-01'),
            'avg_rating': Decimal('1.00'),
            'rating_count': 10,
            'primary_genres': [{'name': 'Indie Rock'}, {'name': 'Post Rock'}],
            'secondary_genres': [{'name': 'Free Jazz'}, {'name': 'Harsh Noise'}],
        }
        res = self.client.post(ALBUMS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        albums = Album.objects.all()
        self.assertEqual(albums.count(), 1)
        album = albums[0]
        self.assertEqual(album.primary_genres.count(), 2)
        self.assertEqual(album.secondary_genres.count(), 2)
        for genre in payload['primary_genres'] + payload['secondary_genres']:
            exists_primary = album.primary_genres.filter(
                name=genre['name']
            ).exists()
            exists_secondary = album.secondary_genres.filter(
                name=genre['name']
            ).exists()
            self.assertTrue(exists_primary or exists_secondary)

    def test_create_album_with_existing_genres(self):
        """Test creating an album with existing genres."""
        genre1 = Genre.objects.create(name='Indie Rock')
        genre2 = Genre.objects.create(name='Free Jazz')
        payload = {
            'title': 'Sample Album Name',
            'artist': [{'name': 'Test Artist'}],
            'release_date': date.fromisoformat('2000-01-01'),
            'avg_rating': Decimal('1.00'),
            'rating_count': 10,
            'primary_genres': [{'name': 'Indie Rock'}, {'name': 'Post Rock'}],
            'secondary_genres': [{'name': 'Free Jazz'}, {'name': 'Harsh Noise'}],
        }

        res = self.client.post(ALBUMS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        albums = Album.objects.all()
        genres = Genre.objects.all()
        self.assertEqual(albums.count(), 1)
        album = albums[0]
        self.assertEqual(album.primary_genres.count(), 2)
        self.assertEqual(album.secondary_genres.count(), 2)
        self.assertEqual(genres.count(), 4)
        self.assertIn(genre1, album.primary_genres.all())
        self.assertIn(genre2, album.secondary_genres.all())
        for genre in payload['primary_genres'] + payload['secondary_genres']:
            exists_primary = album.primary_genres.filter(
                name=genre['name']
            ).exists()
            exists_secondary = album.secondary_genres.filter(
                name=genre['name']
            ).exists()
            self.assertTrue(exists_primary or exists_secondary)

    def test_create_genre_on_update(self):
        """Test creating genres when updating a recipe."""
        album = create_album()

        payload = {
            'primary_genres': [{'name': 'Indie Rock'}],
            'secondary_genres': [{'name': 'Dream Pop'}],
        }
        url = specific_album_url(album.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_genre1 = Genre.objects.get(name='Indie Rock')
        new_genre2 = Genre.objects.get(name='Dream Pop')
        self.assertIn(new_genre1, album.primary_genres.all())
        self.assertIn(new_genre2, album.secondary_genres.all())


    def test_assign_genre_on_update(self):
        """Test assigning an existing genre on update album."""
        genre1 = Genre.objects.create(name='Indie Rock')
        genre2 = Genre.objects.create(name='Free Jazz')
        album = create_album()
        album.primary_genres.add(genre1)
        album.secondary_genres.add(genre2)

        genre_added1 = Genre.objects.create(name='Black Metal')
        genre_added2 = Genre.objects.create(name='Dream Pop')
        payload = {
            'primary_genres': [{'name': 'Black Metal'}],
            'secondary_genres': [{'name': 'Dream Pop'}],
            }
        url = specific_album_url(album.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        album.refresh_from_db()
        self.assertIn(genre_added1, album.primary_genres.all())
        self.assertNotIn(genre1, album.primary_genres.all())
        self.assertIn(genre_added2, album.secondary_genres.all())
        self.assertNotIn(genre2, album.secondary_genres.all())\

    def test_clear_album_genres(self):
        """Test clearing an albums genres."""
        genre1 = Genre.objects.create(name='Indie Rock')
        genre2 = Genre.objects.create(name='Dream Pop')
        album = create_album()
        album.primary_genres.add(genre1)
        album.secondary_genres.add(genre2)

        payload = {'primary_genres': [], 'secondary_genres': []}
        url = specific_album_url(album.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(album.primary_genres.count(), 0)
        self.assertEqual(album.secondary_genres.count(), 0)