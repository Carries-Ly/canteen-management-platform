<template>
  <el-menu
    class="menu"
    :collapse="collapsed"
    router
    :default-active="$route.path"
    background-color="#1f2d3d"
    text-color="#bfcbd9"
    active-text-color="#27ae60"
  >
    <el-menu-item index="/dashboard" @click="$emit('select', '/dashboard')">
      <span>首页总览</span>
    </el-menu-item>
    <el-menu-item index="/orders" @click="$emit('select', '/orders')">
      <span>订单管理</span>
    </el-menu-item>
    <el-menu-item index="/logistics" @click="$emit('select', '/logistics')">
      <span>运餐物流</span>
    </el-menu-item>
    <el-menu-item
      index="/companies"
      v-if="['superadmin', 'admin'].includes(role)"
      @click="$emit('select', '/companies')"
    >
      <span>客户管理</span>
    </el-menu-item>
    <el-menu-item
      index="/meal-standards"
      v-if="['superadmin', 'admin'].includes(role)"
      @click="$emit('select', '/meal-standards')"
    >
      <span>餐标配置</span>
    </el-menu-item>
    <el-menu-item
      index="/staff"
      v-if="role === 'superadmin'"
      @click="$emit('select', '/staff')"
    >
      <span>员工管理</span>
    </el-menu-item>
  </el-menu>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useAuthStore } from '@/store/auth';

const props = defineProps<{ collapsed: boolean }>();

const auth = useAuthStore();
const role = computed(() => auth.user?.role || '');

// #region agent log
fetch('http://127.0.0.1:7242/ingest/afb94993-0489-4bec-ae77-2b991e500ccf', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    sessionId: 'debug-session',
    runId: 'pre-fix',
    hypothesisId: 'H3',
    location: 'src/components/layout/Sidebar.vue:36',
    message: 'Sidebar render with role',
    data: {
      role: role.value || null,
      hasUser: !!auth.user,
    },
    timestamp: Date.now(),
  }),
}).catch(() => {});
// #endregion agent log
</script>

<style scoped>
.menu {
  height: 100%;
  border-right: none;
}
</style>
