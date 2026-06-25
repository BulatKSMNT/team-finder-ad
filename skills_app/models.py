from django.db import models

from team_finder.constants import SKILL_NAME_MAX_LENGTH

class Skill(models.Model):
    name = models.CharField("Название навыка",
                            max_length=SKILL_NAME_MAX_LENGTH,
                            unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self):
        return self.name
