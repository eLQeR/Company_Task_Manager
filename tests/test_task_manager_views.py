from datetime import datetime, timedelta
import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.test import TestCase
from django.urls import reverse

from task_manager.models import Task, Worker

TestCase.fixtures = ["db_task_manager_data.json"]


class UnauthorizedViewsTests(TestCase):

    def test_index_view_is_public(self):
        response = self.client.get(reverse("task_manager:index"))
        self.assertEqual(response.status_code, 200)

    def test_support_view_is_public(self):
        response = self.client.get(reverse("task_manager:support"))
        self.assertEqual(response.status_code, 200)

    def test_login_view_is_public(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)


class AuthorizedViewsTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.first()
        self.client.force_login(self.user)

    def test_team_view(self):
        response = self.client.get(reverse("task_manager:team"))
        team = Worker.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["team"]),
            list(team)
        )

        self.client.logout()
        response = self.client.get(reverse("task_manager:team"))
        self.assertEqual(response.status_code, 302)

    def test_my_profile_login_required(self):
        response = self.client.get(reverse("my-profile"))

        self.assertEqual(response.status_code, 200)

        self.client.logout()
        response = self.client.get(reverse("my-profile"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={reverse('my-profile')}")

    def test_user_profile_login_required(self):
        response = self.client.get(reverse("profile", args=[self.user.id]))

        self.assertEqual(response.status_code, 200)

        self.client.logout()
        response = self.client.get(reverse("profile", args=[self.user.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={reverse('profile', args=[self.user.id])}")


class TasksViewsTest(TestCase):

    def setUp(self) -> None:
        self.user = get_user_model().objects.first()
        self.client.force_login(self.user)

        self.form_data = {
            "name": "Test2 Task with image",
            "description": "Task description",
            "priority": "High",
            "task_type": 2,
            "deadline": (
                    datetime.now() + timedelta(days=1)
            ).strftime("%Y-%m-%dT%H:%M"),
        }

        self.client.post(
            reverse("task_manager:create-task"),
            self.form_data,
        )
        self.task_with_default_image = Task.objects.get(name="Test2 Task with image")

    def test_tasks_view_paginator(self):
        response = self.client.get(reverse("task_manager:tasks"))
        tasks = Task.objects.filter(is_completed=False)[:10]

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(
            list(response.context["tasks"]),
            list(tasks)
        )

    def test_my_tasks_view(self):
        response = self.client.get(reverse("task_manager:my-tasks"))
        tasks = Task.objects.filter(
            Q(creator=self.user) | Q(assignees__id__in=(self.user.id,))
        ).distinct()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["tasks"]),
            list(tasks)
        )

    def test_filtering_ordering_tasks_view(self):
        filtering_ordering_form = {
            "name_task": "Testing",
            "priority": "High",
            "task_type": 5,
            "ordering": "-name"
        }
        response = self.client.get(reverse("task_manager:tasks"), data=filtering_ordering_form)

        tasks = Task.objects.filter(
            is_completed=False,
            name__icontains="Testing",
            priority="High",
            task_type_id=5
        ).order_by("-name")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context_data["tasks"]),
            list(tasks)
        )

    def test_create_task_without_image(self):
        form_data = self.form_data.copy()

        response = self.client.post(
            reverse("task_manager:create-task"),
            data=form_data,
        )

        created_task = Task.objects.order_by("-created").first()

        form_data["task_type_id"] = form_data.pop("task_type")
        form_data["deadline"] = datetime.strptime(
            form_data.pop("deadline"),
            "%Y-%m-%dT%H:%M"
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("task_manager:my-tasks"))
        for key, value in form_data.items():
            self.assertEqual(getattr(created_task, key), value)

    def test_update_task_without_image(self):
        form_data = self.form_data.copy()
        form_data["name"] = "Test Task Without image"

        res = self.client.post(
            reverse("task_manager:create-task"),
            data=form_data,
        )
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("task_manager:my-tasks"))

        created_task = Task.objects.get(name="Test Task Without image")
        self.assertTrue(os.path.exists(created_task.task_image.path))

    def test_create_task_with_image(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)

            form_data = self.form_data.copy()
            form_data["task_image"] = ntf
            form_data["name"] = "Test Task with image"

            res = self.client.post(
                reverse("task_manager:create-task"),
                form_data,
                format="multipart",
            )

        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("task_manager:my-tasks"))

        created_task = Task.objects.get(name="Test Task with image")
        self.assertTrue(os.path.exists(created_task.task_image.path))
        self.assertNotEquals(
            created_task.task_image.path,
            self.task_with_default_image.task_image.path
        )
        os.remove(created_task.task_image.path)

    def test_update_task_another_user_forbidden(self):
        user = get_user_model().objects.last()
        self.client.force_login(user)

        res = self.client.post(
            reverse("task_manager:task-update", args=[self.task_with_default_image.id]),
            self.form_data
        )

        self.assertEqual(res.status_code, 403)

    def test_comment_task_another_user_forbidden(self):
        user = get_user_model().objects.last()
        self.client.force_login(user)

        res = self.client.post(
            reverse("task_manager:task-create-comment", args=[self.task_with_default_image.id]),
            {"content": "Test"}
        )

        self.assertEqual(res.status_code, 403)


class ProfileViewTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.first()
        self.client.force_login(self.user)

    def test_login_view_is_public(self):
        self.client.logout()
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")

    def test_login_view(self):
        form_data = {
            "username": "TestUser",
            "email": "test@test.com",
            "password": "TestPassword!",
        }
        get_user_model().objects.create_user(
            **form_data
        )
        form_data.pop("email")
        response = self.client.post(reverse("login"), data=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("task_manager:index"))

    def test_change_password_view(self):
        form_data = {
            "username": "TestUser",
            "email": "test@test.com",
            "password": "OldTestPassword!",
        }
        form_change_password = {
            "old_password": "TestPassword!",
            "new_password1": "NewTestPassword!10",
            "new_password2": "NewTestPassword!10",
        }

        user = get_user_model().objects.create_user(
            **form_data
        )
        self.client.force_login(user)

        self.client.post(
            reverse("update-password"),
            data=form_change_password
        )
        user.refresh_from_db()

        self.assertFalse(user.check_password("OldTestPassword"))

    def test_update_user_avatar(self):
        form_data = {
            "username": "TestUserAvatar",
            "email": "test@test.com",
            "password": "TestPassword!",
        }
        user_with_avatar = get_user_model().objects.create_user(
            **form_data
        )
        self.client.force_login(user_with_avatar)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            form_data.update({
                "avatar": ntf
            })
            res = self.client.post(
                reverse("my-profile-update", args=[user_with_avatar.id]),
                form_data,
                format="multipart",
            )
        user_with_avatar.refresh_from_db()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(os.path.exists(user_with_avatar.avatar.path))
        self.assertNotEquals(
            user_with_avatar.avatar.path,
            self.user.avatar.path
        )
