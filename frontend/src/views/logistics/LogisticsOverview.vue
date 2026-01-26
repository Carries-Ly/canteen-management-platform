<template>
  <el-card>
    <div class="toolbar">
      <el-select
        v-model="mealType"
        placeholder="选择餐别"
        style="width: 150px"
        clearable
        @change="handleFilterChange"
      >
        <el-option label="早餐" value="早餐" />
        <el-option label="午餐" value="午餐" />
        <el-option label="晚餐" value="晚餐" />
        <el-option label="夜宵" value="夜宵" />
      </el-select>
      <el-date-picker
        v-model="date"
        type="date"
        placeholder="选择日期"
        style="max-width: 200px"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        @change="handleFilterChange"
      />
      <el-input
        v-if="isStaff"
        v-model="companyKeyword"
        placeholder="搜索公司名称"
        clearable
        style="width: 200px"
        @clear="handleFilterChange"
        @keyup.enter="loadData"
      />
      <el-button type="primary" @click="loadData" :loading="loading">查询</el-button>
    </div>

    <!-- user/admin/superadmin 视图 -->
    <template v-if="isStaff">
      <!-- 统计图表 -->
      <div v-if="date && mealType" class="chart-section">
        <LogisticsChart
          :date="date"
          :meal-type="mealType"
          :statistics="statistics"
        />
      </div>

      <!-- 企业客户筛选和物流状态 -->
      <div v-if="date && mealType" class="companies-section">
        <div class="companies-header">
          <h3>企业客户物流状态（{{ date }} {{ getMealTypeName(mealType) }}）</h3>
          <el-checkbox
            :indeterminate="isIndeterminate"
            v-model="checkAll"
            @change="handleCheckAllChange"
          >
            全选
          </el-checkbox>
        </div>

        <div class="companies-board">
          <div
            v-for="company in groupedByCompany"
            :key="company.company_id"
            class="company-card"
          >
            <div class="company-header">
              <el-checkbox
                v-model="selectedCompanies"
                :label="company.company_id"
                @change="handleCompanyCheckChange"
              >
                <strong>{{ company.company_name }}</strong>
              </el-checkbox>
            </div>

            <div
              v-for="logistics in company.orders"
              :key="`${logistics.order_id}-${logistics.stage_prepare_loaded}-${logistics.stage_shipping}-${logistics.stage_arrived}-${logistics.stage_recycled}`"
              class="logistics-item"
            >
              <LogisticsSteps
                :key="`steps-${logistics.order_id}-${logistics.stage_prepare_loaded}-${logistics.stage_shipping}-${logistics.stage_arrived}-${logistics.stage_recycled}`"
                :order-id="logistics.order_id"
                :stage-prepare-loaded="logistics.stage_prepare_loaded"
                :time-prepare-loaded="logistics.time_prepare_loaded"
                :stage-shipping="logistics.stage_shipping"
                :time-shipping="logistics.time_shipping"
                :stage-arrived="logistics.stage_arrived"
                :time-arrived="logistics.time_arrived"
                :stage-recycled="logistics.stage_recycled"
                :time-recycled="logistics.time_recycled"
                :show-actions="selectedCompanies.includes(company.company_id)"
                :user-role="role"
                @stage-change="handleOrderStageChange"
              />
            </div>
          </div>

          <!-- 批量确认按钮 -->
          <div v-if="selectedCompanies.length > 0 && hasSelectedOrders" class="batch-actions">
            <div class="batch-info">
              <span>已选择 {{ Object.keys(selectedOrderStages).length }} 个订单进行更新</span>
            </div>
            <el-button
              type="primary"
              size="large"
              @click="handleBatchConfirm"
              :loading="batchUpdating"
            >
              批量确认更新 ({{ Object.keys(selectedOrderStages).length }})
            </el-button>
          </div>

          <el-empty v-if="groupedByCompany.length === 0" description="暂无数据" />
        </div>
      </div>
    </template>

    <!-- customer 视图 -->
    <template v-else>
      <div v-if="date && mealType" class="customer-section">
        <h3>{{ date }} {{ getMealTypeName(mealType) }} 物流状态</h3>
        <div class="customer-logistics">
          <div
            v-for="logistics in customerLogistics"
            :key="logistics.order_id"
            class="logistics-item"
          >
            <div class="company-name">{{ logistics.company_name }}</div>
            <LogisticsSteps
              :order-id="logistics.order_id"
              :stage-prepare-loaded="logistics.stage_prepare_loaded"
              :time-prepare-loaded="logistics.time_prepare_loaded"
              :stage-shipping="logistics.stage_shipping"
              :time-shipping="logistics.time_shipping"
              :stage-arrived="logistics.stage_arrived"
              :time-arrived="logistics.time_arrived"
              :stage-recycled="logistics.stage_recycled"
              :time-recycled="logistics.time_recycled"
              :show-actions="false"
              :user-role="role"
            />
          </div>
          <el-empty v-if="customerLogistics.length === 0" description="暂无数据" />
        </div>
      </div>
    </template>

    <div v-if="!date || !mealType" class="empty-tip">
      <el-empty description="请选择日期和餐别进行查询" />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { useAuthStore } from '@/store/auth';
