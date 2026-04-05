<template>
  <div class="page">
    <section class="hero panel">
      <div>
        <p class="eyebrow">{{ t('users.heroEyebrow') }}</p>
        <h1>{{ t('users.title') }}</h1>
        <p class="hero-copy">{{ t('users.description') }}</p>
      </div>

      <article class="readiness-card">
        <p class="eyebrow">{{ t('users.statsEyebrow') }}</p>
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-value">{{ users.length }}</span>
            <span class="stat-label">{{ t('users.totalUsers') }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ activeUsers }}</span>
            <span class="stat-label">{{ t('users.activeUsers') }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ apiKeys.length }}</span>
            <span class="stat-label">{{ t('users.totalApiKeys') }}</span>
          </div>
        </div>
      </article>
    </section>

    <!-- Tabs -->
    <div class="tabs-container">
      <div class="tabs">
        <button
          :class="['tab', { active: activeTab === 'users' }]"
          @click="activeTab = 'users'"
        >
          {{ t('users.usersTab') }}
        </button>
        <button
          :class="['tab', { active: activeTab === 'keys' }]"
          @click="activeTab = 'keys'"
        >
          {{ t('users.apiKeysTab') }}
        </button>
        <button
          :class="['tab', { active: activeTab === 'invites' }]"
          @click="activeTab = 'invites'"
        >
          {{ t('users.invitesTab') }}
        </button>
      </div>
    </div>

    <!-- Users Tab -->
    <section v-if="activeTab === 'users'" class="panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">{{ t('users.listEyebrow') }}</p>
          <h2>{{ t('users.listTitle') }}</h2>
        </div>
        <button class="accent-button" @click="showCreateUserModal = true">
          {{ t('users.createUser') }}
        </button>
      </div>

      <p v-if="loading" class="hero-copy">{{ t('report.loading') }}</p>
      <p v-if="successMessage" class="success-text">{{ successMessage }}</p>
      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

      <div v-else class="user-grid">
        <article v-for="user in users" :key="user.username" class="user-card">
          <div class="user-top">
            <div class="user-avatar">
              {{ user.displayName.charAt(0).toUpperCase() }}
            </div>
            <div class="user-info">
              <h3>{{ user.displayName }}</h3>
              <p>@{{ user.username }}</p>
            </div>
            <div class="badge-row">
              <span :class="['capsule', `role-${user.role}`]">{{ formatRole(user.role) }}</span>
              <span v-if="!user.active" class="capsule inactive-pill">{{ t('users.inactive') }}</span>
            </div>
          </div>

          <div class="user-meta">
            <span v-if="user.email">{{ user.email }}</span>
            <span>{{ t('users.createdAt') }}: {{ formatDate(user.createdAt) }}</span>
            <span v-if="user.lastLogin">{{ t('users.lastLogin') }}: {{ formatDate(user.lastLogin) }}</span>
          </div>

          <div class="user-actions">
            <button type="button" @click="openEditUserModal(user)">
              {{ t('users.editUser') }}
            </button>
            <button
              v-if="user.username !== 'admin'"
              type="button"
              class="danger-button"
              @click="handleDeleteUser(user.username)"
            >
              {{ t('users.deleteUser') }}
            </button>
          </div>
        </article>
      </div>
    </section>

    <!-- API Keys Tab -->
    <section v-if="activeTab === 'keys'" class="panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">{{ t('users.apiKeysEyebrow') }}</p>
          <h2>{{ t('users.apiKeysTitle') }}</h2>
        </div>
        <button class="accent-button" @click="showCreateKeyModal = true">
          {{ t('users.createApiKey') }}
        </button>
      </div>

      <p v-if="loadingKeys" class="hero-copy">{{ t('report.loading') }}</p>

      <div v-else class="key-grid">
        <article v-for="key in apiKeys" :key="key.id" class="key-card">
          <div class="key-top">
            <div>
              <h3>{{ key.name }}</h3>
              <p>{{ t('users.owner') }}: {{ key.owner }}</p>
            </div>
            <span :class="['capsule', `status-${key.status}`]">{{ formatStatus(key.status) }}</span>
          </div>

          <div class="key-meta">
            <span>{{ t('users.permissions') }}: {{ key.permissions.join(', ') }}</span>
            <span>{{ t('users.createdAt') }}: {{ formatDate(key.createdAt) }}</span>
            <span v-if="key.expiresAt">{{ t('users.expiresAt') }}: {{ formatDate(key.expiresAt) }}</span>
            <span v-if="key.lastUsed">{{ t('users.lastUsed') }}: {{ formatDate(key.lastUsed) }}</span>
          </div>

          <div v-if="key.fullKey" class="key-display">
            <code>{{ key.fullKey }}</code>
            <button type="button" class="copy-button" @click="copyToClipboard(key.fullKey)">
              {{ t('users.copy') }}
            </button>
          </div>

          <div class="key-actions">
            <button
              v-if="key.status === 'active'"
              type="button"
              class="danger-button"
              @click="handleRevokeKey(key.id)"
            >
              {{ t('users.revokeKey') }}
            </button>
          </div>
        </article>
      </div>
    </section>

    <!-- Invites Tab -->
    <section v-if="activeTab === 'invites'" class="panel">
      <div class="section-heading">
        <div>
          <p class="eyebrow">{{ t('users.invitesEyebrow') }}</p>
          <h2>{{ t('users.invitesTitle') }}</h2>
        </div>
        <button class="accent-button" @click="showCreateInviteModal = true">
          {{ t('users.createInvite') }}
        </button>
      </div>

      <p v-if="loadingInvites" class="hero-copy">{{ t('report.loading') }}</p>

      <div v-else class="invite-grid">
        <article v-for="invite in invites" :key="invite.id" class="invite-card">
          <div class="invite-top">
            <div>
              <h3>{{ invite.email }}</h3>
              <p>{{ t('users.invitedBy') }}: {{ invite.invitedBy }}</p>
            </div>
            <span :class="['capsule', `status-${invite.status}`]">{{ formatStatus(invite.status) }}</span>
          </div>

          <div class="invite-meta">
            <span>{{ t('users.role') }}: {{ formatRole(invite.role) }}</span>
            <span>{{ t('users.createdAt') }}: {{ formatDate(invite.createdAt) }}</span>
            <span>{{ t('users.expiresAt') }}: {{ formatDate(invite.expiresAt) }}</span>
          </div>

          <div v-if="invite.inviteLink && invite.status === 'pending'" class="invite-link">
            <code>{{ invite.inviteLink }}</code>
            <button type="button" class="copy-button" @click="copyToClipboard(invite.inviteLink)">
              {{ t('users.copy') }}
            </button>
          </div>

          <div class="invite-actions">
            <button
              v-if="invite.status === 'pending'"
              type="button"
              class="danger-button"
              @click="handleRevokeInvite(invite.id)"
            >
              {{ t('users.revokeInvite') }}
            </button>
          </div>
        </article>
      </div>
    </section>

    <!-- Create User Modal -->
    <div v-if="showCreateUserModal" class="modal-overlay" @click.self="showCreateUserModal = false">
      <div class="modal">
        <h3>{{ t('users.createUserTitle') }}</h3>
        <form @submit.prevent="handleCreateUser">
          <input v-model="newUser.username" :placeholder="t('users.formUsername')" required />
          <input v-model="newUser.displayName" :placeholder="t('users.formDisplayName')" required />
          <input v-model="newUser.email" type="email" :placeholder="t('users.formEmail')" />
          <input v-model="newUser.password" type="password" :placeholder="t('users.formPassword')" required />
          <select v-model="newUser.role">
            <option value="viewer">{{ t('users.roleViewer') }}</option>
            <option value="auditor">{{ t('users.roleAuditor') }}</option>
            <option value="administrator">{{ t('users.roleAdministrator') }}</option>
          </select>
          <div class="modal-actions">
            <button type="button" @click="showCreateUserModal = false">{{ t('users.cancel') }}</button>
            <button type="submit" class="accent-button">{{ t('users.create') }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Create API Key Modal -->
    <div v-if="showCreateKeyModal" class="modal-overlay" @click.self="showCreateKeyModal = false">
      <div class="modal">
        <h3>{{ t('users.createApiKeyTitle') }}</h3>
        <form @submit.prevent="handleCreateKey">
          <input v-model="newKey.name" :placeholder="t('users.formKeyName')" required />
          <div class="checkbox-group">
            <label v-for="perm in availablePermissions" :key="perm">
              <input type="checkbox" :value="perm" v-model="newKey.permissions" />
              <span>{{ perm }}</span>
            </label>
          </div>
          <input v-model="newKey.expiresAt" type="datetime-local" :placeholder="t('users.formExpiresAt')" />
          <div class="modal-actions">
            <button type="button" @click="showCreateKeyModal = false">{{ t('users.cancel') }}</button>
            <button type="submit" class="accent-button">{{ t('users.create') }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Create Invite Modal -->
    <div v-if="showCreateInviteModal" class="modal-overlay" @click.self="showCreateInviteModal = false">
      <div class="modal">
        <h3>{{ t('users.createInviteTitle') }}</h3>
        <form @submit.prevent="handleCreateInvite">
          <input v-model="newInvite.email" type="email" :placeholder="t('users.formEmail')" required />
          <select v-model="newInvite.role">
            <option value="viewer">{{ t('users.roleViewer') }}</option>
            <option value="auditor">{{ t('users.roleAuditor') }}</option>
            <option value="administrator">{{ t('users.roleAdministrator') }}</option>
          </select>
          <div class="modal-actions">
            <button type="button" @click="showCreateInviteModal = false">{{ t('users.cancel') }}</button>
            <button type="submit" class="accent-button">{{ t('users.create') }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Users Management View Component
 * 用户管理视图组件
 * 
 * This component provides a comprehensive interface for managing users, API keys, and invitations.
 * It includes role-based access control, permission checks, and full CRUD operations.
 * 
 * 本组件提供用于管理用户、API密钥和邀请的综合界面。
 * 它包括基于角色的访问控制、权限检查和完整的CRUD操作。
 * 
 * Features / 功能特性:
 * - User management (create, read, update, delete) / 用户管理（创建、读取、更新、删除）
 * - API Key management with permissions / 带权限的API密钥管理
 * - User invitation system / 用户邀请系统
 * - Role-based access control / 基于角色的访问控制
 * - Permission-based UI rendering / 基于权限的UI渲染
 * - Internationalization support / 国际化支持
 * 
 * Security / 安全:
 * - All operations require proper authentication / 所有操作都需要适当的认证
 * - Permission checks before sensitive operations / 敏感操作前的权限检查
 * - Admin-only operations are protected / 仅管理员的操作受到保护
 * - Passwords are never displayed / 密码从不显示
 * 
 * @component UsersView
 */

import { computed, onMounted, reactive, ref } from 'vue';
import { useI18n } from '../i18n';
import {
  createUser,
  createApiKey,
  createInvite,
  deleteUser,
  fetchAllApiKeys,
  fetchInvites,
  fetchMyApiKeys,
  fetchMyPermissions,
  fetchUsers,
  revokeAnyApiKey,
  revokeInvite,
  revokeMyApiKey,
  updateUser,
  type ApiKey,
  type Invite,
  type User,
  type UserPermissions,
} from '../services/api';

// Internationalization hook / 国际化钩子
// Destructure both t function and locale ref / 解构t函数和locale引用
const { t, locale } = useI18n();

// Active tab state: 'users' | 'keys' | 'invites'
// 活动标签页状态：'users' | 'keys' | 'invites'
const activeTab = ref<'users' | 'keys' | 'invites'>('users');

// Loading states / 加载状态
const loading = ref(true);
const loadingKeys = ref(false);
const loadingInvites = ref(false);

// Message states / 消息状态
const errorMessage = ref('');
const successMessage = ref('');

// Current user permissions for access control
// 当前用户权限用于访问控制
const currentUserPermissions = ref<UserPermissions | null>(null);

// Data stores / 数据存储
const users = ref<User[]>([]);
const apiKeys = ref<(ApiKey & { key?: string })[]>([]);
const invites = ref<(Invite & { inviteLink?: string })[]>([]);

// Modal visibility states / 模态框可见性状态
const showCreateUserModal = ref(false);
const showCreateKeyModal = ref(false);
const showCreateInviteModal = ref(false);

// Form data for creating new user
// 创建新用户的表单数据
const newUser = reactive({
  username: '',
  displayName: '',
  email: '',
  password: '',
  role: 'viewer' as 'viewer' | 'auditor' | 'administrator',
});

// Form data for creating new API key
// 创建新API密钥的表单数据
const newKey = reactive({
  name: '',
  permissions: ['read'] as string[],
  expiresAt: '',
});

// Form data for creating new invitation
// 创建新邀请的表单数据
const newInvite = reactive({
  email: '',
  role: 'viewer' as 'viewer' | 'auditor' | 'administrator',
});

// Available permissions for API keys
// API密钥的可用权限
const availablePermissions = ['read', 'write', 'delete', 'manage_repos', 'manage_audits', 'view_reports'];

// Computed properties / 计算属性

/**
 * Count of active users
 * 活跃用户计数
 */
const activeUsers = computed(() => users.value.filter(u => u.active).length);

/**
 * Whether current user can manage users
 * 当前用户是否可以管理用户
 */
const canManageUsers = computed(() => currentUserPermissions.value?.canManageUsers ?? false);

/**
 * Whether current user can manage API keys
 * 当前用户是否可以管理API密钥
 */
const canManageApiKeys = computed(() => currentUserPermissions.value?.canManageApiKeys ?? false);

// Helper functions / 辅助函数

/**
 * Format date string to locale string
 * 将日期字符串格式化为本地化字符串
 * 
 * @param value - Date string or null / 日期字符串或null
 * @returns Formatted date string or '-' / 格式化的日期字符串或'-'
 */
function formatDate(value: string | null) {
  if (!value) return '-';
  return new Date(value).toLocaleString();
}

/**
 * Format role key to localized display name
 * 将角色键格式化为本地化显示名称
 * 
 * @param role - Role key (administrator, auditor, viewer) / 角色键
 * @returns Localized role name / 本地化的角色名称
 */
function formatRole(role: string) {
  const roles: Record<string, string> = {
    administrator: t('users.roleAdministrator'),
    auditor: t('users.roleAuditor'),
    viewer: t('users.roleViewer'),
  };
  return roles[role] || role;
}

/**
 * Format status key to localized display name
 * 将状态键格式化为本地化显示名称
 * 
 * @param status - Status key / 状态键
 * @returns Localized status name / 本地化的状态名称
 */
function formatStatus(status: string) {
  const statuses: Record<string, string> = {
    active: t('users.statusActive'),
    revoked: t('users.statusRevoked'),
    expired: t('users.statusExpired'),
    pending: t('users.statusPending'),
    accepted: t('users.statusAccepted'),
  };
  return statuses[status] || status;
}

/**
 * Show success message and auto-hide after 3 seconds
 * 显示成功消息并在3秒后自动隐藏
 * 
 * @param message - Success message to display / 要显示的成功消息
 */
function showSuccess(message: string) {
  successMessage.value = message;
  setTimeout(() => {
    successMessage.value = '';
  }, 3000);
}

// Data loading functions / 数据加载函数

/**
 * Load current user's permissions
 * 加载当前用户的权限
 */
async function loadPermissions() {
  try {
    currentUserPermissions.value = await fetchMyPermissions(locale.value);
  } catch (error) {
    console.error('Failed to load permissions:', error);
  }
}

/**
 * Load all users from the server
 * 从服务器加载所有用户
 */
async function loadUsers() {
  loading.value = true;
  errorMessage.value = '';
  try {
    users.value = await fetchUsers(locale.value);
  } catch (error) {
    errorMessage.value = String(error);
  } finally {
    loading.value = false;
  }
}

/**
 * Load API keys (user's own keys + all keys if admin)
 * 加载API密钥（用户自己的密钥 + 如果是管理员则加载所有密钥）
 */
async function loadApiKeys() {
  loadingKeys.value = true;
  try {
    // Load user's own API keys / 加载用户自己的API密钥
    const myKeys = await fetchMyApiKeys(locale.value);
    // If admin, also load all API keys / 如果是管理员，也加载所有API密钥
    const allKeys = canManageApiKeys.value ? await fetchAllApiKeys(locale.value) : [];
    // Combine and deduplicate / 合并并去重
    const keyMap = new Map<string, ApiKey & { key?: string }>();
    myKeys.forEach(key => keyMap.set(key.id, key));
    allKeys.forEach(key => keyMap.set(key.id, key));
    apiKeys.value = Array.from(keyMap.values());
  } catch (error) {
    console.error('Failed to load API keys:', error);
  } finally {
    loadingKeys.value = false;
  }
}

/**
 * Load all invitations from the server
 * 从服务器加载所有邀请
 */
async function loadInvites() {
  loadingInvites.value = true;
  try {
    const invitesData = await fetchInvites(locale.value);
    // Generate invite links for pending invites / 为待处理的邀请生成邀请链接
    invites.value = invitesData.map(invite => ({
      ...invite,
      inviteLink: invite.status === 'pending'
        ? `${window.location.origin}/accept-invite/${invite.id}`
        : undefined,
    }));
  } catch (error) {
    console.error('Failed to load invites:', error);
  } finally {
    loadingInvites.value = false;
  }
}

// User management functions / 用户管理函数

/**
 * Handle creating a new user
 * 处理创建新用户
 */
async function handleCreateUser() {
  try {
    await createUser(locale.value, {
      username: newUser.username,
      password: newUser.password,
      displayName: newUser.displayName,
      email: newUser.email || undefined,
      role: newUser.role,
    });
    showSuccess('User created successfully');
    showCreateUserModal.value = false;
    // Reset form / 重置表单
    newUser.username = '';
    newUser.displayName = '';
    newUser.email = '';
    newUser.password = '';
    newUser.role = 'viewer';
    await loadUsers();
  } catch (error) {
    errorMessage.value = String(error);
  }
}

/**
 * Handle deleting a user
 * 处理删除用户
 * 
 * @param username - Username of the user to delete / 要删除的用户名
 */
async function handleDeleteUser(username: string) {
  if (!confirm(t('users.confirmDelete'))) return;
  try {
    await deleteUser(locale.value, username);
    showSuccess('User deleted successfully');
    await loadUsers();
  } catch (error) {
    errorMessage.value = String(error);
  }
}

/**
 * Open edit user modal (placeholder for future implementation)
 * 打开编辑用户模态框（未来实现的占位符）
 * 
 * @param user - User to edit / 要编辑的用户
 */
function openEditUserModal(user: User) {
  // TODO: Implement edit modal / TODO: 实现编辑模态框
  console.log('Edit user:', user);
  // For now, just show an alert / 目前只显示一个警告
  alert(`Edit user: ${user.username}`);
}

// API Key management functions / API密钥管理函数

/**
 * Handle creating a new API key
 * 处理创建新API密钥
 */
async function handleCreateKey() {
  try {
    const result = await createApiKey(locale.value, {
      name: newKey.name,
      permissions: newKey.permissions,
      expiresAt: newKey.expiresAt || undefined,
    });
    // Add the full key to the list temporarily for display / 将完整密钥临时添加到列表中显示
    apiKeys.value.unshift({
      ...result,
      key: result.fullKey,
    });
    showSuccess('API key created successfully');
    showCreateKeyModal.value = false;
    // Reset form / 重置表单
    newKey.name = '';
    newKey.permissions = ['read'];
    newKey.expiresAt = '';
  } catch (error) {
    errorMessage.value = String(error);
  }
}

/**
 * Handle revoking an API key
 * 处理撤销API密钥
 * 
 * @param keyId - ID of the API key to revoke / 要撤销的API密钥ID
 */
async function handleRevokeKey(keyId: string) {
  if (!confirm(t('users.confirmRevokeKey'))) return;
  try {
    // Try to revoke as admin first, fall back to user revoke
    // 首先尝试作为管理员撤销，回退到用户撤销
    try {
      await revokeAnyApiKey(locale.value, keyId);
    } catch {
      await revokeMyApiKey(locale.value, keyId);
    }
    showSuccess('API key revoked successfully');
    await loadApiKeys();
  } catch (error) {
    errorMessage.value = String(error);
  }
}

// Invitation management functions / 邀请管理函数

/**
 * Handle creating a new invitation
 * 处理创建新邀请
 */
async function handleCreateInvite() {
  try {
    await createInvite(locale.value, {
      email: newInvite.email,
      role: newInvite.role,
    });
    showSuccess('Invitation sent successfully');
    showCreateInviteModal.value = false;
    // Reset form / 重置表单
    newInvite.email = '';
    newInvite.role = 'viewer';
    await loadInvites();
  } catch (error) {
    errorMessage.value = String(error);
  }
}

/**
 * Handle revoking an invitation
 * 处理撤销邀请
 * 
 * @param inviteId - ID of the invitation to revoke / 要撤销的邀请ID
 */
async function handleRevokeInvite(inviteId: string) {
  if (!confirm(t('users.confirmRevokeInvite'))) return;
  try {
    await revokeInvite(locale.value, inviteId);
    showSuccess('Invitation revoked successfully');
    await loadInvites();
  } catch (error) {
    errorMessage.value = String(error);
  }
}

// Utility functions / 工具函数

/**
 * Copy text to clipboard
 * 将文本复制到剪贴板
 * 
 * @param text - Text to copy / 要复制的文本
 */
function copyToClipboard(text: string) {
  navigator.clipboard.writeText(text);
  showSuccess('Copied to clipboard');
}

// Lifecycle hooks / 生命周期钩子

/**
 * Component mounted hook - load initial data
 * 组件挂载钩子 - 加载初始数据
 */
onMounted(async () => {
  await loadPermissions();
  await loadUsers();
  await loadApiKeys();
  await loadInvites();
});
</script>

<style scoped>
/* ============================================
   Users View - Commercial Design System
   用户视图 - 商业化设计系统
   ============================================ */

/* Page Layout / 页面布局 */
.page {
  display: grid;
  gap: var(--space-6);
  max-width: 1400px;
  margin: 0 auto;
}

/* Hero Section / 英雄区域 */
.hero {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: var(--space-6);
  align-items: start;
}

.hero h1 {
  margin: var(--space-2) 0 var(--space-3);
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 700;
  line-height: 1.1;
  background: linear-gradient(135deg, var(--text-primary) 0%, var(--color-primary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-copy {
  color: var(--text-secondary);
  font-size: var(--text-lg);
  max-width: 600px;
}

/* Stats Card / 统计卡片 */
.readiness-card {
  padding: var(--space-5);
  border-radius: var(--radius-xl);
  background: var(--surface-card);
  border: 1px solid var(--surface-border);
  box-shadow: var(--shadow-lg);
}

.readiness-card .eyebrow {
  color: var(--color-primary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
  margin-top: var(--space-4);
}

.stat-item {
  text-align: center;
  padding: var(--space-3);
  border-radius: var(--radius-lg);
  background: var(--bg-tertiary);
}

.stat-value {
  display: block;
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-top: var(--space-1);
}

/* Tabs Navigation / 标签导航 */
.tabs-container {
  display: flex;
  justify-content: center;
}

.tabs {
  display: inline-flex;
  gap: var(--space-1);
  padding: var(--space-1);
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--surface-border);
}

.tab {
  padding: var(--space-3) var(--space-5);
  border-radius: var(--radius-md);
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tab:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.tab.active {
  background: var(--color-primary);
  color: white;
  box-shadow: var(--shadow-md);
}

/* Section Heading / 章节标题 */
.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-4);
}

.section-heading h2 {
  margin: var(--space-2) 0 0;
  font-size: var(--text-2xl);
}

/* Card Grids / 卡片网格 */
.user-grid,
.key-grid,
.invite-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: var(--space-4);
  margin-top: var(--space-5);
}

/* User Card / 用户卡片 */
.user-card,
.key-card,
.invite-card {
  padding: var(--space-5);
  border-radius: var(--radius-xl);
  background: var(--surface-card);
  border: 1px solid var(--surface-border);
  transition: all var(--transition-base);
}

.user-card:hover,
.key-card:hover,
.invite-card:hover {
  border-color: var(--surface-border-hover);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.user-top {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.user-avatar {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-full);
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xl);
  font-weight: 700;
  color: white;
  box-shadow: var(--shadow-md);
}

.user-info h3,
.key-top h3,
.invite-top h3 {
  margin: 0;
  font-size: var(--text-lg);
  color: var(--text-primary);
}

.user-info p,
.key-top p,
.invite-top p {
  margin: var(--space-1) 0 0;
  color: var(--text-tertiary);
  font-size: var(--text-sm);
}

.badge-row {
  margin-left: auto;
  display: flex;
  gap: var(--space-2);
}

/* Role Badges / 角色徽章 */
.capsule {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
  background: var(--bg-tertiary);
  border: 1px solid var(--surface-border);
  color: var(--text-secondary);
}

.role-administrator {
  background: rgba(139, 92, 246, 0.15);
  border-color: rgba(139, 92, 246, 0.3);
  color: #a78bfa;
}

.role-auditor {
  background: var(--color-primary-light);
  border-color: rgba(59, 130, 246, 0.3);
  color: var(--color-primary);
}

.role-viewer {
  background: var(--bg-tertiary);
  border-color: var(--surface-border);
  color: var(--text-secondary);
}

.inactive-pill {
  background: var(--color-danger-light);
  border-color: rgba(244, 63, 94, 0.3);
  color: var(--color-danger);
}

/* Status Badges / 状态徽章 */
.status-active {
  background: var(--color-success-light);
  border-color: rgba(16, 185, 129, 0.3);
  color: var(--color-success);
}

.status-revoked,
.status-expired {
  background: var(--color-danger-light);
  border-color: rgba(244, 63, 94, 0.3);
  color: var(--color-danger);
}

.status-pending {
  background: var(--color-warning-light);
  border-color: rgba(245, 158, 11, 0.3);
  color: var(--color-warning);
}

.status-accepted {
  background: var(--color-success-light);
  border-color: rgba(16, 185, 129, 0.3);
  color: var(--color-success);
}

/* Meta Information / 元信息 */
.user-meta,
.key-meta,
.invite-meta {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  margin-bottom: var(--space-4);
  padding: var(--space-3);
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
}

/* Action Buttons / 操作按钮 */
.user-actions,
.key-actions,
.invite-actions {
  display: flex;
  gap: var(--space-2);
}

.user-actions button,
.key-actions button,
.invite-actions button {
  flex: 1;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  border: 1px solid var(--surface-border);
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.user-actions button:hover,
.key-actions button:hover,
.invite-actions button:hover {
  background: var(--bg-hover);
  border-color: var(--surface-border-hover);
}

.danger-button {
  background: var(--color-danger-light) !important;
  border-color: rgba(244, 63, 94, 0.3) !important;
  color: var(--color-danger) !important;
}

.danger-button:hover {
  background: var(--color-danger) !important;
  border-color: var(--color-danger) !important;
  color: white !important;
}

/* Key Display / 密钥显示 */
.key-display,
.invite-link {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3);
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-3);
  border: 1px solid var(--surface-border);
}

.key-display code,
.invite-link code {
  flex: 1;
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-accent);
  word-break: break-all;
}

.copy-button {
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  border: 1px solid var(--surface-border);
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.copy-button:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* Modal Styles / 模态框样式 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--surface-overlay);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  animation: fadeIn var(--transition-base);
}

.modal {
  background: var(--bg-secondary);
  padding: var(--space-6);
  border-radius: var(--radius-xl);
  border: 1px solid var(--surface-border);
  width: 95%;
  max-width: 480px;
  box-shadow: var(--shadow-xl);
  animation: slideUp var(--transition-base);
}

.modal h3 {
  margin: 0 0 var(--space-5);
  font-size: var(--text-xl);
  color: var(--text-primary);
}

.modal form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.modal input,
.modal select {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  border: 1px solid var(--surface-border);
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.modal input:hover,
.modal select:hover {
  border-color: var(--surface-border-hover);
}

.modal input:focus,
.modal select:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
  outline: none;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  background: var(--bg-tertiary);
  border: 1px solid var(--surface-border);
  cursor: pointer;
  font-size: var(--text-sm);
  color: var(--text-secondary);
  transition: all var(--transition-fast);
}

.checkbox-group label:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.checkbox-group input[type="checkbox"] {
  width: auto;
  accent-color: var(--color-primary);
}

.modal-actions {
  display: flex;
  gap: var(--space-3);
  margin-top: var(--space-4);
}

.modal-actions button {
  flex: 1;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.modal-actions button:first-child {
  background: var(--bg-tertiary);
  border: 1px solid var(--surface-border);
  color: var(--text-primary);
}

.modal-actions button:first-child:hover {
  background: var(--bg-hover);
}

.modal-actions .accent-button {
  background: var(--gradient-primary);
  border: none;
  color: white;
  box-shadow: var(--shadow-md), var(--shadow-glow-primary);
}

.modal-actions .accent-button:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-lg), var(--shadow-glow-primary);
}

/* Key Top Section / 密钥顶部区域 */
.key-top,
.invite-top {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.key-top h3,
.invite-top h3 {
  flex: 1;
}

/* Responsive Design / 响应式设计 */
@media (max-width: 1024px) {
  .hero {
    grid-template-columns: 1fr;
  }
  
  .readiness-card {
    order: -1;
  }
}

@media (max-width: 768px) {
  .page {
    gap: var(--space-4);
  }
  
  .user-grid,
  .key-grid,
  .invite-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .tabs {
    flex-wrap: wrap;
    width: 100%;
  }
  
  .tab {
    flex: 1;
    text-align: center;
  }
  
  .section-heading {
    flex-direction: column;
    gap: var(--space-3);
  }
  
  .section-heading .accent-button {
    width: 100%;
  }
  
  .modal {
    padding: var(--space-4);
  }
  
  .modal-actions {
    flex-direction: column;
  }
  
  .modal-actions button {
    width: 100%;
  }
}
</style>
