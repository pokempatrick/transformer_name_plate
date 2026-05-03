from django.apps import apps
from django.db import models
from helpers.models import TrakingModel
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import (
    PermissionsMixin, UserManager, AbstractBaseUser)
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
import os
import jwt
import uuid
from django.contrib.auth.hashers import make_password
from datetime import date, datetime, timedelta
from helpers.validator import validate_contact, validate_file_size
from helpers.constant import REGION_TYPE, ROLES
from django.core.validators import FileExtensionValidator

from authentification.validators import validate_region


class MyUserManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError("The given username must be set")

        if not email:
            raise ValueError("The given email must be set")

        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password='Bonjour2021', **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password="Bonjour2021", **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)


class User(TrakingModel, AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """
    def get_file_path(instance, filename):
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        return os.path.join('documents/', filename)

    def region_default():
        return ["DRD"]

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(
        _("first name"), max_length=150, blank=False, default="John",)
    last_name = models.CharField(
        _("last name"), max_length=150, blank=False, default="Does")
    role_name = models.CharField(
        _("role name"), max_length=150, choices=ROLES, default="ROLE_ANONYME", blank=False)
    email = models.EmailField(_("email address"), blank=False, unique=True)
    region = models.JSONField(
        max_length=10, default=region_default, validators=[validate_region,
                                                           ])

    added_by = models.CharField(
        max_length=150, blank=True)

    updated_by = models.CharField(
        max_length=150, blank=True)

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date_joined"), default=timezone.now)
    email_verified = models.BooleanField(
        _("email_verified"),
        default=False,
        help_text=_(
            "Designates whether this user email is verified. "
        ),
    )
    limited_access_date = models.DateField(
        default=date.today()+timedelta(days=90)
    )

    occupation = models.TextField()

    image = models.ImageField(
        upload_to=get_file_path,
        max_length=100, blank=True, null=True,
        validators=[validate_file_size,
                    FileExtensionValidator(['jpg', 'png', 'jpeg'])]
    )

    first_contact = models.IntegerField(blank=True, null=True,
                                        validators=[validate_contact,
                                                    ])
    second_contact = models.IntegerField(blank=True, null=True,
                                         validators=[validate_contact,
                                                     ])

    objects = MyUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    @property
    def token(self):
        token = jwt.encode(
            {'username': self.username,
             'email': self.email,
             'exp': datetime.utcnow()+timedelta(hours=24)
             }, settings.SECRET_KEY, algorithm='HS256')
        return token
