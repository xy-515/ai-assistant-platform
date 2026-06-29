"""
Async Code API — 三个独立的 async 视图（带频率限制 + Token 统计）

    POST /api/code/debug    — 代码 + 报错 → 分析 + 修复代码
    POST /api/code/generate — 自然语言需求 → 代码片段
    POST /api/code/review   — 代码 → 风格/性能/安全评审
"""

import asyncio
import json
import logging
import time
from collections import defaultdict

from asgiref.sync import sync_to_async
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from .models import CodeHistory
from .services.llm_service import chat_with_llm

logger = logging.getLogger(__name__)

# ── Rate Limiter (in-memory, per-user) ─────────────────

_rate_window = 60       # 1 minute window
_rate_limit  = 5        # max 5 requests

_user_buckets: dict[int, list[float]] = defaultdict(list)


def _check_rate(user_id: int) -> tuple[bool, int]:
    """Return (allowed, remaining).  Reports False if limit exceeded."""
    now = time.time()
    bucket = _user_buckets[user_id]
    # Purge old entries
    bucket[:] = [t for t in bucket if now - t < _rate_window]
    if len(bucket) >= _rate_limit:
        return False, 0
    bucket.append(now)
    return True, _rate_limit - len(bucket)


# ── JWT ────────────────────────────────────────────────

@sync_to_async
def _get_user_sync(token_str: str):
    try:
        validated = JWTAuthentication().get_validated_token(token_str)
        user = JWTAuthentication().get_user(validated)
        return user if user and user.is_active else None
    except (InvalidToken, TokenError):
        return None


async def _get_user(request):
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    return await _get_user_sync(header[7:])


# ── Response helpers ───────────────────────────────────

def _ok(data: dict) -> JsonResponse:
    return JsonResponse(data)


def _err(msg: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"detail": msg}, status=status)


# ── Save history (sync, run in thread) ─────────────────

def _save_history(user_id: int, func: str, lang: str,
                  code: str, error: str, output: str,
                  tokens: int = 0):
    title = code[:80].replace("\n", " ")
    return CodeHistory.objects.create(
        user_id=user_id,
        function_type=func,
        language=lang,
        title=title,
        code_content=code,
        error_info=error,
        output_content=output,
        token_used=tokens,
    )


# ── Prompt Templates ───────────────────────────────────

PROMPTS = {
    "debug": {
        "system": (
            "你是一位资深调试专家。请分析以下代码的错误原因，并给出修复后的完整代码。\n\n"
            "要求：\n"
            "1. 先解释错误原因（1-2句话）\n"
            "2. 再给出修复后的完整代码\n"
            "3. 如果有多处问题，逐一指出并修复\n"
            "4. 用 Markdown 格式输出"
        ),
        "user_tpl": (
            "## 代码\n```{lang}\n{code}\n```\n"
            "## 报错信息\n```\n{error}\n```\n"
            "请分析并修复。"
        ),
    },
    "generate": {
        "system": (
            "你是一位资深软件工程师。请根据用户的需求描述，生成高质量的代码片段。\n\n"
            "要求：\n"
            "1. 代码完整可运行\n"
            "2. 包含必要的注释\n"
            "3. 优先使用 Python\n"
            "4. 如果需求不明确，给出2-3种实现方案\n"
            "5. 用 Markdown 格式输出，代码块标注语言"
        ),
        "user_tpl": "需求：\n{requirement}\n\n请生成代码。",
    },
    "review": {
        "system": (
            "你是一位资深代码审查专家。请从以下维度审查代码：\n\n"
            "1. **代码风格** — 命名规范、代码结构、注释质量\n"
            "2. **性能问题** — 时间复杂度、空间复杂度、不必要的计算\n"
            "3. **安全隐患** — 注入风险、敏感信息泄露、权限问题\n"
            "4. **错误处理** — 异常捕获、边界条件、空值检查\n"
            "5. **可维护性** — 代码复用、模块化、测试友好性\n\n"
            "每个维度给出评分（1-5★）和具体建议。用 Markdown 格式输出。"
        ),
        "user_tpl": (
            "## 代码\n```{lang}\n{code}\n```\n"
            "请进行全面代码审查。"
        ),
    },
}


