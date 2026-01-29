<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>库存管理</span>
        <div>
          <el-button type="primary" @click="handleStockIn">入库</el-button>
          <el-button type="warning" @click="handleStockOut">出库</el-button>
        </div>
      </div>
    </template>

    <div class="filter-section">
      <el-input
        v-model="keyword"
        placeholder="搜索食材名称"
        clearable
        style="width: 200px; margin-right: 10px"
        @clear="handleSearch"
        @keyup.enter="handleSearch"
      />
      <el-select
        v-model="category"
        placeholder="选择分类"
        clearable
        style="width: 150px; margin-right: 10px"
        @change="handleSearch"
      >
        <el-option label="蔬菜" value="蔬菜" />
        <el-option label="肉类" value="肉类" />
        <el-option label="调料" value="调料" />
        <el-option label="主食" value="主食" />
      </el-select>
      <el-button type="primary" @click="handleSearch">查询</el-button>
    </div>

    <el-table
      :data="inventoryList"
      stripe
      v-loading="loading"
      style="margin-top: 20px"
    >
      <el-table-column prop="ingredient_name" label="食材名称" width="200" />
      <el-table-column prop="category" label="分类" width="100" />
      <el-table-column prop="unit" label="单位" width="80" />
      <el-table-column prop="current_quantity" label="当前库存" width="120">
        <template #default="{ row }">
          <span :style="{ color: row.current_quantity < row.safety_stock ? 'red' : 'inherit' }">
            {{ row.current_quantity }} {{ row.unit }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="safety_stock" label="安全库存" width="120" />
      <el-table-column prop="last_in_date" label="最后入库日期" width="150" />
      <el-table-column prop="last_out_date" label="最后出库日期" width="150" />
    </el-table>

    <!-- 入库对话框 -->
    <el-dialog v-model="stockInDialogVisible" title="食材入库" width="500px">
      <el-form :model="stockInForm" label-width="120px">
        <el-form-item label="食材名称" required>
          <el-select
            v-model="stockInForm.ingredient_id"
            placeholder="选择食材"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="ingredient in allIngredients"
              :key="ingredient.ingredient_id"
              :label="`${ingredient.ingredient_name} (${ingredient.unit})`"
              :value="ingredient.ingredient_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="入库数量" required>
          <el-input-number
            v-model="stockInForm.quantity"
            :min="0"
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="入库日期">
          <el-date-picker
            v-model="stockInForm.in_date"
            type="date"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="保质期到期">
          <el-date-picker
            v-model="stockInForm.expiry_date"
            type="date"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="电子秤重量">
          <el-input-number
            v-model="stockInForm.scale_weight"
            :min="0"
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stockInDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmStockIn" :loading="saving">确认入库</el-button>
      </template>
    </el-dialog>

    <!-- 出库对话框 -->
    <el-dialog v-model="stockOutDialogVisible" title="食材出库" width="500px">
      <el-form :model="stockOutForm" label-width="120px">
        <el-form-item label="食材名称" required>
          <el-select
            v-model="stockOutForm.ingredient_id"
            placeholder="选择食材"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="ingredient in inventoryList"
              :key="ingredient.ingredient_id"
              :label="`${ingredient.ingredient_name} (当前库存: ${ingredient.current_quantity} ${ingredient.unit})`"
              :value="ingredient.ingredient_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="出库数量" required>
          <el-input-number
            v-model="stockOutForm.quantity"
            :min="0"
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="出库日期">
          <el-date-picker
            v-model="stockOutForm.out_date"
            type="date"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="出库用途">
          <el-input v-model="stockOutForm.purpose" placeholder="如：生产使用/损耗/退货等" />
        </el-form-item>
        <el-form-item label="电子秤重量">
          <el-input-number
            v-model="stockOutForm.scale_weight"
            :min="0"
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stockOutDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmStockOut" :loading="saving">确认出库</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { fetchInventory, stockIn, stockOut, type InventoryItem } from '@/api/inventory';

const loading = ref(false);
const saving = ref(false);
const keyword = ref('');
const category = ref('');
const inventoryList = ref<InventoryItem[]>([]);
const allIngredients = ref<InventoryItem[]>([]);
const stockInDialogVisible = ref(false);
const stockOutDialogVisible = ref(false);

const stockInForm = ref({
  ingredient_id: null as number | null,
  quantity: 0,
  in_date: new Date().toISOString().split('T')[0],
  expiry_date: '',
  scale_weight: null as number | null,
});

const stockOutForm = ref({
  ingredient_id: null as number | null,
  quantity: 0,
  out_date: new Date().toISOString().split('T')[0],
  purpose: '',
  scale_weight: null as number | null,
});

const handleSearch = async () => {
  loading.value = true;
  try {
    const params: any = {};
    if (keyword.value) params.keyword = keyword.value;
    if (category.value) params.category = category.value;
    inventoryList.value = await fetchInventory(params);
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '查询失败');
  } finally {
    loading.value = false;
  }
};

const handleStockIn = async () => {
  // 加载所有食材供选择
  try {
    allIngredients.value = await fetchInventory();
    stockInForm.value = {
      ingredient_id: null,
      quantity: 0,
      in_date: new Date().toISOString().split('T')[0],
      expiry_date: '',
      scale_weight: null,
    };
    stockInDialogVisible.value = true;
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '加载食材列表失败');
  }
};

const handleConfirmStockIn = async () => {
  if (!stockInForm.value.ingredient_id || !stockInForm.value.quantity) {
    ElMessage.warning('请填写完整信息');
    return;
  }

  saving.value = true;
  try {
    await stockIn({
      ingredient_id: stockInForm.value.ingredient_id,
      quantity: stockInForm.value.quantity,
      in_date: stockInForm.value.in_date,
      expiry_date: stockInForm.value.expiry_date || undefined,
      scale_weight: stockInForm.value.scale_weight || undefined,
    });
    ElMessage.success('入库成功');
    stockInDialogVisible.value = false;
    await handleSearch();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '入库失败');
  } finally {
    saving.value = false;
  }
};

const handleStockOut = () => {
  stockOutForm.value = {
    ingredient_id: null,
    quantity: 0,
    out_date: new Date().toISOString().split('T')[0],
    purpose: '',
    scale_weight: null,
  };
  stockOutDialogVisible.value = true;
};

const handleConfirmStockOut = async () => {
  if (!stockOutForm.value.ingredient_id || !stockOutForm.value.quantity) {
    ElMessage.warning('请填写完整信息');
    return;
  }

  saving.value = true;
  try {
    await stockOut({
      ingredient_id: stockOutForm.value.ingredient_id,
      quantity: stockOutForm.value.quantity,
      out_date: stockOutForm.value.out_date,
      purpose: stockOutForm.value.purpose || undefined,
      scale_weight: stockOutForm.value.scale_weight || undefined,
    });
    ElMessage.success('出库成功');
    stockOutDialogVisible.value = false;
    await handleSearch();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '出库失败');
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  handleSearch();
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
</style>

