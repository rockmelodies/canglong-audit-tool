"""
User Management API Router
用户管理API路由

This module provides REST API endpoints for user management, including:
本模块提供用户管理的REST API端点，包括：

- User CRUD operations (Create, Read, Update, Delete)
  用户CRUD操作（创建、读取、更新、删除）
- API Key management for programmatic access
  API密钥管理，用于程序化访问
- User invitation system
  用户邀请系统
- Permission and role management
  权限和角色管理

Security / 安全:
- All endpoints require authentication
  所有端点都需要认证
- Admin-only endpoints are protected with require_admin dependency
  仅管理员的端点使用require_admin依赖保护
- Input validation is performed on all payloads
  对所有负载执行输入验证

Author: Canglong Audit Team
Version: 1.0.0
"""

import logging
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from app.models.schemas import (
    ApiKeyCreate,
    ApiKeyListResponse,
    ApiKeyResponse,
    AcceptInviteRequest,
    UserCreate,
    UserInviteCreate,
    UserInviteResponse,
    UserListResponse,
    UserResponse,
    UserUpdate,
    UserProfile,
)
from app.services.auth_service import auth_service, get_current_user, require_admin

# Configure logging / 配置日志
logger = logging.getLogger(__name__)

# Create router with prefix and tag
# 创建带前缀和标签的路由
router = APIRouter(prefix="/api/users", tags=["users"])


# ========================================================================
# Helper Functions / 辅助函数
# ========================================================================

def user_record_to_response(user: Any) -> UserResponse:
    """
    Convert internal UserRecord to API response model.
    将内部UserRecord转换为API响应模型。
    
    Args / 参数:
        user: Internal user record / 内部用户记录
        
    Returns / 返回:
        UserResponse: API response model / API响应模型
    """
    return UserResponse(
        username=user.username,
        displayName=user.display_name,
        email=user.email,
        role=user.role,
        isActive=user.is_active,
        createdAt=user.created_at,
        lastLogin=user.last_login,
    )


def api_key_to_response(key: Any, include_key: bool = False) -> ApiKeyResponse:
    """
    Convert internal ApiKeyRecord to API response model.
    将内部ApiKeyRecord转换为API响应模型。
    
    Args / 参数:
        key: Internal API key record / 内部API密钥记录
        include_key: Whether to include the full key (only on creation) /
                     是否包含完整密钥（仅在创建时）
        
    Returns / 返回:
        ApiKeyResponse: API response model / API响应模型
        
    Security Note / 安全说明:
        The full key is only returned once during creation.
        完整密钥仅在创建时返回一次。
    """
    return ApiKeyResponse(
        id=key.id,
        name=key.name,
        key=key.key if include_key else None,
        keyPrefix=getattr(key, 'key_prefix', key.key[:12] if key.key else None),
        userId=key.user_id,
        permissions=key.permissions,
        status=key.status,
        createdAt=key.created_at,
        expiresAt=key.expires_at,
        lastUsed=key.last_used,
    )


def invite_to_response(invite: Any, include_link: bool = False) -> UserInviteResponse:
    """
    Convert internal InviteRecord to API response model.
    将内部InviteRecord转换为API响应模型。
    
    Args / 参数:
        invite: Internal invite record / 内部邀请记录
        include_link: Whether to include the invite link /
                      是否包含邀请链接
        
    Returns / 返回:
        UserInviteResponse: API response model / API响应模型
    """
    invite_link = None
    if include_link and invite.status == "pending":
        # Generate invite link for pending invitations
        # 为待处理的邀请生成邀请链接
        invite_link = f"/accept-invite/{invite.id}"
    
    return UserInviteResponse(
        id=invite.id,
        email=invite.email,
        role=invite.role,
        invitedBy=invite.invited_by,
        createdAt=invite.created_at,
        expiresAt=invite.expires_at,
        status=invite.status,
        inviteLink=invite_link,
    )


# ========================================================================
# User Management Endpoints / 用户管理端点
# ========================================================================