# ── POST /api/code/debug ───────────────────────────────

@method_decorator(csrf_exempt, name="dispatch")
class CodeDebugView(View):

    async def post(self, request):
        user = await _get_user(request)
        if user is None:
            return _err("未登录或 Token 无效", 401)

        allowed, remaining = _check_rate(user.id)
        if not allowed:
            return _err("请求过于频繁，每分钟最多 5 次", 429)

        try:
            body = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return _err("请求体不是有效的 JSON")

        code  = body.get("code", "").strip()
        error = body.get("error", "").strip()
        lang  = body.get("language", "python")

        if not code:
            return _err("请提供代码")

        prompt = PROMPTS["debug"]
        user_prompt = prompt["user_tpl"].format(lang=lang, code=code,
                                                  error=error or "无报错信息")

        try:
            result = await chat_with_llm(prompt["system"], user_prompt, temperature=0.3)
        except Exception as e:
            return _err(f"AI 分析失败: {e}", 500)

        # Estimate tokens (simple char-count heuristic if API doesn't return count)
        est_tokens = len(code + error + result) // 3

        obj = await asyncio.to_thread(
            _save_history, user.id, "fix", lang,
            code, error, result, est_tokens,
        )

        return _ok({
            "id": obj.id,
            "analysis_and_fix": result,
            "language": lang,
            "tokens_used": est_tokens,
            "rate_remaining": remaining,
            "created_at": obj.created_at.isoformat(),
        })


# ── POST /api/code/generate ────────────────────────────

@method_decorator(csrf_exempt, name="dispatch")
class CodeGenerateView(View):

    async def post(self, request):
        user = await _get_user(request)
        if user is None:
            return _err("未登录或 Token 无效", 401)

        allowed, remaining = _check_rate(user.id)
        if not allowed:
            return _err("请求过于频繁，每分钟最多 5 次", 429)

        try:
            body = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return _err("请求体不是有效的 JSON")

        requirement = body.get("requirement", "").strip()
        lang        = body.get("language", "python")

        if not requirement:
            return _err("请提供需求描述")

        prompt = PROMPTS["generate"]
        user_prompt = prompt["user_tpl"].format(requirement=requirement)

        try:
            result = await chat_with_llm(prompt["system"], user_prompt, temperature=0.5)
        except Exception as e:
            return _err(f"AI 生成失败: {e}", 500)

        est_tokens = len(requirement + result) // 3

        obj = await asyncio.to_thread(
            _save_history, user.id, "generate_test", lang,
            requirement, "", result, est_tokens,
        )

        return _ok({
            "id": obj.id,
            "code": result,
            "language": lang,
            "tokens_used": est_tokens,
            "rate_remaining": remaining,
            "created_at": obj.created_at.isoformat(),
        })


# ── POST /api/code/review ──────────────────────────────

@method_decorator(csrf_exempt, name="dispatch")
class CodeReviewView(View):

    async def post(self, request):
        user = await _get_user(request)
        if user is None:
            return _err("未登录或 Token 无效", 401)

        allowed, remaining = _check_rate(user.id)
        if not allowed:
            return _err("请求过于频繁，每分钟最多 5 次", 429)

        try:
            body = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return _err("请求体不是有效的 JSON")

        code = body.get("code", "").strip()
        lang = body.get("language", "python")

        if not code:
            return _err("请提供代码")

        prompt = PROMPTS["review"]
        user_prompt = prompt["user_tpl"].format(lang=lang, code=code)

        try:
            result = await chat_with_llm(prompt["system"], user_prompt, temperature=0.3)
        except Exception as e:
            return _err(f"AI 评审失败: {e}", 500)

        est_tokens = len(code + result) // 3

        obj = await asyncio.to_thread(
            _save_history, user.id, "review", lang,
            code, "", result, est_tokens,
        )

        return _ok({
            "id": obj.id,
            "review": result,
            "language": lang,
            "tokens_used": est_tokens,
            "rate_remaining": remaining,
            "created_at": obj.created_at.isoformat(),
        })


