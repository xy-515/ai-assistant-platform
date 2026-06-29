"""Quick test for LLM service"""
import os, django, asyncio
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
django.setup()

from assistant.services.llm_service import chat_with_llm_sync, stream_with_llm

# Test 1: Sync
print("1. Sync:", end=" ")
r = chat_with_llm_sync("You are helpful", "Say hello in one word", temperature=0.1)
print(f"OK ({len(r)} chars): {r[:80]}")

# Test 2: Bad API key
print("2. Bad key:", end=" ")
from django.conf import settings
old = settings.LLM_API_KEY
settings.LLM_API_KEY = "bad"
try:
    chat_with_llm_sync("test", "test")
    print("FAIL")
except Exception as e:
    print(f"OK ({type(e).__name__})")
settings.LLM_API_KEY = old

# Test 3: Stream
async def ts():
    chunks = []
    async for c in stream_with_llm("You are helpful", "Say hello", temperature=0.1, max_tokens=20):
        chunks.append(c)
    return chunks

chunks = asyncio.run(ts())
text = "".join(chunks)
print(f"3. Stream: OK ({len(chunks)} chunks): {repr(text[:50])}")

print("\nALL TESTS PASSED")
