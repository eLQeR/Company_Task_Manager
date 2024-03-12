from django.contrib.auth.models import AbstractUser
from django.db import models


class TaskType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    position = models.ForeignKey(to=Position, on_delete=models.PROTECT, related_name="workers", null=True)
    avatar = models.ImageField(
        upload_to="avatars/",
        default="/media/avatars/default_user.png"
    )
    linkedin_url = models.CharField(max_length=255, default="Uknown")
    github_url = models.CharField(max_length=255, default="Uknown")
    instagram_url = models.CharField(max_length=255, default="Uknown")
    telegram_url = models.CharField(max_length=255, default="Uknown")


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

    def __str__(self):
        return self.name

class Commentary(models.Model):
    user = models.ForeignKey(
        to=Worker,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    task = models.ForeignKey(
        to=Task,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    content = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
