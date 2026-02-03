<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>子菜单管理</span>
        <el-button type="primary" @click="handleSelectSubMenu" v-if="canEdit">选择子菜单</el-button>
      </div>
    </template>

    <div class="filter-section">
      <el-date-picker
        v-model="selectedWeekDate"
        type="week"
        placeholder="选择周（周一-周日）"
        style="width: 220px; margin-right: 10px"
        format="YYYY 第 ww 周"
      />
      <span v-if="selectedWeekInfo" style="margin-right: 10px; color: #909399; font-size: 13px;">
        第{{ selectedWeekInfo.weekNumber }}周
      </span>
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

    <!-- 选择子菜单对话框 - 表格形式 -->
    <el-dialog
      v-model="selectDialogVisible"
      title="选择子菜单"
      width="90%"
      v-if="canEdit"
    >
      <div v-if="selectedWeeklyMenu">
        <div class="dialog-header">
          <div>
            <span><strong>总菜单：</strong>第{{ selectedWeeklyMenu.week_number }}周 ({{ selectedWeeklyMenu.week_start_date }} 至 {{ selectedWeeklyMenu.week_end_date }})</span>
            <span style="margin-left: 20px; color: #67c23a;">
              <strong>已选择 {{ selectedItemsCount }} 个菜品</strong>
            </span>
          </div>
          <div>
            <el-button size="small" @click="handleSelectAll">全选</el-button>
            <el-button size="small" @click="handleClearAll">清空</el-button>
          </div>
        </div>
        
        <div class="menu-table-wrap">
          <el-table
            :data="selectTableData"
            border
            stripe
            height="500px"
            class="menu-table"
            :span-method="arraySpanMethod"
          >
            <el-table-column prop="mealTypeLabel" label="餐别" width="90" fixed="left" />
            <el-table-column prop="category" label="分类" width="90" fixed="left" />

            <el-table-column
              v-for="d in dayColumns"
              :key="d.key"
              :prop="d.key"
              :label="d.label"
              min-width="140"
            >
              <template #default="{ row }">
                <div
                  class="dish-cell"
                  :class="{ selected: isCellSelected(row, d.day) }"
                  @click="handleCellClick(row, d.day)"
                  :title="isCellSelected(row, d.day) ? '点击取消选择' : '点击选择'"
                >
                  <div
                    v-for="(dish, idx) in getCellDishes(row, d.key)"
                    :key="idx"
                    class="dish-item"
                  >
                    {{ dish.dish_name }}
                  </div>
                  <div v-if="getCellDishes(row, d.key).length === 0" class="dish-empty">—</div>
                  <div v-if="isCellSelected(row, d.day)" class="selected-badge">✓</div>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div style="margin-top: 20px; padding: 15px; background-color: #f5f7fa; border-radius: 4px;">
          <div style="margin-bottom: 10px; font-size: 14px; color: #606266;">
            <strong>选择适用的客户企业：</strong>（可多选）
          </div>
          <el-select
            v-model="selectedCompanyIds"
            multiple
            placeholder="请选择客户企业"
            style="width: 100%"
            filterable
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
        <el-button type="primary" @click="handleConfirmSelect" :loading="saving" :disabled="selectedItemsCount === 0 || selectedCompanyIds.length === 0">
          确认创建子菜单
        </el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 - 表格形式 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="子菜单详情"
      width="90%"
    >
      <div v-if="currentSubMenu">
        <div class="detail-info">
          <span>客户企业：{{ currentSubMenu.company_name }}</span>
          <span>周次：第{{ currentSubMenu.week_number }}周</span>
        </div>
        
        <div class="menu-table-wrap" style="margin-top: 20px">
          <el-table
            :data="detailTableData"
            border
            stripe
            height="500px"
            class="menu-table"
            :span-method="detailArraySpanMethod"
          >
            <el-table-column prop="mealTypeLabel" label="餐别" width="90" fixed="left" />
            <el-table-column prop="category" label="分类" width="90" fixed="left" />

            <el-table-column
              v-for="d in dayColumns"
              :key="d.key"
              :prop="d.key"
              :label="d.label"
              min-width="140"
            >
              <template #default="{ row }">
                <div class="dish-cell detail-cell">
                  <div
                    v-for="(dish, idx) in getDetailCellDishes(row, d.key)"
                    :key="idx"
                    class="dish-item"
                  >
                    {{ dish.dish_name }}
                  </div>
                  <div v-if="getDetailCellDishes(row, d.key).length === 0" class="dish-empty">—</div>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { useAuthStore } from '@/store/auth';
import { fetchSubMenus, getSubMenu, selectSubMenu, getSubMenuHistory, type SubMenu } from '@/api/subMenu';
import { fetchWeeklyMenus, getWeeklyMenu, type WeeklyMenu, type WeeklyMenuItem } from '@/api/weeklyMenu';
import { fetchCompanies, type Company } from '@/api/companies';

