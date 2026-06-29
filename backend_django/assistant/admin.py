"""Django Admin — 后台管理界面"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User, PaperHistory, CodeHistory, UploadedFile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "student_id", "department", "email",
                    "paper_count", "code_count", "date_joined"]
    list_filter = ["department", "is_active", "date_joined"]
    search_fields = ["username", "student_id", "email"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("学生信息", {"fields": ("student_id", "department", "major", "avatar", "bio")}),
    )

    @admin.display(description="论文次数")
    def paper_count(self, obj):
        return obj.paper_histories.count()

    @admin.display(description="代码次数")
    def code_count(self, obj):
        return obj.code_histories.count()


@admin.register(PaperHistory)
class PaperHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "function_badge", "title_preview", "token_used", "created_at"]
    list_filter = ["function_type", "created_at"]
    search_fields = ["title", "input_content", "user__username"]
    readonly_fields = ["input_content", "output_content", "created_at"]
    date_hierarchy = "created_at"

    @admin.display(description="功能")
    def function_badge(self, obj):
        return obj.get_function_type_display()

    @admin.display(description="标题")
    def title_preview(self, obj):
        return obj.title[:60]


@admin.register(CodeHistory)
class CodeHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "function_badge", "language", "title_preview", "created_at"]
    list_filter = ["function_type", "language", "created_at"]
    search_fields = ["title", "code_content", "user__username"]
    readonly_fields = ["code_content", "error_info", "output_content", "created_at"]
    date_hierarchy = "created_at"

    @admin.display(description="功能")
    def function_badge(self, obj):
        return obj.get_function_type_display()

    @admin.display(description="标题")
    def title_preview(self, obj):
        return obj.title[:60]


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "original_name", "file_type", "file_size_display", "uploaded_at"]
    list_filter = ["file_type", "uploaded_at"]
    search_fields = ["original_name", "user__username"]
    readonly_fields = ["uploaded_at"]

    @admin.display(description="文件大小")
    def file_size_display(self, obj):
        size = obj.file_size
        for unit in ["B", "KB", "MB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} GB"
