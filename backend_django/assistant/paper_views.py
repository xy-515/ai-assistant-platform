"""
Async Paper API — 三个独立的 async 视图

    POST /api/paper/outline   — 输入题目 → 输出大纲
    POST /api/paper/polish    — 输入文本 + 模式 → 输出润色后文本
    POST /api/paper/feedback  — 输入论文片段 → 输出整体点评
"""

import asyncio
import logging

from asgiref.sync import sync_to_async
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from .models import PaperHistory
from .services.llm_service import chat_with_llm

logger = logging.getLogger(__name__)

# ── Prompt Templates ────────────────────────────────────

PROMPTS = {
    "outline": {
        "system": (
            "你是一位计算机专业学术论文写作导师。"
            "请根据用户提供的论文题目，生成一份详细的论文大纲。\n\n"
            "要求：\n"
            "1. 使用标准学术论文结构（摘要→引言→相关工作→系统设计→实验→结论）\n"
            "2. 每个章节下列出 3-5 个要点\n"
            "3. 标注每节的预估字数比例\n"
            "4. 用 Markdown 格式输出，层级清晰"
        ),
        "user_tpl": "论文题目：{title}\n\n请生成论文大纲。",
    },
    "polish": {
        "system": {
            "academic": (
                "你是一位学术论文语言润色专家。"
                "请将以下文本润色为正式学术风格。\n\n"
                "要求：\n"
                "1. 保持原意不变\n"
                "2. 使用规范的学术用语\n"
                "3. 修正语法错误和表达不清的句子\n"
                "4. 标注主要修改（用 **粗体** 标记修改过的部分）\n"
                "5. 先输出润色后的完整文本，再列出修改说明"
            ),
            "concise": (
                "你是一位学术论文语言润色专家。"
                "请将以下文本简化，去除冗余表达。\n\n"
                "要求：\n"
                "1. 保持核心信息完整\n"
                "2. 删除多余修饰词和重复表述\n"
                "3. 缩短句子长度\n"
                "4. 标注删减比例\n"
                "5. 先输出简化后的文本，再列出主要删减内容"
            ),
            "deweight": (
                "你是一位学术论文降重专家。"
                "请对以下文本进行降重改写，降低重复率。\n\n"
                "要求：\n"
                "1. 保持原意和学术严谨性\n"
                "2. 使用不同的表达方式和句式结构\n"
                "3. 替换非核心术语的同义词\n"
                "4. 重新组织段落逻辑顺序\n"
                "5. 标注改写策略\n"
                "6. 先输出改写后的文本"
            ),
        },
        "user_tpl": "原文：\n\n{text}\n\n请进行{p_mode}处理。",
    },
    "feedback": {
        "system": (
            "你是一位计算机专业本科毕业论文审稿专家。"
            "请对以下论文片段给出全面点评。\n\n"
            "评审维度：\n"
            "1. **技术描述** — 技术方案是否准确、完整\n"
            "2. **逻辑结构** — 论述逻辑是否清晰\n"
            "3. **创新表达** — 创新点是否明确\n"
            "4. **语言质量** — 是否有语病、表述不清\n"
            "5. **学术规范** — 术语使用、引用格式等\n\n"
            "用 Markdown 格式输出，每个维度给出评分（1-5★）和具体建议。"
        ),
        "user_tpl": "论文片段：\n\n{fragment}\n\n请给出整体点评。",
    },
}

MODE_LABELS = {
    "academic": "学术风格润色",
    "concise": "简洁化",
    "deweight": "降重改写",
}


# ── Async Views ─────────────────────────────────────────

@sync_to_async
def _get_user_sync(token_str: str):
    """Validate JWT and return User (sync — called via sync_to_async)."""
    try:
        validated = JWTAuthentication().get_validated_token(token_str)
        user = JWTAuthentication().get_user(validated)
        return user if user and user.is_active else None
    except (InvalidToken, TokenError):
        return None


