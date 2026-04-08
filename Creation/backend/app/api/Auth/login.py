"""
登录接口（Login API / 登录接口）。

校验用户密码（password verification/密码校验）并签发 JWT（Json Web Token/令牌）。
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.response import json_response
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.entity.user import User
from app.models.user import UserModel

router = APIRouter(prefix="/login", tags=["Auth"])


@router.post("")
def login(user: User, db: Session = Depends(get_db)) -> JSONResponse:
    """用户登录（Sign in / 登录）：成功返回 access_token（访问令牌）。"""
    db_user = db.scalar(select(UserModel).where(UserModel.username == user.username))
    if not db_user:
        return JSONResponse(
            status_code=401,
            content=json_response(status_code=401, message="账号或密码错误"),
        )

    valid_password = verify_password(user.password, db_user.password_hash)
    if not valid_password:
        return JSONResponse(
            status_code=401,
            content=json_response(status_code=401, message="账号或密码错误"),
        )

    access_token = create_access_token(subject=db_user.username)
    return JSONResponse(
        status_code=200,
        content=json_response(
            status_code=200,
            message="登录成功",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "is_member": db_user.is_member,
            },
        ),
    )
