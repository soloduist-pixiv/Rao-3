"""
数据库连接与会话（Database session / 数据库会话）。

- engine: SQLAlchemy Engine（连接引擎）
- SessionLocal: sessionmaker（会话工厂）
- get_db: FastAPI Depends 用的会话依赖（dependency/依赖）
"""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:123456@localhost:5432/demo4_auth")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """提供数据库会话（Provide DB session / 提供会话），请求结束自动关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
