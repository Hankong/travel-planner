"""串行调用 LLM 三次，记录总耗时。之后会和并发版对比。

运行方式：uv run python scripts/serial_llm.py
"""
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.environ["LLM_BASE_URL"],
    api_key=os.environ["LLM_API_KEY"],
    timeout=120,
    max_retries=6,
)

QUESTION = "用一句话解释什么是复利"

start = time.perf_counter()          # 高精度计时，开表
for i in range(3):
    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model=os.environ["LLM_MODEL"],
        max_tokens=256,
        messages=[{"role": "user", "content": f"第{i + 1}次：{QUESTION}"}],
    )
    print(f"第 {i + 1} 次调用耗时 {time.perf_counter() - t0:.1f} 秒")
total = time.perf_counter() - start  # 停表
print(f"\n串行总耗时：{total:.1f} 秒")