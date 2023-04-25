"""
Tests for models.
"""
from decimal import Decimal
from datetime import date

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from core import models


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@example.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that ceating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_album(self):
        """Test creating an album is successful."""
        artist = models.Artist.objects.create(name='Sample Artist Name')
        album = models.Album.objects.create(
            title='Sample Album Name',
            release_date=date.fromisoformat('2000-01-01'),
            avg_rating=Decimal('1.00'),
            rating_count=1_000,
        )

        self.assertEqual(str(album), album.title)

    def test_create_artist(self):
        """Test creating an artist is successful."""
        artist = models.Artist.objects.create(name='Sample Artist Name')

        self.assertEqual(str(artist), artist.name)

    def test_create_duplicate_artist_fails(self):
        """Test creating a duplicate artist fails."""
        name = 'Sample Artist Name'
        models.Artist.objects.create(name=name)

        with self.assertRaises(IntegrityError):
            models.Artist.objects.create(name=name)