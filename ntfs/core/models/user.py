#!/usr/bin/env python
"""base user model class defination
"""
from django.contrib.auth.base_user import (
    AbstractBaseUser,
    BaseUserManager,
)
from django.contrib.auth.models import Group, PermissionsMixin
from django.db import models
import uuid
from knox.models import AuthToken
from django.utils import timezone
import datetime
from services.utils import Cache

cache = Cache()


class UserManager(BaseUserManager):
    """user manager class defination

    Attributes
    ----------


    Methods
    -------
        - create_user()

        - create_superuser()
    """

    def create_user(self, email, password=None) -> AbstractBaseUser:
        """creates and saves user when called.

        Parameters
        ----------
            - email: str

                email address

            - phone_no: str

                phone number

        Returns
        -------
            User
        """

        if not email:
            raise ValueError("User must have a valid email")

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password=None) -> AbstractBaseUser:
        """creates a superuser
        params:
            email [str]: email address to use
            password [str]: password to use

        returns:
            The base user
        """
        user = self.create_user(
            email=email,
            password=password,
        )

        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User model class definition

    Attributes
    ----------
        - email: str, required

            user email address

        - phone_no: str, optional

            user phone number

        - user_id: uuid.UUID, required

            auto generated unique user id

        - groups: list, optional

            groups a user belongs to

        - date_joined: datetime.datetime, required

            the date and time the user joined

        - last_login: datetime.datetime, auto

            timestamp of the list time the user logged in

        - is_active: bool,

            is the user verified and active

                - default: False

        - is_admin: bool

            is the user an admin

                - default: False

        - USERNAME_FIELD: str

            field to use as USERNAME when loggin in

        - REQUIRED_FIELDS: list

            a list of required fields when creating new user

        - objects: UserManager

            The User Manager Class of this model

    Methods
    -------
        - is_staff():

            checks if is_admin attribute of user is True or False

    """

    GENDER_TYPE = [
        ("F", "Female"),
        ("M", "Male"),
        ("NB", "None Binary"),
    ]

    username = models.CharField(
        "Username", max_length=16, unique=True, blank=True, null=True
    )
    email = models.EmailField("Email Address", unique=True, blank=True)
    phone_no = models.CharField(
        "Phone Number", max_length=15, unique=True, blank=True, null=True
    )
    user_id = models.UUIDField(
        "User ID", primary_key=True, default=uuid.uuid4, unique=True
    )
    groups = models.ManyToManyField(Group, blank=True, related_name="user_groups")
    roles = models.ManyToManyField("Role", blank=True, related_name="users")
    gender = models.CharField("Gender", max_length=2, choices=GENDER_TYPE, blank=True)
    date_joined = models.DateTimeField("Date Joined", auto_now_add=True)
    last_login = models.DateTimeField("Last Login", auto_now=True)
    is_active = models.BooleanField("Is Active", default=True)
    is_admin = models.BooleanField("Is Admin", default=False)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        cache.invalidate("users")
        cache.invalidate_many("users")
        return super().save(*args, **kwargs)

    @property
    def is_staff(self) -> bool:
        """Is user a staff or member

        Parameters
        ----------
            - self: the User instance itself

        Returns
        -------
            bool
        """
        return self.is_admin

    def is_superuser(self):
        """ """
        return self.is_admin

    @property
    def id(self) -> uuid.UUID:
        """get user ID"""
        return self.user_id


class RefreshToken(models.Model):
    auth_token = models.OneToOneField(AuthToken, on_delete=models.SET_NULL, blank=True, null=True)
    refresh_token = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.refresh_token

    @property
    def is_expired(self):
        return self.created < (timezone.now() - datetime.timedelta(days=5))
