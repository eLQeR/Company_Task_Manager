from django import forms
from django.contrib.auth.forms import UserCreationForm

from task_manager.models import Task, Worker


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = Worker
        fields = [
            "username", "email", "first_name",
            "last_name", "password1", "password2"
        ]


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = [
            "username", "email", "first_name", "last_name",
            "avatar", "linkedin_url", "github_url",
            "instagram_url", "telegram_url"
        ]


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            "name", "description", "priority",
            "task_type", "task_image", "assignees"
        )
