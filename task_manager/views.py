from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.core.exceptions import FieldError
from django.db.models import Q, QuerySet
from django.http import (
    HttpResponseForbidden,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    Http404,
)
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import TaskForm, UserUpdateForm
from .models import Task, Worker, Commentary
from django.core.mail import send_mail


def send_task_created_assignees(task: Task, assignees: list):
    emails_of_assignees = [
        get_object_or_404(Worker, pk=worker_id).email for worker_id in assignees
    ]
    send_mail(
        subject=f'New Task "{task.name}" from {task.creator}',
        message=(
            f"Decription: {task.description}\n\n"
            f"Priority: {task.priority}\n"
            f"Deadline: {task.get_deadline()}\n"
            f"Type task: {task.task_type}\n"
            f"URL: http://127.0.0.1:8000/tasks/{task.id}/\n"
        ),
        from_email="rosulka.abaldui@gmail.com",
        recipient_list=emails_of_assignees,
        fail_silently=False,
    )


class IndexView(generic.TemplateView):
    template_name = "index.html"


class SupportView(generic.TemplateView):
    template_name = "support.html"


class ProfileView(LoginRequiredMixin, generic.TemplateView):
    template_name = "registration/profile.html"


class TeamView(LoginRequiredMixin, generic.ListView):
    queryset = Worker.objects.all().select_related("position")
    template_name = "team.html"
    context_object_name = "team"


def get_filtered_ordered_queryset(request, tasks: QuerySet):
    name_task = request.GET.get("name_task", "")
    priority = request.GET.get("priority", "")
    task_type = request.GET.get("task_type", "")
    ordering = request.GET.get("ordering", "")

    try:
        if name_task:
            tasks = tasks.filter(name__icontains=name_task)
        if task_type:
            tasks = tasks.filter(task_type=task_type)
        if priority:
            tasks = tasks.filter(priority=priority)
    except ValueError:
        raise Http404()

    if ordering:
        try:
            tasks = tasks.order_by(ordering)
        except FieldError:
            raise Http404()
    return tasks


class TasksView(LoginRequiredMixin, generic.ListView):
    queryset = Task.objects.filter(is_completed=False).select_related("task_type")
    template_name = "task/tasks.html"
    context_object_name = "tasks"
    paginate_by = 10

    def get_queryset(self):
        tasks = self.queryset
        return get_filtered_ordered_queryset(self.request, tasks)


