"""
认证模块路由导出（Auth routers export / 认证路由导出）。

用于把登录与注册路由（login/register routers/登录注册路由）集中对外暴露。
"""

from .login import router as login_router
from .register import router as register_router

__all__ = ["login_router", "register_router"]
