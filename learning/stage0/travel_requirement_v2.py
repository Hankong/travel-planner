"""TravelRequirement v2：用「时间窗」替代裸天数（回应真实场景：
用户不说"玩 3 天"，说的是"周五晚下班出发，周一要上班"）。

对比 v1 学习三个新东西：
1. datetime 字段：Pydantic 宽限模式能把 ISO 字符串自动转成 datetime
2. model_validator(mode="after")：跨字段校验（所有字段各自合法之后，
   检查字段之间的关系）——业务级校验的雏形
3. @property 派生属性：夜数/游玩天数由程序从时间窗推导，不让 LLM 填
   ——原则：schema 放原料，程序算成品

运行自测：uv run python learning/stage0/travel_requirement_v2.py
"""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ValidationError, model_validator


class Pace(str, Enum):
    relaxed = "relaxed"
    normal = "normal"
    intense = "intense"


class Party(BaseModel):
    adults: int = Field(ge=1, description="成人数")
    children: int = Field(default=0, ge=0, description="儿童数")


class TravelRequirement(BaseModel):
    origin_city: str = Field(description="出发城市")
    destination: str | None = Field(default=None, description="目的地；None=走推荐流程")

    # —— 时间窗：建模用户说的话 ——
    depart_after: datetime | None = Field(default=None, description="最早出发时刻")
    return_before: datetime | None = Field(default=None, description="最晚返回时刻")
    # days 降级为兜底字段：用户只说"玩3天"给不出时刻时才用它
    days: int | None = Field(default=None, ge=1, le=30, description="兜底：无法给出时刻窗时才填")

    budget_total_cny: float | None = Field(default=None, ge=0)
    party: Party = Field(default_factory=lambda: Party(adults=1))
    pace: Pace = Field(default=Pace.normal)
    preferences: list[str] = Field(default_factory=list)
    must_go: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    notes: str | None = Field(default=None, description="只装结构化不了的残余")

    @model_validator(mode="after")
    def check_time_consistency(self):
        """跨字段校验：时刻窗和兜底天数至少有一个；窗内先后顺序要合理"""
        if self.depart_after is None and self.return_before is None and self.days is None:
            raise ValueError("出发/返回时刻与天数至少提供其一")
        if self.depart_after and self.return_before and self.return_before <= self.depart_after:
            raise ValueError("返回时刻必须晚于出发时刻")
        return self

    # —— 派生属性：程序算，LLM 无权填写 ——
    @property
    def nights(self) -> int | None:
        """在外过夜数 = 酒店晚数。周五晚去周日晚回 = 2 晚"""
        if self.depart_after and self.return_before:
            return max((self.return_before.date() - self.depart_after.date()).days, 0)
        return None

    @property
    def play_days(self) -> float | None:
        """有效游玩天数 = 总时长扣掉睡眠后折算。行程编排的排程依据"""
        if self.depart_after and self.return_before:
            total_h = (self.return_before - self.depart_after).total_seconds() / 3600
            awake_h = max(total_h - (self.nights or 0) * 8, 0)  # 粗估每晚睡 8 小时
            return round(awake_h / 24, 1)
        return None


if __name__ == "__main__":
    # ⑤ 用户的真实场景：周五晚出发，周日晚回（2026-10-16 恰好是周五）
    weekend = TravelRequirement(
        origin_city="杭州",
        destination="上海",
        depart_after="2026-10-16 19:30",
        return_before="2026-10-18 22:00",
        party={"adults": 1},
        notes="不想起太早",
    )
    print(f"⑤ 日历天：3（周五/六/日），过夜：{weekend.nights} 晚，"
          f"有效游玩：{weekend.play_days} 天")

    # ⑥ 日期写反了：跨字段校验应当拦下
    try:
        TravelRequirement(
            origin_city="杭州",
            depart_after="2026-10-18 22:00",
            return_before="2026-10-16 19:30",
        )
    except ValidationError as e:
        print(f"⑥ 拒绝：{e.errors()[0]['msg']}")

    # ⑦ 只说"玩3天"、给不出时刻：兜底 days 生效
    vague = TravelRequirement(origin_city="杭州", days=3)
    print(f"⑦ 兜底：days={vague.days}，夜数={vague.nights}（时刻窗缺失，派生值为 None）")
