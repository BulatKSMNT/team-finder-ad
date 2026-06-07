from django.db import models
from django.conf import settings
from skills_app.models import ProjectSkill


class IdeaProject(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'Open for participants'),
        ('CLOSED', 'Closed / Finished'),
    )

    project_title = models.CharField(max_length=150)
    project_description = models.TextField()

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='my_created_projects'
    )

    date_published = models.DateTimeField(auto_now_add=True)
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')

    joined_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='participating_in',
        blank=True
    )

    required_skills = models.ManyToManyField(
        ProjectSkill,
        related_name='projects_with_this_skill',
        blank=True
    )

    def __str__(self):
        return self.project_title

    class Meta:
        ordering = ['-date_published']
