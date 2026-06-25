from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from team_finder.constants import USERS_PER_PAGE
from team_finder.services import paginate_queryset

from .forms import EditProfileForm, LoginForm, RegistrationForm
from .models import User


def register_user(request):
    form = RegistrationForm(request.POST or None)

    if form.is_valid():
        form.save()

        return redirect("users:login")

    return render(request, "users/register.html", {"form": form})


def login_user(request):
    next_url = request.POST.get("next") or request.GET.get("next")
    form = LoginForm(request, data=request.POST or None)

    if form.is_valid():
        login(request, form.get_user())

        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
        ):
            return redirect(next_url)

        return redirect("projects:main_page")

    return render(
        request,
        "users/login.html",
        {
            "form": form,
            "next": next_url,
        },
    )


def logout_user(request):
    logout(request)

    return redirect("projects:main_page")


def users_directory(request):
    participants = User.objects.filter(is_active=True).order_by("-date_joined")
    participants_page = paginate_queryset(
        request=request,
        queryset=participants,
        per_page=USERS_PER_PAGE,
    )

    return render(
        request,
        "users/participants.html",
        {
            "participants": participants_page,
        },
    )


def view_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id, is_active=True)
    projects = (
        profile_user
        .owned_projects
        .all()
        .prefetch_related("participants", "skills")
    )

    return render(
        request,
        "users/user-details.html",
        {
            "user": profile_user,
            "profile_user": profile_user,
            "projects": projects,
        },
    )


@login_required
def edit_profile(request):
    form = EditProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )

    if form.is_valid():
        form.save()

        return redirect("users:profile", user_id=request.user.id)

    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    form = PasswordChangeForm(
        request.user,
        data=request.POST or None,
    )

    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)

        return redirect("users:profile", user_id=request.user.id)

    return render(request, "users/change_password.html", {"form": form})