import LogisticsChart from '@/components/logistics/LogisticsChart.vue';
import LogisticsSteps from '@/components/logistics/LogisticsSteps.vue';
import {
  fetchLogistics,
  getLogisticsStatistics,
  updateLogisticsStage,
  batchUpdateLogisticsStages,
  type LogisticsData,
  type LogisticsStatistics,
} from '@/api/logistics';

const auth = useAuthStore();
const role = computed(() => auth.user?.role || '');
const isStaff = computed(() => ['user', 'admin', 'superadmin'].includes(role.value));

const loading = ref(false);
const batchUpdating = ref(false);
const date = ref<string | null>(null);
const mealType = ref<string | null>(null);
const companyKeyword = ref('');
const logisticsList = ref<LogisticsData[]>([]);
const statistics = ref<LogisticsStatistics | null>(null);
const selectedCompanies = ref<number[]>([]);
// 存储每个订单选择的状态：{ orderId: stage }
const selectedOrderStages = ref<Record<number, string>>({});

// 按企业分组（支持公司名称筛选）
const groupedByCompany = computed(() => {
  const groups: Record<
    number,
    { company_id: number; company_name: string; orders: LogisticsData[] }
  > = {};
  
  for (const item of logisticsList.value) {
    // 如果设置了公司关键词，进行筛选
    if (companyKeyword.value && item.company_name) {
      if (!item.company_name.toLowerCase().includes(companyKeyword.value.toLowerCase())) {
        continue;
      }
    }
    
    if (!groups[item.company_id]) {
      groups[item.company_id] = {
        company_id: item.company_id,
        company_name: item.company_name || '未知企业',
        orders: [],
      };
    }
    groups[item.company_id].orders.push(item);
  }
  
  return Object.values(groups);
});

// customer 视图的物流数据
const customerLogistics = computed(() => {
  return logisticsList.value;
});

// 全选状态
const checkAll = computed({
  get() {
    if (groupedByCompany.value.length === 0) return false;
    return selectedCompanies.value.length === groupedByCompany.value.length;
  },
  set(val: boolean) {
    if (val) {
      selectedCompanies.value = groupedByCompany.value.map((c) => c.company_id);
    } else {
      selectedCompanies.value = [];
    }
  },
});

const isIndeterminate = computed(() => {
  const checkedCount = selectedCompanies.value.length;
  return checkedCount > 0 && checkedCount < groupedByCompany.value.length;
});

const handleCheckAllChange = (val: boolean) => {
  selectedCompanies.value = val ? groupedByCompany.value.map((c) => c.company_id) : [];
  // 如果取消全选，清除所有订单的状态选择
  if (!val) {
    selectedOrderStages.value = {};
  }
};

const handleCompanyCheckChange = () => {
  // 当取消选择企业时，清除该企业下所有订单的选中状态
  const allSelectedOrderIds = new Set<number>();
  for (const companyId of selectedCompanies.value) {
    const company = groupedByCompany.value.find((c) => c.company_id === companyId);
    if (company) {
      for (const logistics of company.orders) {
        allSelectedOrderIds.add(logistics.order_id);
      }
    }
  }
  
  // 移除不在选中企业中的订单的状态选择
  for (const orderId of Object.keys(selectedOrderStages.value)) {
    const orderIdNum = parseInt(orderId, 10);
    if (!allSelectedOrderIds.has(orderIdNum)) {
      delete selectedOrderStages.value[orderIdNum];
    }
  }
};

const getMealTypeName = (type: string) => {
  const names: Record<string, string> = {
    breakfast: '早餐',
    lunch: '午餐',
    dinner: '晚餐',
    supper: '夜宵',
  };
  return names[type] || type;
};

const canOperateStage = (stage: string) => {
  if (stage === 'prepare_loaded' || stage === 'shipping') {
    return role.value === 'admin' || role.value === 'superadmin';
  }
  if (stage === 'arrived' || stage === 'recycled') {
    return role.value === 'admin' || role.value === 'superadmin' || role.value === 'user';
  }
  return false;
};

// 是否有选中的订单需要更新
const hasSelectedOrders = computed(() => {
  return Object.keys(selectedOrderStages.value).length > 0;
});

