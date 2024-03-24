import os
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


class TaskType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


def create_avatar_path(instance, filename):
    _, extension = os.path.splitext(filename)
    return os.path.join(
        "avatars/",
        f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"
    )


class Worker(AbstractUser):
    position = models.ForeignKey(
        to=Position,
        on_delete=models.PROTECT,
        related_name="workers",
        null=True
    )
    avatar = models.ImageField(
        upload_to=create_avatar_path,
        default="avatars/default_user.png"
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


def create_task_image_path(instance, filename):
    _, extension = os.path.splitext(filename)
    return os.path.join(
        "uploads/images/",
        f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"
    )


class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(choices=Priorities.choices, max_length=63)
    task_type = models.ForeignKey(
        to=TaskType,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    creator = models.ForeignKey(
        to=Worker,
        on_delete=models.DO_NOTHING,
        related_name="own_tasks",
        null=True,
        blank=True
    )
    task_image = models.ImageField(
        upload_to=create_task_image_path,
        default="uploads/images/no-photo-task.jpg"
    )
    assignees = models.ManyToManyField(to=Worker, related_name="tasks")

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.name

    def get_date_created(self):
        return self.created.strftime("%Y-%m-%d %H:%M:%S")

    def get_deadline(self):
        if self.deadline:
            return self.deadline.strftime("%Y-%m-%d %H:%M:%S")
        return None

    def get_description_len(self):
        return len(self.description)


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

    def get_date_created(self):
        return self.created_time.strftime("%Y-%m-%d %H:%M:%S")
