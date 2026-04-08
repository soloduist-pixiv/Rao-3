"""
问卷评估工具（Report evaluator / 问卷评估）。

优先使用 LLM（Large Language Model/大语言模型）评估；当缺少依赖或密钥时使用规则（rules/规则）兜底。
输出统一结构，包含字段分数与两条曲线点（curve points/曲线点）。
"""

from __future__ import annotations

import json
import os
from math import floor
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.report import ReportModel

try:
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI
except ImportError:
    HumanMessage = None
    SystemMessage = None
    ChatOpenAI = None

    def tool(func):
        return func


REQUIRED_FIELDS = [
    "industry_primary",
    "industry_secondary",
    "budget",
    "rent_term",
    "rent_mode",
    "manpower",
    "time_input",
    "profit_per_customer",
    "target_audience",
    "has_channel",
    "differentiation",
    "differentiation_type",
    "payback_period",
]


class FieldScore(BaseModel):
    comment: str = Field(min_length=1, max_length=10)
    score: int = Field(ge=0, le=100)

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, value: str) -> str:
        return value.strip()[:10]


class CurvePoint(BaseModel):
    x: float = Field(ge=0)
    y: float = Field(ge=0)


class ReportEvaluation(BaseModel):
    field_scores: dict[str, FieldScore]
    total_score: int = Field(ge=0, le=100)
    overall_comment: str = Field(min_length=1, max_length=10)
    time_cost_points: list[CurvePoint] = Field(min_length=2)
    time_profit_points: list[CurvePoint] = Field(min_length=2)

    @model_validator(mode="after")
    def validate_total_score(self) -> "ReportEvaluation":
        missing_fields = [field for field in REQUIRED_FIELDS if field not in self.field_scores]
        if missing_fields:
            raise ValueError("field_scores 缺少必须字段")
        sum_score = sum(item.score for item in self.field_scores.values())
        if sum_score != self.total_score:
            raise ValueError("field_scores 的分数总和必须等于 total_score")
        if len(self.time_cost_points) != len(self.time_profit_points):
            raise ValueError("time_cost_points 和 time_profit_points 点数必须一致")
        cost_x = [point.x for point in self.time_cost_points]
        profit_x = [point.x for point in self.time_profit_points]
        if cost_x != sorted(cost_x) or profit_x != sorted(profit_x):
            raise ValueError("曲线坐标点 x 必须升序")
        if cost_x != profit_x:
            raise ValueError("两条曲线必须共享同一组 x 坐标")
        return self


@tool
def format_report_evaluation(payload: dict[str, Any]) -> str:
    """标准化评估结果并输出 JSON 字符串。"""
    normalized = ReportEvaluation.model_validate(payload)
    return normalized.model_dump_json(ensure_ascii=False)


