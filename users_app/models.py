from django.db import models
from django.contrib.auth.models import AbstractUser

class SystemUser(AbstractUser):
    avatar_image = models.ImageField(upload_to='avatars/', null=True, blank=True)
    short_about_me = models.TextField(max_length=500, blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    git_profile = models.URLField(max_length=200, blank=True, null=True)


    groups = models.ManyToManyField(
        'auth.Group',
        related_name='system_users_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='system_users_permissions',
        blank=True
    )

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
