from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CategoryForm, ProjectForm, TaskForm
from .models import Category, Project, Task
from django.db.models import Count
from django.urls import reverse, reverse_lazy
from django.db.models import Count, F, Q


class OwnerQuerysetMixin(LoginRequiredMixin):
    """Only ever return the logged-in user's own tasks."""

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user).select_related(
            "project", "category"
        )


class TaskListView(OwnerQuerysetMixin, ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"
    paginate_by = 10

    # Whitelist: users can only pick these, never arbitrary field names
    SORT_OPTIONS = {
        "due": [F("due_date").asc(nulls_last=True), "-created_at"],
        "due_desc": [F("due_date").desc(nulls_last=True), "-created_at"],
        "newest": ["-created_at"],
        "oldest": ["created_at"],
        "title": ["title"],
    }
    SORT_LABELS = [
        ("due", "Due date (soonest)"),
        ("due_desc", "Due date (latest)"),
        ("newest", "Newest first"),
        ("oldest", "Oldest first"),
        ("title", "Title A-Z"),
    ]

    def get_queryset(self):
        qs = super().get_queryset()  # already limited to the current user
        params = self.request.GET

        status = params.get("status", "")
        if status in Task.Status.values:
            qs = qs.filter(status=status)

        priority = params.get("priority", "")
        if priority in Task.Priority.values:
            qs = qs.filter(priority=priority)

        project = params.get("project", "")
        if project.isdigit():
            qs = qs.filter(project_id=project)

        category = params.get("category", "")
        if category.isdigit():
            qs = qs.filter(category_id=category)

        q = params.get("q", "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        sort = params.get("sort", "due")
        order = self.SORT_OPTIONS.get(sort, self.SORT_OPTIONS["due"])
        return qs.order_by(*order)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        params = self.request.GET

        context["projects"] = Project.objects.filter(owner=user)
        context["categories"] = Category.objects.filter(owner=user)
        context["status_choices"] = Task.Status.choices
        context["priority_choices"] = Task.Priority.choices
        context["sort_labels"] = self.SORT_LABELS

        # Currently selected values, so the form keeps them after submit
        context["filters"] = {
            "q": params.get("q", ""),
            "status": params.get("status", ""),
            "priority": params.get("priority", ""),
            "project": params.get("project", ""),
            "category": params.get("category", ""),
            "sort": params.get("sort", "due"),
        }

        # Current query string without "page", for pagination links
        qs = params.copy()
        qs.pop("page", None)
        context["querystring"] = qs.urlencode()
        return context


class TaskDetailView(OwnerQuerysetMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"


class TaskFormMixin:
    """Shared by create and update: passes the user to the form."""

    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class TaskCreateView(LoginRequiredMixin, TaskFormMixin, CreateView):
    model = Task

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Task created.")
        return super().form_valid(form)


class TaskUpdateView(OwnerQuerysetMixin, TaskFormMixin, UpdateView):
    def form_valid(self, form):
        messages.success(self.request, "Task updated.")
        return super().form_valid(form)


class TaskDeleteView(OwnerQuerysetMixin, DeleteView):
    template_name = "tasks/task_confirm_delete.html"
    context_object_name = "task"
    success_url = reverse_lazy("task_list")

    def form_valid(self, form):
        messages.success(self.request, "Task deleted.")
        return super().form_valid(form)


class TaskCompleteView(LoginRequiredMixin, View):
    """POST-only: mark a task as done."""

    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk, owner=request.user)
        task.status = Task.Status.DONE
        task.save()
        messages.success(request, "Task marked as done.")
        return redirect(request.POST.get("next") or "task_list")
# ---------- Projects ----------

class ProjectListView(LoginRequiredMixin, ListView):
    template_name = "tasks/project_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user).annotate(
            task_count=Count("tasks")
        )


class ProjectDetailView(LoginRequiredMixin, DetailView):
    template_name = "tasks/project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = self.object.tasks.filter(
            owner=self.request.user
        ).select_related("category")
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    form_class = ProjectForm
    template_name = "tasks/project_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Project created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("project_detail", kwargs={"pk": self.object.pk})


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProjectForm
    template_name = "tasks/project_form.html"

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Project updated.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("project_detail", kwargs={"pk": self.object.pk})


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "tasks/project_confirm_delete.html"
    context_object_name = "project"
    success_url = reverse_lazy("project_list")

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Project deleted.")
        return super().form_valid(form)


# ---------- Categories ----------

class CategoryListView(LoginRequiredMixin, ListView):
    template_name = "tasks/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user).annotate(
            task_count=Count("tasks")
        )


class CategoryFormMixin:
    form_class = CategoryForm
    template_name = "tasks/category_form.html"
    success_url = reverse_lazy("category_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class CategoryCreateView(LoginRequiredMixin, CategoryFormMixin, CreateView):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Category created.")
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, CategoryFormMixin, UpdateView):
    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Category updated.")
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "tasks/category_confirm_delete.html"
    context_object_name = "category"
    success_url = reverse_lazy("category_list")

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Category deleted.")
        return super().form_valid(form)