"""并发调用 LLM 三次（asyncio），和串行版对比总耗时。

运行方式：uv run python learning/stage0/async_llm.py
"""
import asyncio
import os
import time

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

client = AsyncOpenAI(
    base_url=os.environ["LLM_BASE_URL"],
    api_key=os.environ["LLM_API_KEY"],
    timeout=120,
    max_retries=6,
)

QUESTION = "用一句话解释什么是复利"


async def ask(i: int) -> float:
    """发起一次调用，返回本次耗时（async 版的调用必须 await）"""
    t0 = time.perf_counter()
    await client.chat.completions.create(
        model=os.environ["LLM_MODEL"],
        max_tokens=256,
        messages=[{"role": "user", "content": f"第{i}次：{QUESTION}"}],
    )
    return time.perf_counter() - t0


async def main() -> None:
    start = time.perf_counter()
    times = await asyncio.gather(
        ask(1),
        ask(2),
        ask(3),
    )
    for i, t in enumerate(times, 1):
        print(f"第 {i} 次调用耗时 {t:.1f} 秒")
    print(f"\n并发总耗时：{time.perf_counter() - start:.1f} 秒")


if __name__ == "__main__":
    asyncio.run(main())