from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from skills_app.models import Skill
from .forms import ProjectForm
from .models import Project


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


def wants_json(request):
    return (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or request.content_type == "application/json"
        or "application/json" in request.headers.get("accept", "")
    )


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

    paginator = Paginator(projects, 12)
    page_number = request.GET.get("page")
    projects_page = paginator.get_page(page_number)

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

    is_participant = False

    if request.user.is_authenticated:
        is_participant = (project.
                          participants.
                          filter(id=request.user.id).exists())

    return render(
        request,
        "projects/project-details.html",
        {
            "project": project,
            "skills": project.skills.all(),
            "participants": project.participants.all(),
            "is_participant": is_participant,
            "can_manage_project": can_manage_project(request.user, project),
        },
    )


@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)

            return redirect("projects:project_details", project_id=project.id)
    else:
        form = ProjectForm()

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

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()
            return redirect("projects:project_details", project_id=project.id)
    else:
        form = ProjectForm(instance=project)

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
            status=403,
        )

    if project.status != "open":
        return JsonResponse(
            {
                "status": "error",
                "message": "Проект уже закрыт.",
                "project_status": project.status,
            },
            status=400,
        )

    project.status = "closed"
    project.save(update_fields=["status"])

    return JsonResponse(
        {
            "status": "ok",
            "project_status": "closed",
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
                status=400,
            )

        return redirect("projects:project_details", project_id=project.id)

    if project.status != "open":
        if wants_json(request):
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Нельзя присоединиться к закрытому проекту.",
                    "participating": False,
                },
                status=400,
            )

        return redirect("projects:project_details", project_id=project.id)

    if project.participants.filter(id=request.user.id).exists():
        project.participants.remove(request.user)
        participating = False
    else:
        project.participants.add(request.user)
        participating = True

    if wants_json(request):
        return JsonResponse(
            {
                "status": "ok",
                "participating": participating,
            }
        )

    return redirect("projects:project_details", project_id=project.id)