@router.get(
    "",
    response_model=UserListResponse,
    summary="List all users / 列出所有用户",
    description="Retrieve a list of all users. Requires administrator role. / 获取所有用户列表。需要管理员角色。",
)
def list_users(
    current_user: UserProfile = Depends(require_admin)
) -> UserListResponse:
    """
    List all users in the system.
    列出系统中的所有用户。
    
    This endpoint requires administrator privileges.
    此端点需要管理员权限。
    
    Args / 参数:
        current_user: Authenticated admin user / 已认证的管理员用户
        
    Returns / 返回:
        UserListResponse: List of users with total count / 用户列表和总数
    """
    logger.info(f"Admin {current_user.username} listing all users / 管理员正在列出所有用户")
    
    users = auth_service.list_users()
    
    return UserListResponse(
        users=[user_record_to_response(u) for u in users],
        total=len(users),
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user / 创建新用户",
    description="Create a new user account. Requires administrator role. / 创建新用户账户。需要管理员角色。",
)
def create_user(
    payload: UserCreate,
    current_user: UserProfile = Depends(require_admin),
) -> UserResponse:
    """
    Create a new user account.
    创建新用户账户。
    
    This endpoint requires administrator privileges.
    此端点需要管理员权限。
    
    Args / 参数:
        payload: User creation data / 用户创建数据
        current_user: Authenticated admin user / 已认证的管理员用户
        
    Returns / 返回:
        UserResponse: Created user data / 创建的用户数据
        
    Raises / 异常:
        HTTPException: 400 if validation fails / 验证失败返回400
    """
    logger.info(f"Admin {current_user.username} creating user: {payload.username} / 管理员正在创建用户")
    
    try:
        user = auth_service.create_user(
            username=payload.username,
            password=payload.password,
            display_name=payload.displayName,
            role=payload.role,
            email=payload.email,
        )
        
        logger.info(f"User created successfully: {payload.username} / 用户创建成功")
        
        return user_record_to_response(user)
    
    except ValueError as e:
        logger.warning(f"User creation failed: {e} / 用户创建失败")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile / 获取当前用户配置",
    description="Retrieve the authenticated user's profile. / 获取已认证用户的配置。",
)
def get_current_user_profile(
    current_user: UserProfile = Depends(get_current_user)
) -> UserResponse:
    """
    Get the current authenticated user's profile.
    获取当前已认证用户的配置。
    
    Args / 参数:
        current_user: Authenticated user / 已认证用户
        
    Returns / 返回:
        UserResponse: Current user's profile / 当前用户配置
        
    Raises / 异常:
        HTTPException: 404 if user not found / 用户未找到返回404
    """
    user = auth_service.get_user_by_username(current_user.username)
    
    if not user:
        logger.error(f"User not found: {current_user.username} / 用户未找到")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found / 用户未找到"
        )
    
    return user_record_to_response(user)


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile / 更新当前用户配置",
    description="Update the authenticated user's display name and email. / 更新已认证用户的显示名称和邮箱。",
)
def update_current_user(
    payload: UserUpdate,
    current_user: UserProfile = Depends(get_current_user),
) -> UserResponse:
    """
    Update the current authenticated user's profile.
    更新当前已认证用户的配置。
    
    Users can only update their own display name and email.
    Role and active status changes require administrator privileges.
    用户只能更新自己的显示名称和邮箱。
    角色和激活状态更改需要管理员权限。
    
    Args / 参数:
        payload: Update data / 更新数据
        current_user: Authenticated user / 已认证用户
        
    Returns / 返回:
        UserResponse: Updated user profile / 更新后的用户配置
        
    Raises / 异常:
        HTTPException: 404 if user not found / 用户未找到返回404
    """
    logger.info(f"User {current_user.username} updating profile / 用户正在更新配置")
    
    # Users can only update their own display name and email
    # 用户只能更新自己的显示名称和邮箱
    user = auth_service.update_user(
        username=current_user.username,
        display_name=payload.displayName,
        email=payload.email,
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found / 用户未找到"
        )
    
    return user_record_to_response(user)


@router.get(
    "/me/permissions",
    response_model=dict,
    summary="Get current user permissions / 获取当前用户权限",
    description="Retrieve the authenticated user's permissions. / 获取已认证用户的权限。",
)
def get_my_permissions(
    current_user: UserProfile = Depends(get_current_user)
) -> dict:
    """
    Get the current authenticated user's permissions.
    获取当前已认证用户的权限。
    
    Args / 参数:
        current_user: Authenticated user / 已认证用户
        
    Returns / 返回:
        dict: User's role and permissions / 用户角色和权限
    """
    permissions = auth_service.get_permissions(current_user.role)
    
    return {
        "role": current_user.role,
        "permissions": permissions,
        "canManageUsers": "manage_users" in permissions,
        "canManageApiKeys": "manage_keys" in permissions,
        "canCreateAudit": "manage_audits" in permissions,
        "canViewReport": "view_reports" in permissions,
    }


