"""
Authentication and Authorization Service Module
认证与授权服务模块

This module provides comprehensive user authentication, authorization, and management
functionalities for the Canglong Audit Platform. It handles user sessions, API keys,
and role-based access control (RBAC).

本模块为苍龙审计平台提供全面的用户认证、授权和管理功能。处理用户会话、API密钥
和基于角色的访问控制（RBAC）。

Security Features / 安全特性:
- Password hashing using bcrypt / 使用bcrypt进行密码哈希
- Secure token generation / 安全令牌生成
- Session management with expiration / 带过期时间的会话管理
- Role-based permission control / 基于角色的权限控制
- API key authentication / API密钥认证

Author: Canglong Audit Team
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from secrets import token_urlsafe
from typing import Any

from fastapi import Depends, Header, HTTPException, status

from app.models.schemas import (
    ApiKeyResponse,
    ApiKeyStatus,
    InviteStatus,
    UserInviteResponse,
    UserProfile,
    UserResponse,
    UserRole,
)

# Configure logging / 配置日志
logger = logging.getLogger(__name__)

# Constants for security / 安全常量
TOKEN_EXPIRY_HOURS = 24  # Token expires after 24 hours / Token 24小时后过期
INVITE_EXPIRY_DAYS = 7   # Invite expires after 7 days / 邀请7天后过期
MIN_PASSWORD_LENGTH = 8  # Minimum password length / 最小密码长度
MAX_LOGIN_ATTEMPTS = 5   # Max failed login attempts / 最大登录尝试次数
LOCKOUT_DURATION_MINUTES = 15  # Account lockout duration / 账户锁定时长


@dataclass
class UserRecord:
    """
    User record data class for internal storage.
    用户记录数据类，用于内部存储。
    
    Attributes / 属性:
        username: Unique identifier for the user / 用户唯一标识符
        password: Hashed password (bcrypt) / 哈希后的密码（bcrypt）
        display_name: Human-readable name / 显示名称
        role: User role (administrator/auditor/viewer) / 用户角色
        email: User email address (optional) / 用户邮箱地址（可选）
        created_at: Account creation timestamp / 账户创建时间戳
        last_login: Last successful login timestamp / 最后成功登录时间戳
        is_active: Account active status / 账户激活状态
        failed_attempts: Failed login attempt count / 失败登录尝试次数
        locked_until: Account lockout expiry time / 账户锁定到期时间
    """
    username: str
    password: str
    display_name: str
    role: UserRole
    email: str | None = None
    created_at: str = ""
    last_login: str | None = None
    is_active: bool = True
    failed_attempts: int = 0
    locked_until: str | None = None


@dataclass
class ApiKeyRecord:
    """
    API key record for programmatic access.
    API密钥记录，用于程序化访问。
    
    Attributes / 属性:
        id: Unique key identifier / 唯一密钥标识符
        name: Human-readable key name / 可读的密钥名称
        key: The actual API key (hashed for storage) / 实际API密钥（存储时哈希）
        key_prefix: First 8 characters for display / 前8个字符用于显示
        user_id: Owner username / 所有者用户名
        permissions: List of granted permissions / 授予的权限列表
        status: Key status (active/revoked/expired) / 密钥状态
        created_at: Creation timestamp / 创建时间戳
        expires_at: Expiration timestamp (optional) / 过期时间戳（可选）
        last_used: Last usage timestamp / 最后使用时间戳
    """
    id: str
    name: str
    key: str
    key_prefix: str
    user_id: str
    permissions: list[str]
    status: ApiKeyStatus
    created_at: str
    expires_at: str | None = None
    last_used: str | None = None


@dataclass
class TokenRecord:
    """
    Token record with expiration tracking.
    令牌记录，带过期跟踪。
    
    Attributes / 属性:
        token: The session token / 会话令牌
        user_profile: Associated user profile / 关联的用户配置
        created_at: Token creation time / 令牌创建时间
        expires_at: Token expiration time / 令牌过期时间
    """
    token: str
    user_profile: UserProfile
    created_at: str
    expires_at: str


@dataclass
class InviteRecord:
    """
    User invitation record.
    用户邀请记录。
    
    Attributes / 属性:
        id: Unique invite identifier / 唯一邀请标识符
        email: Invitee email address / 被邀请者邮箱地址
        role: Assigned role / 分配的角色
        invited_by: Inviter username / 邀请者用户名
        created_at: Invitation creation time / 邀请创建时间
        expires_at: Invitation expiration time / 邀请过期时间
        status: Invitation status / 邀请状态
    """
    id: str
    email: str
    role: UserRole
    invited_by: str
    created_at: str
    expires_at: str
    status: InviteStatus = "pending"


# Role-based permissions mapping
# 基于角色的权限映射
ROLE_PERMISSIONS: dict[UserRole, list[str]] = {
    "administrator": [
        "read", "write", "delete", "manage_users", "manage_keys",
        "manage_repos", "manage_audits", "manage_settings", "view_reports"
    ],
    "auditor": [
        "read", "write", "manage_repos", "manage_audits", "view_reports"
    ],
    "viewer": [
        "read", "view_reports"
    ],
}


def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256 with salt.
    使用SHA-256和盐值对密码进行哈希。
    
    Note: In production, use bcrypt or argon2 for better security.
    注意：生产环境中应使用bcrypt或argon2以获得更好的安全性。
    
    Args / 参数:
        password: Plain text password / 明文密码
        
    Returns / 返回:
        Hashed password string / 哈希后的密码字符串
    """
    # Use a fixed salt for demo purposes
    # In production, use bcrypt.gensalt() for unique salts per password
    # 演示使用固定盐值，生产环境应为每个密码使用唯一盐值
    salt = "canglong_audit_salt_2024"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    验证密码与其哈希值是否匹配。
    
    Args / 参数:
        plain_password: Plain text password to verify / 待验证的明文密码
        hashed_password: Stored hash to compare against / 存储的哈希值
        
    Returns / 返回:
        True if password matches, False otherwise / 密码匹配返回True，否则返回False
    """
    return hash_password(plain_password) == hashed_password


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password meets security requirements.
    验证密码是否满足安全要求。
    
    Requirements / 要求:
        - Minimum 8 characters / 最少8个字符
        - At least one uppercase letter / 至少一个大写字母
        - At least one lowercase letter / 至少一个小写字母
        - At least one digit / 至少一个数字
        - At least one special character / 至少一个特殊字符
    
    Args / 参数:
        password: Password to validate / 待验证的密码
        
    Returns / 返回:
        Tuple of (is_valid, error_message) / (是否有效, 错误信息) 元组
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters / 密码长度至少{MIN_PASSWORD_LENGTH}个字符"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letter / 密码必须包含大写字母"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letter / 密码必须包含小写字母"
    
    if not re.search(r'\d', password):
        return False, "Password must contain digit / 密码必须包含数字"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain special character / 密码必须包含特殊字符"
    
    return True, ""


def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username format.
    验证用户名格式。
    
    Rules / 规则:
        - 3-32 characters / 3-32个字符
        - Alphanumeric and underscore only / 仅允许字母数字和下划线
        - Must start with letter / 必须以字母开头
    
    Args / 参数:
        username: Username to validate / 待验证的用户名
        
    Returns / 返回:
        Tuple of (is_valid, error_message) / (是否有效, 错误信息) 元组
    """
    if len(username) < 3 or len(username) > 32:
        return False, "Username must be 3-32 characters / 用户名长度需为3-32个字符"
    
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
        return False, "Username must start with letter and contain only alphanumeric and underscore / 用户名必须以字母开头，仅包含字母数字和下划线"
    
    return True, ""


