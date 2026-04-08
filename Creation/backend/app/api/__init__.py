"""
API 路由聚合（API router aggregation）。

把各子模块的 APIRouter（路由/Router）统一挂载到 api_router，供 main.py 引入。
"""

from fastapi import APIRouter

from .Auth.login import router as login_router
from .Auth.register import router as register_router
from .report import router as report_router

api_router = APIRouter()
api_router.include_router(login_router)
api_router.include_router(register_router)
api_router.include_router(report_router)
