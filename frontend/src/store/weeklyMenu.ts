import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useWeeklyMenuStore = defineStore('weeklyMenu', () => {
  const pollInterval = ref<number | null>(null);
  const generatingMenuId = ref<number | null>(null);
  const pollCount = ref(0);
  const MAX_POLL_COUNT = 600; // 最大轮询600次（20分钟，每2秒一次）

  const startPolling = (intervalId: number, menuId: number) => {
    pollInterval.value = intervalId;
    generatingMenuId.value = menuId;
    pollCount.value = 0;
  };

  const stopPolling = () => {
    if (pollInterval.value !== null) {
      clearInterval(pollInterval.value);
      pollInterval.value = null;
    }
    generatingMenuId.value = null;
    pollCount.value = 0;
  };

  const incrementPollCount = () => {
    pollCount.value++;
  };

  const resetPollCount = () => {
    pollCount.value = 0;
  };

  return {
    pollInterval,
    generatingMenuId,
    pollCount,
    MAX_POLL_COUNT,
    startPolling,
    stopPolling,
    incrementPollCount,
    resetPollCount,
  };
});

