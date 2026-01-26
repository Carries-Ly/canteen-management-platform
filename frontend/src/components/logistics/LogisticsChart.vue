<template>
  <div ref="chartRef" class="chart-container"></div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from 'vue';
import * as echarts from 'echarts';

interface Statistics {
  prepare_loaded: number;
  shipping: number;
  arrived: number;
  recycled: number;
}

const props = defineProps<{
  statistics?: Statistics | null;
  date?: string | null;
  mealType?: string | null;
}>();

const chartRef = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

const initChart = () => {
  if (!chartRef.value) return;
  chart = echarts.init(chartRef.value);
  updateChart();
};

const updateChart = () => {
  if (!chart) return;
  
  const stats = props.statistics || {
    prepare_loaded: 0,
    shipping: 0,
    arrived: 0,
    recycled: 0,
  };
  
  const title = props.date && props.mealType
    ? `${props.date} ${getMealTypeName(props.mealType)} 物流阶段完成情况`
    : '物流阶段完成情况';
  
  chart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    title: { text: title, left: 'center', textStyle: { fontSize: 14 } },
    xAxis: {
      type: 'category',
      data: ['备餐装车中', '运输中', '已到达', '已回收'],
    },
    yAxis: { type: 'value', name: '订单数' },
    series: [
      {
        name: '完成订单数',
        type: 'bar',
        data: [
          stats.prepare_loaded,
          stats.shipping,
          stats.arrived,
          stats.recycled,
        ],
        itemStyle: { color: '#27ae60' },
        label: {
          show: true,
          position: 'top',
        },
      },
    ],
  });
};

const getMealTypeName = (mealType: string) => {
  const names: Record<string, string> = {
    breakfast: '早餐',
    lunch: '午餐',
    dinner: '晚餐',
    supper: '夜宵',
  };
  return names[mealType] || mealType;
};

onMounted(() => {
  initChart();
});

onBeforeUnmount(() => {
  chart?.dispose();
});

watch(
  () => [props.statistics, props.date, props.mealType],
  () => {
    updateChart();
  },
  { deep: true }
);
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 300px;
}
</style>

