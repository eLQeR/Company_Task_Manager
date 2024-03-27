from django.test import TestCase
from task_manager.models import TaskType
from task_manager.forms import UserRegisterForm, UserUpdateForm, TaskForm


class FormsTests(TestCase):
    def setUp(self) -> None:
        self.create_form_data = {
            "username": "Test1",
            "email": "test@test.com",
            "first_name": "Test",
            "last_name": "Test",
            "password1": "TestPassword!",
            "password2": "TestPassword!",
        }
        self.update_form_data = {
            "username": "Test2",
            "email": "test@test.com",
            "first_name": "Test",
            "last_name": "Test",
            "linkedin_url": "linkedin_url",
            "github_url": "github_url",
            "instagram_url": "instagram_url",
            "telegram_url": "telegram_url",
        }

        self.task_type = TaskType.objects.create(name="Test feature")

        self.task_form_data = {
            "name": "Test2",
            "description": "Make Test",
            "priority": "High",
            "task_type": self.task_type,
            "assignees": []
        }

    def test_user_register_form(self):
        form = UserRegisterForm(data=self.create_form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, self.create_form_data)

    def test_user_update_form(self):
        form = UserUpdateForm(data=self.update_form_data)
        self.update_form_data.update({"avatar": "avatars/default_user.png"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, self.update_form_data)

    def test_task_form(self):
        form = TaskForm(data=self.task_form_data)
        self.task_form_data.update(
            {
                "task_image": "uploads/images/no-photo-task.jpg",
            }
        )
        self.assertTrue(form.is_valid())
        form.cleaned_data["assignees"] = list(form.cleaned_data.get("assignees"))
        self.assertEqual(form.cleaned_data, self.task_form_data)
