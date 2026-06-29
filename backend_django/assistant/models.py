"""
Django Models — AI Assistant Platform (毕业设计智能辅助平台)

App: assistant

Relationships:
    User (AbstractUser)
    ├── PaperHistory (1:N)  论文对话历史
    ├── CodeHistory  (1:N)  代码对话历史
    └── UploadedFile (1:N)  上传文件记录
"""

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# ═══════════════════════════════════════════════════════════
# 1. Custom User — 学生用户
# ═══════════════════════════════════════════════════════════

class User(AbstractUser):
    """
    扩展 Django 默认 User，增加学生身份字段。

    Fields inherited from AbstractUser:
        username, password, email, first_name, last_name,
        is_active, is_staff, is_superuser, date_joined
    """
    student_id = models.CharField(
        "学号", max_length=20, unique=True, null=True, blank=True,
        help_text="学校统一学号，用于身份识别"
    )
    department = models.CharField(
        "院系", max_length=100, blank=True,
        help_text="如：计算机科学与技术学院"
    )
    major = models.CharField(
        "专业", max_length=100, blank=True,
        help_text="如：人工智能"
    )
    avatar = models.ImageField(
        "头像", upload_to="avatars/", null=True, blank=True
    )
    bio = models.TextField("个人简介", max_length=500, blank=True)

    class Meta:
        db_table = "users"
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.username} ({self.student_id or 'N/A'})"

    @property
    def paper_count(self) -> int:
        """论文助手使用次数"""
        return self.paper_histories.count()

    @property
    def code_count(self) -> int:
        """代码助手使用次数"""
        return self.code_histories.count()


# ═══════════════════════════════════════════════════════════
# 2. PaperHistory — 论文对话历史
# ═══════════════════════════════════════════════════════════

class PaperHistory(models.Model):
    """
    每次论文助手调用的完整记录。

    存储：用户输入 → AI 输出，支持按功能类型分类查询。
    """

    class FunctionType(models.TextChoices):
        POLISH  = "polish",  "润色优化"
        OUTLINE = "outline", "大纲生成"
        REVIEW  = "review",  "论文点评"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="paper_histories",
        verbose_name="用户",
    )
    title = models.CharField(
        "标题", max_length=200, blank=True,
        help_text="自动从输入截取，也可手动指定"
    )
    function_type = models.CharField(
        "功能类型", max_length=20,
        choices=FunctionType.choices,
    )
    input_content = models.TextField(
        "输入内容",
        help_text="用户提交的论文原文或主题描述"
    )
    output_content = models.TextField(
        "AI 返回结果", blank=True, default="",
        help_text="Markdown 格式的 AI 输出"
    )
    token_used = models.PositiveIntegerField(
        "消耗 Token 数", default=0,
    )
    meta = models.JSONField(
        "附加参数", default=dict, blank=True,
        help_text="存储 polish_mode 等扩展参数"
    )
    created_at = models.DateTimeField(
        "创建时间", default=timezone.now, db_index=True
    )

    class Meta:
        db_table = "paper_histories"
        verbose_name = "论文对话记录"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "function_type"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.title and self.input_content:
            self.title = self.input_content[:80].replace("\n", " ")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.get_function_type_display()}] {self.title[:50]}"

    @property
    def input_preview(self) -> str:
        return self.input_content[:200]

    @property
    def output_preview(self) -> str:
        return self.output_content[:200]


# ═══════════════════════════════════════════════════════════
# 3. CodeHistory — 代码对话历史
# ═══════════════════════════════════════════════════════════

class CodeHistory(models.Model):
    """
    每次代码助手调用的完整记录。

    额外存储报错信息和代码语言，便于分类检索。
    """

    class FunctionType(models.TextChoices):
        REVIEW        = "review",        "代码审查"
        GENERATE_TEST = "generate_test", "生成测试"
        FIX           = "fix",           "修复 Bug"

    class Language(models.TextChoices):
        PYTHON     = "python",     "Python"
        JAVASCRIPT = "javascript", "JavaScript"
        JAVA       = "java",       "Java"
        CPP        = "cpp",        "C++"
        GO         = "go",         "Go"
        OTHER      = "other",      "其他"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="code_histories",
        verbose_name="用户",
    )
    title = models.CharField(
        "标题", max_length=200, blank=True,
    )
    function_type = models.CharField(
        "功能类型", max_length=20,
        choices=FunctionType.choices,
    )
    language = models.CharField(
        "编程语言", max_length=20,
        choices=Language.choices, default=Language.PYTHON,
    )
    code_content = models.TextField(
        "原始代码",
    )
    error_info = models.TextField(
        "报错信息", blank=True, default="",
    )
    output_content = models.TextField(
        "AI 返回结果", blank=True, default="",
    )
    token_used = models.PositiveIntegerField(
        "消耗 Token 数", default=0,
    )
    created_at = models.DateTimeField(
        "创建时间", default=timezone.now, db_index=True
    )

    class Meta:
        db_table = "code_histories"
        verbose_name = "代码对话记录"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "function_type"]),
            models.Index(fields=["user", "language"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.title and self.code_content:
            self.title = self.code_content[:80].replace("\n", " ")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.get_function_type_display()}] {self.title[:50]}"


# ═══════════════════════════════════════════════════════════
# 4. UploadedFile — 上传文件记录
# ═══════════════════════════════════════════════════════════

def upload_path(instance, filename):
    """按用户 ID 分目录存储：uploads/{user_id}/{type}/{timestamp}_{filename}"""
    import uuid
    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
    return f"uploads/{instance.user_id}/{instance.file_type}/{uuid.uuid4().hex[:8]}_{filename}"


class UploadedFile(models.Model):
    """
    记录用户上传的文件（代码 zip 或论文文档）。

    保存原始文件名和服务器存储路径，关联到对应的对话历史。
    """

    class FileType(models.TextChoices):
        CODE_ZIP   = "code_zip",   "代码压缩包"
        DOCUMENT   = "document",   "论文文档（Word/PDF）"
        OTHER      = "other",      "其他"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_files",
        verbose_name="用户",
    )
    file = models.FileField(
        "文件", upload_to=upload_path,
        help_text="支持 .zip .docx .pdf .py"
    )
    file_type = models.CharField(
        "文件类型", max_length=20,
        choices=FileType.choices,
    )
    original_name = models.CharField(
        "原始文件名", max_length=255,
        help_text="保留用户上传时的文件名"
    )
    file_size = models.PositiveIntegerField(
        "文件大小（字节）", default=0,
    )
    # 可选：关联到某个对话历史
    paper_history = models.ForeignKey(
        PaperHistory,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="files",
        verbose_name="关联论文记录",
    )
    code_history = models.ForeignKey(
        CodeHistory,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="files",
        verbose_name="关联代码记录",
    )
    uploaded_at = models.DateTimeField(
        "上传时间", default=timezone.now, db_index=True
    )

    class Meta:
        db_table = "uploaded_files"
        verbose_name = "上传文件"
        verbose_name_plural = verbose_name
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.original_name} ({self.get_file_type_display()})"

    def save(self, *args, **kwargs):
        if self.file and not self.file_size:
            self.file_size = self.file.size
        if not self.original_name and self.file:
            self.original_name = self.file.name.split("/")[-1]
        super().save(*args, **kwargs)
