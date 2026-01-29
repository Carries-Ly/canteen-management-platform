<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>子菜单管理</span>
        <el-button type="primary" @click="handleSelectSubMenu" v-if="canEdit">选择子菜单</el-button>
      </div>
    </template>

    <div class="filter-section">
      <el-select v-model="selectedWeekYear" placeholder="选择年份" style="width: 120px; margin-right: 10px">
        <el-option
          v-for="year in years"
          :key="year"
          :label="year"
          :value="year"
        />
      </el-select>
      <el-select
        v-model="selectedCompanyId"
        placeholder="选择客户企业"
        clearable
        style="width: 200px; margin-right: 10px"
        v-if="isStaff"
      >
        <el-option
          v-for="company in companies"
          :key="company.id"
          :label="company.name"
          :value="company.id"
        />
      </el-select>
      <el-button type="primary" @click="handleLoadHistory">查询历史</el-button>
    </div>

    <el-table
      :data="subMenus"
      stripe
      v-loading="loading"
      style="margin-top: 20px"
    >
      <el-table-column prop="week_year" label="年份" width="100" />
      <el-table-column prop="week_number" label="周数" width="100" />
      <el-table-column prop="company_name" label="客户企业" width="200" />
      <el-table-column prop="name" label="子菜单名称" min-width="200" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'confirmed' ? 'success' : 'info'">
            {{ row.status === 'confirmed' ? '已确认' : '草稿' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleViewDetail(row.id)">查看详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 选择子菜单对话框 -->
    <el-dialog
      v-model="selectDialogVisible"
      title="选择子菜单"
      width="80%"
      v-if="canEdit"
    >
      <div v-if="selectedWeeklyMenu">
        <div class="dialog-header">
          <span>总菜单：第{{ selectedWeeklyMenu.week_number }}周</span>
          <el-checkbox v-model="selectAllDays" @change="handleSelectAllDays">全选</el-checkbox>
        </div>
        <el-table
          :data="weeklyMenuItems"
          border
          stripe
          style="margin-top: 10px"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="day_of_week" label="星期" width="80">
            <template #default="{ row }">
              {{ getDayName(row.day_of_week) }}
            </template>
          </el-table-column>
          <el-table-column prop="meal_type" label="餐别" width="80" />
          <el-table-column prop="dish_category" label="分类" width="100" />
          <el-table-column prop="dish_name" label="菜品名称" />
        </el-table>
        <div style="margin-top: 20px">
          <el-select
            v-model="selectedCompanyIds"
            multiple
            placeholder="选择适用的客户企业"
            style="width: 100%"
          >
            <el-option
              v-for="company in companies"
              :key="company.id"
              :label="company.name"
              :value="company.id"
            />
          </el-select>
        </div>
      </div>
      <template #footer>
        <el-button @click="selectDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmSelect" :loading="saving">确认</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="子菜单详情"
      width="70%"
    >
      <div v-if="currentSubMenu">
        <div class="detail-info">
          <span>客户企业：{{ currentSubMenu.company_name }}</span>
          <span>周次：第{{ currentSubMenu.week_number }}周</span>
        </div>
        <el-table
          :data="currentSubMenu.items"
          border
          stripe
          style="margin-top: 20px"
        >
          <el-table-column prop="day_of_week" label="星期" width="100">
            <template #default="{ row }">
              {{ getDayName(row.day_of_week) }}
            </template>
          </el-table-column>
          <el-table-column prop="meal_type" label="餐别" width="100" />
          <el-table-column prop="dish_category" label="分类" width="120" />
          <el-table-column prop="dish_name" label="菜品名称" />
        </el-table>
      </div>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { useAuthStore } from '@/store/auth';
import { fetchSubMenus, getSubMenu, selectSubMenu, getSubMenuHistory, type SubMenu } from '@/api/subMenu';
import { fetchWeeklyMenus, getWeeklyMenu, type WeeklyMenu, type WeeklyMenuItem } from '@/api/weeklyMenu';
import { fetchCompanies, type Company } from '@/api/companies';

interface SubMenuWithWeek extends SubMenu {
  week_year?: number;
  week_number?: number;
}

const auth = useAuthStore();
const role = computed(() => auth.user?.role || '');
const isStaff = computed(() => ['user', 'admin', 'superadmin'].includes(role.value));
const canEdit = computed(() => ['admin', 'superadmin'].includes(role.value));

const loading = ref(false);
const saving = ref(false);
const selectedWeekYear = ref(new Date().getFullYear());
const selectedCompanyId = ref<number | null>(null);
const subMenus = ref<SubMenuWithWeek[]>([]);
const companies = ref<Company[]>([]);
const selectDialogVisible = ref(false);
const detailDialogVisible = ref(false);
const selectedWeeklyMenu = ref<WeeklyMenu | null>(null);
const weeklyMenuItems = ref<WeeklyMenuItem[]>([]);
const selectedItems = ref<WeeklyMenuItem[]>([]);
const selectedCompanyIds = ref<number[]>([]);
const selectAllDays = ref(false);
const currentSubMenu = ref<SubMenu | null>(null);

const years = computed(() => {
  const currentYear = new Date().getFullYear();
  return Array.from({ length: 3 }, (_, i) => currentYear - 1 + i);
});

const getDayName = (day: number) => {
  const days = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日'];
  return days[day] || '';
};

const handleLoadHistory = async () => {
  loading.value = true;
  try {
    const params: any = {};
    if (selectedWeekYear.value) {
      params.week_year = selectedWeekYear.value;
    }
    if (selectedCompanyId.value && isStaff.value) {
      params.company_id = selectedCompanyId.value;
    }
    const data = await getSubMenuHistory(params);
    subMenus.value = data;
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '加载历史失败');
  } finally {
    loading.value = false;
  }
};

const handleSelectSubMenu = async () => {
  // 先加载总菜单列表供选择
  try {
    const menus = await fetchWeeklyMenus({ week_year: selectedWeekYear.value });
    if (menus.length === 0) {
      ElMessage.warning('请先生成总菜单');
      return;
    }
    // 选择最新的总菜单
    const menu = await getWeeklyMenu(menus[0].id);
    selectedWeeklyMenu.value = menu;
    weeklyMenuItems.value = menu.items || [];
    selectedItems.value = [];
    selectedCompanyIds.value = [];
    selectDialogVisible.value = true;
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '加载总菜单失败');
  }
};

