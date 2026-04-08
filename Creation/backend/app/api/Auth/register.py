"""
注册接口（Register API / 注册接口）。

创建用户并存储密码哈希（password hash/密码哈希），避免明文密码（plain password/明文）落库。
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.response import json_response
from app.core.security import hash_password
from app.db.session import get_db
from app.entity.user import User
from app.models.user import UserModel

router = APIRouter(prefix="/login", tags=["Auth"])


@router.post("/register")
def register(user: User, db: Session = Depends(get_db)) -> JSONResponse:
    """用户注册（Sign up / 注册）：成功返回用户信息。"""
    exists_user = db.scalar(select(UserModel).where(UserModel.username == user.username))
    if exists_user:
        return JSONResponse(
            status_code=400,
            content=json_response(status_code=400, message="账号已存在"),
        )

    new_user = UserModel(
        username=user.username,
        password_hash=hash_password(user.password),
        is_member=user.isMember,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return JSONResponse(
        status_code=201,
        content=json_response(
            status_code=201,
            message="注册成功",
            data={
                "user_id": new_user.id,
                "username": new_user.username,
                "is_member": new_user.is_member,
            },
        ),
    )
