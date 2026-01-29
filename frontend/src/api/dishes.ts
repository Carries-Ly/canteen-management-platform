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
      const errorMsg = error.response?.data?.msg || error.message || '';
      if (errorMsg.includes('Token已过期') || errorMsg.includes('Token无效') || errorMsg.includes('缺少Token')) {
        auth.logout();
        if (typeof window !== 'undefined') window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );
  return instance;
}

export interface DishSearchItem {
  id: string | number;
  name: string;
}

// 占位接口：你后续可以把后端替换为真实“菜品库模糊查询”实现
export async function searchDishes(q: string) {
  const client = authAxios();
  const { data } = await client.get<{ items: DishSearchItem[] }>('/api/dishes/search', { params: { q } });
  return data.items || [];
}

