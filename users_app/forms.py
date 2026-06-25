import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from team_finder.constants import PHONE_PATTERN
from team_finder.form_mixins import GithubUrlValidationMixin

from .models import User
from .services import get_phone_uniqueness_variants, normalize_phone


PHONE_RE = re.compile(PHONE_PATTERN)


class AdminUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Повторите пароль",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = (
            "email",
            "name",
            "surname",
            "is_staff",
            "is_active",
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")

        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].strip().lower()
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

        return user


class AdminUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label="Пароль")

    class Meta:
        model = User
        fields = "__all__"


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].strip().lower()
        user.name = self.cleaned_data["name"].strip()
        user.surname = self.cleaned_data["surname"].strip()
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None

        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            email = email.strip().lower()
            self.user = authenticate(
                self.request,
                username=email,
                password=password,
            )

            if self.user is None:
                raise forms.ValidationError("Неверный имейл или пароль.")

        return cleaned_data

    def get_user(self):
        return self.user


class EditProfileForm(GithubUrlValidationMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "name",
            "surname",
            "email",
            "avatar",
            "about",
            "phone",
            "github_url",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["phone"].required = True
        self.fields["avatar"].required = False

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        email_exists = (
            User.objects
            .filter(email__iexact=email)
            .exclude(pk=self.instance.pk)
            .exists()
        )

        if email_exists:
            raise forms.ValidationError("Пользователь с таким email уже существует.")

        return email

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()

        if not PHONE_RE.match(phone):
            raise forms.ValidationError(
                "Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX."
            )

        normalized_phone = normalize_phone(phone)
        phone_variants = get_phone_uniqueness_variants(normalized_phone)

        phone_exists = (
            User.objects
            .filter(phone__in=phone_variants)
            .exclude(pk=self.instance.pk)
            .exists()
        )

        if phone_exists:
            raise forms.ValidationError(
                "Пользователь с таким телефоном уже существует."
            )

        return normalized_phone
