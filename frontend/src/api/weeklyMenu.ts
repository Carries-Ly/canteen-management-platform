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

export interface WeeklyMenu {
  id: number;
  week_year: number;
  week_number: number;
  week_start_date: string;
  week_end_date: string;
  status: string;
  created_by: number | null;
  created_at: string | null;
  updated_at: string | null;
  items?: WeeklyMenuItem[];
}

export interface WeeklyMenuItem {
  id: number;
  day_of_week: number; // 1-7, 1=周一
  meal_type: string; // 早餐/午餐/晚餐/夜宵
  dish_name: string;
  dish_category: string | null; // 大荤一/大荤二/小荤一/小荤二/素菜一/素菜二/例汤
  sort_order: number;
}

export async function fetchWeeklyMenus(params?: {
  week_year?: number;
  week_number?: number;
}) {
  const client = authAxios();
  const { data } = await client.get<WeeklyMenu[]>('/api/weekly-menus', { params });
  return data;
}

export async function getWeeklyMenu(id: number) {
  const client = authAxios();
  const { data } = await client.get<WeeklyMenu>(`/api/weekly-menus/${id}`);
  return data;
}

export async function generateWeeklyMenu(weekYear: number, weekNumber: number) {
  const client = authAxios();
  const { data } = await client.post<{ id: number; msg: string }>('/api/weekly-menus/generate', {
    week_year: weekYear,
    week_number: weekNumber,
  });
  return data;
}

export async function createWeeklyMenu(menu: {
  week_year: number;
  week_number: number;
  status?: string;
  items: WeeklyMenuItem[];
}) {
  const client = authAxios();
  const { data } = await client.post<{ id: number; msg: string }>('/api/weekly-menus', menu);
  return data;
}

export async function updateWeeklyMenu(id: number, menu: { status?: string; items?: WeeklyMenuItem[] }) {
  const client = authAxios();
  const { data } = await client.put<{ msg: string }>(`/api/weekly-menus/${id}`, menu);
  return data;
}

export async function replaceWeeklyMenuItem(
  menuId: number,
  payload: { day_of_week: number; meal_type: string; dish_category: string; new_dish_name: string }
) {
  const client = authAxios();
  const { data } = await client.put<{ msg: string; item: WeeklyMenuItem }>(
    `/api/weekly-menus/${menuId}/items/replace`,
    payload
  );
  return data;
}

