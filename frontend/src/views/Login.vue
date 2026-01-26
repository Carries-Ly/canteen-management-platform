<template>
  <div class="login-wrapper">
    <el-card class="login-card">
      <h2 class="title">中央厨房管理平台</h2>
      <el-form @submit.prevent="onSubmit">
        <el-form-item>
          <el-input v-model="username" placeholder="用户名" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="password" placeholder="密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" style="width: 100%" @click="onSubmit" :loading="loading">
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'vue-router';

const username = ref('');
const password = ref('');
const loading = ref(false);

const auth = useAuthStore();
const router = useRouter();

const onSubmit = async () => {
  if (!username.value || !password.value) return;
  loading.value = true;
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/afb94993-0489-4bec-ae77-2b991e500ccf', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      sessionId: 'debug-session',
      runId: 'pre-fix',
      hypothesisId: 'H2',
      location: 'src/views/Login.vue:onSubmit',
      message: 'Login onSubmit',
      data: {
        hasUsername: !!username.value,
        hasPassword: !!password.value,
      },
      timestamp: Date.now(),
    }),
  }).catch(() => {});
  // #endregion
  try {
    await auth.login(username.value, password.value);
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/afb94993-0489-4bec-ae77-2b991e500ccf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId: 'debug-session',
        runId: 'pre-fix',
        hypothesisId: 'H2',
        location: 'src/views/Login.vue:onSubmit',
        message: 'Login success, redirecting',
        data: {},
        timestamp: Date.now(),
      }),
    }).catch(() => {});
    // #endregion
    router.push('/');
  } catch (error: any) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/afb94993-0489-4bec-ae77-2b991e500ccf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId: 'debug-session',
        runId: 'pre-fix',
        hypothesisId: 'H2',
        location: 'src/views/Login.vue:onSubmit',
        message: 'Login error',
        data: {
          errorName: error.name,
          errorMsg: error.message,
          status: error.response?.status,
        },
        timestamp: Date.now(),
      }),
    }).catch(() => {});
    // #endregion
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #27ae60, #2ecc71);
}
.login-card {
  width: 360px;
  max-width: 90%;
}
.title {
  text-align: center;
  margin-bottom: 24px;
  color: #27ae60;
}
</style>
