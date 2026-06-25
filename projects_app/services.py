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
    content_type = (request.content_type or "").lower()
    accept_header = request.headers.get("accept", "").lower()

    return (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or content_type == "application/json"
        or "application/json" in accept_header
    )


def is_project_participant(user, project):
    if not user.is_authenticated:
        return False

    return project.participants.filter(id=user.id).exists()