@router.get(
    "/{username}",
    response_model=UserResponse,
    summary="Get user by username / 通过用户名获取用户",
    description="Retrieve a specific user's profile. Requires administrator role. / 获取特定用户的配置。需要管理员角色。",
)
def get_user(
    username: str,
    current_user: UserProfile = Depends(require_admin),
) -> UserResponse:
    """
    Get a specific user by username.
    通过用户名获取特定用户。
    
    This endpoint requires administrator privileges.
    此端点需要管理员权限。
    
    Args / 参数:
        username: Username to look up / 待查询的用户名
        current_user: Authenticated admin user / 已认证的管理员用户
        
    Returns / 返回:
        UserResponse: User profile / 用户配置
        
    Raises / 异常:
        HTTPException: 404 if user not found / 用户未找到返回404
    """
    user = auth_service.get_user_by_username(username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found / 用户 '{username}' 未找到"
        )
    
    return user_record_to_response(user)


@router.patch(
    "/{username}",
    response_model=UserResponse,
    summary="Update user / 更新用户",
    description="Update a user's profile. Requires administrator role. / 更新用户配置。需要管理员角色。",
)
def update_user(
    username: str,
    payload: UserUpdate,
    current_user: UserProfile = Depends(require_admin),
) -> UserResponse:
    """
    Update a user's profile.
    更新用户配置。
    
    This endpoint requires administrator privileges.
    Administrators can update all user fields including role and active status.
    此端点需要管理员权限。
    管理员可以更新所有用户字段，包括角色和激活状态。
    
    Args / 参数:
        username: Username to update / 待更新的用户名
        payload: Update data / 更新数据
        current_user: Authenticated admin user / 已认证的管理员用户
        
    Returns / 返回:
        UserResponse: Updated user profile / 更新后的用户配置
        
    Raises / 异常:
        HTTPException: 404 if user not found / 用户未找到返回404
    """
    logger.info(f"Admin {current_user.username} updating user: {username} / 管理员正在更新用户")
    
    user = auth_service.update_user(
        username=username,
        display_name=payload.displayName,
        email=payload.email,
        role=payload.role,
        is_active=payload.isActive,
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found / 用户 '{username}' 未找到"
        )
    
    return user_record_to_response(user)


@router.delete(
    "/{username}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user / 删除用户",
    description="Delete a user account. Requires administrator role. Cannot delete admin user. / 删除用户账户。需要管理员角色。无法删除管理员用户。",
)
def delete_user(
    username: str,
    current_user: UserProfile = Depends(require_admin),
) -> None:
    """
    Delete a user account.
    删除用户账户。
    
    This endpoint requires administrator privileges.
    The default admin user cannot be deleted.
    此端点需要管理员权限。
    默认管理员用户无法删除。
    
    Args / 参数:
        username: Username to delete / 待删除的用户名
        current_user: Authenticated admin user / 已认证的管理员用户
        
    Raises / 异常:
        HTTPException: 400 if trying to delete admin / 尝试删除管理员返回400
        HTTPException: 404 if user not found / 用户未找到返回404
    """
    logger.info(f"Admin {current_user.username} deleting user: {username} / 管理员正在删除用户")
    
    try:
        success = auth_service.delete_user(username)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{username}' not found / 用户 '{username}' 未找到"
            )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ========================================================================
# API Key Management Endpoints / API密钥管理端点
# ========================================================================

@router.get(
    "/me/keys",
    response_model=ApiKeyListResponse,
    summary="List current user's API keys / 列出当前用户的API密钥",
    description="Retrieve the authenticated user's API keys. / 获取已认证用户的API密钥。",
)
def list_my_api_keys(
    current_user: UserProfile = Depends(get_current_user)
) -> ApiKeyListResponse:
    """
    List the current authenticated user's API keys.
    列出当前已认证用户的API密钥。
    
    Args / 参数:
        current_user: Authenticated user / 已认证用户
        
    Returns / 返回:
        ApiKeyListResponse: List of API keys / API密钥列表
    """
    keys = auth_service.list_api_keys(user_id=current_user.username)
    
    return ApiKeyListResponse(
        keys=[api_key_to_response(k) for k in keys],
        total=len(keys),
    )


