"""
认证接口测试（Auth API tests / 认证测试）。

覆盖注册与登录的成功/失败分支（happy path & error path/成功与错误分支）。
"""

from fastapi.testclient import TestClient


def test_register_success(client: TestClient) -> None:
    response = client.post(
        "/login/register", json={"username": "alice001", "password": "secret123"}
    )
    body = response.json()
    assert response.status_code == 201
    assert body["status_code"] == 201
    assert body["message"] == "注册成功"
    assert body["data"]["username"] == "alice001"
    assert body["data"]["is_member"] is False


def test_register_fail_when_username_exists(client: TestClient) -> None:
    client.post("/login/register", json={"username": "bob001", "password": "secret123"})
    response = client.post(
        "/login/register", json={"username": "bob001", "password": "other123"}
    )
    body = response.json()
    assert response.status_code == 400
    assert body["status_code"] == 400
    assert body["message"] == "账号已存在"


def test_login_success(client: TestClient) -> None:
    client.post("/login/register", json={"username": "carol001", "password": "secret123"})
    response = client.post("/login", json={"username": "carol001", "password": "secret123"})
    body = response.json()
    assert response.status_code == 200
    assert body["status_code"] == 200
    assert body["message"] == "登录成功"
    assert "access_token" in body["data"]
    assert body["data"]["token_type"] == "bearer"
    assert body["data"]["is_member"] is False


def test_login_fail_with_wrong_password(client: TestClient) -> None:
    client.post("/login/register", json={"username": "david001", "password": "secret123"})
    response = client.post("/login", json={"username": "david001", "password": "badpass999"})
    body = response.json()
    assert response.status_code == 401
    assert body["status_code"] == 401
    assert body["message"] == "账号或密码错误"
