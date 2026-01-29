import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import Login from '@/views/Login.vue';
import AppLayout from '@/components/layout/AppLayout.vue';
import Dashboard from '@/views/Dashboard.vue';
import OrdersList from '@/views/orders/OrdersList.vue';
import OrderDetail from '@/views/orders/OrderDetail.vue';
import LogisticsOverview from '@/views/logistics/LogisticsOverview.vue';
import MealStandards from '@/views/system/MealStandards.vue';
import Companies from '@/views/system/Companies.vue';
import Staff from '@/views/system/Staff.vue';
import WeeklyMenu from '@/views/menu/WeeklyMenu.vue';
import SubMenu from '@/views/menu/SubMenu.vue';
import InventoryManagement from '@/views/inventory/InventoryManagement.vue';
import PurchaseList from '@/views/purchase/PurchaseList.vue';
import { useAuthStore } from '@/store/auth';

const routes: RouteRecordRaw[] = [
  { path: '/login', name: 'Login', component: Login, meta: { public: true } },
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'Dashboard', component: Dashboard },
      { path: 'orders', name: 'OrdersList', component: OrdersList },
      { path: 'orders/:id', name: 'OrderDetail', component: OrderDetail, props: true },
      { path: 'logistics', name: 'LogisticsOverview', component: LogisticsOverview },
      {
        path: 'companies',
        name: 'Companies',
        component: Companies,
        meta: { roles: ['superadmin', 'admin'] },
      },
      {
        path: 'meal-standards',
        name: 'MealStandards',
        component: MealStandards,
        meta: { roles: ['superadmin', 'admin'] },
      },
      {
        path: 'staff',
        name: 'Staff',
        component: Staff,
        meta: { roles: ['superadmin'] },
      },
      {
        path: 'weekly-menu',
        name: 'WeeklyMenu',
        component: WeeklyMenu,
        meta: { roles: ['user', 'admin', 'superadmin'] },
      },
      {
        path: 'sub-menu',
        name: 'SubMenu',
        component: SubMenu,
        meta: { roles: ['user', 'admin', 'superadmin', 'customer'] },
      },
      {
        path: 'inventory',
        name: 'InventoryManagement',
        component: InventoryManagement,
        meta: { roles: ['user', 'admin', 'superadmin'] },
      },
      {
        path: 'purchase-list',
        name: 'PurchaseList',
        component: PurchaseList,
        meta: { roles: ['user', 'admin', 'superadmin'] },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore();
  if (to.meta.public) return next();
  if (!auth.isLoggedIn) return next('/login');

  const needRoles = to.meta.roles as string[] | undefined;
  if (needRoles && !needRoles.includes(auth.user?.role || '')) {
    return next('/dashboard');
  }
  next();
});

export default router;
