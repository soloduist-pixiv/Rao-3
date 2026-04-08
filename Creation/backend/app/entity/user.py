"""
请求/响应实体（Pydantic schema / 数据模型）。

用于接口参数校验（validation/校验），区别于数据库 ORM Model（ORM/对象关系映射）。
"""

from pydantic import BaseModel, Field


class User(BaseModel):
    """用户输入模型（User payload / 用户请求体）。"""
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    isMember: bool = Field(default=False)
