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
        location: 'src/api/companies.ts:authAxios',
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
    (response) => {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/afb94993-0489-4bec-ae77-2b991e500ccf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: 'debug-session',
          runId: 'pre-fix',
          hypothesisId: 'H1',
          location: 'src/api/companies.ts:response',
          message: 'API response success',
          data: {
            url: response.config.url,
            status: response.status,
            hasData: !!response.data,
          },
          timestamp: Date.now(),
        }),
      }).catch(() => {});
      // #endregion
      return response;
    },
    (error) => {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/afb94993-0489-4bec-ae77-2b991e500ccf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: 'debug-session',
          runId: 'post-fix',
          hypothesisId: 'H3',
          location: 'src/api/companies.ts:error',
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

export interface Company {
  id: number;
  name: string;
  contact_person?: string | null;
  contact_phone?: string | null;
  address?: string | null;
  created_at?: string | null;
}

export async function fetchCompanies(params?: { keyword?: string }) {
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/afb94993-0489-4bec-ae77-2b991e500ccf', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      sessionId: 'debug-session',
      runId: 'pre-fix',
      hypothesisId: 'H1',
      location: 'src/api/companies.ts:fetchCompanies',
      message: 'fetchCompanies called',
      data: { params },
      timestamp: Date.now(),
    }),
  }).catch(() => {});
  // #endregion
  const client = authAxios();
  const { data } = await client.get<Company[]>('/api/companies', { params });
  return data;
}

export async function getCompany(id: number) {
  const client = authAxios();
  const { data } = await client.get<Company>(`/api/companies/${id}`);
  return data;
}

export async function createCompany(payload: {
  name: string;
  contact_person?: string;
  contact_phone?: string;
  address?: string;
}) {
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/afb94993-0489-4bec-ae77-2b991e500ccf', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      sessionId: 'debug-session',
      runId: 'pre-fix',
      hypothesisId: 'H1',
      location: 'src/api/companies.ts:createCompany',
      message: 'createCompany called',
      data: { hasName: !!payload.name },
      timestamp: Date.now(),
    }),
  }).catch(() => {});
  // #endregion
  const client = authAxios();
  const { data } = await client.post<Company>('/api/companies', payload);
  return data;
}

export async function updateCompany(
  id: number,
  payload: {
    name?: string;
    contact_person?: string;
    contact_phone?: string;
    address?: string;
  }
) {
  const client = authAxios();
  const { data } = await client.put<Company>(`/api/companies/${id}`, payload);
  return data;
}

export async function deleteCompany(id: number) {
  const client = authAxios();
  const { data } = await client.delete<{ msg: string }>(`/api/companies/${id}`);
  return data;
}
