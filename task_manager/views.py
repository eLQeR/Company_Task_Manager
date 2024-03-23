from datetime import datetime
from string import ascii_lowercase

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponseForbidden, HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Task, Worker, Commentary
from django.core.mail import send_mail


def send_task_created_assignees(task: Task, assignees: list):
    emails_of_assignees = [get_object_or_404(Worker, pk=worker_id).email for worker_id in assignees]
    send_mail(
        f"New Task \"{task.name}\" from {task.creator}",
        (
            f"Decription: {task.description}\n\n"
            f"Priority: {task.priority}"
            f"Deadline: {task.get_deadline()}"
            f"Type task: {task.task_type}"
            f"URL: http://127.0.0.1:8000/tasks/{task.id}/"
        ),
        "rosulka.abaldui@gmail.com",
        emails_of_assignees,
        fail_silently=False,
    )

def index(request: HttpRequest):
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
    paginate_by = 10

    def get_queryset(self):
        tasks = self.queryset
        name_task = self.request.GET.get("name_task", "")
        priority = self.request.GET.get("priority", "")
        task_type = self.request.GET.get("task_type", "")
        ordering = self.request.GET.get("ordering", "")

        if name_task:
            tasks = tasks.filter(name__icontains=name_task)
        if task_type:
            tasks = tasks.filter(task_type=task_type)
        if priority:
            tasks = tasks.filter(priority=priority)
        if ordering:
            tasks = tasks.order_by(ordering)
        return tasks


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    queryset = Task.objects.all().prefetch_related("assignees")
    template_name = "task-detail.html"
    context_object_name = "task"


@login_required
def my_tasks(request):
    tasks_as_assigner = Task.objects.filter(assignees__id__in=(request.user.id,))
    tasks = Task.objects.filter(creator_id=request.user.id).union(tasks_as_assigner)
    context = {
        "tasks": tasks,
        "tasks_count": tasks.count(),
    }
    return render(request, "my-tasks.html", context=context)


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = Worker
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ["username", "email", "first_name", "last_name", "avatar", "linkedin_url", "github_url", "instagram_url", "telegram_url"]


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("name", "description", "priority", "task_type", "task_image", "assignees")


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    template_name = "task-create.html"
    success_url = reverse_lazy("task_manager:my-tasks")

    # def form_valid(self, form):
    #     self.object = form.save(commit=False)
    #     self.object.creator = self.request.user
    #     self.object.save()
    #     return HttpResponseRedirect(reverse_lazy("task_manager:my-tasks"))
    def post(self, request, *args, **kwargs):
        form = TaskForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            #make creator by ruquest user by default
            task = form.save(commit=False)
            task.creator = request.user
            # set deadline
            deadline = request.POST.get("deadline")
            if deadline:
                try:
                    task.deadline = datetime.strptime(deadline, "%Y-%m-%dT%H:%M")
                except ValueError:
                    return HttpResponseBadRequest()
            task.save()
            #send letters for assignees
            send_task_created_assignees(
                task=task,
                assignees=request.POST.get("assignees")
            )
            return HttpResponseRedirect(reverse_lazy("task_manager:my-tasks"))
        return HttpResponseBadRequest()


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "task-update.html"
    success_url = reverse_lazy("task_manager:tasks")

    def get(self, request, *args, **kwargs):
        if request.user != get_object_or_404(Task, pk=kwargs.get("pk")).creator:
            return HttpResponseForbidden()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user != get_object_or_404(Task, pk=kwargs.get("pk")).creator:
            return HttpResponseForbidden()
        form = self.get_form()
        if form.is_valid():
            task = form.save(commit=False)
            task.creator = request.user
            deadline = request.POST.get("deadline")
            if deadline:
                try:
                    task.deadline = deadline
                except Exception as e:
                    print(e)
            task.save()
            return HttpResponseRedirect(reverse_lazy("task_manager:my-tasks"))
        return HttpResponseBadRequest()


@login_required
def task_done(request, *args, **kwargs):
    task = get_object_or_404(Task, pk=kwargs.get("pk"))
    if request.user != task.creator and request.user not in task.assignees.all():
        return HttpResponseForbidden()
    if request.method == "GET":
        context = {
            "task": task
        }
        return render(request, "task-confirm-done.html", context=context)
    if request.method == "POST":
        task.is_completed = True
        task.save()
        return HttpResponseRedirect(reverse_lazy("task_manager:my-tasks"))
    return HttpResponseBadRequest()


class UserCreateView(generic.CreateView):
    model = Worker
    form_class = UserRegisterForm
    template_name = "registration/sign-up.html"
    success_url = reverse_lazy("task_manager:index")


class UserUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Worker
    form_class = UserUpdateForm
    template_name = "profile-update.html"
    success_url = reverse_lazy("task_manager:index")

    def get(self, request, *args, **kwargs):
        if request.user != get_object_or_404(Worker, pk=kwargs.get("pk")):
            return HttpResponseForbidden()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user != get_object_or_404(Worker, pk=kwargs.get("pk")):
            return HttpResponseForbidden()
        return super().post(request, *args, **kwargs)


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
    fields = ("content",)

    def post(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get("pk")
        task = get_object_or_404(Task, pk=pk)
        if user not in task.assignees.all():
            return HttpResponseForbidden()
        text = request.POST.get("content")
        if text:
            Commentary.objects.create(user=user, task=task, content=text)
            return redirect("task_manager:task-detail", pk=pk)
        return HttpResponseBadRequest()


@login_required
def team(request):
    context = {
        "team": Worker.objects.all(),
        "quantity": Worker.objects.all().count()
    }
    return render(request, "team.html", context=context)


class PasswordChangeViewCustom(PasswordChangeView):
    success_url = reverse_lazy("task_manager:index")
    template_name = "change-password.html"

def support_view(request):
    return render(request, "support.html")
