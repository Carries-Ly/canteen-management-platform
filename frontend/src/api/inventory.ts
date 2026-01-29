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
      if (
        errorMsg.includes('Token已过期') ||
        errorMsg.includes('Token无效') ||
        errorMsg.includes('缺少Token')
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

export interface InventoryItem {
  ingredient_id: number;
  ingredient_name: string;
  category: string | null;
  unit: string;
  safety_stock: number;
  current_quantity: number;
  last_in_date: string | null;
  last_out_date: string | null;
}

export async function fetchInventory(params?: {
  keyword?: string;
  category?: string;
}) {
  const client = authAxios();
  const { data } = await client.get<InventoryItem[]>('/api/inventory', { params });
  return data;
}

export async function stockIn(params: {
  ingredient_id: number;
  quantity: number;
  in_date?: string;
  expiry_date?: string;
  scale_weight?: number;
}) {
  const client = authAxios();
  const { data } = await client.post<{ msg: string; id: number }>('/api/inventory/stock-in', params);
  return data;
}

export async function stockOut(params: {
  ingredient_id: number;
  quantity: number;
  out_date?: string;
  purchase_order_id?: number;
  purpose?: string;
  scale_weight?: number;
}) {
  const client = authAxios();
  const { data } = await client.post<{ msg: string; id: number }>('/api/inventory/stock-out', params);
  return data;
}

