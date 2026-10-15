"""Pydantic 入门：定义、校验、看报错长什么样。

运行方式：uv run python learning/stage0/pydantic_intro.py
"""
from pydantic import BaseModel, ValidationError, ConfigDict, field_validator

class TravelRequirement(BaseModel):
    destination: str
    days: int
    budget_total_cny: float

    @field_validator("budget_total_cny", mode="before")
    @classmethod
    def parse_cn_amount(cls, v):
        """人类写法预处理：'1万' → 10000.0。mode='before' = 在 Pydantic 自己的类型转换之前先跑我"""
        if isinstance(v, str) and v.endswith("万"):
            return float(v[:-1]) * 10_000
        return v   # 不是"X万"格式就原样交还给 Pydantic 处理


# # ① 合法数据：正常通过，像访问对象属性一样用
# req = TravelRequirement(
#     destination="成都",
#     days=4,
#     budget_total_cny=10000,
# )
# print(f"通过校验：{req.destination} {req.days} 天，预算 {req.budget_total_cny} 元")

# # ② 非法数据：days 传了字符串，看 Pydantic 什么反应
# try:
#     TravelRequirement(destination="成都", days="4", budget_total_cny=10000)
# except ValidationError as e:
#     print("\n=== 校验失败，Pydantic 的报错 ===")
#     print(e)


try:
    req2 = TravelRequirement(destination="成都", days="4", budget_total_cny="1万")
    print(f"③ 通过！days={req2.days!r}，budget={req2.budget_total_cny!r}")
except ValidationError as e:
    print(f"③ 失败：{e.errors()[0]['type']}")


# ④ 严格模式：同样的数据还过得了吗？（贴在 try 块后面）
class StrictReq(TravelRequirement):
    model_config = ConfigDict(strict=True)

try:
    StrictReq(destination="成都", days="4", budget_total_cny=10000)
except ValidationError as e:
    print(f"\n④ 严格模式拒绝：{e.errors()[0]['type']}")