class MyTasksView(LoginRequiredMixin, generic.ListView):
    template_name = "task/my-tasks.html"
    context_object_name = "tasks"

    def get_queryset(self):
        """Get all tasks where user is whether creator or assigner"""

        tasks = Task.objects.filter(
            Q(creator=self.request.user) | Q(assignees__id__in=(self.request.user.id,))
        )
        tasks = get_filtered_ordered_queryset(self.request, tasks)
        return tasks.distinct().select_related("creator", "task_type")

    def get_context_data(self, *args, **kwargs):
        """Add to context_date full information with statistics about tasks"""

        context = super(MyTasksView, self).get_context_data(*args, **kwargs)

        self.queryset = self.get_queryset()

        tasks_count = self.queryset.all()
        tasks_count_month = tasks_count.filter(
            created__month=datetime.now().month,
            created__year=datetime.now().year
        )

        tasks_done = self.queryset.filter(is_completed=True)
        tasks_done_month = tasks_done.filter(
            created__month=datetime.now().month,
            created__year=datetime.now().year
        )

        tasks_not_done = self.queryset.filter(is_completed=False)
        tasks_not_done_month = tasks_not_done.filter(
            created__month=datetime.now().month,
            created__year=datetime.now().year
        )

        tasks_created = self.queryset.filter(creator=self.request.user)
        tasks_created_month = tasks_created.filter(
            created__month=datetime.now().month,
            created__year=datetime.now().year
        )

        extra_context = {
            "tasks_count": tasks_count.count(),
            "tasks_count_month": tasks_count_month.count(),
            "tasks_done": tasks_done.count(),
            "tasks_done_month": tasks_done_month.count(),
            "tasks_not_done": tasks_not_done.count(),
            "tasks_not_done_month": tasks_not_done_month.count(),
            "tasks_created": tasks_created.count(),
            "tasks_created_month": tasks_created_month.count(),
        }
        context.update(extra_context)
        return context


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    queryset = Task.objects.all().prefetch_related("assignees__position", "comments")
    template_name = "task/task-detail.html"
    context_object_name = "task"


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    template_name = "task/task-create.html"
    success_url = reverse_lazy("task_manager:my-tasks")

    def post(self, request, *args, **kwargs):
        """
        Create tasks with creator as request user by default,
        take deadline from form as datetime object.
        Send letter for assignees with notification about the creation of a new task
        """

        form = TaskForm(data=request.POST, files=request.FILES)
        if form.is_valid():

            task = form.save()
            task.creator = request.user

            deadline = request.POST.get("deadline")
            if deadline:
                try:
                    task.deadline = datetime.strptime(deadline, "%Y-%m-%dT%H:%M")
                except ValueError:
                    return HttpResponseBadRequest()
            task.save()
            if request.POST.getlist("assignees"):
                send_task_created_assignees(
                    task=task, assignees=request.POST.getlist("assignees")
                )
            return HttpResponseRedirect(self.success_url)
        return HttpResponseBadRequest()


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "task/task-update.html"
    success_url = reverse_lazy("task_manager:my-tasks")

    def get(self, request, *args, **kwargs):
        if request.user != self.get_object().creator:
            return HttpResponseForbidden()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user != self.get_object().creator:
            return HttpResponseForbidden()
        task = self.get_object()
        deadline = request.POST.get("deadline")
        if deadline:
            try:
                task.deadline = datetime.strptime(deadline, "%Y-%m-%dT%H:%M")
            except ValueError:
                return HttpResponseBadRequest(
                    "Invalid datetime deadline data!"
                )
        task.save()
        return super().post(request, *args, **kwargs)


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    template_name = "task/task-delete-confirm.html"
    success_url = reverse_lazy("task_manager:my-tasks")


class TaskDoneView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "task/task-confirm-done.html"
    context_object_name = "task"
    
    def get(self, request, *args, **kwargs):
        task = self.get_object()
        if request.user != task.creator and request.user not in task.assignees.all():
            return HttpResponseForbidden()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        if request.user != task.creator and request.user not in task.assignees.all():
            return HttpResponseForbidden()
        task.is_completed = True
        task.save()
        return HttpResponseRedirect(reverse_lazy("task_manager:my-tasks"))


class UserUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Worker
    form_class = UserUpdateForm
    template_name = "profile-update.html"
    success_url = reverse_lazy("task_manager:index")

    def get(self, request, *args, **kwargs):
        if request.user != self.get_object():
            return HttpResponseForbidden()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user != self.get_object():
            return HttpResponseForbidden()
        return super().post(request, *args, **kwargs)


class ProfileDetailView(LoginRequiredMixin, generic.DetailView):
    queryset = Worker.objects.all()
    template_name = "profile-detail.html"
    context_object_name = "user"


class CommentaryCreateView(LoginRequiredMixin, generic.CreateView):
    model = Commentary
    template_name = "task/task-detail.html"
    fields = ("content",)

    def post(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get("pk")
        task = get_object_or_404(Task, pk=pk)
        if user not in task.assignees.all() and user != task.creator:
            return HttpResponseForbidden()
        text = request.POST.get("content")
        if text:
            Commentary.objects.create(user=user, task=task, content=text)
            return redirect("task_manager:task-detail", pk=pk)
        return HttpResponseBadRequest()


class PasswordChangeViewCustom(PasswordChangeView):
    success_url = reverse_lazy("task_manager:index")
    template_name = "registration/change-password.html"
