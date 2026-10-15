"""阶段 1 · 步骤①：Function Calling 初体验——完整观察一次「点菜-上菜」。

流程：
  1. 带着工具菜单问模型"上海天气怎么样"
  2. 模型不直接回答，而是返回 tool_calls（点菜单：想调哪个工具+什么参数）
  3. 你（不是模型！）执行工具，把结果作为 tool 消息喂回去
  4. 模型拿到结果，才说出最终的自然语言回答

运行：uv run python learning/stage1/tool_call_demo.py
"""
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.environ["LLM_BASE_URL"],
    api_key=os.environ["LLM_API_KEY"],
    timeout=120,
    max_retries=6,
)

# —— 工具菜单：用 JSON Schema 描述"有哪些工具、参数长什么样" ——
# 模型只能看到这份描述来决定点不点菜，所以 description 写得越清楚越好
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的当前天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名，如：上海"}
                },
                "required": ["city"],
            },
        },
    }
]


def get_weather(city: str) -> dict:
    """工具的真实实现（现在是假数据——阶段 1 后期会换成真实 API）"""
    fake_db = {"上海": {"天气": "多云", "气温": "22℃", "提醒": "早晚偏凉"}}
    return fake_db.get(city, {"天气": "未知", "提醒": f"数据库里没有 {city}"})


def main() -> None:
    messages = [
        {"role": "user", "content": "上海今天天气怎么样？我该穿什么？"}
    ]

    # ===== 第 1 轮调用：带上菜单 =====
    resp = client.chat.completions.create(
        model=os.environ["LLM_MODEL"],
        messages=messages,
        tools=TOOLS,
        max_tokens=2048,
    )
    msg = resp.choices[0].message

    # 模型可能点菜，也可能不点（直接回答）。永远先检查！
    if not msg.tool_calls:
        print(f"模型没用工具，直接回答了：{msg.content}")
        return

    # ===== 看清点菜单长什么样 =====
    print("===== 模型点的菜 =====")
    print(f"工具名: {msg.tool_calls[0].function.name}")
    print(f"参数:   {msg.tool_calls[0].function.arguments}")
    print(f"参数类型: {type(msg.tool_calls[0].function.arguments).__name__}\n")

    # 点菜单要原样放回对话历史（模型需要记得自己点过什么）
    messages.append(msg)

    # ===== 你来执行：注意 arguments 是 JSON 字符串，要手动解析 =====
    call = msg.tool_calls[0]
    args = json.loads(call.function.arguments)
    result = get_weather(**args)

    print(f"===== 你执行的结果 =====\n{result}\n")

    # ===== 上菜：把执行结果作为 tool 消息喂回去 =====
    messages.append({
        "role": "tool",
        "tool_call_id": call.id,          # 告诉模型这是哪道菜的成果
        "content": json.dumps(result, ensure_ascii=False),
    })

    # ===== 第 2 轮调用：模型见到菜，才给出最终回答 =====
    resp2 = client.chat.completions.create(
        model=os.environ["LLM_MODEL"],
        messages=messages,
        tools=TOOLS,                      # 菜单继续带着，它可能还想再点
        max_tokens=2048,
    )
    print("===== 模型最终回答 =====")
    print(resp2.choices[0].message.content)


if __name__ == "__main__":
    main()
