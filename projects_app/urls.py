from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("list/", views.show_all_projects, name="main_page"),
    path("create-project/", views.create_project, name="create_project"),

    path("<int:project_id>/", views.view_project, name="project_details"),
    path("<int:project_id>/edit/", views.edit_project, name="edit_project"),
    path("<int:project_id>/complete/", views.complete_project,
         name="complete_project"),

    path(
        "<int:project_id>/toggle-participate",
        views.toggle_participate,
        name="toggle_participate",
    ),
    path(
        "<int:project_id>/toggle-participate/",
        views.toggle_participate,
    ),
]
