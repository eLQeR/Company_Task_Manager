from django.urls import path

from task_manager.views import index, tasks

urlpatterns = [
    path("", index),
    path("tasks/", tasks)
]

app_name = "task_manager"