@router.post(
    "/me/keys",
    response_model=ApiKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create API key / 创建API密钥",
    description="Create a new API key for the authenticated user. / 为已认证用户创建新的API密钥。",
)
def create_api_key(
    payload: ApiKeyCreate,
    current_user: UserProfile = Depends(get_current_user),
) -> ApiKeyResponse:
    """
    Create a new API key for the authenticated user.
    为已认证用户创建新的API密钥。
    
    The full key is only returned once - store it securely!
    完整密钥仅返回一次 - 请安全存储！
    
    Args / 参数:
        payload: API key creation data / API密钥创建数据
        current_user: Authenticated user / 已认证用户
        
    Returns / 返回:
        ApiKeyResponse: Created API key (full key shown only once) /
                       创建的API密钥（完整密钥仅显示一次）
        
    Raises / 异常:
        HTTPException: 400 if creation fails / 创建失败返回400
    """
    logger.info(f"User {current_user.username} creating API key: {payload.name} / 用户正在创建API密钥")
    
    try:
        key = auth_service.create_api_key(
            user_id=current_user.username,
            name=payload.name,
            permissions=payload.permissions,
            expires_at=payload.expiresAt,
        )
        
        return api_key_to_response(key, include_key=True)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/me/keys/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke own API key / 撤销自己的API密钥",
    description="Revoke an API key owned by the authenticated user. / 撤销已认证用户拥有的API密钥。",
)
def revoke_my_api_key(
    key_id: str,
    current_user: UserProfile = Depends(get_current_user),
) -> None:
    """
    Revoke an API key owned by the current user.
    撤销当前用户拥有的API密钥。
    
    Args / 参数:
        key_id: API key ID to revoke / 待撤销的API密钥ID
        current_user: Authenticated user / 已认证用户
        
    Raises / 异常:
        HTTPException: 404 if key not found or not owned by user /
                       密钥未找到或不属于用户返回404
    """
    # Verify ownership
    # 验证所有权
    keys = auth_service.list_api_keys(user_id=current_user.username)
    
    if not any(k.id == key_id for k in keys):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found or not owned by you / API密钥未找到或不属于您"
        )
    
    auth_service.revoke_api_key(key_id)
    
    logger.info(f"User {current_user.username} revoked API key: {key_id} / 用户撤销了API密钥")


@router.get(
    "/keys",
    response_model=ApiKeyListResponse,
    summary="List all API keys / 列出所有API密钥",
    description="Retrieve all API keys. Requires administrator role. / 获取所有API密钥。需要管理员角色。",
)
def list_all_api_keys(
    current_user: UserProfile = Depends(require_admin)
) -> ApiKeyListResponse:
    """
    List all API keys in the system.
    列出系统中的所有API密钥。
    
    This endpoint requires administrator privileges.
    此端点需要管理员权限。
    
    Args / 参数:
        current_user: Authenticated admin user / 已认证的管理员用户
        
    Returns / 返回:
        ApiKeyListResponse: List of all API keys / 所有API密钥列表
    """
    logger.info(f"Admin {current_user.username} listing all API keys / 管理员正在列出所有API密钥")
    
    keys = auth_service.list_api_keys()
    
    return ApiKeyListResponse(
        keys=[api_key_to_response(k) for k in keys],
        total=len(keys),
    )


@router.delete(
    "/keys/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke any API key / 撤销任意API密钥",
    description="Revoke any API key. Requires administrator role. / 撤销任意API密钥。需要管理员角色。",
)
def revoke_any_api_key(
    key_id: str,
    current_user: UserProfile = Depends(require_admin),
) -> None:
    """
    Revoke any API key (admin only).
    撤销任意API密钥（仅管理员）。
    
    This endpoint requires administrator privileges.
    此端点需要管理员权限。
    
    Args / 参数:
        key_id: API key ID to revoke / 待撤销的API密钥ID
        current_user: Authenticated admin user / 已认证的管理员用户
        
    Raises / 异常:
        HTTPException: 404 if key not found / 密钥未找到返回404
    """
    logger.info(f"Admin {current_user.username} revoking API key: {key_id} / 管理员正在撤销API密钥")
    
    success = auth_service.revoke_api_key(key_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found / API密钥未找到"
        )


# ========================================================================
# User Invitation Endpoints / 用户邀请端点
# ========================================================================

