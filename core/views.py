from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.utils import timezone
from django.views.generic import TemplateView

from tasks.models import Task


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()

        # Only this user's tasks, same ownership rule as everywhere else
        tasks = Task.objects.filter(owner=self.request.user)

        # All the counts in a single database query
        counts = tasks.aggregate(
            total=Count("id"),
            todo=Count("id", filter=Q(status=Task.Status.TODO)),
            in_progress=Count("id", filter=Q(status=Task.Status.IN_PROGRESS)),
            done=Count("id", filter=Q(status=Task.Status.DONE)),
            overdue=Count(
                "id",
                filter=Q(due_date__lt=today) & ~Q(status=Task.Status.DONE),
            ),
        )
        # Guard against dividing by zero when the user has no tasks
        if counts["total"]:
            counts["percent"] = round(counts["done"] * 100 / counts["total"])
        else:
            counts["percent"] = 0
        context["counts"] = counts

        context["overdue_tasks"] = (
            tasks.filter(due_date__lt=today)
            .exclude(status=Task.Status.DONE)
            .select_related("project")
            .order_by("due_date")[:5]
        )
        context["due_today"] = (
            tasks.filter(due_date=today)
            .exclude(status=Task.Status.DONE)
            .select_related("project")
        )
        context["recent_tasks"] = tasks.select_related("project").order_by(
            "-created_at"
        )[:5]
        return context