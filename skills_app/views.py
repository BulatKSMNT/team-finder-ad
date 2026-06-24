import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from projects_app.models import Project
from .models import Skill


def can_manage_project(user, project):
    return (
        user.is_authenticated
        and (
            project.owner_id == user.id
            or user.is_staff
            or user.is_superuser
            or user.has_perm("projects_app.change_project")
        )
    )


def get_request_data(request):
    content_type = request.headers.get("content-type", "")

    if content_type.startswith("application/json"):
        try:
            return json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return None

    return request.POST


@require_GET
def search_skills(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse([], safe=False)

    skills = (
        Skill.objects
        .filter(name__istartswith=query)
        .order_by("name")
        .values("id", "name")[:10]
    )

    return JsonResponse(list(skills), safe=False)


@login_required
@require_POST
def add_skill_to_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if not can_manage_project(request.user, project):
        return JsonResponse({"error": "Недостаточно прав."}, status=403)

    data = get_request_data(request)

    if data is None:
        return JsonResponse({"error": "Некорректный JSON."}, status=400)

    skill_id = data.get("skill_id")
    skill_name = (data.get("name") or "").strip()

    created = False

    if skill_id:
        skill = get_object_or_404(Skill, id=skill_id)
    elif skill_name:
        if len(skill_name) > 124:
            return JsonResponse(
                {"error": "Название навыка не "
                          "должно быть длиннее 124 символов."},
                status=400,
            )

        existing_skill = Skill.objects.filter(name__iexact=skill_name).first()

        if existing_skill:
            skill = existing_skill
        else:
            skill = Skill.objects.create(name=skill_name)
            created = True
    else:
        return JsonResponse(
            {"error": "Передайте skill_id или name."},
            status=400,
        )

    already_added = project.skills.filter(id=skill.id).exists()

    if already_added:
        added = False
    else:
        project.skills.add(skill)
        added = True

    return JsonResponse(
        {
            "skill_id": skill.id,
            "created": created,
            "added": added,
        }
    )


@login_required
@require_POST
def remove_skill_from_project(request, project_id, skill_id):
    project = get_object_or_404(Project, id=project_id)

    if not can_manage_project(request.user, project):
        return JsonResponse({"error": "Недостаточно прав."}, status=403)

    skill = get_object_or_404(Skill, id=skill_id)

    if not project.skills.filter(id=skill.id).exists():
        return JsonResponse(
            {"error": "Этот навык не добавлен к проекту."},
            status=400,
        )

    project.skills.remove(skill)

    return JsonResponse(
        {
            "status": "ok",
            "removed": True,
        }
    )
