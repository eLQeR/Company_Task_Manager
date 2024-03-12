from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from .models import Task, Worker


def index(request):
    return render(request, "index.html")


def tasks(request):
    tasks = Task.objects.filter(is_completed=False)
    context = {
        "tasks": tasks
    }
    return render(request, "tasks.html", context=context)


def my_tasks(request):
    tasks = Task.objects.filter()
    context = {
        "tasks": tasks
    }
    return render(request, "tasks.html", context=context)

class RegisterForm(UserCreationForm):
    class Meta:
        model = Worker
        fields = ["username", "email", "password1", "password2"]


class UserCreateView(generic.CreateView):
    model = Worker
    form_class = RegisterForm
    template_name = "registration/sign-up.html"
    success_url = reverse_lazy("task_manager:index")


def profile(request):
    return render(request, "registration/profile.html")