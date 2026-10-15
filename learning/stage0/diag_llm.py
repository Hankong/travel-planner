"""诊断脚本：查明中转站实际支持的模型列表，并逐个测试。

只打印脱敏后的密钥，可放心把输出发给任何人。
运行：uv run python scripts/diag_llm.py
"""
import os

import httpx
from dotenv import load_dotenv

load_dotenv()
base = os.environ["ANTHROPIC_BASE_URL"].rstrip("/")
key = os.environ["ANTHROPIC_API_KEY"]
# 同时带上两种认证头，覆盖中转站的多种口味
headers = {"x-api-key": key, "Authorization": f"Bearer {key}"}

print(f"端点: {base}")
print(f"密钥: {key[:6]}...{key[-4:]}（已脱敏）\n")

# 第 1 步：查询模型列表（多数中转站支持 OpenAI 风格的 GET /v1/models）
print("== 1. 查询可用模型列表 ==")
r = httpx.get(f"{base}/v1/models", headers=headers, timeout=30)
print(f"HTTP {r.status_code}")

models = []
if r.status_code == 200:
    try:
        models = [m.get("id", "") for m in r.json().get("data", [])]
        print(f"共 {len(models)} 个模型:")
        for m in models:
            print(f"  - {m}")
    except Exception as e:
        print(f"解析失败: {e}\n原始返回: {r.text[:500]}")
else:
    print(f"原始返回: {r.text[:300]}")

# 第 2 步：优先测 .env 里配的模型，再补测列表里的 glm 系（最多 3 个）
candidates = [os.environ.get("LLM_MODEL", "glm-5.3-flash")]
candidates += [m for m in models if "glm" in m.lower() and m not in candidates][:3]

print("\n== 2. 逐个发送最小测试请求 ==")
for name in candidates:
    print(f"--- 模型: {name} ---")
    try:
        r = httpx.post(
            f"{base}/v1/messages",
            headers=headers,
            json={
                "model": name,
                "max_tokens": 32,
                "messages": [{"role": "user", "content": "回复两个字：OK"}],
            },
            timeout=60,
        )
        print(f"HTTP {r.status_code}: {r.text[:300]}")
    except Exception as e:
        print(f"请求异常: {e}")
    print()
