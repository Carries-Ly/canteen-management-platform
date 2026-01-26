import axios from 'axios';
import { useAuthStore } from '@/store/auth';

function authAxios() {
  const auth = useAuthStore();
  const instance = axios.create();
  instance.interceptors.request.use((config) => {
    if (auth.token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${auth.token}`;
    }
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/afb94993-0489-4bec-ae77-2b991e500ccf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId: 'debug-session',
        runId: 'pre-fix',
        hypothesisId: 'H1',
        location: 'src/api/mealStandards.ts:authAxios',
        message: 'API request prepared',
        data: {
          url: config.url,
          method: config.method,
          hasToken: !!auth.token,
          hasAuthHeader: !!config.headers?.Authorization,
        },
        timestamp: Date.now(),
      }),
    }).catch(() => {});
    // #endregion
    return config;
  });
  instance.interceptors.response.use(
    (response) => response,
    (error) => {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/afb94993-0489-4bec-ae77-2b991e500ccf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: 'debug-session',
          runId: 'post-fix',
          hypothesisId: 'H3',
          location: 'src/api/mealStandards.ts:error',
          message: 'API response error',
          data: {
            url: error.config?.url,
            status: error.response?.status,
            errorMsg: error.message,
            errorData: error.response?.data,
          },
          timestamp: Date.now(),
        }),
      }).catch(() => {});
      // #endregion
      
      // 检测 token 格式错误，自动清除旧 token
      const errorMsg = error.response?.data?.msg || error.message || '';
      if (errorMsg.includes('Subject must be a string') || 
          errorMsg.includes('Token格式错误') ||
          errorMsg.includes('Token无效')) {
        // 清除旧的 token
        auth.logout();
        // 跳转到登录页
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      }
      
      return Promise.reject(error);
    }
  );
  return instance;
}

export async function fetchMealStandards(params?: { status?: string }) {
  const client = authAxios();
  const { data } = await client.get('/api/meal-standards', { params });
  return data;
}

export async function createMealStandard(payload: any) {
  const client = authAxios();
  const { data } = await client.post('/api/meal-standards', payload);
  return data;
}

export async function updateMealStandard(id: number, payload: any) {
  const client = authAxios();
  const { data } = await client.put(`/api/meal-standards/${id}`, payload);
  return data;
}