interface SubMenuWithWeek extends SubMenu {
  week_year?: number;
  week_number?: number;
}

interface TableRow {
  mealType: string;
  mealTypeLabel: string;
  category: string;
  monday: WeeklyMenuItem[];
  tuesday: WeeklyMenuItem[];
  wednesday: WeeklyMenuItem[];
  thursday: WeeklyMenuItem[];
  friday: WeeklyMenuItem[];
  saturday: WeeklyMenuItem[];
  sunday: WeeklyMenuItem[];
}

const auth = useAuthStore();
const role = computed(() => auth.user?.role || '');
const isStaff = computed(() => ['user', 'admin', 'superadmin'].includes(role.value));
const canEdit = computed(() => ['admin', 'superadmin'].includes(role.value));

const loading = ref(false);
const saving = ref(false);
const selectedWeekDate = ref<Date | null>(null);
const selectedCompanyId = ref<number | null>(null);
const subMenus = ref<SubMenuWithWeek[]>([]);
const companies = ref<Company[]>([]);
const selectDialogVisible = ref(false);
const detailDialogVisible = ref(false);
const selectedWeeklyMenu = ref<WeeklyMenu | null>(null);
const selectedItems = ref<Set<number>>(new Set()); // 使用Set存储选中的菜品ID
const selectedCompanyIds = ref<number[]>([]);
const currentSubMenu = ref<SubMenu | null>(null);

const dayColumns = [
  { key: 'monday', label: '周一', day: 1 },
  { key: 'tuesday', label: '周二', day: 2 },
  { key: 'wednesday', label: '周三', day: 3 },
  { key: 'thursday', label: '周四', day: 4 },
  { key: 'friday', label: '周五', day: 5 },
  { key: 'saturday', label: '周六', day: 6 },
  { key: 'sunday', label: '周日', day: 7 },
] as const;

type DayKey = (typeof dayColumns)[number]['key'];

type WeekInfo = { weekYear: number; weekNumber: number; weekStart: Date; weekEnd: Date };

function getISOWeekInfo(date: Date): WeekInfo {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  const day = d.getUTCDay() || 7; // 1..7 (Mon..Sun)
  d.setUTCDate(d.getUTCDate() + 4 - day); // Thu
  const weekYear = d.getUTCFullYear();
  const yearStart = new Date(Date.UTC(weekYear, 0, 1));
  const weekNumber = Math.ceil((((d.getTime() - yearStart.getTime()) / 86400000) + 1) / 7);

  const weekStart = new Date(d);
  weekStart.setUTCDate(d.getUTCDate() - 3); // Mon
  const weekEnd = new Date(weekStart);
  weekEnd.setUTCDate(weekStart.getUTCDate() + 6); // Sun

  return {
    weekYear,
    weekNumber,
    weekStart: new Date(weekStart.getUTCFullYear(), weekStart.getUTCMonth(), weekStart.getUTCDate()),
    weekEnd: new Date(weekEnd.getUTCFullYear(), weekEnd.getUTCMonth(), weekEnd.getUTCDate()),
  };
}

const selectedWeekInfo = computed<WeekInfo | null>(() => {
  if (!selectedWeekDate.value) return null;
  // 处理可能是字符串或Date对象的情况
  const date = selectedWeekDate.value instanceof Date 
    ? selectedWeekDate.value 
    : new Date(selectedWeekDate.value);
  return getISOWeekInfo(date);
});

// 构建选择表格数据
const selectTableData = computed<TableRow[]>(() => {
  if (!selectedWeeklyMenu.value || !selectedWeeklyMenu.value.items) return [];

  const items = selectedWeeklyMenu.value.items;
  const rows: TableRow[] = [];

  const mealTypes = ['午餐', '晚餐'];
  const categoriesByMeal: Record<string, string[]> = {
    午餐: ['大荤一', '大荤二', '大荤三', '小荤一', '小荤二', '素菜一', '素菜二', '例汤'],
    晚餐: ['大荤一', '大荤二', '小荤一', '小荤二', '素菜一', '素菜二', '例汤'],
  };

  mealTypes.forEach(mealType => {
    const categories = categoriesByMeal[mealType] || [];
    categories.forEach((category, categoryIdx) => {
      const row: TableRow = {
        mealType,
        mealTypeLabel: categoryIdx === 0 ? mealType : '',
        category,
        monday: [],
        tuesday: [],
        wednesday: [],
        thursday: [],
        friday: [],
        saturday: [],
        sunday: [],
      };

      for (let day = 1; day <= 7; day++) {
        const dayItems = items.filter(
          item => item.day_of_week === day && item.meal_type === mealType && item.dish_category === category
        ).sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0));
        
        const dayKey = dayColumns[day - 1].key as DayKey;
        (row as any)[dayKey] = dayItems;
      }

      rows.push(row);
    });
  });

  return rows;
});

