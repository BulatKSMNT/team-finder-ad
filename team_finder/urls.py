from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", RedirectView.as_view(url="/projects/list/", permanent=False)),
    path("project/list/", RedirectView.as_view(url="/projects/list/",
                                               permanent=False)),

    path("projects/", include("skills_app.urls")),
    path("projects/", include("projects_app.urls")),
    path("users/", include("users_app.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
