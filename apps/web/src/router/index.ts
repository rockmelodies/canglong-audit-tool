import { createRouter, createWebHistory } from 'vue-router';
import { getAccessToken } from '../auth/session';
import LoginView from '../views/LoginView.vue';
import MissionsView from '../views/MissionsView.vue';
import OverviewView from '../views/OverviewView.vue';
import ProjectDetailView from '../views/ProjectDetailView.vue';
import ProjectsView from '../views/ProjectsView.vue';
import ReportView from '../views/ReportView.vue';
import SettingsView from '../views/SettingsView.vue';
import UsersView from '../views/UsersView.vue';
import WorkspaceView from '../views/WorkspaceView.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/projects',
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { public: true },
    },
    {
      path: '/overview',
      name: 'overview',
      component: OverviewView,
      meta: { requiresAuth: true },
    },
    {
      path: '/projects',
      name: 'projects',
      component: ProjectsView,
      meta: { requiresAuth: true },
    },
    {
      path: '/projects/:id',
      name: 'project-detail',
      component: ProjectDetailView,
      meta: { requiresAuth: true },
    },
    {
      path: '/workspace',
      name: 'workspace',
      component: WorkspaceView,
      meta: { requiresAuth: true },
    },
    {
      path: '/missions',
      name: 'missions',
      component: MissionsView,
      meta: { requiresAuth: true },
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView,
      meta: { requiresAuth: true },
    },
    {
      path: '/reports/:jobId',
      name: 'report',
      component: ReportView,
      meta: { requiresAuth: true },
    },
    {
      path: '/users',
      name: 'users',
      component: UsersView,
      meta: { requiresAuth: true, requiresAdmin: true },
    },
  ],
});

router.beforeEach((to) => {
  const hasToken = Boolean(getAccessToken());
  if (to.meta.requiresAuth && !hasToken) {
    return '/login';
  }

  if (to.path === '/login' && hasToken) {
    return '/overview';
  }

  return true;
});

export default router;