// 构建详情表格数据
const detailTableData = computed<TableRow[]>(() => {
  if (!currentSubMenu.value || !currentSubMenu.value.items) return [];

  const items = currentSubMenu.value.items;
  const rows: TableRow[] = [];

  const mealTypes = ['午餐', '晚餐'];
  const categoriesByMeal: Record<string, string[]> = {
    午餐: ['大荤一', '大荤二', '大荤三', '小荤一', '小荤二', '素菜一', '素菜二', '例汤'],
    晚餐: ['大荤一', '大荤二', '小荤一', '小荤二', '素菜一', '素菜二', '例汤'],
  };

  mealTypes.forEach(mealType => {
    const categories = categoriesByMeal[mealType] || [];
    categories.forEach((category, categoryIdx) => {
      const row: TableRow = {
        mealType,
        mealTypeLabel: categoryIdx === 0 ? mealType : '',
        category,
        monday: [],
        tuesday: [],
        wednesday: [],
        thursday: [],
        friday: [],
        saturday: [],
        sunday: [],
      };

      for (let day = 1; day <= 7; day++) {
        const dayItems = items.filter(
          item => item.day_of_week === day && item.meal_type === mealType && item.dish_category === category
        );
        
        // 转换为WeeklyMenuItem格式（用于统一显示）
        const dayKey = dayColumns[day - 1].key as keyof TableRow;
        row[dayKey] = dayItems.map(item => ({
          id: item.id,
          day_of_week: item.day_of_week,
          meal_type: item.meal_type,
          dish_name: item.dish_name,
          dish_category: item.dish_category || null,
          sort_order: 0,
        })) as any;
      }

      rows.push(row);
    });
  });

  return rows;
});

const arraySpanMethod = ({ row, columnIndex }: { row: TableRow; columnIndex: number }) => {
  const rowIndex = selectTableData.value.findIndex(r => r === row);
  if (rowIndex === -1) return { rowspan: 1, colspan: 1 };
  
  if (columnIndex === 0) {
    if (!row.mealTypeLabel) {
      return { rowspan: 0, colspan: 0 };
    }
    let rowspan = 1;
    for (let i = rowIndex + 1; i < selectTableData.value.length; i++) {
      if (selectTableData.value[i].mealType === row.mealType) {
        rowspan++;
      } else {
        break;
      }
    }
    return { rowspan, colspan: 1 };
  }
  return { rowspan: 1, colspan: 1 };
};

const detailArraySpanMethod = ({ row, columnIndex }: { row: TableRow; columnIndex: number }) => {
  const rowIndex = detailTableData.value.findIndex(r => r === row);
  if (rowIndex === -1) return { rowspan: 1, colspan: 1 };
  
  if (columnIndex === 0) {
    if (!row.mealTypeLabel) {
      return { rowspan: 0, colspan: 0 };
    }
    let rowspan = 1;
    for (let i = rowIndex + 1; i < detailTableData.value.length; i++) {
      if (detailTableData.value[i].mealType === row.mealType) {
        rowspan++;
      } else {
        break;
      }
    }
    return { rowspan, colspan: 1 };
  }
  return { rowspan: 1, colspan: 1 };
};

const getCellDishes = (row: TableRow, key: DayKey): WeeklyMenuItem[] => {
  return (row[key] as WeeklyMenuItem[]) || [];
};

const getDetailCellDishes = (row: TableRow, key: DayKey): Array<{ dish_name: string }> => {
  const items = (row[key] as WeeklyMenuItem[]) || [];
  return items.map(item => ({ dish_name: item.dish_name }));
};

const isCellSelected = (row: TableRow, day: number): boolean => {
  const dayKey = dayColumns[day - 1].key as keyof TableRow;
  const items = row[dayKey] as WeeklyMenuItem[];
  if (!items || items.length === 0) return false;
  return items.every(item => selectedItems.value.has(item.id));
};

const handleCellClick = (row: TableRow, day: number) => {
  const dayKey = dayColumns[day - 1].key as keyof TableRow;
  const items = row[dayKey] as WeeklyMenuItem[];
  if (!items || items.length === 0) return;

  const allSelected = items.every(item => selectedItems.value.has(item.id));
  
  if (allSelected) {
    // 取消选择
    items.forEach(item => selectedItems.value.delete(item.id));
  } else {
    // 选择
    items.forEach(item => selectedItems.value.add(item.id));
  }
};

const selectedItemsCount = computed(() => selectedItems.value.size);

