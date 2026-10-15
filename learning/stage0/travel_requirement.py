"""TravelRequirement：旅行需求的结构化模型（阶段 0 毕业版）。

这是项目的第一块核心砖：用户的自然语言需求被 LLM 解析成 JSON 后，
必须通过本模型校验才算合法。阶段 1 会把它接进 RequirementParser。

运行自测：uv run python learning/stage0/travel_requirement.py
"""
from enum import Enum

from pydantic import BaseModel, Field, ValidationError


class Pace(str, Enum):
    """游玩节奏（游玩模式）"""

    relaxed = "relaxed"  # 休闲慢节奏：一天 2~3 个点
    normal = "normal"  # 常规：一天 3~4 个点
    intense = "intense"  # 特种兵：一天 5 个点以上


class Party(BaseModel):
    """出行人员构成（嵌套模型：模型套模型）"""

    adults: int = Field(ge=1, description="成人数，至少 1")
    children: int = Field(default=0, ge=0, description="儿童数")


class TravelRequirement(BaseModel):
    """一次旅行规划的结构化需求

    设计原则：必填字段越少越好——LLM 少写一个字段就少一个出错点，
    拿不准的字段一律 Optional + 默认值。
    """

    origin_city: str = Field(description="出发城市")

    # 可空：目的地没定 = None，上层流程据此走"目的地推荐"而不是规划
    destination: str | None = Field(default=None, description="目的地；None=未定，走推荐流程")

    # 约束：Field(ge=1, le=30) 挡住"0 天游""365 天游"这类 LLM 可能编出的数字
    days: int = Field(ge=1, le=30, description="旅行天数")

    # 约束只能挡"数学上错误"（负数），挡不住"荒谬但合法"（100 元玩 7 天）——那是业务规则的事
    budget_total_cny: float | None = Field(default=None, ge=0, description="总预算（元）")

    # default_factory：列表/嵌套模型这类可变对象必须用工厂函数给默认值，
    # 不能写 =[] （否则所有实例会共享同一个列表——经典大坑）
    party: Party = Field(default_factory=lambda: Party(adults=1), description="出行人员，默认 1 成人")
    pace: Pace = Field(default=Pace.normal, description="游玩节奏，默认常规")

    preferences: list[str] = Field(default_factory=list, description="偏好标签：美食/亲子/自然/人文...")
    must_go: list[str] = Field(default_factory=list, description="必去清单")
    avoid: list[str] = Field(default_factory=list, description="排除清单")
    notes: str | None = Field(default=None, description="自由备注")


if __name__ == "__main__":
    # ① 完整合法数据（注意 party 传的是 dict，嵌套模型自动转换；
    #    pace 传字符串，宽限模式下自动转成枚举）
    full = TravelRequirement(
        origin_city="杭州",
        destination="成都",
        days=4,
        budget_total_cny=10000,
        party={"adults": 2, "children": 1},
        pace="relaxed",
        preferences=["美食", "亲子"],
        must_go=["大熊猫基地"],
        avoid=["夜店"],
        notes="带孩子，别太累",
    )
    print(f"① 通过：{full.destination} {full.days} 天，节奏={full.pace.value}，"
          f"{full.party.adults}大{full.party.children}小")

    # ② 只填必填字段：所有默认值应生效
    minimal = TravelRequirement(origin_city="杭州", days=3)
    print(f"② 通过：目的地={minimal.destination}，预算={minimal.budget_total_cny}，"
          f"节奏={minimal.pace.value}，人员={minimal.party.adults}大{minimal.party.children}小")

    # ③ 非法枚举值：三个合法值之外
    try:
        TravelRequirement(origin_city="杭州", days=3, pace="特种兵")
    except ValidationError as e:
        print(f"③ 拒绝：{e.errors()[0]['type']}（详细：{e.errors()[0]['msg']}）")

    # ④ 违反约束：days=0
    try:
        TravelRequirement(origin_city="杭州", days=0)
    except ValidationError as e:
        print(f"④ 拒绝：{e.errors()[0]['type']}（详细：{e.errors()[0]['msg']}）")
