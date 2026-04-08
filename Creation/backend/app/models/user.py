"""
用户表 ORM（User ORM model / 用户表模型）。

使用 SQLAlchemy ORM（Object-Relational Mapping/对象关系映射）定义 users 表结构。
"""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserModel(Base):
    """users 表映射（table mapping/表映射）。"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_member: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
