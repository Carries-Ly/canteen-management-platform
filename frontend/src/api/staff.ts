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
    return config;
  });
  instance.interceptors.response.use(
    (response) => response,
    (error) => {
      // 检测 token 格式错误，自动清除旧 token
      const errorMsg = error.response?.data?.msg || error.message || '';
      if (
        errorMsg.includes('Subject must be a string') ||
        errorMsg.includes('Token格式错误') ||
        errorMsg.includes('Token无效')
      ) {
        auth.logout();
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      }
      return Promise.reject(error);
    }
  );
  return instance;
}

export interface Staff {
  id: number;
  username: string;
  role: 'admin' | 'user';
  company_id?: number | null;
}

export async function fetchStaff(params?: { role?: 'admin' | 'user'; keyword?: string }) {
  const client = authAxios();
  const { data } = await client.get<Staff[]>('/api/staff', { params });
  return data;
}

export async function getStaff(id: number) {
  const client = authAxios();
  const { data } = await client.get<Staff>(`/api/staff/${id}`);
  return data;
}

export async function createStaff(payload: {
  username: string;
  password: string;
  role: 'admin' | 'user';
}) {
  const client = authAxios();
  const { data } = await client.post<Staff>('/api/staff', payload);
  return data;
}

export async function updateStaff(
  id: number,
  payload: {
    username?: string;
    role?: 'admin' | 'user';
  }
) {
  const client = authAxios();
  const { data } = await client.put<Staff>(`/api/staff/${id}`, payload);
  return data;
}

export async function resetStaffPassword(id: number, newPassword?: string) {
  const client = authAxios();
  const { data } = await client.post<{ msg: string; new_password?: string }>(
    `/api/staff/${id}/reset-password`,
    newPassword ? { new_password: newPassword } : {}
  );
  return data;
}

export async function deleteStaff(id: number) {
  const client = authAxios();
  const { data } = await client.delete<{ msg: string }>(`/api/staff/${id}`);
  return data;
}