const loadData = async () => {
  if (!date.value || !mealType.value) {
    ElMessage.warning('请选择日期和餐别');
    return;
  }

  loading.value = true;
  try {
    // 加载物流数据（后端暂不支持公司筛选，前端过滤）
    const logisticsData = await fetchLogistics({
      order_date: date.value,
      meal_type: mealType.value,
    });
    logisticsList.value = logisticsData;

    // 加载统计数据（仅staff角色显示图表）
    if (isStaff.value) {
      try {
        const stats = await getLogisticsStatistics({
          order_date: date.value,
          meal_type: mealType.value,
        });
        statistics.value = stats;
      } catch (error) {
        console.error('加载统计数据失败:', error);
      }
    }
    
    // 清除已选中的订单状态（因为数据已更新）
    selectedOrderStages.value = {};
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '加载物流数据失败');
  } finally {
    loading.value = false;
  }
};

const handleFilterChange = () => {
  // 筛选条件变化时重置数据（公司关键词筛选不影响数据加载，只影响显示）
  if (companyKeyword.value) {
    // 如果只是公司关键词变化，不需要重新加载数据
    return;
  }
  // 日期或餐别变化时重置
  logisticsList.value = [];
  statistics.value = null;
  selectedCompanies.value = [];
  selectedOrderStages.value = {};
};

// 处理订单状态变化（从LogisticsSteps组件触发）
const handleOrderStageChange = (orderId: number, selectedStage: string | null) => {
  if (selectedStage) {
    selectedOrderStages.value[orderId] = selectedStage;
  } else {
    delete selectedOrderStages.value[orderId];
  }
};

const handleBatchConfirm = async () => {
  if (Object.keys(selectedOrderStages.value).length === 0) {
    ElMessage.warning('请至少选择一个订单的状态进行更新');
    return;
  }

  // 构建更新列表
  const updates: Array<{ order_id: number; stage: string }> = [];
  const errors: string[] = [];

  for (const [orderIdStr, stage] of Object.entries(selectedOrderStages.value)) {
    const orderId = parseInt(orderIdStr, 10);
    const logistics: LogisticsData | undefined = logisticsList.value.find((l: LogisticsData) => l.order_id === orderId);
    
    if (!logistics) {
      errors.push(`订单 ${orderId} 不存在`);
      continue;
    }

    // 验证选中的状态是否可以更新
    const stageKey = `stage_${stage}` as keyof LogisticsData;
    if (logistics[stageKey]) {
      errors.push(`订单 ${orderId}：${stage} 状态已完成，无法再次更新`);
      continue;
    }

    // 检查前置阶段是否完成
    let canUpdate = false;
    if (stage === 'prepare_loaded') {
      canUpdate = true;
    } else if (stage === 'shipping') {
      canUpdate = logistics.stage_prepare_loaded || false;
      if (!canUpdate) {
        errors.push(`订单 ${orderId}：备餐装车未完成，无法更新到运输中`);
      }
    } else if (stage === 'arrived') {
      canUpdate = logistics.stage_shipping || false;
      if (!canUpdate) {
        errors.push(`订单 ${orderId}：运输中未完成，无法更新到已到达`);
      }
    } else if (stage === 'recycled') {
      canUpdate = logistics.stage_arrived || false;
      if (!canUpdate) {
        errors.push(`订单 ${orderId}：已到达未完成，无法更新到已回收`);
      }
    }

    if (canUpdate) {
      updates.push({ order_id: orderId, stage });
    }
  }

  if (updates.length === 0) {
    if (errors.length > 0) {
      ElMessage.warning(errors.slice(0, 5).join('; ') + (errors.length > 5 ? '...' : ''));
    } else {
      ElMessage.warning('没有可更新的订单');
    }
    return;
  }

  batchUpdating.value = true;
  try {
    const result = await batchUpdateLogisticsStages(updates);
    ElMessage.success(result.msg || `成功更新 ${result.success_count || updates.length} 个订单`);
    
    // 显示错误信息
    const allErrors = [...errors, ...(result.errors || [])];
    if (allErrors.length > 0) {
      ElMessage.warning(`部分更新失败: ${allErrors.slice(0, 5).join('; ')}${allErrors.length > 5 ? '...' : ''}`);
    }
    
    // 重置选中状态
    selectedOrderStages.value = {};
    // 重新加载数据
    await loadData();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '批量更新失败');
  } finally {
    batchUpdating.value = false;
  }
};

// 初始化默认日期（明天）
onMounted(() => {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  date.value = tomorrow.toISOString().split('T')[0];
});
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.chart-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #fafafa;
  border-radius: 4px;
}

.companies-section {
  margin-top: 20px;
}

.companies-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.companies-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.companies-board {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.company-card {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 16px;
  background: #fff;
}

.company-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.logistics-item {
  margin-top: 16px;
}

.batch-actions {
  margin-top: 24px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  position: sticky;
  bottom: 0;
  z-index: 10;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
}

.batch-info {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.customer-section {
  margin-top: 20px;
}

.customer-section h3 {
  margin-bottom: 20px;
  font-size: 16px;
  font-weight: 600;
}

.customer-logistics {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.customer-logistics .logistics-item {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 20px;
  background: #fff;
}

.company-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #27ae60;
}

.empty-tip {
  padding: 60px 0;
}
</style>
