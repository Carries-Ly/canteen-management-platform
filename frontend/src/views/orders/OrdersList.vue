<template>
  <el-card>
    <!-- user/admin/superadmin 视图 -->
    <template v-if="isStaff">
      <div class="toolbar">
        <el-date-picker
          v-model="orderDate"
          type="date"
          placeholder="选择日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          clearable
          @change="loadData"
          style="width: 200px"
        />
        <el-input
          v-model="companyKeyword"
          placeholder="搜索公司名称"
          clearable
          style="width: 200px"
          @clear="loadData"
          @keyup.enter="loadData"
        />
        <el-button type="primary" @click="loadData" :loading="loading">查询</el-button>
        <div style="margin-left: auto">
          <el-button
            v-if="selectedOrders.length > 0"
            type="success"
            @click="handleBatchConfirm"
            :loading="confirming"
          >
            批量确认接收 ({{ selectedOrders.length }})
          </el-button>
        </div>
      </div>

      <el-table
        :data="displayRows"
        stripe
        v-loading="loading"
        border
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" :selectable="isSelectable" />
        <el-table-column prop="company_name" label="客户公司" width="150" :rowspan="getRowspan" />
        <el-table-column prop="order_date" label="订单日期" width="120" :rowspan="getRowspan" />
        <el-table-column prop="meal_type" label="订单餐别" width="100" />
        <el-table-column label="餐标明细" min-width="300">
          <template #default="{ row }">
            <div v-for="(item: any, idx: number) in row.items" :key="idx" class="meal-item">
              <span>{{ item.meal_name }}</span>
              <span style="margin-left: 16px; color: #666">数量：{{ item.quantity }}</span>
              <span style="margin-left: 16px; color: #666">单价：¥{{ item.unit_price.toFixed(2) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="total_quantity" label="总份数" width="100" align="right" />
        <el-table-column prop="total_amount" label="总金额" width="120" align="right">
          <template #default="{ row }">
            ¥{{ row.total_amount?.toFixed(2) || '0.00' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="150">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="current_stage" label="物流阶段" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.current_stage" size="small" type="info">
              {{ getStageName(row.current_stage) }}
            </el-tag>
            <span v-else>待处理</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row.order_id)">查看详情</el-button>
            <el-button
              v-if="canEdit"
              size="small"
              type="warning"
              @click="openEdit(row.order_id)"
            >
              编辑
            </el-button>
            <el-button
              v-if="canEdit"
              size="small"
              type="danger"
              @click="handleDelete(row.order_id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </template>

    <!-- customer 视图 -->
    <template v-else>
      <div class="toolbar">
        <el-date-picker
          v-model="orderDate"
          type="date"
          placeholder="选择日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          clearable
          @change="loadData"
          style="width: 200px"
        />
        <el-select
          v-model="statusFilter"
          placeholder="选择状态"
          clearable
          @change="loadData"
          style="width: 200px"
        >
          <el-option label="已提交，等待确认" value="已提交，等待确认" />
          <el-option label="订餐已收到" value="订餐已收到" />
        </el-select>
        <el-button type="primary" @click="openCreateDialog">创建订单</el-button>
      </div>

      <!-- 创建订单对话框 -->
      <el-dialog
        v-model="dialogVisible"
        :title="currentOrder?.id ? '编辑订单' : '创建订单'"
        width="700px"
      >
        <el-form :model="form" label-width="100px">
          <el-form-item label="订餐日期" required>
            <el-date-picker
              v-model="form.order_date"
              type="date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="订单明细" required>
            <div v-for="(item, index) in form.items" :key="index" class="order-item">
              <el-select
                v-model="item.meal_type"
                placeholder="选择餐别"
                style="width: 120px"
                @change="onMealTypeChange(index)"
              >
                <el-option label="早餐" value="早餐" />
                <el-option label="午餐" value="午餐" />
                <el-option label="晚餐" value="晚餐" />
                <el-option label="夜宵" value="夜宵" />
              </el-select>
              <el-select
                v-model="item.meal_standard_id"
                placeholder="选择餐标"
                style="width: 200px; margin-left: 10px"
                @change="onMealStandardChange(index)"
              >
                <el-option
                  v-for="meal in getAvailableMealsForType(item.meal_type)"
                  :key="meal.id"
                  :label="`${meal.name} (¥${meal.price})`"
                  :value="meal.id"
                />
              </el-select>
              <el-input-number
                v-model="item.quantity"
                :min="1"
                placeholder="数量"
                style="width: 120px; margin-left: 10px"
              />
              <span style="margin-left: 10px; color: #666">
                单价：¥{{ item.unit_price?.toFixed(2) || '0.00' }}
              </span>
              <span style="margin-left: 10px; color: #666">
                小计：¥{{ ((item.unit_price || 0) * (item.quantity || 0)).toFixed(2) }}
              </span>
              <el-button
                type="danger"
                size="small"
                @click="removeItem(index)"
                style="margin-left: 10px"
                v-if="form.items.length > 1"
              >
                删除
              </el-button>
            </div>
            <el-button type="primary" size="small" @click="addItem" style="margin-top: 10px">
              添加明细
            </el-button>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="save" :loading="saving">保存</el-button>
        </template>
      </el-dialog>

      <!-- 订单子board -->
      <div v-if="orderDate && customerOrders.length > 0" class="customer-board">
        <h3>{{ orderDate }} 订单列表</h3>
        <el-table :data="customerOrders" stripe border>
          <el-table-column prop="order_date" label="订单日期" width="120" />
          <el-table-column label="明细" min-width="400">
            <template #default="{ row }">
              <div v-for="(item, idx) in row.items" :key="idx" class="order-item-row">
                <el-tag size="small">{{ item.meal_type }}</el-tag>
                <span style="margin-left: 8px">{{ item.meal_name }}</span>
                <span style="margin-left: 16px">数量：{{ item.quantity }}</span>
                <span style="margin-left: 16px">单价：¥{{ item.unit_price.toFixed(2) }}</span>
                <span style="margin-left: 16px">小计：¥{{ (item.unit_price * item.quantity).toFixed(2) }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="total_quantity" label="总份数" width="100" align="right" />
          <el-table-column prop="total_amount" label="总金额" width="120" align="right">
            <template #default="{ row }">
              ¥{{ row.total_amount?.toFixed(2) || '0.00' }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="150">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button size="small" @click="viewDetail(row.id)">查看详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-empty v-else-if="orderDate && customerOrders.length === 0" description="暂无订单" />
    </template>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useAuthStore } from '@/store/auth';
import {
  fetchOrders,
  createOrder,
  updateOrder,
  deleteOrder,
  confirmOrder,
  batchConfirmOrders,
  type Order,
} from '@/api/orders';
import { fetchMealStandards } from '@/api/mealStandards';

const router = useRouter();
const auth = useAuthStore();
const role = computed(() => auth.user?.role || '');
const isStaff = computed(() => ['user', 'admin', 'superadmin'].includes(role.value));
const canEdit = computed(() => ['admin', 'superadmin'].includes(role.value));

const loading = ref(false);
const saving = ref(false);
const confirming = ref(false);
const orderDate = ref<string | null>(null);
const companyKeyword = ref('');
const statusFilter = ref<string>('');
const list = ref<Order[]>([]);
const availableMeals = ref<any[]>([]);
const dialogVisible = ref(false);
const currentOrder = ref<Order | null>(null);
const selectedOrders = ref<number[]>([]);
const form = ref({
  order_date: '',
  items: [{ meal_type: '午餐', meal_standard_id: null, quantity: 1, unit_price: 0 }],
});

// 用于表格行合并的数据（现在每个订单只有一个餐别）
const displayRows = computed(() => {
  if (!isStaff.value) return [];
  
  const rows: any[] = [];
  // 按公司和日期分组
  const groups: Record<string, Order[]> = {};
  
  for (const order of list.value) {
    const key = `${order.company_id}_${order.order_date}`;
    if (!groups[key]) {
      groups[key] = [];
    }
    groups[key].push(order);
  }
  
  // 展开为表格行（现在每个订单就是一行）
  for (const key in groups) {
    const orders = groups[key];
    for (let i = 0; i < orders.length; i++) {
      const order = orders[i];
      rows.push({
        company_id: order.company_id,
        company_name: order.company_name,
        order_date: order.order_date,
        order_id: order.id,
        meal_type: order.meal_type || (order.items && order.items[0]?.meal_type) || '',
        items: order.items || [],
        total_quantity: order.total_quantity || 0,
        total_amount: order.total_amount || 0,
        status: order.status,
        current_stage: order.current_stage,
        rowspan: orders.length, // 记录需要合并的行数
        itemIndex: i, // 当前项索引
      });
    }
  }
  
  return rows;
});

// 计算行合并
const getRowspan = ({ row, column }: any) => {
  if (column.property === 'company_name' || column.property === 'order_date') {
    return row.itemIndex === 0 ? row.rowspan : 0;
  }
  return 1;
};

// 判断行是否可选（只能选择"已提交，等待确认"状态的订单）
const isSelectable = (row: any) => {
  return row.status === '已提交，等待确认';
};

// 处理选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedOrders.value = selection.map((row) => row.order_id);
};

// customer订单
const customerOrders = computed(() => {
  return list.value;
});

const getStatusType = (status: string) => {
  if (status === '已提交，等待确认') return 'warning';
  if (status === '订餐已收到') return 'success';
  return 'info';
};

const getStageName = (stage: string) => {
  const map: Record<string, string> = {
    prepare_loaded: '备餐装车',
    shipping: '运输中',
    arrived: '已到达',
    recycled: '已回收',
  };
  return map[stage] || stage;
};

const loadData = async () => {
  loading.value = true;
  try {
    const params: any = {};
    if (orderDate.value) params.order_date = orderDate.value;
    if (companyKeyword.value) params.company_keyword = companyKeyword.value;
    if (statusFilter.value) params.status = statusFilter.value;

    const res = await fetchOrders(params);
    list.value = res;
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '加载订单列表失败');
  } finally {
    loading.value = false;
  }
};

const loadMeals = async () => {
  try {
    const meals = await fetchMealStandards({ status: 'enabled' });
    availableMeals.value = meals;
  } catch (error) {
    console.error('加载餐标失败', error);
  }
};

const getAvailableMealsForType = (mealType: string) => {
  return availableMeals.value.filter((m) => m.meal_type === mealType);
};

const openCreateDialog = () => {
  currentOrder.value = null;
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  form.value = {
    order_date: tomorrow.toISOString().split('T')[0],
    items: [{ meal_type: '午餐', meal_standard_id: null, quantity: 1, unit_price: 0 }],
  };
  dialogVisible.value = true;
};

const openEdit = async (orderId: number) => {
  if (!canEdit.value) return;
  try {
    const order = await fetchOrders({ order_date: orderDate.value || '' });
    const targetOrder = order.find((o) => o.id === orderId);
    if (!targetOrder) {
      ElMessage.error('订单不存在');
      return;
    }
    currentOrder.value = targetOrder;
    form.value = {
      order_date: targetOrder.order_date,
      items: targetOrder.items.map((item) => ({
        meal_type: item.meal_type,
        meal_standard_id: null, // 需要根据meal_name找到对应的meal_standard_id
        quantity: item.quantity,
        unit_price: item.unit_price,
      })),
    };
    dialogVisible.value = true;
  } catch (error: any) {
    ElMessage.error('加载订单详情失败');
  }
};

const addItem = () => {
  form.value.items.push({ meal_type: '午餐', meal_standard_id: null, quantity: 1, unit_price: 0 });
};

const removeItem = (index: number) => {
  form.value.items.splice(index, 1);
};

const onMealTypeChange = (index: number) => {
  // 切换餐别时清空餐标选择
  form.value.items[index].meal_standard_id = null;
  form.value.items[index].unit_price = 0;
};

const onMealStandardChange = (index: number) => {
  const mealId = form.value.items[index].meal_standard_id;
  const meal = availableMeals.value.find((m) => m.id === mealId);
  if (meal) {
    form.value.items[index].unit_price = meal.price;
  }
};

const save = async () => {
  if (!form.value.order_date || form.value.items.length === 0) {
    ElMessage.warning('请填写完整信息');
    return;
  }
  
  // 验证所有明细都已填写
  for (const item of form.value.items) {
    if (!item.meal_type || !item.meal_standard_id || !item.quantity) {
      ElMessage.warning('请填写完整的订单明细');
      return;
    }
  }

  saving.value = true;
  try {
    const payload = {
      order_date: form.value.order_date,
      items: form.value.items.map((item) => ({
        meal_standard_id: item.meal_standard_id!,
        meal_type: item.meal_type,
        quantity: item.quantity,
        unit_price: item.unit_price,
      })),
    };

    if (currentOrder.value?.id) {
      await updateOrder(currentOrder.value.id, payload);
      ElMessage.success('更新成功');
    } else {
      const result = await createOrder(payload);
      ElMessage.success(`成功创建 ${result.count || 1} 个订单`);
    }
    dialogVisible.value = false;
    await loadData();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '操作失败');
  } finally {
    saving.value = false;
  }
};

const handleBatchConfirm = async () => {
  if (selectedOrders.value.length === 0) {
    ElMessage.warning('请至少选择一个订单');
    return;
  }

  try {
    await ElMessageBox.confirm(
      `确定要确认接收选中的 ${selectedOrders.value.length} 个订单吗？`,
      '批量确认提示',
      {
        type: 'warning',
      }
    );
    confirming.value = true;
    const result = await batchConfirmOrders(selectedOrders.value);
    ElMessage.success(result.msg || '批量确认成功');
    if (result.errors && result.errors.length > 0) {
      ElMessage.warning(`部分订单确认失败: ${result.errors.join('; ')}`);
    }
    selectedOrders.value = [];
    await loadData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.msg || '批量确认失败');
    }
  } finally {
    confirming.value = false;
  }
};

const handleDelete = async (orderId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除该订单吗？删除后无法恢复。', '删除确认', {
      type: 'warning',
    });
    await deleteOrder(orderId);
    ElMessage.success('删除成功');
    await loadData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.msg || '删除失败');
    }
  }
};

const viewDetail = (id: number) => {
  router.push(`/orders/${id}`);
};

// 初始化默认日期（明天）
onMounted(() => {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  orderDate.value = tomorrow.toISOString().split('T')[0];
  loadData();
  loadMeals();
});
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.order-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 10px;
}

.customer-board {
  margin-top: 20px;
}

.customer-board h3 {
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
}

.order-item-row {
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.order-item-row:last-child {
  border-bottom: none;
}

.meal-item {
  padding: 4px 0;
}
</style>
