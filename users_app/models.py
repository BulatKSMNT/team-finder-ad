import hashlib
import io

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email обязателен.")

        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь "
                             "должен иметь is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email", unique=True)

    name = models.CharField("Имя", max_length=124)
    surname = models.CharField("Фамилия", max_length=124)

    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True)

    phone = models.CharField(
        "Телефон",
        max_length=12,
        unique=True,
        blank=True,
        null=True,
    )

    github_url = models.URLField("GitHub", blank=True)
    about = models.TextField("О себе", max_length=256, blank=True)

    is_active = models.BooleanField("Активен", default=True)
    is_staff = models.BooleanField("Администратор", default=False)

    date_joined = models.DateTimeField("Дата регистрации",
                                       default=timezone.now)

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
        if self.phone == "":
            self.phone = None

        if not self.avatar:
            self._generate_initial_avatar()

        super().save(*args, **kwargs)

    def _generate_initial_avatar(self):
        letter_source = self.name or self.email or "U"
        letter = letter_source[0].upper()

        colors = [
            "#6D8EA0",
            "#7A9E7E",
            "#B08968",
            "#8E7DBE",
            "#6096BA",
            "#A98467",
        ]

        hash_value = int(hashlib.sha256(letter_source.
                                        encode("utf-8")).hexdigest(), 16)
        background_color = colors[hash_value % len(colors)]

        size = 256
        image = Image.new("RGB", (size, size), background_color)
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", 120)
        except OSError:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (size - text_width) / 2
        y = (size - text_height) / 2 - 10

        draw.text((x, y), letter, fill="white", font=font)

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")

        file_hash = hashlib.sha256((self.email or letter_source)
                                   .encode("utf-8")).hexdigest()[:16]
        self.avatar.save(
            f"generated_{file_hash}.png",
            ContentFile(buffer.getvalue()),
            save=False,
        )
