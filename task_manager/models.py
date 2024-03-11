from django.contrib.auth.models import AbstractUser
from django.db import models


class TaskType(models.Model):
    name = models.CharField(max_length=255, unique=True)


class Position(models.Model):
    name = models.CharField(max_length=255, unique=True)


class Worker(AbstractUser):
    position = models.ForeignKey(to=Position, on_delete=models.PROTECT, related_name="workers")


class Priorities(models.TextChoices):
    URGENT = "Urgent!!!"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(choices=Priorities.choices, max_length=63)
    task_type = models.ForeignKey(to=TaskType, on_delete=models.CASCADE, related_name="tasks")
    assignees = models.ManyToManyField(to=Worker, related_name="tasks")
