from django.urls import path
from . import views
app_name = 'users'
urlpatterns = [
    path('list/', views.users_directory, name='users_list'),
    path('profile/<int:user_id>/', views.view_profile, name='user_profile'),
    path('register/', views.register_student, name='register'),
    path('login/', views.login_student, name='login'),
    path('logout/', views.logout_student, name='logout'),
    path('edit/', views.edit_my_profile, name='edit_profile'),
    path('password/', views.change_my_password, name='change_password'),
]
