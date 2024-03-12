from django.urls import path

from task_manager.views import index, tasks, my_tasks

urlpatterns = [
    path("", index, name="index"),
    path("tasks/", tasks, name="tasks"),
    path("my-tasks/", my_tasks, name="my-tasks")
]

app_name = "task_manager"
