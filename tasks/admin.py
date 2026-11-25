from django.contrib import admin

from .models import Category, Project, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "status", "priority", "due_date")
    list_filter = ("status", "priority")
    search_fields = ("title",)


admin.site.register(Project)
admin.site.register(Category)