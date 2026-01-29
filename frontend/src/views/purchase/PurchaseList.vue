<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>采购清单</span>
        <el-button type="primary" @click="handleCreatePurchaseOrder">生成采购单</el-button>
      </div>
    </template>

    <div class="filter-section">
      <el-select
        v-model="selectedSubMenuId"
        placeholder="选择子菜单"
        clearable
        style="width: 300px; margin-right: 10px"
        @change="handleLoadSubMenu"
      >
        <el-option
          v-for="subMenu in subMenus"
          :key="subMenu.id"
          :label="`${subMenu.company_name} - 第${subMenu.week_number}周`"
          :value="subMenu.id"
        />
      </el-select>
      <el-button type="primary" @click="handleGeneratePurchaseList" :disabled="!selectedSubMenuId">
        生成采购清单
      </el-button>
    </div>

    <el-table
      :data="purchaseList"
      stripe
      v-loading="loading"
      style="margin-top: 20px"
    >
      <el-table-column prop="ingredient_name" label="食材名称" width="200" />
      <el-table-column prop="unit" label="单位" width="80" />
      <el-table-column prop="required_quantity" label="所需数量" width="120" />
      <el-table-column prop="stock_quantity" label="当前库存" width="120" />
      <el-table-column prop="use_stock" label="使用库存" width="100">
        <template #default="{ row }">
          <el-checkbox v-model="row.use_stock" @change="handleUpdatePurchaseQuantity(row)" />
        </template>
      </el-table-column>
      <el-table-column prop="purchase_quantity" label="采购数量" width="120">
        <template #default="{ row }">
          <el-input-number
            v-model="row.purchase_quantity"
            :min="0"
            :precision="2"
            style="width: 100%"
            @change="handleUpdateSubtotal(row)"
          />
        </template>
      </el-table-column>
      <el-table-column prop="unit_price" label="单价" width="100">
        <template #default="{ row }">
          <el-input-number
            v-model="row.unit_price"
            :min="0"
            :precision="2"
            style="width: 100%"
            @change="handleUpdateSubtotal(row)"
          />
        </template>
      </el-table-column>
      <el-table-column prop="subtotal" label="小计" width="120">
        <template #default="{ row }">
          ¥{{ row.subtotal.toFixed(2) }}
        </template>
      </el-table-column>
    </el-table>

    <div class="total-section" v-if="purchaseList.length > 0">
      <div class="total-amount">
        预估总金额：<span class="amount">¥{{ totalAmount.toFixed(2) }}</span>
      </div>
      <el-button type="primary" @click="handleCreatePurchaseOrder" :loading="saving">
        生成采购单
      </el-button>
    </div>

    <!-- 采购单列表 -->
    <el-divider>采购单列表</el-divider>
    <el-table
      :data="purchaseOrders"
      stripe
      v-loading="loadingOrders"
      style="margin-top: 20px"
    >
      <el-table-column prop="order_number" label="采购单号" width="200" />
      <el-table-column prop="total_amount" label="总金额" width="120">
        <template #default="{ row }">
          ¥{{ row.total_amount.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleViewOrder(row.id)">查看详情</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { getSubMenuHistory, type SubMenu } from '@/api/subMenu';
import { fetchInventory, type InventoryItem } from '@/api/inventory';
import { fetchPurchaseOrders, createPurchaseOrder, type PurchaseOrder } from '@/api/purchaseOrder';

const loading = ref(false);
const loadingOrders = ref(false);
const saving = ref(false);
const selectedSubMenuId = ref<number | null>(null);
const subMenus = ref<SubMenu[]>([]);
const purchaseList = ref<Array<{
  ingredient_id: number;
  ingredient_name: string;
  unit: string;
  required_quantity: number;
  stock_quantity: number;
  use_stock: boolean;
  purchase_quantity: number;
  unit_price: number;
  subtotal: number;
}>>([]);
const purchaseOrders = ref<PurchaseOrder[]>([]);

const totalAmount = computed(() => {
  return purchaseList.value.reduce((sum, item) => sum + item.subtotal, 0);
});

const handleLoadSubMenu = async () => {
  if (!selectedSubMenuId.value) return;
  // 这里可以加载子菜单详情，用于计算所需食材
};

const handleGeneratePurchaseList = async () => {
  if (!selectedSubMenuId.value) {
    ElMessage.warning('请选择子菜单');
    return;
  }

  loading.value = true;
  try {
    // 这里应该根据子菜单计算所需食材
    // 由于菜单库xlsx解析功能较复杂，这里先提供一个基础框架
    // 实际应该调用后端API解析菜单库并计算食材需求
    
    // 示例：加载库存信息
    const inventory = await fetchInventory();
    
    // 这里应该根据子菜单计算所需食材，暂时使用示例数据
    purchaseList.value = inventory.slice(0, 5).map(item => ({
      ingredient_id: item.ingredient_id,
      ingredient_name: item.ingredient_name,
      unit: item.unit,
      required_quantity: 10, // 应该根据菜单计算
      stock_quantity: item.current_quantity,
      use_stock: false,
      purchase_quantity: 10,
      unit_price: 10, // 应该从食材库获取
      subtotal: 100,
    }));
    
    ElMessage.success('采购清单生成成功（示例数据）');
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '生成采购清单失败');
  } finally {
    loading.value = false;
  }
};

const handleUpdatePurchaseQuantity = (row: any) => {
  if (row.use_stock) {
    row.purchase_quantity = Math.max(0, row.required_quantity - row.stock_quantity);
  } else {
    row.purchase_quantity = row.required_quantity;
  }
  handleUpdateSubtotal(row);
};

const handleUpdateSubtotal = (row: any) => {
  row.subtotal = row.purchase_quantity * row.unit_price;
};

const handleCreatePurchaseOrder = async () => {
  if (purchaseList.value.length === 0) {
    ElMessage.warning('请先生成采购清单');
    return;
  }

  saving.value = true;
  try {
    const result = await createPurchaseOrder({
      sub_menu_id: selectedSubMenuId.value || undefined,
      items: purchaseList.value.map(item => ({
        ingredient_id: item.ingredient_id,
        required_quantity: item.required_quantity,
        use_stock: item.use_stock,
        purchase_quantity: item.purchase_quantity,
        unit_price: item.unit_price,
      })),
    });
    ElMessage.success('采购单创建成功');
    await loadPurchaseOrders();
    // 清空采购清单
    purchaseList.value = [];
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '创建采购单失败');
  } finally {
    saving.value = false;
  }
};

const loadPurchaseOrders = async () => {
  loadingOrders.value = true;
  try {
    purchaseOrders.value = await fetchPurchaseOrders();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '加载采购单列表失败');
  } finally {
    loadingOrders.value = false;
  }
};

const handleViewOrder = (id: number) => {
  ElMessage.info('查看采购单详情功能待实现');
};

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    draft: 'info',
    confirmed: 'success',
    purchased: 'success',
  };
  return types[status] || 'info';
};

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    draft: '草稿',
    confirmed: '已确认',
    purchased: '已采购',
  };
  return texts[status] || status;
};

onMounted(async () => {
  try {
    subMenus.value = await getSubMenuHistory();
    await loadPurchaseOrders();
  } catch (error) {
    console.error('初始化失败:', error);
  }
});
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-section {
  margin-bottom: 20px;
}

.total-section {
  margin-top: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-amount {
  font-size: 16px;
  font-weight: bold;
}

.amount {
  color: #f56c6c;
  font-size: 20px;
}
</style>

