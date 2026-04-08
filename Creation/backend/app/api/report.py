"""
问卷/报告接口（Report API / 报告接口）。

负责接收用户问卷数据，写入数据库，并触发评估逻辑（evaluation/评估）。
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.response import json_response
from app.db.session import get_db
from app.entity.report import Report
from app.models.report import ReportModel
from app.models.user import UserModel
from app.tool.chatWithReport import ChatWithReport

router = APIRouter(prefix="/report", tags=["Report"])


@router.post("")
def create_report(
    payload: Report,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> JSONResponse:
    """创建问卷报告（Create report / 创建报告）并返回评估结果（analysis/分析）。"""
    report = ReportModel(
        user_id=current_user.id,
        username=current_user.username,
        industry_primary=payload.industryPrimary,
        industry_secondary=payload.industrySecondary,
        budget=payload.budget,
        rent_term=payload.rentTerm,
        rent_mode=payload.rentMode,
        manpower=payload.manpower,
        time_input=payload.resolve_time_input(),
        profit_per_customer=payload.profitPerCustomer,
        target_audience=payload.targetAudience,
        has_channel=payload.hasChannel,
        differentiation=payload.differentiation,
        differentiation_type=payload.differentiationType,
        payback_period=payload.paybackPeriod,
    )
    db.add(report)
    analyzer = ChatWithReport()
    analysis = analyzer.evaluate_report(report)
    report.time_cost_points = analysis.get("time_cost_points", [])
    report.time_profit_points = analysis.get("time_profit_points", [])
    db.commit()
    db.refresh(report)

    return JSONResponse(
        status_code=201,
        content=json_response(
            status_code=201,
            message="问卷提交成功",
            data={
                "report_id": report.id,
                "user_id": current_user.id,
                "username": current_user.username,
                "analysis": analysis,
            },
        ),
    )
