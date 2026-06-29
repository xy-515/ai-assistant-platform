"""DRF Serializers — API 序列化"""
from rest_framework import serializers

from .models import User, PaperHistory, CodeHistory, UploadedFile


class UserSerializer(serializers.ModelSerializer):
    paper_count = serializers.IntegerField(read_only=True)
    code_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "student_id",
                  "department", "major", "bio", "avatar",
                  "paper_count", "code_count", "date_joined"]
        read_only_fields = ["date_joined"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "email", "password", "student_id"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# ── Paper ──────────────────────────────────────────────

class PaperHistoryListSerializer(serializers.ModelSerializer):
    """列表视图（不返回完整内容，节省带宽）"""
    function_display = serializers.CharField(source="get_function_type_display", read_only=True)

    class Meta:
        model = PaperHistory
        fields = ["id", "title", "function_type", "function_display",
                  "token_used", "created_at"]


class PaperHistoryDetailSerializer(serializers.ModelSerializer):
    """详情视图（包含完整输入输出）"""
    class Meta:
        model = PaperHistory
        fields = "__all__"


class PaperCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaperHistory
        fields = ["function_type", "input_content"]


# ── Code ───────────────────────────────────────────────

class CodeHistoryListSerializer(serializers.ModelSerializer):
    function_display = serializers.CharField(source="get_function_type_display", read_only=True)

    class Meta:
        model = CodeHistory
        fields = ["id", "title", "function_type", "function_display",
                  "language", "token_used", "created_at"]


class CodeHistoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeHistory
        fields = "__all__"


class CodeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeHistory
        fields = ["function_type", "language", "code_content", "error_info"]


# ── File ───────────────────────────────────────────────

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = "__all__"
        read_only_fields = ["user", "file_size", "uploaded_at"]
