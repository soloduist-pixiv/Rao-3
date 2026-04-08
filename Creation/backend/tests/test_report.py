"""
报告接口测试（Report API tests / 报告测试）。

验证创建报告需要鉴权（auth required/需要登录）以及返回评估结果结构。
"""

from fastapi.testclient import TestClient


def _create_login_token(client: TestClient, username: str) -> str:
    """创建测试用户并登录（test login / 测试登录），返回 JWT（token/令牌）。"""
    client.post("/login/register", json={"username": username, "password": "secret123"})
    response = client.post("/login", json={"username": username, "password": "secret123"})
    body = response.json()
    return body["data"]["access_token"]


def test_create_report_success(client: TestClient) -> None:
    token = _create_login_token(client, "report_user1")
    payload = {
        "industryPrimary": "computer",
        "industrySecondary": "前端方向",
        "budget": "1000-3000",
        "rentTerm": "long",
        "rentMode": "online",
        "manpower": "1-3",
        "time投入": "31+",
        "profitPerCustomer": "20-30",
        "targetAudience": "school",
        "hasChannel": "yes",
        "differentiation": "has",
        "differentiationType": "network",
        "paybackPeriod": "10-30",
    }
    response = client.post(
        "/report",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    body = response.json()
    assert response.status_code == 201
    assert body["status_code"] == 201
    assert body["message"] == "问卷提交成功"
    assert body["data"]["username"] == "report_user1"
    assert body["data"]["report_id"] > 0
    assert body["data"]["analysis"]["total_score"] <= 100
    assert "industry_primary" in body["data"]["analysis"]["field_scores"]
    assert len(body["data"]["analysis"]["time_cost_points"]) >= 2
    assert len(body["data"]["analysis"]["time_profit_points"]) >= 2
    assert (
        body["data"]["analysis"]["time_cost_points"][0]["x"]
        == body["data"]["analysis"]["time_profit_points"][0]["x"]
    )


def test_create_report_fail_without_token(client: TestClient) -> None:
    response = client.post("/report", json={})
    assert response.status_code == 401
