import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from task_manager.models import Task, Commentary, Position, TaskType


class ModelsTests(TestCase):
	def setUp(self) -> None:
		self.position = Position.objects.create(name="Test DevOps")
		self.task_type = TaskType.objects.create(name="Test Bug")
		self.worker = get_user_model().objects.create_user(
			username="test",
			email="test@gmail.com",
			password="testCase"
		)
		self.task = Task.objects.create(
			name="Test Task",
			description="Test description",
			task_type=self.task_type,
			deadline=datetime.datetime.strptime(
				"2023-11-11 11:00:00",
				"%Y-%m-%d %H:%M:%S"
			),
			priority="High",
			creator=self.worker,
		)

	def test_position_str(self):
		self.assertEqual(str(self.position), "Test DevOps")

	def test_task_type_str(self):
		self.assertEqual(str(self.task_type), "Test Bug")

	def test_commentary_get_date_created(self):
		now = datetime.datetime.now()
		commentary = Commentary.objects.create(
			content="Hello test",
			created_time=now,
			user=self.worker,
			task=self.task
		)
		self.assertEqual(commentary.get_date_created(), now.strftime("%Y-%m-%d %H:%M:%S"))

	def test_task_get_date_created(self):
		now = datetime.datetime.now()
		self.task.created = now
		self.assertEqual(self.task.get_date_created(), now.strftime("%Y-%m-%d %H:%M:%S"))

	def test_task_get_deadline(self):
		self.assertEqual(self.task.get_deadline(), "2023-11-11 11:00:00")
