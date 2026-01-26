import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { loginApi } from '@/api/auth';

interface UserInfo {
  id: number;
  username: string;
  role: string;
  company_id?: number | null;
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'));
  const user = ref<UserInfo | null>(
    token.value ? JSON.parse(localStorage.getItem('user') || 'null') : null,
  );

  const isLoggedIn = computed(() => !!token.value);

  const setAuth = (tk: string, u: UserInfo) => {
    token.value = tk;
    user.value = u;
    localStorage.setItem('token', tk);
    localStorage.setItem('user', JSON.stringify(u));
  };

  const logout = () => {
    token.value = null;
    user.value = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  const login = async (username: string, password: string) => {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/afb94993-0489-4bec-ae77-2b991e500ccf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId: 'debug-session',
        runId: 'pre-fix',
        hypothesisId: 'H2',
        location: 'src/store/auth.ts:login',
        message: 'login start',
        data: {
          hasUsername: !!username,
          hasPassword: !!password,
        },
        timestamp: Date.now(),
      }),
    }).catch(() => {});
    // #endregion
    try {
      const res = await loginApi(username, password);
      setAuth(res.access_token, res.user);
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/afb94993-0489-4bec-ae77-2b991e500ccf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: 'debug-session',
          runId: 'pre-fix',
          hypothesisId: 'H2',
          location: 'src/store/auth.ts:login',
          message: 'login success',
          data: {
            hasToken: !!res.access_token,
            hasUser: !!res.user,
            userRole: res.user?.role,
          },
          timestamp: Date.now(),
        }),
      }).catch(() => {});
      // #endregion
    } catch (error: any) {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/afb94993-0489-4bec-ae77-2b991e500ccf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: 'debug-session',
          runId: 'pre-fix',
          hypothesisId: 'H2',
          location: 'src/store/auth.ts:login',
          message: 'login error',
          data: {
            errorName: error.name,
            errorMsg: error.message,
            status: error.response?.status,
            errorData: error.response?.data,
          },
          timestamp: Date.now(),
        }),
      }).catch(() => {});
      // #endregion
      throw error;
    }
  };

  return { token, user, isLoggedIn, login, logout };
});
