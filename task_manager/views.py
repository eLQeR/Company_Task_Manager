from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Task, Worker, Commentary


def index(request):
    return render(request, "index.html")

@login_required
def tasks(request):
    tasks = Task.objects.filter(is_completed=False)
    context = {
        "tasks": tasks
    }
    return render(request, "tasks.html", context=context)


class TaskView(LoginRequiredMixin, generic.ListView):
    queryset = Task.objects.filter(is_completed=False)
    template_name = "tasks.html"
    context_object_name = "tasks"


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    queryset = Task.objects.all().prefetch_related("assignees")
    template_name = "task-detail.html"
    context_object_name = "task"


@login_required
def my_tasks(request):
    tasks = Task.objects.filter(assignees__id__in=(request.user.id, ))
    context = {
        "tasks": tasks,
        "tasks_count": tasks.filter(is_completed=True).count(),
        "tasks_completed": tasks.count(),
    }
    return render(request, "my-tasks.html", context=context)


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = Worker
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]


class UserUpdateForm(UserChangeForm):
    class Meta:
        model = Worker
        fields = ["username", "email", "first_name", "last_name", "avatar"]

class TaskForm(UserChangeForm):
    class Meta:
        model = Task
        fields = "__all__"

class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    template_name = "task-create.html"
    success_url = reverse_lazy("task_manager:index")


class UserCreateView(LoginRequiredMixin, generic.CreateView):
    model = Worker
    form_class = UserRegisterForm
    template_name = "registration/sign-up.html"
    success_url = reverse_lazy("task_manager:index")


class UserUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Worker
    form_class = UserUpdateForm
    template_name = "profile-update.html"
    success_url = reverse_lazy("task_manager:index")

@login_required
def profile(request):
    return render(request, "registration/profile.html")


class ProfileDetailView(LoginRequiredMixin, generic.DetailView):
    queryset = Worker.objects.all()
    template_name = "profile-detail.html"
    context_object_name = "user"


class CommentaryCreateView(LoginRequiredMixin, generic.CreateView):
    model = Commentary
    template_name = "task-detail.html"
    fields = ("content", )

    def post(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get("pk")
        task = get_object_or_404(Task, pk=pk)
        if user not in task.assignees.all():
            #TODO
            return redirect("task_manager:task-detail", pk=pk)
        text = request.POST["content"]
        if text:
            Commentary.objects.create(user=user, task=task, content=text)
            return redirect("task_manager:task-detail", pk=pk)

