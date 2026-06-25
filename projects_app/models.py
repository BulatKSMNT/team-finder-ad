from django.conf import settings
from django.db import models
from django.urls import reverse

from team_finder.constants import (
    GITHUB_URL_MAX_LENGTH,
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_STATUS_CHOICES,
    PROJECT_STATUS_MAX_LENGTH,
    PROJECT_STATUS_OPEN,
)


class Project(models.Model):
    STATUS_CHOICES = PROJECT_STATUS_CHOICES

    name = models.CharField(
        "Название проекта",
        max_length=PROJECT_NAME_MAX_LENGTH,
    )
    description = models.TextField(
        "Описание проекта",
        blank=True,
        default="",
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Автор",
    )

    created_at = models.DateTimeField(
        "Дата создания",
        auto_now_add=True,
    )

    github_url = models.URLField(
        "GitHub",
        max_length=GITHUB_URL_MAX_LENGTH,
        blank=True,
        default="",
    )

    status = models.CharField(
        "Статус",
        max_length=PROJECT_STATUS_MAX_LENGTH,
        choices=STATUS_CHOICES,
        default=PROJECT_STATUS_OPEN,
    )

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name="Участники",
    )

    skills = models.ManyToManyField(
        "skills_app.Skill",
        related_name="projects",
        blank=True,
        verbose_name="Необходимые навыки",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "projects:project_details",
            kwargs={"project_id": self.pk},
        )
