"""
测试公共配置（Pytest fixtures / 测试夹具）。

为测试启用独立 SQLite 数据库（test database/测试库），并覆盖 FastAPI 的 get_db 依赖。
"""

from collections.abc import Generator

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./demo4_test.db"
os.environ["DATABASE_URL"] = SQLALCHEMY_TEST_DATABASE_URL

from app.db.base import Base
from app.db.session import get_db
from app.main import app

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


def override_get_db() -> Generator[Session, None, None]:
    """测试用 DB 会话（Testing DB session / 测试会话）。"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    """提供 TestClient（HTTP client/测试客户端），每次用例重建表结构。"""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