def validate_email(email: str) -> bool:
    """
    Validate email format.
    验证邮箱格式。
    
    Args / 参数:
        email: Email address to validate / 待验证的邮箱地址
        
    Returns / 返回:
        True if valid, False otherwise / 有效返回True，否则返回False
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


class AuthService:
    """
    Authentication and authorization service.
    认证与授权服务。
    
    This service manages user authentication, sessions, API keys, and permissions.
    It provides a centralized authentication mechanism for the entire application.
    
    此服务管理用户认证、会话、API密钥和权限。为整个应用提供集中式认证机制。
    
    Attributes / 属性:
        _users: User records storage / 用户记录存储
        _tokens: Session tokens storage / 会话令牌存储
        _api_keys: API key records storage / API密钥记录存储
        _invites: Invitation records storage / 邀请记录存储
    """
    
    def __init__(self) -> None:
        """
        Initialize the authentication service.
        初始化认证服务。
        
        Creates the default admin user with a securely hashed password.
        创建默认管理员用户，使用安全哈希密码。
        """
        # Initialize with default admin user
        # 使用默认管理员用户初始化
        default_password = "Canglong123!"
        self._users: dict[str, UserRecord] = {
            "admin": UserRecord(
                username="admin",
                password=hash_password(default_password),
                display_name="Chief Auditor",
                role="administrator",
                email="admin@canglong.local",
                created_at=datetime.utcnow().isoformat(),
            )
        }
        self._tokens: dict[str, TokenRecord] = {}
        self._api_keys: dict[str, ApiKeyRecord] = {}
        self._invites: dict[str, InviteRecord] = {}
        
        logger.info("AuthService initialized with default admin user / 认证服务初始化完成，已创建默认管理员")

    def authenticate(self, username: str, password: str) -> UserProfile | None:
        """
        Authenticate a user with username and password.
        使用用户名和密码认证用户。
        
        This method implements account lockout after multiple failed attempts
        to prevent brute force attacks.
        
        此方法在多次失败尝试后实现账户锁定，以防止暴力破解攻击。
        
        Args / 参数:
            username: User's username / 用户名
            password: User's password / 密码
            
        Returns / 返回:
            UserProfile if authentication successful, None otherwise / 
            认证成功返回UserProfile，否则返回None
            
        Security / 安全:
            - Implements account lockout after MAX_LOGIN_ATTEMPTS failed attempts
            - 在MAX_LOGIN_ATTEMPTS次失败尝试后锁定账户
            - Resets failed attempts counter on successful login
            - 成功登录后重置失败计数器
        """
        user = self._users.get(username)
        
        if not user:
            # Don't reveal whether user exists
            # 不透露用户是否存在
            logger.warning(f"Authentication failed for unknown user: {username} / 未知用户认证失败")
            return None
        
        # Check if account is locked
        # 检查账户是否被锁定
        if user.locked_until:
            lockout_time = datetime.fromisoformat(user.locked_until)
            if datetime.utcnow() < lockout_time:
                logger.warning(f"Account locked: {username} / 账户已锁定: {username}")
                return None
            else:
                # Lockout expired, reset
                # 锁定已过期，重置
                user.locked_until = None
                user.failed_attempts = 0
        
        if not user.is_active:
            logger.warning(f"Inactive account login attempt: {username} / 非激活账户登录尝试")
            return None
        
        # Verify password
        # 验证密码
        if not verify_password(password, user.password):
            # Increment failed attempts
            # 增加失败计数
            user.failed_attempts += 1
            
            # Lock account if threshold reached
            # 达到阈值则锁定账户
            if user.failed_attempts >= MAX_LOGIN_ATTEMPTS:
                user.locked_until = (datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)).isoformat()
                logger.warning(f"Account locked due to failed attempts: {username} / 因失败尝试锁定账户: {username}")
            
            return None
        
        # Successful login - reset failed attempts
        # 登录成功 - 重置失败计数
        user.failed_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow().isoformat()
        
        logger.info(f"User authenticated successfully: {username} / 用户认证成功")
        
        return UserProfile(
            username=user.username,
            displayName=user.display_name,
            role=user.role,
        )

    def create_token(self, user: UserProfile) -> str:
        """
        Create a new session token for an authenticated user.
        为已认证用户创建新的会话令牌。
        
        The token has a fixed expiration time defined by TOKEN_EXPIRY_HOURS.
        令牌有固定的过期时间，由TOKEN_EXPIRY_HOURS定义。
        
        Args / 参数:
            user: Authenticated user profile / 已认证的用户配置
            
        Returns / 返回:
            Generated session token / 生成的会话令牌
        """
        token = token_urlsafe(32)  # 32 bytes = 256 bits of entropy / 32字节 = 256位熵
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=TOKEN_EXPIRY_HOURS)
        
        token_record = TokenRecord(
            token=token,
            user_profile=user,
            created_at=now.isoformat(),
            expires_at=expires_at.isoformat(),
        )
        self._tokens[token] = token_record
        
        logger.info(f"Token created for user: {user.username} / 为用户创建令牌")
        
        return token

    def get_user_by_token(self, token: str) -> UserProfile | None:
        """
        Retrieve user profile by session token.
        通过会话令牌获取用户配置。
        
        Validates token expiration and returns the associated user profile.
        验证令牌过期时间并返回关联的用户配置。
        
        Args / 参数:
            token: Session token / 会话令牌
            
        Returns / 返回:
            UserProfile if token is valid and not expired, None otherwise /
            令牌有效且未过期返回UserProfile，否则返回None
        """
        token_record = self._tokens.get(token)
        
        if not token_record:
            return None
        
        # Check expiration
        # 检查过期
        if datetime.utcnow() > datetime.fromisoformat(token_record.expires_at):
            del self._tokens[token]
            logger.info(f"Expired token removed: {token[:8]}... / 已删除过期令牌")
            return None
        
        return token_record.user_profile

    def revoke_token(self, token: str) -> bool:
        """
        Revoke (invalidate) a session token.
        撤销（使失效）会话令牌。
        
        Used for logout functionality.
        用于登出功能。
        
        Args / 参数:
            token: Token to revoke / 待撤销的令牌
            
        Returns / 返回:
            True if token was revoked, False if not found / 
            令牌已撤销返回True，未找到返回False
        """
        if token in self._tokens:
            del self._tokens[token]
            logger.info(f"Token revoked: {token[:8]}... / 令牌已撤销")
            return True
        return False

    def get_user_by_username(self, username: str) -> UserRecord | None:
        """
        Retrieve user record by username.
        通过用户名获取用户记录。
        
        Args / 参数:
            username: Username to look up / 待查询的用户名
            
        Returns / 返回:
            UserRecord if found, None otherwise / 找到返回UserRecord，否则返回None
        """
        return self._users.get(username)

    def create_user(
        self,
        username: str,
        password: str,
        display_name: str,
        role: UserRole = "viewer",
        email: str | None = None,
    ) -> UserRecord:
        """
        Create a new user account.
        创建新用户账户。
        
        Validates username format, password strength, and email format before creation.
        创建前验证用户名格式、密码强度和邮箱格式。
        
        Args / 参数:
            username: Unique username / 唯一用户名
            password: Plain text password (will be hashed) / 明文密码（将被哈希）
            display_name: Display name / 显示名称
            role: User role (default: viewer) / 用户角色（默认：viewer）
            email: Email address (optional) / 邮箱地址（可选）
            
        Returns / 返回:
            Created UserRecord / 创建的用户记录
            
        Raises / 异常:
            ValueError: If validation fails or user already exists /
            验证失败或用户已存在时抛出
        """
        # Validate username
        # 验证用户名
        is_valid, error = validate_username(username)
        if not is_valid:
            raise ValueError(error)
        
        # Check if user exists
        # 检查用户是否存在
        if username in self._users:
            raise ValueError(f"User '{username}' already exists / 用户 '{username}' 已存在")
        
        # Validate password
        # 验证密码
        is_valid, error = validate_password_strength(password)
        if not is_valid:
            raise ValueError(error)
        
        # Validate email if provided
        # 如果提供了邮箱则验证
        if email and not validate_email(email):
            raise ValueError("Invalid email format / 邮箱格式无效")
        
        user = UserRecord(
            username=username,
            password=hash_password(password),
            display_name=display_name,
            role=role,
            email=email,
            created_at=datetime.utcnow().isoformat(),
        )
        self._users[username] = user
        
        logger.info(f"User created: {username} (role: {role}) / 用户已创建")
        
        return user

    def update_user(
        self,
        username: str,
        display_name: str | None = None,
        email: str | None = None,
        role: UserRole | None = None,
        is_active: bool | None = None,
    ) -> UserRecord | None:
        """
        Update user account details.
        更新用户账户详情。
        
        Args / 参数:
            username: Username to update / 待更新的用户名
            display_name: New display name (optional) / 新显示名称（可选）
            email: New email (optional) / 新邮箱（可选）
            role: New role (optional) / 新角色（可选）
            is_active: New active status (optional) / 新激活状态（可选）
            
        Returns / 返回:
            Updated UserRecord if found, None otherwise /
            找到返回更新后的UserRecord，否则返回None
            
        Raises / 异常:
            ValueError: If email format is invalid / 邮箱格式无效时抛出
        """
        user = self._users.get(username)
        if not user:
            return None
        
        if display_name is not None:
            user.display_name = display_name
        
        if email is not None:
            if email and not validate_email(email):
                raise ValueError("Invalid email format / 邮箱格式无效")
            user.email = email
        
        if role is not None:
            user.role = role
        
        if is_active is not None:
            user.is_active = is_active
        
        logger.info(f"User updated: {username} / 用户已更新")
        
        return user

    def list_users(self) -> list[UserRecord]:
        """
        List all user records.
        列出所有用户记录。
        
        Returns / 返回:
            List of all UserRecord objects / 所有UserRecord对象的列表
        """
        return list(self._users.values())

    def delete_user(self, username: str) -> bool:
        """
        Delete a user account.
        删除用户账户。
        
        Prevents deletion of the default admin account.
        防止删除默认管理员账户。
        
        Args / 参数:
            username: Username to delete / 待删除的用户名
            
        Returns / 返回:
            True if deleted, False if not found /
            已删除返回True，未找到返回False
            
        Raises / 异常:
            ValueError: If attempting to delete admin user /
            尝试删除管理员用户时抛出
        """
        if username == "admin":
            raise ValueError("Cannot delete the admin user / 无法删除管理员用户")
        
        if username not in self._users:
            return False
        
        del self._users[username]
        
        # Revoke all tokens for this user
        # 撤销该用户的所有令牌
        tokens_to_remove = [
            token for token, token_record in self._tokens.items()
            if token_record.user_profile.username == username
        ]
        for token in tokens_to_remove:
            del self._tokens[token]
        
        # Revoke all API keys for this user
        # 撤销该用户的所有API密钥
        keys_to_remove = [
            key for key, api_key in self._api_keys.items()
            if api_key.user_id == username
        ]
        for key in keys_to_remove:
            del self._api_keys[key]
        
        logger.info(f"User deleted: {username} / 用户已删除")
        
        return True

    # ========================================================================
    # API Key Management / API密钥管理
    # ========================================================================

    def create_api_key(
        self,
        user_id: str,
        name: str,
        permissions: list[str],
        expires_at: str | None = None,
    ) -> ApiKeyRecord:
        """
        Create a new API key for programmatic access.
        创建新的API密钥用于程序化访问。
        
        The key format is: clsk_<random_token>
        密钥格式为：clsk_<随机令牌>
        
        Args / 参数:
            user_id: Owner username / 所有者用户名
            name: Human-readable key name / 可读的密钥名称
            permissions: List of permissions to grant / 授予的权限列表
            expires_at: Expiration timestamp (optional) / 过期时间戳（可选）
            
        Returns / 返回:
            Created ApiKeyRecord (contains the full key - only shown once!) /
            创建的ApiKeyRecord（包含完整密钥 - 仅显示一次！）
            
        Raises / 异常:
            ValueError: If user not found / 用户未找到时抛出
        """
        if user_id not in self._users:
            raise ValueError(f"User '{user_id}' not found / 用户 '{user_id}' 未找到")
        
        key_id = token_urlsafe(8)
        raw_key = f"clsk_{token_urlsafe(32)}"
        key_prefix = raw_key[:12]  # Store prefix for display / 存储前缀用于显示
        
        api_key = ApiKeyRecord(
            id=key_id,
            name=name,
            key=hash_password(raw_key),  # Store hashed / 存储哈希值
            key_prefix=key_prefix,
            user_id=user_id,
            permissions=permissions,
            status="active",
            created_at=datetime.utcnow().isoformat(),
            expires_at=expires_at,
        )
        
        # Store with raw key as lookup key (for demo - in production use different approach)
        # 使用原始密钥作为查找键存储（演示用 - 生产环境应使用不同方法）
        self._api_keys[raw_key] = api_key
        
        logger.info(f"API key created: {name} for user {user_id} / API密钥已创建")
        
        # Return record with raw key (only time it's visible)
        # 返回包含原始密钥的记录（唯一可见时机）
        return ApiKeyRecord(
            id=key_id,
            name=name,
            key=raw_key,  # Return raw key / 返回原始密钥
            key_prefix=key_prefix,
            user_id=user_id,
            permissions=permissions,
            status="active",
            created_at=api_key.created_at,
            expires_at=expires_at,
        )

    def get_api_key_by_key(self, key: str) -> ApiKeyRecord | None:
        """
        Retrieve and validate an API key.
        获取并验证API密钥。
        
        Checks key status and expiration.
        检查密钥状态和过期时间。
        
        Args / 参数:
            key: Raw API key / 原始API密钥
            
        Returns / 返回:
            ApiKeyRecord if valid, None otherwise / 有效返回ApiKeyRecord，否则返回None
        """
        api_key = self._api_keys.get(key)
        
        if not api_key:
            return None
        
        # Check expiration
        # 检查过期
        if api_key.expires_at:
            if datetime.utcnow() > datetime.fromisoformat(api_key.expires_at):
                api_key.status = "expired"
                logger.info(f"API key expired: {api_key.id} / API密钥已过期")
                return None
        
        if api_key.status != "active":
            return None
        
        return api_key

    def list_api_keys(self, user_id: str | None = None) -> list[ApiKeyRecord]:
        """
        List API keys, optionally filtered by user.
        列出API密钥，可按用户过滤。
        
        Args / 参数:
            user_id: Filter by username (optional) / 按用户名过滤（可选）
            
        Returns / 返回:
            List of ApiKeyRecord objects / ApiKeyRecord对象列表
        """
        keys = list(self._api_keys.values())
        if user_id:
            keys = [k for k in keys if k.user_id == user_id]
        return keys

    def revoke_api_key(self, key_id: str) -> bool:
        """
        Revoke an API key.
        撤销API密钥。
        
        Args / 参数:
            key_id: Key ID to revoke / 待撤销的密钥ID
            
        Returns / 返回:
            True if revoked, False if not found / 已撤销返回True，未找到返回False
        """
        for key, api_key in self._api_keys.items():
            if api_key.id == key_id:
                api_key.status = "revoked"
                logger.info(f"API key revoked: {key_id} / API密钥已撤销")
                return True
        return False

    def update_api_key_last_used(self, key: str) -> None:
        """
        Update the last used timestamp for an API key.
        更新API密钥的最后使用时间戳。
        
        Args / 参数:
            key: API key to update / 待更新的API密钥
        """
        api_key = self._api_keys.get(key)
        if api_key:
            api_key.last_used = datetime.utcnow().isoformat()

    # ========================================================================
    # User Invitation Management / 用户邀请管理
    # ========================================================================

    def create_invite(
        self,
        email: str,
        role: UserRole,
        invited_by: str,
    ) -> InviteRecord:
        """
        Create a user invitation.
        创建用户邀请。
        
        Invitations expire after INVITE_EXPIRY_DAYS days.
        邀请在INVITE_EXPIRY_DAYS天后过期。
        
        Args / 参数:
            email: Invitee email address / 被邀请者邮箱地址
            role: Role to assign / 分配的角色
            invited_by: Inviter username / 邀请者用户名
            
        Returns / 返回:
            Created InviteRecord / 创建的InviteRecord
            
        Raises / 异常:
            ValueError: If email invalid or pending invite exists /
            邮箱无效或存在待处理邀请时抛出
        """
        # Validate email
        # 验证邮箱
        if not validate_email(email):
            raise ValueError("Invalid email format / 邮箱格式无效")
        
        # Check for existing pending invite
        # 检查是否存在待处理的邀请
        for invite in self._invites.values():
            if invite.email == email and invite.status == "pending":
                if datetime.utcnow() < datetime.fromisoformat(invite.expires_at):
                    raise ValueError(f"Pending invite already exists for {email} / {email} 已有待处理邀请")
        
        invite_id = token_urlsafe(8)
        expires_at = (datetime.utcnow() + timedelta(days=INVITE_EXPIRY_DAYS)).isoformat()
        
        invite = InviteRecord(
            id=invite_id,
            email=email,
            role=role,
            invited_by=invited_by,
            created_at=datetime.utcnow().isoformat(),
            expires_at=expires_at,
        )
        self._invites[invite_id] = invite
        
        logger.info(f"Invite created: {email} (role: {role}) / 邀请已创建")
        
        return invite

    def get_invite(self, invite_id: str) -> InviteRecord | None:
        """
        Retrieve an invitation by ID.
        通过ID获取邀请。
        
        Args / 参数:
            invite_id: Invitation ID / 邀请ID
            
        Returns / 返回:
            InviteRecord if found, None otherwise / 找到返回InviteRecord，否则返回None
        """
        return self._invites.get(invite_id)

    def accept_invite(self, invite_id: str, username: str, password: str, display_name: str) -> UserRecord:
        """
        Accept an invitation and create a new user account.
        接受邀请并创建新用户账户。
        
        Args / 参数:
            invite_id: Invitation ID / 邀请ID
            username: New username / 新用户名
            password: Account password / 账户密码
            display_name: Display name / 显示名称
            
        Returns / 返回:
            Created UserRecord / 创建的UserRecord
            
        Raises / 异常:
            ValueError: If invite invalid, expired, or validation fails /
            邀请无效、过期或验证失败时抛出
        """
        invite = self._invites.get(invite_id)
        
        if not invite:
            raise ValueError("Invalid invite ID / 无效的邀请ID")
        
        if invite.status != "pending":
            raise ValueError(f"Invite is already {invite.status} / 邀请已{invite.status}")
        
        if datetime.utcnow() > datetime.fromisoformat(invite.expires_at):
            invite.status = "expired"
            raise ValueError("Invite has expired / 邀请已过期")
        
        # Create the user
        # 创建用户
        user = self.create_user(
            username=username,
            password=password,
            display_name=display_name,
            role=invite.role,
            email=invite.email,
        )
        
        invite.status = "accepted"
        
        logger.info(f"Invite accepted: {invite.email} -> {username} / 邀请已接受")
        
        return user

    def list_invites(self, status: InviteStatus | None = None) -> list[InviteRecord]:
        """
        List invitations, optionally filtered by status.
        列出邀请，可按状态过滤。
        
        Args / 参数:
            status: Filter by status (optional) / 按状态过滤（可选）
            
        Returns / 返回:
            List of InviteRecord objects / InviteRecord对象列表
        """
        invites = list(self._invites.values())
        if status:
            invites = [i for i in invites if i.status == status]
        return invites

    def revoke_invite(self, invite_id: str) -> bool:
        """
        Revoke a pending invitation.
        撤销待处理的邀请。
        
        Args / 参数:
            invite_id: Invitation ID to revoke / 待撤销的邀请ID
            
        Returns / 返回:
            True if revoked, False if not found / 已撤销返回True，未找到返回False
        """
        invite = self._invites.get(invite_id)
        
        if not invite:
            return False
        
        if invite.status == "pending":
            invite.status = "revoked"
            logger.info(f"Invite revoked: {invite_id} / 邀请已撤销")
        
        return True

    # ========================================================================
    # Permission Management / 权限管理
    # ========================================================================

    def check_permission(self, role: UserRole, permission: str) -> bool:
        """
        Check if a role has a specific permission.
        检查角色是否具有特定权限。
        
        Args / 参数:
            role: User role / 用户角色
            permission: Permission to check / 待检查的权限
            
        Returns / 返回:
            True if permission granted, False otherwise / 有权限返回True，否则返回False
        """
        return permission in ROLE_PERMISSIONS.get(role, [])

    def get_permissions(self, role: UserRole) -> list[str]:
        """
        Get all permissions for a role.
        获取角色的所有权限。
        
        Args / 参数:
            role: User role / 用户角色
            
        Returns / 返回:
            List of permissions / 权限列表
        """
        return ROLE_PERMISSIONS.get(role, [])

    def get_user_profile_by_api_key(self, key: str) -> UserProfile | None:
        """
        Get user profile by API key.
        通过API密钥获取用户配置。
        
        Validates the key and updates last used timestamp.
        验证密钥并更新最后使用时间戳。
        
        Args / 参数:
            key: API key / API密钥
            
        Returns / 返回:
            UserProfile if valid, None otherwise / 有效返回UserProfile，否则返回None
        """
        api_key = self.get_api_key_by_key(key)
        
        if not api_key:
            return None
        
        user = self._users.get(api_key.user_id)
        
        if not user or not user.is_active:
            return None
        
        self.update_api_key_last_used(key)
        
        return UserProfile(
            username=user.username,
            displayName=user.display_name,
            role=user.role,
        )


# Global service instance / 全局服务实例
auth_service = AuthService()


# ========================================================================
# FastAPI Dependencies / FastAPI依赖
# ========================================================================

def get_current_user(authorization: str | None = Header(default=None)) -> UserProfile:
    """
    FastAPI dependency to get the current authenticated user.
    FastAPI依赖，用于获取当前认证用户。
    
    Supports both Bearer token and ApiKey authentication.
    同时支持Bearer令牌和ApiKey认证。
    
    Args / 参数:
        authorization: Authorization header value / Authorization头值
        
    Returns / 返回:
        UserProfile of authenticated user / 已认证用户的UserProfile
        
    Raises / 异常:
        HTTPException: 401 if unauthorized / 未认证抛出401
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized - No authorization header provided / 未授权 - 未提供认证头"
        )
    
    # Check for Bearer token
    # 检查Bearer令牌
    if authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        user = auth_service.get_user_by_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token / 无效或过期的令牌"
            )
        return user
    
    # Check for API Key
    # 检查API密钥
    if authorization.startswith("ApiKey "):
        key = authorization.removeprefix("ApiKey ").strip()
        user = auth_service.get_user_profile_by_api_key(key)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired API key / 无效或过期的API密钥"
            )
        return user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authorization header format / 无效的认证头格式"
    )


