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

export interface SubMenu {
  id: number;
  weekly_menu_id: number;
  week_year?: number;
  week_number?: number;
  company_id: number;
  company_name: string | null;
  name: string | null;
  status: string;
  created_by: number | null;
  created_at: string | null;
  items?: SubMenuItem[];
}

export interface SubMenuItem {
  id: number;
  day_of_week: number;
  meal_type: string;
  dish_name: string;
  dish_category: string | null;
}

export async function fetchSubMenus(params?: {
  weekly_menu_id?: number;
  company_id?: number;
}) {
  const client = authAxios();
  const { data } = await client.get<SubMenu[]>('/api/sub-menus', { params });
  return data;
}

export async function getSubMenu(id: number) {
  const client = authAxios();
  const { data } = await client.get<SubMenu>(`/api/sub-menus/${id}`);
  return data;
}

export async function selectSubMenu(params: {
  weekly_menu_id: number;
  company_ids: number[];
  selected_items: Array<{
    weekly_menu_item_id?: number;
    day_of_week?: number;
    meal_type?: string;
    dish_name?: string;
    dish_category?: string | null;
  }>;
  name?: string;
}) {
  const client = authAxios();
  const { data } = await client.post<{ ids: number[]; count: number; msg: string }>(
    '/api/sub-menus/select',
    params
  );
  return data;
}

export async function getSubMenuHistory(params?: {
  company_id?: number;
  week_year?: number;
}) {
  const client = authAxios();
  const { data } = await client.get<SubMenu[]>('/api/sub-menus/history', { params });
  return data;
}

