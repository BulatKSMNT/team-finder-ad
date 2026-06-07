from django.urls import path
from . import views
app_name = 'projects'
urlpatterns = [
    path('', views.show_all_projects, name='main_page'),
    path('list', views.show_all_projects, name='main_page'),
]
