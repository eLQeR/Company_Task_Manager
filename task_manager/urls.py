from django.urls import path

from task_manager.views import index, tasks, my_tasks, TaskView, TaskDetailView, TaskCreateView, CommentaryCreateView

urlpatterns = [
    path("", index, name="index"),
    path("tasks/", TaskView.as_view(), name="tasks"),
    path("create-task/", TaskCreateView.as_view(), name="create-tasks"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("tasks/<int:pk>/create-comment/", CommentaryCreateView.as_view(), name="task-create-comment"),
    path("my-tasks/", my_tasks, name="my-tasks")
]

app_name = "task_manager"
