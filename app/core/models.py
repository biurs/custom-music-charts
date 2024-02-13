"""
Database models.
"""
from django.conf import settings
from django.db import models
from django.db.models import Q, F
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save, and return a new user."""
        if not email:
            raise ValueError('User must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Artist(models.Model):
    """Artist object."""
    name = models.CharField(max_length=255, unique=True)
    origin_country = models.CharField(max_length=3, blank=True)
    start_year = models.IntegerField(null=True, blank=True)
    end_year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(
                    end_year__gte=models.F('start_year')
                ),
                name='end_year_gte_start_year',
            )
        ]


class Album(models.Model):
    """Album object."""
    title = models.CharField(max_length=255)
    artist = models.ManyToManyField('Artist', related_name='artists_albums')
    release_date = models.DateField()
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2)
    rating_count = models.IntegerField()
    link = models.CharField(max_length=255, blank=True)
    primary_genres = models.ManyToManyField('Genre', related_name='primary_albums', blank=True)
    secondary_genres = models.ManyToManyField('Genre', related_name='secondary_albums', blank=True)
    tags = models.ManyToManyField('Tag', related_name='tag_albums', blank=True)

    def __str__(self):
        return self.title


class Genre(models.Model):
    """Genres for albums."""
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Tags for albums."""
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Entry(models.Model):
    """Each Item entry on a list"""
    album = models.ForeignKey('Album', on_delete=models.CASCADE)
    owner_list = models.ForeignKey('List', related_name='entries', on_delete=models.CASCADE)
    description = models.CharField(max_length=4096, blank=True)


class List(models.Model):
    """Custom Lists"""
    label = models.CharField(max_length=255)
    user = models.ForeignKey('User', related_name='user_lists', on_delete=models.CASCADE)
    albums = models.ManyToManyField(Album, through='Entry')
    public = models.BooleanField(default=False)