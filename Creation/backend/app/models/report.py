"""
报告表 ORM（Report ORM model / 报告表模型）。

存储用户提交的问卷（questionnaire/问卷）以及评估曲线（curve points/曲线点）。
"""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReportModel(Base):
    """reports 表映射（table mapping/表映射）。"""
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    industry_primary: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    industry_secondary: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    budget: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    rent_term: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    rent_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    manpower: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    time_input: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    profit_per_customer: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    target_audience: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    has_channel: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    differentiation: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    differentiation_type: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    payback_period: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    time_cost_points: Mapped[list[dict[str, float]]] = mapped_column(JSON, nullable=False, default=list, server_default="[]")
    time_profit_points: Mapped[list[dict[str, float]]] = mapped_column(JSON, nullable=False, default=list, server_default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
