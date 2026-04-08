"""
接口依赖（Dependencies / 依赖注入）。

集中放置 FastAPI Depends（Dependency Injection/依赖注入）相关的通用逻辑，例如获取当前用户。
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import UserModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserModel:
    """
    获取当前登录用户（Get current user / 获取当前用户）。

    - token: OAuth2 Bearer Token（Bearer 令牌）从请求头解析
    - db: 数据库会话（DB session / 数据库会话）
    """
    username = decode_access_token(token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效凭证")

    db_user = db.scalar(select(UserModel).where(UserModel.username == username))
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

    return db_user
