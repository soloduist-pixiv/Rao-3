"""
问卷请求体（Report payload / 报告请求体）。

用于接收前端问卷字段并做基础校验（validation/校验）。
"""

from pydantic import BaseModel, Field


class Report(BaseModel):
    """问卷数据模型（Report schema / 问卷模型）。"""
    industryPrimary: str = Field(default="")
    industrySecondary: str = Field(default="")
    budget: str = Field(default="")
    rentTerm: str = Field(default="")
    rentMode: str = Field(default="")
    manpower: str = Field(default="")
    time投入: str = Field(default="")
    time: str = Field(default="")
    profitPerCustomer: str = Field(default="")
    targetAudience: str = Field(default="")
    hasChannel: str = Field(default="")
    differentiation: str = Field(default="")
    differentiationType: str = Field(default="")
    paybackPeriod: str = Field(default="")
    timeCostPoints: list[dict[str, float]] = Field(default_factory=list)
    timeProfitPoints: list[dict[str, float]] = Field(default_factory=list)

    def resolve_time_input(self) -> str:
        """兼容字段（Backward compatibility/向后兼容）：time投入 优先，否则用 time。"""
        return self.time投入 or self.time
