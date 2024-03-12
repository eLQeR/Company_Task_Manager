from django.shortcuts import render
from .models import Task


def index(request):
    return render(request, "index.html")


def tasks(request):
    tasks = Task.objects.filter(is_completed=False)
    context = {
        "tasks": tasks
    }
    return render(request, "tasks.html", context=context)
