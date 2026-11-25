from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Task

User = get_user_model()


class TaskTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pass12345")
        self.bob = User.objects.create_user("bob", password="pass12345")
        self.task = Task.objects.create(owner=self.alice, title="Alice task")

    def test_register_and_login(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "password1": "Str0ngPass!234",
                "password2": "Str0ngPass!234",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertTrue(self.client.login(username="alice", password="pass12345"))

    def test_create_task_sets_owner(self):
        self.client.login(username="alice", password="pass12345")
        self.client.post(reverse("task_create"), {
            "title": "New task",
            "priority": "medium",
            "status": "todo",
        })
        new_task = Task.objects.get(title="New task")
        self.assertEqual(new_task.owner, self.alice)

    def test_other_user_cannot_access_task(self):
        self.client.login(username="bob", password="pass12345")
        url_args = {"pk": self.task.pk}
        self.assertEqual(self.client.get(reverse("task_detail", kwargs=url_args)).status_code, 404)
        self.assertEqual(self.client.get(reverse("task_update", kwargs=url_args)).status_code, 404)
        self.assertEqual(self.client.post(reverse("task_delete", kwargs=url_args)).status_code, 404)
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())

    def test_is_overdue(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        overdue = Task.objects.create(owner=self.alice, title="Late", due_date=yesterday)
        self.assertTrue(overdue.is_overdue)
        overdue.status = Task.Status.DONE
        overdue.save()
        self.assertFalse(overdue.is_overdue)

    def test_dashboard_counts(self):
        Task.objects.create(owner=self.alice, title="Done one", status=Task.Status.DONE)
        self.client.login(username="alice", password="pass12345")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.context["counts"]["total"], 2)
        self.assertEqual(response.context["counts"]["done"], 1)

    def test_login_required(self):
        response = self.client.get(reverse("task_list"))
        self.assertEqual(response.status_code, 302)