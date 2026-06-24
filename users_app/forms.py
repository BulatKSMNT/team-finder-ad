import re
from urllib.parse import urlparse

from django import forms
from django.contrib.auth import authenticate

from .models import User


PHONE_RE = re.compile(r"^(8\d{10}|\+7\d{10})$")


def normalize_phone(phone):
    phone = phone.strip()

    if phone.startswith("8"):
        return "+7" + phone[1:]

    return phone


def validate_github_url(value):
    if not value:
        return value

    parsed = urlparse(value)
    host = parsed.netloc.lower()

    if host not in ("github.com", "www.github.com"):
        raise forms.ValidationError("Ссылка должна вести на GitHub.")

    return value


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Email",
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Пользователь "
                                        "с таким email уже существует.")

        return email

    def save(self, commit=True):
        user = User(
            email=self.cleaned_data["email"].strip().lower(),
            name=self.cleaned_data["name"].strip(),
            surname=self.cleaned_data["surname"].strip(),
        )
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

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


class EditProfileForm(forms.ModelForm):
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
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Email",
            "avatar": "Аватар",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "GitHub",
        }

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
            raise forms.ValidationError("Пользователь с таким "
                                        "email уже существует.")

        return email

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()

        if not PHONE_RE.match(phone):
            raise forms.ValidationError(
                "Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX."
            )

        normalized_phone = normalize_phone(phone)
        alternative_phone = "8" + normalized_phone[2:]

        phone_exists = (
            User.objects
            .filter(phone__in=[normalized_phone, alternative_phone])
            .exclude(pk=self.instance.pk)
            .exists()
        )

        if phone_exists:
            raise forms.ValidationError("Пользователь с таким "
                                        "телефоном уже существует.")

        return normalized_phone

    def clean_github_url(self):
        return validate_github_url(self.cleaned_data.get("github_url", ""))
