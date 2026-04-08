"""
统一响应结构（Response schema / 响应结构）。

用一个固定字段的 dict 约定接口返回格式，便于前端处理（frontend consumption/前端处理）。
"""

from typing import Any


def json_response(status_code: int, message: str, data: Any = None) -> dict[str, Any]:
    """生成统一 JSON 响应体（Build response payload / 构建响应体）。"""
    return {"status_code": status_code, "message": message, "data": data}
