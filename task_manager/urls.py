from django.urls import path

from task_manager.views import (
    IndexView,
    TasksView,
    TaskDetailView,
    TaskCreateView,
    CommentaryCreateView,
    TaskUpdateView,
    TaskDoneView,
    MyTasksView,
    TaskDeleteView,
    TeamView,
    SupportView,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("team/", TeamView.as_view(), name="team"),
    path("tasks/", TasksView.as_view(), name="tasks"),
    path("support/", SupportView.as_view(), name="support"),
    path("create-task/", TaskCreateView.as_view(), name="create-task"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path(
        "tasks/<int:pk>/update/",
        TaskUpdateView.as_view(),
        name="task-update"
    ),
    path(
        "tasks/<int:pk>/delete/",
        TaskDeleteView.as_view(),
        name="task-delete"
    ),
    path(
        "tasks/<int:pk>/create-comment/",
        CommentaryCreateView.as_view(),
        name="task-create-comment"
    ),
    path("tasks/<int:pk>/done/", TaskDoneView.as_view(), name="task-done"),
    path("my-tasks/", MyTasksView.as_view(), name="my-tasks")
]

app_name = "task_manager"
