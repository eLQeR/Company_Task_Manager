from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.core.exceptions import FieldError
from django.db.models import Q
from django.http import HttpRequest, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseRedirect, \
    Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import TaskForm, UserRegisterForm, UserUpdateForm
from .models import Task, Worker, Commentary
from django.core.mail import send_mail


def send_task_created_assignees(task: Task, assignees: list):
    emails_of_assignees = [get_object_or_404(Worker, pk=worker_id).email for worker_id in assignees]
    send_mail(
        subject=f"New Task \"{task.name}\" from {task.creator}",
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


def index(request: HttpRequest):
    return render(request, "index.html")


def support_view(request):
    return render(request, "support.html")


@login_required
def team(request):
    context = {
        "team": Worker.objects.all().select_related("position"),
        "quantity": Worker.objects.all().count()
    }
    return render(request, "team.html", context=context)


@login_required
def profile(request):
    return render(request, "registration/profile.html")


class TasksView(LoginRequiredMixin, generic.ListView):
    queryset = Task.objects.filter(is_completed=False).select_related("task_type")
    template_name = "task/tasks.html"
    context_object_name = "tasks"
    paginate_by = 10

    def get_queryset(self):
        tasks = self.queryset
        name_task = self.request.GET.get("name_task", "")
        priority = self.request.GET.get("priority", "")
        task_type = self.request.GET.get("task_type", "")
        ordering = self.request.GET.get("ordering", "")

        try:
            if name_task:
                tasks = tasks.filter(name__icontains=name_task)
            if task_type:
                tasks = tasks.filter(task_type=task_type)
            if priority:
                tasks = tasks.filter(priority=priority)
        except ValueError:
            raise Http404

        # IS IT RIGHT???? TODO

        if ordering:
            try:
                tasks = tasks.order_by(ordering)
            except FieldError:
                raise Http404
        return tasks


class MyTasksView(LoginRequiredMixin, generic.ListView):
    template_name = "task/my-tasks.html"
    context_object_name = "tasks"

    def get_queryset(self):
        return Task.objects.filter(
            Q(creator=self.request.user) | Q(assignees__id__in=(self.request.user.id,))
        ).distinct().select_related("creator", "task_type")

    def get_context_data(self, *args, **kwargs):
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
        form = TaskForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            # make creator by request user by default
            task = form.save()
            task.creator = request.user
            # set deadline
            deadline = request.POST.get("deadline")
            if deadline:
                try:
                    task.deadline = datetime.strptime(deadline, "%Y-%m-%dT%H:%M")
                except ValueError:
                    return HttpResponseBadRequest()
            task.save()
            # send letters for assignees
            send_task_created_assignees(
                task=task,
                assignees=request.POST.getlist("assignees")
            )
            return HttpResponseRedirect(self.success_url)
        return HttpResponseBadRequest()


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "task/task-update.html"
    success_url = reverse_lazy("task_manager:my-tasks")

    def get(self, request, *args, **kwargs):
        if request.user != get_object_or_404(Task, pk=kwargs.get("pk")).creator:
            return HttpResponseForbidden()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user != get_object_or_404(Task, pk=kwargs.get("pk")).creator:
            return HttpResponseForbidden()
        task = self.get_object()
        deadline = request.POST.get("deadline")
        if deadline:
            try:
                task.deadline = datetime.strptime(deadline, "%Y-%m-%dT%H:%M")
            except ValueError:
                return HttpResponseBadRequest("Invalid datetime deadline data!")
        task.save()
        return super().post(request, *args, **kwargs)
        # return HttpResponseBadRequest()


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    template_name = "task/task-delete-confirm.html"
    success_url = reverse_lazy("task_manager:my-tasks")


@login_required
def task_done(request, *args, **kwargs):
    task = get_object_or_404(Task, pk=kwargs.get("pk"))
    if request.user != task.creator and request.user not in task.assignees.all():
        return HttpResponseForbidden()
    if request.method == "GET":
        context = {
            "task": task
        }
        return render(request, "task/task-confirm-done.html", context=context)
    if request.method == "POST":
        task.is_completed = True
        task.save()
        return HttpResponseRedirect(reverse_lazy("task_manager:my-tasks"))
    return HttpResponseBadRequest()

    # DISABLED OPTION SIGN-UP#
# class UserCreateView(generic.CreateView):
#     model = Worker
#     form_class = UserRegisterForm
#     template_name = "registration/sign-up.html"
#     success_url = reverse_lazy("task_manager:index")


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
