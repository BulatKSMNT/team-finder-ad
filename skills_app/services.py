import json

from .models import Skill
from team_finder.constants import SKILL_NAME_MAX_LENGTH


def get_request_data(request):
    content_type = request.content_type or ""

    if content_type.startswith("application/json"):
        try:
            return json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return None

    return request.POST


def is_skill_name_too_long(skill_name):
    return len(skill_name) > SKILL_NAME_MAX_LENGTH


def get_existing_skill_by_name(skill_name):
    return Skill.objects.filter(name__iexact=skill_name).first()
