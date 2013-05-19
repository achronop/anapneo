from django.db import models
from django.contrib.auth.models import User
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator

from datetime import datetime


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    email = models.EmailField(max_length=100)
    display_name = models.CharField(max_length=50, unique=True,
        validators=[
            RegexValidator(regex=r'("")|(^[a-z0-9_]+$)',
                           message='Please only a-z characters, numbers and '
                                   'underscores.')])
    first_name = models.CharField(max_length=100, blank=True, verbose_name="First Name")
    last_name = models.CharField(max_length=100, blank=True, verbose_name="Last Name")
    city = models.CharField(max_length=40, blank=True, verbose_name="City")
    country = models.CharField(max_length=40, blank=True, verbose_name="Country")
    lat = models.CharField(max_length=20, blank=True, verbose_name="Latitude")
    lon = models.CharField(max_length=20, blank=True, verbose_name="Longitude")


class Neo(models.Model):
    user = models.ForeignKey(User)
    no = models.IntegerField(verbose_name="ID", unique=True)
    score = models.PositiveIntegerField(verbose_name="Score (%)")
    observation_date = models.DateTimeField(verbose_name="Observation Date")
    position_ra = models.CharField(max_length=100, verbose_name="R.A.")
    position_dec = models.CharField(max_length=100, verbose_name="Declination")
    magnitude = models.CharField(max_length=100, verbose_name="Magnitude")
    created = models.DateTimeField(max_length=100, default=datetime.now)
    updated =  models.DateTimeField(max_length=100, verbose_name="Latest Observation")
    note = models.TextField(max_length=300, verbose_name="Notes", blank=True)
    num_obs = models.PositiveIntegerField(verbose_name="Number of Observations")
    arc = models.FloatField(verbose_name="Arc", validators=[MinValueValidator(0.0)])
    nominal_h = models.FloatField(verbose_name="Nominal H", blank=True, validators=[MinValueValidator(0.0)])
    image = models.ImageField(upload_to='.', verbose_name="Image", blank=True)


class Feedback(models.Model):
    user = models.ForeignKey(User)
    neo = models.ForeignKey(Neo)
    vote = models.IntegerField()
