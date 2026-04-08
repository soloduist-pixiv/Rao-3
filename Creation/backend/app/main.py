"""
FastAPI 应用入口（Entrypoint / 启动入口）。

负责创建 FastAPI app、挂载路由（router/路由）、配置中间件（middleware/中间件），并在启动阶段初始化数据库表。
"""

from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

if __package__ is None and __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root))

from app.api import api_router
from app.db.base import Base
from app.db.session import engine


def _ensure_backward_compatible_columns() -> None:
    """启动时做轻量兼容迁移（migration-lite/轻量迁移）：缺列则补齐。"""
    with engine.begin() as connection:
        schema_inspector = inspect(connection)
        existing_tables = set(schema_inspector.get_table_names())
        dialect_name = connection.dialect.name

        if "users" in existing_tables:
            user_columns = {item["name"] for item in schema_inspector.get_columns("users")}
            if "is_member" not in user_columns:
                if dialect_name == "postgresql":
                    connection.execute(text("ALTER TABLE users ADD COLUMN is_member BOOLEAN NOT NULL DEFAULT FALSE"))
                else:
                    connection.execute(text("ALTER TABLE users ADD COLUMN is_member BOOLEAN NOT NULL DEFAULT 0"))

        if "reports" in existing_tables:
            report_columns = {item["name"] for item in schema_inspector.get_columns("reports")}
            if "time_cost_points" not in report_columns:
                if dialect_name == "postgresql":
                    connection.execute(
                        text("ALTER TABLE reports ADD COLUMN time_cost_points JSONB NOT NULL DEFAULT '[]'::jsonb")
                    )
                else:
                    connection.execute(text("ALTER TABLE reports ADD COLUMN time_cost_points JSON NOT NULL DEFAULT '[]'"))
            if "time_profit_points" not in report_columns:
                if dialect_name == "postgresql":
                    connection.execute(
                        text("ALTER TABLE reports ADD COLUMN time_profit_points JSONB NOT NULL DEFAULT '[]'::jsonb")
                    )
                else:
                    connection.execute(text("ALTER TABLE reports ADD COLUMN time_profit_points JSON NOT NULL DEFAULT '[]'"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    """生命周期钩子（lifespan hook/生命周期）：启动建表并做补列。"""
    Base.metadata.create_all(bind=engine)
    _ensure_backward_compatible_columns()
    yield


app = FastAPI(title="Demo4 Auth Service", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8000")))