class ChatWithReport:
    """问卷评估入口（Evaluator facade/评估入口）：封装 LLM 与规则评估。"""
    def __init__(
        self,
        model_name: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com/v1",
        api_key: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.4,
    ):
        resolved_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.use_llm = (
            ChatOpenAI is not None
            and HumanMessage is not None
            and SystemMessage is not None
            and bool(resolved_key)
        )
        if self.use_llm:
            self.model = ChatOpenAI(
                model=model_name,
                base_url=base_url,
                api_key=resolved_key,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            self.model_with_tools = self.model.bind_tools(
                [format_report_evaluation],
                tool_choice="format_report_evaluation",
            )
            self.system_message = SystemMessage(content=self._build_system_prompt())

    def _build_system_prompt(self) -> str:
        return (
            "你是创业可行性评估助手。"
            "你将收到数据库中的用户创业问卷。"
            "字段含义："
            "industry_primary=行业一级方向；"
            "industry_secondary=行业二级细分；"
            "budget=预算；"
            "rent_term=场地租期；"
            "rent_mode=场地形式；"
            "manpower=团队人力；"
            "time_input=投入周期；"
            "profit_per_customer=单客收益；"
            "target_audience=目标人群；"
            "has_channel=是否有渠道；"
            "differentiation=是否有差异化；"
            "differentiation_type=差异化类型；"
            "payback_period=回本周期。"
            "输出要求："
            "必须调用工具 format_report_evaluation。"
            "field_scores 中必须包含以上 13 个字段。"
            "每个字段给出 comment(10字以内) 和 score(0-100整数)。"
            "所有字段 score 之和必须等于 total_score。"
            "total_score 满分 100。"
            "overall_comment 10字以内。"
            "必须返回 time_cost_points 与 time_profit_points。"
            "两者均为点数组，每个点格式为 {x: 数值, y: 数值}。"
            "两条曲线点数一致，x 坐标一致且升序。"
            "分数建议体现可行性，越高越可行。"
        )

    def _query_latest_report(
        self,
        db: Session,
        user_id: int | None = None,
        username: str | None = None,
    ) -> ReportModel:
        stmt = select(ReportModel)
        if user_id is not None:
            stmt = stmt.where(ReportModel.user_id == user_id)
        elif username:
            stmt = stmt.where(ReportModel.username == username)
        else:
            raise ValueError("user_id 和 username 至少传一个")

        stmt = stmt.order_by(desc(ReportModel.created_at))
        report = db.scalar(stmt)
        if not report:
            raise ValueError("未找到该用户的问卷记录")
        return report

    def _build_report_payload(self, report: ReportModel) -> dict[str, str]:
        return {
            "industry_primary": report.industry_primary,
            "industry_secondary": report.industry_secondary,
            "budget": report.budget,
            "rent_term": report.rent_term,
            "rent_mode": report.rent_mode,
            "manpower": report.manpower,
            "time_input": report.time_input,
            "profit_per_customer": report.profit_per_customer,
            "target_audience": report.target_audience,
            "has_channel": report.has_channel,
            "differentiation": report.differentiation,
            "differentiation_type": report.differentiation_type,
            "payback_period": report.payback_period,
        }

    def _rule_comment_score(self, field_name: str, field_value: str) -> FieldScore:
        value = field_value or ""
        scoring_rules: dict[str, dict[str, tuple[int, str]]] = {
            "industry_primary": {"": (2, "方向待定"), "default": (8, "方向清晰")},
            "industry_secondary": {"": (2, "细分缺失"), "default": (7, "细分明确")},
            "budget": {
                "0-200": (3, "预算偏低"),
                "200-1000": (5, "预算一般"),
                "1000-3000": (8, "预算合理"),
                "3000-10000": (8, "预算充足"),
                "10000+": (7, "投入较高"),
                "": (2, "预算未知"),
            },
            "rent_term": {"long": (6, "周期稳定"), "short": (5, "周期灵活"), "": (2, "租期未知")},
            "rent_mode": {"online": (6, "线上轻量"), "stall": (5, "地推可行"), "": (2, "形式未知")},
            "manpower": {"1-3": (6, "团队精简"), "3-5": (8, "人力适中"), "7+": (7, "人力充足"), "": (2, "人力未知")},
            "time_input": {"11-31": (5, "周期适中"), "31+": (6, "投入充分"), "": (2, "周期未知")},
            "profit_per_customer": {"0-10": (4, "客单偏低"), "10-15": (6, "收益一般"), "15-20": (8, "收益可观"), "20-30": (10, "收益较高"), "30+": (9, "收益很高"), "": (2, "收益未知")},
            "target_audience": {"school": (8, "客群聚焦"), "social": (6, "范围较广"), "nearby-school": (7, "客群稳定"), "office": (7, "支付较强"), "": (2, "客群未知")},
            "has_channel": {"yes": (9, "渠道已具备"), "no": (3, "渠道不足"), "": (2, "渠道未知")},
            "differentiation": {"has": (9, "优势清晰"), "none": (3, "同质风险"), "": (2, "优势未知")},
            "differentiation_type": {
                "network": (7, "人脉资源"),
                "storage": (7, "库存能力"),
                "location": (7, "位置优势"),
                "supply": (7, "供应稳固"),
                "": (2, "优势待补"),
            },
            "payback_period": {"10": (8, "回本很快"), "10-30": (7, "回本合理"), "30+": (4, "回本偏慢"), "": (2, "回本未知")},
        }
        field_rule = scoring_rules.get(field_name, {})
        score, comment = field_rule.get(value, field_rule.get("default", (5, "信息一般")))
        return FieldScore(comment=comment, score=score)

    def _normalize_scores(self, field_scores: dict[str, FieldScore]) -> tuple[dict[str, FieldScore], int]:
        raw_total = sum(item.score for item in field_scores.values())
        if raw_total <= 100:
            return field_scores, raw_total

        keys = list(field_scores.keys())
        scaled_values = [field_scores[key].score * 100 / raw_total for key in keys]
        base_values = [floor(value) for value in scaled_values]
        remain = 100 - sum(base_values)
        fractions = sorted(
            enumerate(scaled_values),
            key=lambda pair: pair[1] - floor(pair[1]),
            reverse=True,
        )
        for index, _ in fractions[:remain]:
            base_values[index] += 1

        normalized_scores: dict[str, FieldScore] = {}
        for idx, key in enumerate(keys):
            normalized_scores[key] = FieldScore(
                comment=field_scores[key].comment,
                score=int(base_values[idx]),
            )
        return normalized_scores, 100

    def _estimate_horizon_days(self, time_input: str) -> int:
        mapping = {
            "11-31": 30,
            "31+": 60,
        }
        return mapping.get(time_input, 21)

    def _generate_curve_points(self, report_payload: dict[str, str]) -> tuple[list[dict[str, float]], list[dict[str, float]]]:
        horizon_days = self._estimate_horizon_days(report_payload.get("time_input", ""))
        budget_value = {
            "0-200": 200,
            "200-1000": 1000,
            "1000-3000": 3000,
            "3000-10000": 10000,
            "10000+": 15000,
        }.get(report_payload.get("budget", ""), 800)
        unit_profit = {
            "0-10": 10,
            "10-15": 15,
            "15-20": 20,
            "20-30": 30,
            "30+": 40,
        }.get(report_payload.get("profit_per_customer", ""), 12)
        manpower_factor = {
            "1-3": 1.0,
            "3-5": 1.4,
            "7+": 1.8,
        }.get(report_payload.get("manpower", ""), 0.9)
        channel_factor = 1.25 if report_payload.get("has_channel", "") == "yes" else 0.85
        differentiation_factor = 1.15 if report_payload.get("differentiation", "") == "has" else 0.9
        audience_factor = {
            "school": 1.1,
            "nearby-school": 1.0,
            "office": 1.2,
            "social": 0.95,
        }.get(report_payload.get("target_audience", ""), 0.9)
        rent_factor = {
            "online": 0.85,
            "stall": 1.15,
        }.get(report_payload.get("rent_mode", ""), 1.0)

        startup_cost = budget_value * 0.45
        daily_cost = max(30.0, budget_value * 0.008 * rent_factor + 70 * manpower_factor)
        peak_daily_profit = unit_profit * 4.2 * manpower_factor * channel_factor * differentiation_factor * audience_factor

        points_count = 8
        days_step = horizon_days / (points_count - 1)
        x_values = [round(days_step * idx, 2) for idx in range(points_count)]

        time_cost_points: list[dict[str, float]] = []
        time_profit_points: list[dict[str, float]] = []
        cumulative_profit = 0.0

        for index, x_day in enumerate(x_values):
            if index == 0:
                cumulative_profit = 0.0
            else:
                prev_day = x_values[index - 1]
                interval_days = x_day - prev_day
                progress = min(1.0, x_day / max(1.0, horizon_days * 0.45))
                daily_profit = peak_daily_profit * progress
                cumulative_profit += daily_profit * interval_days

            current_cost = startup_cost + daily_cost * x_day
            time_cost_points.append({"x": x_day, "y": round(current_cost, 2)})
            time_profit_points.append({"x": x_day, "y": round(cumulative_profit, 2)})

        return time_cost_points, time_profit_points

    def _evaluate_with_rules(self, report_payload: dict[str, str]) -> dict[str, Any]:
        field_scores: dict[str, FieldScore] = {}
        for field_name in REQUIRED_FIELDS:
            field_value = report_payload.get(field_name, "")
            field_scores[field_name] = self._rule_comment_score(field_name, field_value)
        normalized_scores, total_score = self._normalize_scores(field_scores)
        if total_score >= 80:
            overall_comment = "可行性较高"
        elif total_score >= 60:
            overall_comment = "可行性中等"
        else:
            overall_comment = "需优化方案"
        time_cost_points, time_profit_points = self._generate_curve_points(report_payload)
        normalized = ReportEvaluation(
            field_scores=normalized_scores,
            total_score=total_score,
            overall_comment=overall_comment,
            time_cost_points=time_cost_points,
            time_profit_points=time_profit_points,
        )
        return normalized.model_dump(mode="json")

    def _evaluate_with_llm(self, report_payload: dict[str, str]) -> dict[str, Any]:
        human_message = HumanMessage(content=json.dumps(report_payload, ensure_ascii=False))
        response = self.model_with_tools.invoke([self.system_message, human_message])

        if getattr(response, "tool_calls", None):
            for tool_call in response.tool_calls:
                if tool_call.get("name") == "format_report_evaluation":
                    tool_result = format_report_evaluation.invoke(tool_call.get("args", {}))
                    return json.loads(tool_result)

        content = response.content if isinstance(response.content, str) else "{}"
        try:
            fallback_data = json.loads(content)
            tool_result = format_report_evaluation.invoke(fallback_data)
            return json.loads(tool_result)
        except Exception:
            return self._evaluate_with_rules(report_payload)

    def evaluate_report(self, report: ReportModel) -> dict[str, Any]:
        report_payload = self._build_report_payload(report)
        if self.use_llm:
            result = self._evaluate_with_llm(report_payload)
        else:
            result = self._evaluate_with_rules(report_payload)
        if isinstance(report.time_cost_points, list) and report.time_cost_points:
            result["time_cost_points"] = report.time_cost_points
        if isinstance(report.time_profit_points, list) and report.time_profit_points:
            result["time_profit_points"] = report.time_profit_points
        return result

    def evaluate_user_plan(
        self,
        db: Session,
        user_id: int | None = None,
        username: str | None = None,
    ) -> dict[str, Any]:
        report = self._query_latest_report(db=db, user_id=user_id, username=username)
        return self.evaluate_report(report)
    
