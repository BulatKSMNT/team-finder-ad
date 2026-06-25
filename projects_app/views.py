from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from skills_app.models import Skill
from team_finder.constants import (
    PROJECT_STATUS_CLOSED,
    PROJECT_STATUS_OPEN,
    PROJECTS_PER_PAGE,
)
from team_finder.services import paginate_queryset

from .forms import ProjectForm
from .models import Project
from .services import can_manage_project, is_project_participant, wants_json


def show_all_projects(request):
    projects = (
        Project.objects
        .select_related("owner")
        .prefetch_related("participants", "skills")
        .order_by("-created_at")
    )

    active_skill = request.GET.get("skill", "").strip()

    if active_skill:
        projects = projects.filter(skills__name=active_skill).distinct()

    projects_page = paginate_queryset(
        request=request,
        queryset=projects,
        per_page=PROJECTS_PER_PAGE,
    )

    all_skills = Skill.objects.all().order_by("name")

    return render(
        request,
        "projects/project_list.html",
        {
            "projects": projects_page,
            "all_skills": all_skills,
            "active_skill": active_skill,
        },
    )


def view_project(request, project_id):
    project = get_object_or_404(
        Project.objects
        .select_related("owner")
        .prefetch_related("participants", "skills"),
        id=project_id,
    )

    return render(
        request,
        "projects/project-details.html",
        {
            "project": project,
            "skills": project.skills.all(),
            "participants": project.participants.all(),
            "is_participant": is_project_participant(request.user, project),
            "can_manage_project": can_manage_project(request.user, project),
        },
    )


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)

    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)

        return redirect("projects:project_details", project_id=project.id)

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": False,
        },
    )


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if not can_manage_project(request.user, project):
        return HttpResponseForbidden("Вы не можете редактировать этот проект.")

    form = ProjectForm(request.POST or None, instance=project)

    if form.is_valid():
        form.save()

        return redirect("projects:project_details", project_id=project.id)

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": True,
            "project": project,
        },
    )


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if not can_manage_project(request.user, project):
        return JsonResponse(
            {
                "status": "error",
                "message": "Недостаточно прав.",
                "project_status": project.status,
            },
            status=HTTPStatus.FORBIDDEN,
        )

    if project.status != PROJECT_STATUS_OPEN:
        return JsonResponse(
            {
                "status": "error",
                "message": "Проект уже закрыт.",
                "project_status": project.status,
            },
            status=HTTPStatus.BAD_REQUEST,
        )

    project.status = PROJECT_STATUS_CLOSED
    project.save(update_fields=["status"])

    return JsonResponse(
        {
            "status": "ok",
            "project_status": PROJECT_STATUS_CLOSED,
        }
    )


@login_required
@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner_id == request.user.id:
        if wants_json(request):
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Автор уже является участником проекта.",
                    "participating": True,
                },
                status=HTTPStatus.BAD_REQUEST,
            )

        return redirect("projects:project_details", project_id=project.id)

    if project.status != PROJECT_STATUS_OPEN:
        if wants_json(request):
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Нельзя присоединиться к закрытому проекту.",
                    "participating": False,
                },
                status=HTTPStatus.BAD_REQUEST,
            )

        return redirect("projects:project_details", project_id=project.id)

    if is_participating := project.participants.filter(id=request.user.id).exists():
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)

    participating = not is_participating

    if wants_json(request):
        return JsonResponse(
            {
                "status": "ok",
                "participating": participating,
            }
        )

    return redirect("projects:project_details", project_id=project.id)