@router.post(
    "/invites",
    response_model=UserInviteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user invitation / 创建用户邀请",
    description="Invite a new user via email. Requires administrator role. / 通过邮件邀请新用户。需要管理员角色。",
)
def create_invite(
    payload: UserInviteCreate,
    current_user: UserProfile = Depends(require_admin),
) -> UserInviteResponse:
    """
    Create a new user invitation.
    创建新的用户邀请。
    
    This endpoint requires administrator privileges.
    Invitations expire after 7 days by default.
    此端点需要管理员权限。
    邀请默认在7天后过期。
    
    Args / 参数:
        payload: Invitation data / 邀请数据
        current_user: Authenticated admin user / 已认证的管理员用户
        
    Returns / 返回:
        UserInviteResponse: Created invitation with invite link /
                           创建的邀请及邀请链接
        
    Raises / 异常:
        HTTPException: 400 if email invalid or pending invite exists /
                       邮箱无效或存在待处理邀请返回400
    """
    logger.info(f"Admin {current_user.username} creating invite for: {payload.email} / 管理员正在创建邀请")
    
    try:
        invite = auth_service.create_invite(
            email=payload.email,
            role=payload.role,
            invited_by=current_user.username,
        )
        
        return invite_to_response(invite, include_link=True)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/invites",
    response_model=list[UserInviteResponse],
    summary="List invitations / 列出邀请",
    description="List all invitations. Requires administrator role. / 列出所有邀请。需要管理员角色。",
)
def list_invites(
    current_user: UserProfile = Depends(require_admin),
    status_filter: str | None = Query(
        default=None,
        description="Filter by status (pending/accepted/expired/revoked) / 按状态过滤",
        alias="status"
    ),
) -> list[UserInviteResponse]:
    """
    List all invitations.
    列出所有邀请。
    
    This endpoint requires administrator privileges.
    此端点需要管理员权限。
    
    Args / 参数:
        current_user: Authenticated admin user / 已认证的管理员用户
        status_filter: Optional status filter / 可选的状态过滤
        
    Returns / 返回:
        list[UserInviteResponse]: List of invitations / 邀请列表
    """
    invites = auth_service.list_invites(
        status=status_filter if status_filter else None
    )
    
    return [invite_to_response(i) for i in invites]


@router.delete(
    "/invites/{invite_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke invitation / 撤销邀请",
    description="Revoke a pending invitation. Requires administrator role. / 撤销待处理的邀请。需要管理员角色。",
)
def revoke_invite(
    invite_id: str,
    current_user: UserProfile = Depends(require_admin),
) -> None:
    """
    Revoke a pending invitation.
    撤销待处理的邀请。
    
    This endpoint requires administrator privileges.
    此端点需要管理员权限。
    
    Args / 参数:
        invite_id: Invitation ID to revoke / 待撤销的邀请ID
        current_user: Authenticated admin user / 已认证的管理员用户
        
    Raises / 异常:
        HTTPException: 404 if invite not found / 邀请未找到返回404
    """
    logger.info(f"Admin {current_user.username} revoking invite: {invite_id} / 管理员正在撤销邀请")
    
    success = auth_service.revoke_invite(invite_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found / 邀请未找到"
        )


@router.post(
    "/accept-invite/{invite_id}",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Accept invitation / 接受邀请",
    description="Accept a user invitation and create account. / 接受用户邀请并创建账户。",
)
def accept_invite(
    invite_id: str,
    payload: AcceptInviteRequest = Body(...),
) -> UserResponse:
    """
    Accept a user invitation and create a new account.
    接受用户邀请并创建新账户。
    
    This endpoint is public (no authentication required).
    此端点是公开的（无需认证）。
    
    Args / 参数:
        invite_id: Invitation ID / 邀请ID
        payload: Account creation data / 账户创建数据
        
    Returns / 返回:
        UserResponse: Created user account / 创建的用户账户
        
    Raises / 异常:
        HTTPException: 400 if invite invalid, expired, or validation fails /
                       邀请无效、过期或验证失败返回400
    """
    logger.info(f"Accepting invite: {invite_id} / 正在接受邀请")
    
    try:
        user = auth_service.accept_invite(
            invite_id=invite_id,
            username=payload.username,
            password=payload.password,
            display_name=payload.displayName,
        )
        
        logger.info(f"Invite accepted, user created: {payload.username} / 邀请已接受，用户已创建")
        
        return user_record_to_response(user)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
