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

export interface LogisticsData {
  order_id: number;
  company_id: number;
  company_name: string | null;
  order_date: string;
  meal_types: string[];
  stage_prepare_loaded: boolean;
  time_prepare_loaded: string | null;
  stage_shipping: boolean;
  time_shipping: string | null;
  stage_arrived: boolean;
  time_arrived: string | null;
  stage_recycled: boolean;
  time_recycled: string | null;
}

export interface LogisticsStatistics {
  prepare_loaded: number;
  shipping: number;
  arrived: number;
  recycled: number;
}

export async function fetchLogistics(params?: {
  order_date?: string;
  meal_type?: string;
}) {
  const client = authAxios();
  const { data } = await client.get<LogisticsData[]>('/api/logistics', { params });
  return data;
}

export async function getLogisticsStatistics(params: {
  order_date: string;
  meal_type: string;
}) {
  const client = authAxios();
  const { data } = await client.get<LogisticsStatistics>('/api/logistics/statistics', {
    params,
  });
  return data;
}

export async function updateLogisticsStage(orderId: number, stage: string) {
  const client = authAxios();
  const { data } = await client.post<{ msg: string }>(
    `/api/logistics/${orderId}/update_stage`,
    { stage }
  );
  return data;
}

export async function batchUpdateLogisticsStages(updates: Array<{ order_id: number; stage: string }>) {
  const client = authAxios();
  const { data } = await client.post<{
    msg: string;
    success_count: number;
    errors: string[];
  }>('/api/logistics/batch-update-stages', { updates });
  return data;
}

