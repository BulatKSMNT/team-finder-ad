from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import SystemUser

class StudentRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = SystemUser
        fields = ('username', 'first_name', 'last_name', 'email')

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = SystemUser
        fields = ('first_name', 'last_name', 'avatar_image', 'short_about_me', 'contact_phone', 'git_profile')