async def _get_user(request):
    """Extract user from JWT Bearer token (async-safe)."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return await _get_user_sync(auth_header[7:])


def _json_error(msg: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"detail": msg}, status=status)


def _save_history(user, func: str, input_text: str, output_text: str,
                  meta: dict | None = None) -> PaperHistory:
    title = input_text[:80].replace("\n", " ")
    return PaperHistory.objects.create(
        user=user,
        function_type=func,
        title=title,
        input_content=input_text,
        output_content=output_text,
        meta=meta or {},
    )


# ── POST /api/paper/outline ─────────────────────────────

@method_decorator(csrf_exempt, name="dispatch")
class PaperOutlineView(View):
    """输入论文题目 → 返回大纲"""

    async def post(self, request):
        user = await _get_user(request)
        if user is None:
            return _json_error("未登录或 Token 无效", 401)

        import json
        try:
            body = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return _json_error("请求体不是有效的 JSON")

        title = body.get("title", "").strip()
        if not title:
            return _json_error("请输入论文题目")

        prompt = PROMPTS["outline"]
        user_prompt = prompt["user_tpl"].format(title=title)

        try:
            result = await chat_with_llm(prompt["system"], user_prompt, temperature=0.7)
        except Exception as e:
            logger.error("Outline LLM error: %s", e)
            return _json_error(f"AI 生成失败: {e}", 500)

        # DB save is sync — run in thread
        meta = {"title": title}
        obj = await asyncio.to_thread(_save_history, user, "outline",
                                       f"题目: {title}", result, meta)

        return JsonResponse({
            "id": obj.id,
            "outline": result,
            "title": title,
            "created_at": obj.created_at.isoformat(),
        })


# ── POST /api/paper/polish ──────────────────────────────

@method_decorator(csrf_exempt, name="dispatch")
class PaperPolishView(View):
    """输入文本 + 模式 → 返回润色后文本"""

    async def post(self, request):
        user = await _get_user(request)
        if user is None:
            return _json_error("未登录或 Token 无效", 401)

        import json
        try:
            body = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return _json_error("请求体不是有效的 JSON")

        text = body.get("text", "").strip()
        mode = body.get("mode", "academic")

        if not text:
            return _json_error("请输入待润色的文本")

        if mode not in ("academic", "concise", "deweight"):
            return _json_error("mode 必须是 academic / concise / deweight")

        prompt = PROMPTS["polish"]
        system = prompt["system"][mode]
        user_prompt = prompt["user_tpl"].format(text=text, p_mode=MODE_LABELS[mode])

        try:
            result = await chat_with_llm(system, user_prompt, temperature=0.5)
        except Exception as e:
            return _json_error(f"AI 润色失败: {e}", 500)

        meta = {"mode": mode, "char_count": len(text)}
        obj = await asyncio.to_thread(_save_history, user, "polish",
                                       f"[{MODE_LABELS[mode]}] {text[:60]}",
                                       result, meta)

        return JsonResponse({
            "id": obj.id,
            "polished": result,
            "mode": mode,
            "original_length": len(text),
            "created_at": obj.created_at.isoformat(),
        })


# ── POST /api/paper/feedback ────────────────────────────

@method_decorator(csrf_exempt, name="dispatch")
class PaperFeedbackView(View):
    """输入论文片段 → 返回整体点评"""

    async def post(self, request):
        user = await _get_user(request)
        if user is None:
            return _json_error("未登录或 Token 无效", 401)

        import json
        try:
            body = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return _json_error("请求体不是有效的 JSON")

        fragment = body.get("fragment", "").strip()
        if not fragment:
            return _json_error("请输入论文片段")

        prompt = PROMPTS["feedback"]
        user_prompt = prompt["user_tpl"].format(fragment=fragment)

        try:
            result = await chat_with_llm(prompt["system"], user_prompt, temperature=0.5)
        except Exception as e:
            return _json_error(f"AI 点评失败: {e}", 500)

        obj = await asyncio.to_thread(_save_history, user, "review",
                                       f"[论文点评] {fragment[:60]}",
                                       result)

        return JsonResponse({
            "id": obj.id,
            "feedback": result,
            "fragment_preview": fragment[:100],
            "created_at": obj.created_at.isoformat(),
        })


# ═══════════════════════════════════════════════════════════
# SSE Streaming Views
# ═══════════════════════════════════════════════════════════

import asyncio
from django.http import StreamingHttpResponse
from .services.llm_service import stream_with_llm


async def _sse_event(event_type: str, data: dict | str) -> str:
    """Format a single SSE event."""
    if isinstance(data, dict):
        data = json.dumps(data, ensure_ascii=False)
    return f"event: {event_type}\ndata: {data}\n\n"


class _PaperStreamMixin:
    """Shared SSE streaming logic for paper endpoints."""

    async def _stream_paper(self, request, func_type: str):
        """Validate, stream LLM response, save history, yield SSE events."""
        user = await _get_user(request)
        if user is None:
            yield await _sse_event("error", {"type": "error", "message": "未登录或 Token 无效"})
            return

        try:
            body = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            yield await _sse_event("error", {"type": "error", "message": "请求体不是有效的 JSON"})
            return

        prompt = PROMPTS[func_type]
        if func_type == "outline":
            title = body.get("title", "").strip()
            if not title:
                yield await _sse_event("error", {"type": "error", "message": "请输入论文题目"})
                return
            system = prompt["system"]
            user_prompt = prompt["user_tpl"].format(title=title)
            input_text = f"题目: {title}"
            meta = {"title": title}
            temperature = 0.7
        elif func_type == "polish":
            text = body.get("text", "").strip()
            mode = body.get("mode", "academic")
            if not text:
                yield await _sse_event("error", {"type": "error", "message": "请输入待润色的文本"})
                return
            if mode not in ("academic", "concise", "deweight"):
                mode = "academic"
            system = prompt["system"][mode]
            user_prompt = prompt["user_tpl"].format(text=text, p_mode=MODE_LABELS[mode])
            input_text = f"[{MODE_LABELS[mode]}] {text[:60]}"
            meta = {"mode": mode, "char_count": len(text)}
            temperature = 0.5
        elif func_type == "feedback":
            fragment = body.get("fragment", "").strip()
            if not fragment:
                yield await _sse_event("error", {"type": "error", "message": "请输入论文片段"})
                return
            system = prompt["system"]
            user_prompt = prompt["user_tpl"].format(fragment=fragment)
            input_text = f"[论文点评] {fragment[:60]}"
            meta = {}
            temperature = 0.5
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

        # Save history (sync → thread)
        obj = await asyncio.to_thread(_save_history, user, func_type, input_text, full_output, meta)
        yield await _sse_event("meta", {"type": "meta", "id": obj.id, "created_at": obj.created_at.isoformat()})
        yield await _sse_event("done", '{"type":"done"}')
        yield "event: done\ndata: [DONE]\n\n"


@method_decorator(csrf_exempt, name="dispatch")
class PaperStreamOutlineView(_PaperStreamMixin, View):
    async def post(self, request):
        return StreamingHttpResponse(
            self._stream_paper(request, "outline"),
            content_type="text/event-stream",
            headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
        )


@method_decorator(csrf_exempt, name="dispatch")
class PaperStreamPolishView(_PaperStreamMixin, View):
    async def post(self, request):
        return StreamingHttpResponse(
            self._stream_paper(request, "polish"),
            content_type="text/event-stream",
            headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
        )


@method_decorator(csrf_exempt, name="dispatch")
class PaperStreamFeedbackView(_PaperStreamMixin, View):
    async def post(self, request):
        return StreamingHttpResponse(
            self._stream_paper(request, "feedback"),
            content_type="text/event-stream",
            headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
        )
