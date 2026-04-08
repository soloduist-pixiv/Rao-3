"""
安全相关工具（Security utilities / 安全工具）。

- Password hashing: PBKDF2（Password-Based Key Derivation Function/口令派生函数）
- Token: JWT（JSON Web Token/令牌）
"""

import os
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
HASH_ITERATIONS = 100_000
HASH_ALGORITHM = "sha256"

# 加密密码（Hash password / 密码哈希）
def hash_password(password: str) -> str:
    """生成带 salt 的 PBKDF2 哈希字符串（PBKDF2 hash with salt / 带盐哈希）。"""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        HASH_ALGORITHM, password.encode("utf-8"), salt.encode("utf-8"), HASH_ITERATIONS
    ).hex()
    return f"pbkdf2_sha256${HASH_ITERATIONS}${salt}${digest}"

# 验证密码（Verify password / 密码校验）
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码是否匹配存储哈希（verify plaintext vs stored hash / 校验明文与哈希）。"""
    try:
        method, iterations, salt, digest = hashed_password.split("$")
    except ValueError:
        return False
    if method != "pbkdf2_sha256":
        return False
    expected_digest = hashlib.pbkdf2_hmac(
        HASH_ALGORITHM,
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    ).hex()
    return hmac.compare_digest(expected_digest, digest)


def create_access_token(subject: str) -> str:
    """创建 JWT 访问令牌（Create JWT access token / 创建访问令牌）。"""
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire_at}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """解析并验证 JWT（Decode & verify JWT / 解析并验签）：成功返回 sub。"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
    subject = payload.get("sub")
    if not isinstance(subject, str):
        return None
    return subject
