from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import StudentRegistrationForm, EditProfileForm
from .models import SystemUser
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


def register_student(request):
    if request.method == 'POST':
        form_data = StudentRegistrationForm(request.POST)
        if form_data.is_valid():
            new_student = form_data.save()
            # login user immediately after registration
            login(request, new_student)
            return redirect('main_page')
    else:
        # just show empty form if GET request
        form_data = StudentRegistrationForm()

    return render(request, 'users/register.html', {'form': form_data})


def login_student(request):
    if request.method == 'POST':
        form_data = AuthenticationForm(request, data=request.POST)
        if form_data.is_valid():
            found_user = form_data.get_user()
            login(request, found_user)
            return redirect('main_page')
    else:
        form_data = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form_data})


def logout_student(request):
    logout(request)
    return redirect('main_page')


def users_directory(request):
    # show all users from newest to oldest
    all_users = SystemUser.objects.all().order_by('-date_joined')

    # 12 profiles per page
    page_maker = Paginator(all_users, 12)
    page_num = request.GET.get('page')
    paged_users = page_maker.get_page(page_num)

    return render(request, 'users/participants.html', {'users_list': paged_users})


def view_profile(request, user_id):
    profile_owner = get_object_or_404(SystemUser, id=user_id)
    user_projects = profile_owner.my_created_projects.all()

    context_data = {
        'profile_owner': profile_owner,
        'projects': user_projects
    }
    # ИСПРАВИЛ НАЗВАНИЕ ШАБЛОНА ТУТ:
    return render(request, 'users/user-details.html', context_data)


@login_required
def edit_my_profile(request):
    if request.method == 'POST':
        form_data = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form_data.is_valid():
            form_data.save()
            return redirect('user_profile', user_id=request.user.id)
    else:
        form_data = EditProfileForm(instance=request.user)

    # ИСПРАВИЛ НАЗВАНИЕ ШАБЛОНА ТУТ:
    return render(request, 'users/edit_profile.html', {'form': form_data})


@login_required
def change_my_password(request):
    # Logic for changing user password
    if request.method == 'POST':
        form_data = PasswordChangeForm(request.user, request.POST)
        if form_data.is_valid():
            user = form_data.save()
            # update session so user is not logged out after password change
            update_session_auth_hash(request, user)
            return redirect('user_profile', user_id=request.user.id)
    else:
        form_data = PasswordChangeForm(request.user)

    return render(request, 'users/change_password.html', {'form': form_data})