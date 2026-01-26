<template>
  <el-container class="layout">
    <el-aside
      :width="isMobile ? (sidebarOpened ? '200px' : '0px') : collapsed ? '64px' : '200px'"
      class="sidebar"
    >
      <Sidebar :collapsed="collapsed" @select="onMenuSelect" />
    </el-aside>
    <el-container>
      <el-header class="header">
        <HeaderBar
          :collapsed="collapsed"
          :is-mobile="isMobile"
          @toggleSidebar="toggleSidebar"
          @toggleMobile="toggleMobile"
        />
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import Sidebar from './Sidebar.vue';
import HeaderBar from './HeaderBar.vue';

const collapsed = ref(false);
const isMobile = ref(false);
const sidebarOpened = ref(false);
const router = useRouter();

const onMenuSelect = (path: string) => {
  router.push(path);
  if (isMobile.value) sidebarOpened.value = false;
};

const handleResize = () => {
  isMobile.value = window.innerWidth < 768;
};

onMounted(() => {
  handleResize();
  window.addEventListener('resize', handleResize);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
});

const toggleSidebar = () => {
  collapsed.value = !collapsed.value;
};

const toggleMobile = () => {
  sidebarOpened.value = !sidebarOpened.value;
};
</script>

<style scoped>
.layout {
  height: 100vh;
}
.sidebar {
  transition: width 0.2s;
  overflow: hidden;
}
.header {
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}
.main {
  padding: 16px;
}
</style>