# ═══════════════════════════════════════════════════════════
# SSE Streaming Views
# ═══════════════════════════════════════════════════════════

from django.http import StreamingHttpResponse
from .services.llm_service import stream_with_llm


async def _sse_event(event_type: str, data: dict | str) -> str:
    if isinstance(data, dict):
        data = json.dumps(data, ensure_ascii=False)
    return f"event: {event_type}\ndata: {data}\n\n"


class _CodeStreamMixin:
    """Shared SSE streaming logic for code endpoints."""

    async def _stream_code(self, request, func_type: str):
        user = await _get_user(request)
        if user is None:
            yield await _sse_event("error", {"type": "error", "message": "未登录或 Token 无效"})
            return

        # Rate limit
        allowed, remaining = _check_rate(user.id)
        if not allowed:
            yield await _sse_event("error", {"type": "error", "message": "请求过于频繁，每分钟最多 5 次"})
            return

        try:
            body = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            yield await _sse_event("error", {"type": "error", "message": "请求体不是有效的 JSON"})
            return

        prompt = PROMPTS[func_type]
        lang = body.get("language", "python")

        if func_type == "debug":
            code = body.get("code", "").strip()
            error = body.get("error", "").strip()
            if not code:
                yield await _sse_event("error", {"type": "error", "message": "请提供代码"})
                return
            system = prompt["system"]
            user_prompt = prompt["user_tpl"].format(lang=lang, code=code, error=error or "无报错信息")
            save_code = code
            save_error = error
            temperature = 0.3
        elif func_type == "generate":
            requirement = body.get("requirement", "").strip()
            if not requirement:
                yield await _sse_event("error", {"type": "error", "message": "请提供需求描述"})
                return
            system = prompt["system"]
            user_prompt = prompt["user_tpl"].format(requirement=requirement)
            save_code = requirement
            save_error = ""
            temperature = 0.5
        elif func_type == "review":
            code = body.get("code", "").strip()
            if not code:
                yield await _sse_event("error", {"type": "error", "message": "请提供代码"})
                return
            system = prompt["system"]
            user_prompt = prompt["user_tpl"].format(lang=lang, code=code)
            save_code = code
            save_error = ""
            temperature = 0.3
        else:
            yield await _sse_event("error", {"type": "error", "message": "未知功能类型"})
            return

        try:
            full_output = ""
            async for chunk in stream_with_llm(system, user_prompt, temperature=temperature):
                full_output += chunk
                yield await _sse_event("chunk", {"type": "chunk", "content": chunk})
        except Exception as e:
            logger.error("Stream error for %s: %s", func_type, e)
            yield await _sse_event("error", {"type": "error", "message": f"AI 生成失败: {e}"})
            return

        # Save history
        est_tokens = len(save_code + save_error + full_output) // 3
        save_func = {"debug": "fix", "generate": "generate_test", "review": "review"}[func_type]
        obj = await asyncio.to_thread(
            _save_history, user.id, save_func, lang,
            save_code, save_error, full_output, est_tokens,
        )
        yield await _sse_event("meta", {"type": "meta", "id": obj.id, "rate_remaining": remaining, "created_at": obj.created_at.isoformat()})
        yield "event: done\ndata: [DONE]\n\n"


@method_decorator(csrf_exempt, name="dispatch")
class CodeStreamDebugView(_CodeStreamMixin, View):
    async def post(self, request):
        return StreamingHttpResponse(
            self._stream_code(request, "debug"),
            content_type="text/event-stream",
            headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
        )


@method_decorator(csrf_exempt, name="dispatch")
class CodeStreamGenerateView(_CodeStreamMixin, View):
    async def post(self, request):
        return StreamingHttpResponse(
            self._stream_code(request, "generate"),
            content_type="text/event-stream",
            headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
        )


@method_decorator(csrf_exempt, name="dispatch")
class CodeStreamReviewView(_CodeStreamMixin, View):
    async def post(self, request):
        return StreamingHttpResponse(
            self._stream_code(request, "review"),
            content_type="text/event-stream",
            headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
        )
