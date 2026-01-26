<template>
  <div class="header-bar">
    <div class="left">
      <el-button text @click="$emit('toggleSidebar')" class="pc-only">
        菜单
      </el-button>
      <el-button text @click="$emit('toggleMobile')" class="mobile-only">
        菜单
      </el-button>
      <span class="title">中央厨房管理平台</span>
    </div>
    <div class="right">
      <el-dropdown>
        <span class="user">
          {{ user?.username || '未登录' }}
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="onLogout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'vue-router';

const props = defineProps<{ collapsed: boolean; isMobile?: boolean }>();

const auth = useAuthStore();
const router = useRouter();

const user = computed(() => auth.user);

const onLogout = () => {
  auth.logout();
  router.push('/login');
};
</script>

<style scoped>
.header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}
.left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.title {
  font-weight: 600;
  color: #27ae60;
}
.right {
  display: flex;
  align-items: center;
}
.mobile-only {
  display: none;
}
.pc-only {
  display: inline-flex;
}
@media (max-width: 768px) {
  .mobile-only {
    display: inline-flex;
  }
  .pc-only {
    display: none;
  }
}
</style>
