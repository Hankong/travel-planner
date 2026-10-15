"""第一个 LLM 调用（OpenAI 格式）：验证端点、密钥、SDK 三件套。

运行方式：uv run python scripts/hello_llm.py
"""
import os

from dotenv import load_dotenv
from openai import OpenAI

# 把项目根目录 .env 文件里的键值对加载进环境变量
load_dotenv()

# OpenAI SDK 会向 {base_url}/chat/completions 发请求，
# 所以 base_url 要带上 /v1
client = OpenAI(
    base_url=os.environ["LLM_BASE_URL"],
    api_key=os.environ["LLM_API_KEY"],
    timeout=120,     # 单次请求最长等 120 秒
    max_retries=6,   # 遇到 5xx 等临时错误自动重试（指数退避），最多 6 次
)

response = client.chat.completions.create(
    model=os.environ["LLM_MODEL"],
    max_tokens=1024,  # 推理模型会先"思考"再回答，给足额度
    messages=[
        {"role": "user", "content": "你好！请用一句话介绍你自己，并说出你的模型名。"}
    ],
)

message = response.choices[0].message

# 推理模型的两段输出：先思考（reasoning_content），再回答（content）
if message.reasoning_content:
    print(f"[思考过程] {message.reasoning_content[:120]}...\n")
print(f"[回答] {message.content}")
print(f"\n[本次消耗] 输入 {response.usage.prompt_tokens} token，"
      f"输出 {response.usage.completion_tokens} token")
