from django.contrib import admin
from .models import Worker, TaskType, Task, Position

admin.site.register(Worker)
admin.site.register(Task)
admin.site.register(TaskType)
admin.site.register(Position)
