"""DRF ViewSets — REST API"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Count

from .models import User, PaperHistory, CodeHistory, UploadedFile
from .serializers import (
    UserSerializer, RegisterSerializer,
    PaperHistoryListSerializer, PaperHistoryDetailSerializer, PaperCreateSerializer,
    CodeHistoryListSerializer, CodeHistoryDetailSerializer, CodeCreateSerializer,
    UploadedFileSerializer,
)


class AuthViewSet(viewsets.GenericViewSet):
    """注册 + 登录（JWT）"""
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["post"])
    def register(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "token": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def login(self, request):
        from django.contrib.auth import authenticate
        user = authenticate(
            username=request.data.get("username"),
            password=request.data.get("password"),
        )
        if not user:
            return Response({"detail": "用户名或密码错误"}, status=401)
        refresh = RefreshToken.for_user(user)
        return Response({
            "token": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        })


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """当前用户信息"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=["get"])
    def me(self, request):
        return Response(UserSerializer(request.user).data)


class PaperHistoryViewSet(viewsets.ModelViewSet):
    """论文对话历史 — 分页列表 + 详情 + 删除"""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (PaperHistory.objects
                .filter(user=self.request.user)
                .order_by("-created_at"))

    def get_serializer_class(self):
        if self.action == "list":
            return PaperHistoryListSerializer
        if self.action == "create":
            return PaperCreateSerializer
        return PaperHistoryDetailSerializer

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save(user=request.user)
        return Response(PaperHistoryDetailSerializer(obj).data, status=201)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CodeHistoryViewSet(viewsets.ModelViewSet):
    """代码对话历史 — 分页列表 + 详情 + 删除"""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (CodeHistory.objects
                .filter(user=self.request.user)
                .order_by("-created_at"))

    def get_serializer_class(self):
        if self.action == "list":
            return CodeHistoryListSerializer
        if self.action == "create":
            return CodeCreateSerializer
        return CodeHistoryDetailSerializer

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save(user=request.user)
        return Response(CodeHistoryDetailSerializer(obj).data, status=201)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UploadedFileViewSet(viewsets.ModelViewSet):
    """文件上传 — 列表 + 上传 + 删除"""
    serializer_class = UploadedFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UploadedFile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
