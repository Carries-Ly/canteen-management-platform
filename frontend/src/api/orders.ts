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

export interface OrderItem {
  id: number;
  meal_name: string;
  meal_type: string;
  unit_price: number;
  quantity: number;
}

export interface Order {
  id: number;
  company_id: number;
  company_name: string | null;
  order_date: string;
  status: string;
  items: OrderItem[];
  total_quantity: number;
  total_amount: number;
  current_stage?: string | null;
  created_at?: string | null;
}

export async function fetchOrders(params?: {
  order_date?: string;
  company_keyword?: string;
  status?: string;
}) {
  const client = authAxios();
  const { data } = await client.get<Order[]>('/api/orders', { params });
  return data;
}

export async function getOrder(id: number) {
  const client = authAxios();
  const { data } = await client.get<Order>(`/api/orders/${id}`);
  return data;
}

export async function createOrder(payload: {
  order_date: string;
  items: Array<{
    meal_standard_id: number;
    meal_type: string;
    quantity: number;
    unit_price?: number;
  }>;
}) {
  const client = authAxios();
  const { data } = await client.post<{ ids: number[]; count: number }>('/api/orders', payload);
  return data;
}

export async function updateOrder(
  id: number,
  payload: {
    status?: string;
    items?: Array<{
      meal_standard_id: number;
      meal_type: string;
      quantity: number;
      unit_price?: number;
    }>;
  }
) {
  const client = authAxios();
  const { data } = await client.put<{ msg: string }>(`/api/orders/${id}`, payload);
  return data;
}

export async function deleteOrder(id: number) {
  const client = authAxios();
  const { data } = await client.delete<{ msg: string }>(`/api/orders/${id}`);
  return data;
}

export async function confirmOrder(id: number) {
  const client = authAxios();
  const { data } = await client.post<{ msg: string }>(`/api/orders/${id}/confirm`);
  return data;
}

export async function batchConfirmOrders(orderIds: number[]) {
  const client = authAxios();
  const { data } = await client.post<{ msg: string; success_count: number; errors: string[] }>(
    '/api/orders/batch-confirm',
    { order_ids: orderIds }
  );
  return data;
}

