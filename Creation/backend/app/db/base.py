"""
SQLAlchemy 基类（SQLAlchemy Declarative Base / 声明式基类）。

所有 ORM Model（Object-Relational Mapping/对象关系映射）都继承自 Base，
并通过 Base.metadata 管理表结构（table metadata/表元数据）。
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """ORM 基类（Declarative base / 声明基类）。"""
