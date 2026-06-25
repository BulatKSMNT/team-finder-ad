from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from team_finder.constants import (
    AVATAR_UPLOAD_TO,
    GITHUB_URL_MAX_LENGTH,
    USER_ABOUT_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
    USER_SURNAME_MAX_LENGTH,
)

from .managers import UserManager
from .services import generate_initial_avatar_content, normalize_phone


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email", unique=True)

    name = models.CharField(
        "Имя",
        max_length=USER_NAME_MAX_LENGTH,
    )
    surname = models.CharField(
        "Фамилия",
        max_length=USER_SURNAME_MAX_LENGTH,
    )

    avatar = models.ImageField(
        "Аватар",
        upload_to=AVATAR_UPLOAD_TO,
        blank=True,
    )

    phone = models.CharField(
        "Телефон",
        max_length=USER_PHONE_MAX_LENGTH,
        unique=True,
        blank=True,
        null=True,
    )

    github_url = models.URLField(
        "GitHub",
        max_length=GITHUB_URL_MAX_LENGTH,
        blank=True,
    )

    about = models.TextField(
        "О себе",
        max_length=USER_ABOUT_MAX_LENGTH,
        blank=True,
    )

    is_active = models.BooleanField("Активен", default=True)
    is_staff = models.BooleanField("Администратор", default=False)

    date_joined = models.DateTimeField(
        "Дата регистрации",
        default=timezone.now,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    class Meta:
        ordering = ["id"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.surname} {self.name}".strip() or self.email

    def get_full_name(self):
        return f"{self.name} {self.surname}".strip()

    def get_short_name(self):
        return self.name

    def save(self, *args, **kwargs):
        self.phone = normalize_phone(self.phone)

        if not self.avatar:
            filename, content = generate_initial_avatar_content(
                email=self.email,
                name=self.name,
            )
            self.avatar.save(filename, content, save=False)

        super().save(*args, **kwargs)