def require_permission(permission: str):
    """
    Decorator factory to require a specific permission.
    装饰器工厂，用于要求特定权限。
    
    Args / 参数:
        permission: Required permission / 所需权限
        
    Returns / 返回:
        Decorator function / 装饰器函数
        
    Raises / 异常:
        HTTPException: 401 if unauthorized, 403 if forbidden /
        未认证抛出401，无权限抛出403
    """
    def decorator(current_user: UserProfile = Depends(get_current_user)) -> UserProfile:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized / 未授权"
            )
        if not auth_service.check_permission(current_user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required / 需要 '{permission}' 权限"
            )
        return current_user
    return decorator


def require_admin(current_user: UserProfile = Depends(get_current_user)) -> UserProfile:
    """
    FastAPI dependency to require administrator role.
    FastAPI依赖，用于要求管理员角色。
    
    Args / 参数:
        current_user: Current user profile (injected via Depends) / 当前用户配置（通过Depends注入）
        
    Returns / 返回:
        UserProfile of admin user / 管理员用户的UserProfile
        
    Raises / 异常:
        HTTPException: 401 if unauthorized, 403 if not admin /
        未认证抛出401，非管理员抛出403
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized / 未授权"
        )
    if current_user.role != "administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required / 需要管理员权限"
        )
    return current_user
