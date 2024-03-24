from django.urls import path

from task_manager.views import (
    index,
    TasksView,
    TaskDetailView,
    TaskCreateView,
    CommentaryCreateView,
    TaskUpdateView,
    task_done,
    team,
    MyTasksView,
    TaskDeleteView
)

urlpatterns = [
    path("", index, name="index"),
    path("team/", team, name="team"),
    path("tasks/", TasksView.as_view(), name="tasks"),
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
    path("tasks/<int:pk>/done/", task_done, name="task-done"),
    path("my-tasks/", MyTasksView.as_view(), name="my-tasks")
]

app_name = "task_manager"
