from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from projects_app.models import Project
from projects_app.services import can_manage_project
from team_finder.constants import (
    SKILL_NAME_MAX_LENGTH,
    SKILLS_SUGGESTIONS_LIMIT,
)

from .models import Skill
from .services import (
    get_existing_skill_by_name,
    get_request_data,
    is_skill_name_too_long,
)


@require_GET
def search_skills(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse([], safe=False)

    skills = (
        Skill.objects
        .filter(name__istartswith=query)
        .order_by("name")
        .values("id", "name")[:SKILLS_SUGGESTIONS_LIMIT]
    )

    return JsonResponse(list(skills), safe=False)


@login_required
@require_POST
def add_skill_to_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if not can_manage_project(request.user, project):
        return JsonResponse(
            {"error": "Недостаточно прав."},
            status=HTTPStatus.FORBIDDEN,
        )

    data = get_request_data(request)

    if data is None:
        return JsonResponse(
            {"error": "Некорректный JSON."},
            status=HTTPStatus.BAD_REQUEST,
        )

    skill_id = data.get("skill_id")
    skill_name = (data.get("name") or "").strip()

    created = False

    if skill_id:
        skill = get_object_or_404(Skill, id=skill_id)
    elif skill_name:
        if is_skill_name_too_long(skill_name):
            return JsonResponse(
                {
                    "error": (
                        "Название навыка не должно быть длиннее "
                        f"{SKILL_NAME_MAX_LENGTH} символов."
                    )
                },
                status=HTTPStatus.BAD_REQUEST,
            )

        skill = get_existing_skill_by_name(skill_name)

        if skill is None:
            skill = Skill.objects.create(name=skill_name)
            created = True
    else:
        return JsonResponse(
            {"error": "Передайте skill_id или name."},
            status=HTTPStatus.BAD_REQUEST,
        )

    already_added = project.skills.filter(id=skill.id).exists()

    if not already_added:
        project.skills.add(skill)

    return JsonResponse(
        {
            "skill_id": skill.id,
            "created": created,
            "added": not already_added,
        }
    )


@login_required
@require_POST
def remove_skill_from_project(request, project_id, skill_id):
    project = get_object_or_404(Project, id=project_id)

    if not can_manage_project(request.user, project):
        return JsonResponse(
            {"error": "Недостаточно прав."},
            status=HTTPStatus.FORBIDDEN,
        )

    skill = get_object_or_404(Skill, id=skill_id)
    skill_is_added = project.skills.filter(id=skill.id).exists()

    if not skill_is_added:
        return JsonResponse(
            {"error": "Этот навык не добавлен к проекту."},
            status=HTTPStatus.BAD_REQUEST,
        )

    project.skills.remove(skill)

    return JsonResponse(
        {
            "status": "ok",
            "removed": True,
        }
    )