const handleSelectAllDays = (val: boolean) => {
  if (val) {
    selectedItems.value = [...weeklyMenuItems.value];
  } else {
    selectedItems.value = [];
  }
};

const handleConfirmSelect = async () => {
  if (selectedCompanyIds.value.length === 0) {
    ElMessage.warning('请选择至少一个客户企业');
    return;
  }
  if (selectedItems.value.length === 0) {
    ElMessage.warning('请选择至少一个菜品');
    return;
  }

  saving.value = true;
  try {
    await selectSubMenu({
      weekly_menu_id: selectedWeeklyMenu.value!.id,
      company_ids: selectedCompanyIds.value,
      selected_items: selectedItems.value.map(item => ({
        weekly_menu_item_id: item.id,
        day_of_week: item.day_of_week,
        meal_type: item.meal_type,
        dish_name: item.dish_name,
        dish_category: item.dish_category || null,
      })),
    });
    ElMessage.success('子菜单创建成功');
    selectDialogVisible.value = false;
    await handleLoadHistory();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '创建子菜单失败');
  } finally {
    saving.value = false;
  }
};

const handleViewDetail = async (id: number) => {
  try {
    const subMenu = await getSubMenu(id);
    currentSubMenu.value = subMenu;
    detailDialogVisible.value = true;
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '加载详情失败');
  }
};

onMounted(async () => {
  if (isStaff.value) {
    try {
      companies.value = await fetchCompanies();
    } catch (error) {
      console.error('加载公司列表失败:', error);
    }
  }
  await handleLoadHistory();
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

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.detail-info {
  display: flex;
  gap: 20px;
  margin-bottom: 10px;
}
</style>

