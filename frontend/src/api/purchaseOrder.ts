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

export interface PurchaseOrder {
  id: number;
  order_number: string;
  sub_menu_id: number | null;
  total_amount: number;
  status: string;
  created_by: number | null;
  created_at: string | null;
  items?: PurchaseOrderItem[];
}

export interface PurchaseOrderItem {
  id: number;
  ingredient_id: number;
  ingredient_name?: string;
  required_quantity: number;
  stock_quantity: number;
  use_stock: boolean;
  purchase_quantity: number;
  unit_price: number;
  subtotal: number;
}

export async function fetchPurchaseOrders(params?: {
  status?: string;
}) {
  const client = authAxios();
  const { data } = await client.get<PurchaseOrder[]>('/api/purchase-orders', { params });
  return data;
}

export async function createPurchaseOrder(params: {
  sub_menu_id?: number;
  items: Array<{
    ingredient_id: number;
    required_quantity: number;
    use_stock: boolean;
    purchase_quantity: number;
    unit_price: number;
  }>;
}) {
  const client = authAxios();
  const { data } = await client.post<{ id: number; order_number: string; msg: string }>(
    '/api/purchase-orders',
    params
  );
  return data;
}