const handleSelectAll = () => {
  if (!selectedWeeklyMenu.value || !selectedWeeklyMenu.value.items) return;
  selectedWeeklyMenu.value.items.forEach(item => selectedItems.value.add(item.id));
};

const handleClearAll = () => {
  selectedItems.value.clear();
};

const loadSubMenuHistory = async () => {
  if (!selectedWeekDate.value) {
    subMenus.value = [];
    return;
  }
  
  loading.value = true;
  try {
    const params: any = {};
    if (selectedWeekInfo.value) {
      params.week_year = selectedWeekInfo.value.weekYear;
      params.week_number = selectedWeekInfo.value.weekNumber;
    }
    if (selectedCompanyId.value && isStaff.value) {
      params.company_id = selectedCompanyId.value;
    }
    const data = await getSubMenuHistory(params);
    subMenus.value = data;
    
    // 移除自动展示详情的逻辑，让用户手动点击"查看详情"按钮
  } catch (error: any) {
    console.error('加载子菜单失败:', error);
    subMenus.value = [];
  } finally {
    loading.value = false;
  }
};

const handleSelectSubMenu = async () => {
  if (!selectedWeekDate.value) {
    ElMessage.warning('请先选择周');
    return;
  }
  
  try {
    const weekInfo = selectedWeekInfo.value;
    if (!weekInfo) {
      ElMessage.warning('请先选择周');
      return;
    }
    
    const menus = await fetchWeeklyMenus({ week_year: weekInfo.weekYear, week_number: weekInfo.weekNumber });
    if (menus.length === 0) {
      ElMessage.warning('该周还没有生成总菜单，请先生成总菜单');
      return;
    }
    const menu = await getWeeklyMenu(menus[0].id);
    selectedWeeklyMenu.value = menu;
    selectedItems.value.clear();
    selectedCompanyIds.value = [];
    selectDialogVisible.value = true;
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '加载总菜单失败');
  }
};

const handleConfirmSelect = async () => {
  if (selectedCompanyIds.value.length === 0) {
    ElMessage.warning('请选择至少一个客户企业');
    return;
  }
  if (selectedItems.value.size === 0) {
    ElMessage.warning('请选择至少一个菜品');
    return;
  }

  saving.value = true;
  try {
    // 获取选中的菜品详情
    const selectedItemsList = Array.from(selectedItems.value)
      .map(id => selectedWeeklyMenu.value!.items!.find(item => item.id === id))
      .filter(Boolean) as WeeklyMenuItem[];

    await selectSubMenu({
      weekly_menu_id: selectedWeeklyMenu.value!.id,
      company_ids: selectedCompanyIds.value,
      selected_items: selectedItemsList.map(item => ({
        weekly_menu_item_id: item.id,
        day_of_week: item.day_of_week,
        meal_type: item.meal_type,
        dish_name: item.dish_name,
        dish_category: item.dish_category || null,
      })),
    });
    ElMessage.success('子菜单创建成功');
    selectDialogVisible.value = false;
    await loadSubMenuHistory();
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

// 监听日期和公司变化，自动加载子菜单
watch([selectedWeekDate, selectedCompanyId], () => {
  if (selectedWeekDate.value) {
    loadSubMenuHistory();
  }
}, { immediate: false });

onMounted(async () => {
  // 默认选择当前周
  selectedWeekDate.value = new Date();
  
  if (isStaff.value) {
    try {
      companies.value = await fetchCompanies();
      // 默认选择第一个公司
      if (companies.value.length > 0) {
        selectedCompanyId.value = companies.value[0].id;
      }
    } catch (error) {
      console.error('加载公司列表失败:', error);
    }
  }
  
  // 等待计算属性更新
  await new Promise(resolve => setTimeout(resolve, 100));
  
  // 默认加载当前周的子菜单
  await loadSubMenuHistory();
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

.menu-table-wrap {
  margin-top: 10px;
}

.menu-table {
  width: 100%;
}

.dish-cell {
  min-height: 60px;
  padding: 8px;
  cursor: pointer;
  border: 2px solid transparent;
  border-radius: 4px;
  transition: all 0.2s;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.dish-cell:hover {
  background-color: #f5f7fa;
  border-color: #dcdfe6;
}

.dish-cell.selected {
  background-color: #e1f3d8;
  border-color: #67c23a;
}

.dish-cell.detail-cell {
  cursor: default;
  background-color: #fafafa;
}

.dish-cell.detail-cell:hover {
  background-color: #f5f7fa;
  border-color: transparent;
}

.selected-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 20px;
  height: 20px;
  background-color: #67c23a;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.dish-item {
  padding: 4px 0;
  font-size: 16px;
  line-height: 1.6;
  text-align: center;
  width: 100%;
}

.dish-empty {
  color: #909399;
  font-size: 12px;
  text-align: center;
  padding: 10px 0;
  width: 100%;
}
</style>
