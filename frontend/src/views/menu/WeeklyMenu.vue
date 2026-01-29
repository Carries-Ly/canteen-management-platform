<template>
  <el-card class="weekly-menu-card">
    <template #header>
      <div class="card-header">
        <span>一周总菜单</span>
        <div>
          <el-date-picker
            v-model="selectedWeekDate"
            type="week"
            placeholder="选择周（周一-周日）"
            style="width: 220px; margin-right: 10px"
          />
          <el-button type="primary" @click="handleGenerate" :loading="generating" :disabled="!selectedWeekInfo">
            生成菜单
          </el-button>
          <el-button @click="handleLoadMenu" :loading="loading" :disabled="!selectedWeekInfo">
            查询历史
          </el-button>
        </div>
      </div>
    </template>

    <div v-if="currentMenu" class="menu-container">
      <div class="menu-info">
        <span>第{{ currentMenu.week_number }}周 ({{ currentMenu.week_start_date }} 至 {{ currentMenu.week_end_date }})</span>
        <el-tag :type="currentMenu.status === 'published' ? 'success' : 'info'">
          {{ currentMenu.status === 'published' ? '已发布' : '草稿' }}
        </el-tag>
      </div>

      <div class="menu-table-wrap">
        <el-table
          :data="tableData"
          border
          stripe
          height="100%"
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
              <button
                class="dish-cell-btn"
                type="button"
                @click="openEditCell(row, d.day)"
                :title="getCellText(row, d.key)"
              >
                <span class="dish-cell-text">{{ getCellText(row, d.key) || '—' }}</span>
              </button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <el-empty v-else description="请选择一个周（周一-周日），生成或查询历史菜单" />

    <el-dialog v-model="editDialogVisible" title="替换菜品" width="520px">
      <div class="edit-meta">
        <div><strong>星期</strong>：{{ editContext.dayLabel }}</div>
        <div><strong>餐别</strong>：{{ editContext.mealType }}</div>
        <div><strong>分类</strong>：{{ editContext.category }}</div>
        <div><strong>当前</strong>：{{ editContext.currentDish || '—' }}</div>
      </div>

      <div class="edit-search">
        <el-input v-model="dishKeyword" placeholder="输入菜品名称进行模糊查询" clearable />
        <el-button @click="handleSearchDishes" :loading="searching" :disabled="!dishKeyword.trim()">搜索</el-button>
      </div>

      <div class="edit-results">
        <el-scrollbar height="240px">
          <div
            v-for="it in dishOptions"
            :key="String(it.id)"
            class="dish-option"
            :class="{ active: selectedDish?.id === it.id }"
            @click="selectedDish = it"
          >
            {{ it.name }}
          </div>
          <div v-if="dishOptions.length === 0" class="empty-hint">暂无结果（后端接口可替换为真实菜品库查询）</div>
        </el-scrollbar>
      </div>

      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmReplace" :disabled="!selectedDish || !currentMenu">
          确认替换
        </el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { fetchWeeklyMenus, getWeeklyMenu, generateWeeklyMenu, replaceWeeklyMenuItem, type WeeklyMenu, type WeeklyMenuItem } from '@/api/weeklyMenu';
import { searchDishes, type DishSearchItem } from '@/api/dishes';

const loading = ref(false);
const generating = ref(false);
const selectedWeekDate = ref<Date | null>(null);
const currentMenu = ref<WeeklyMenu | null>(null);

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
  const info = getISOWeekInfo(selectedWeekDate.value);
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/4b46b970-547e-4662-a3c2-96b8ed9f0e6d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'WeeklyMenu.vue:selectedWeekInfo',message:'week selected',data:{pickerDate:selectedWeekDate.value?.toISOString?.(),weekYear:info.weekYear,weekNumber:info.weekNumber,weekStart:info.weekStart.toISOString(),weekEnd:info.weekEnd.toISOString(),weekStartDay:info.weekStart.getDay(),weekEndDay:info.weekEnd.getDay()},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
  // #endregion
  return info;
});

interface TableRow {
  mealType: string; // 用于业务定位
  mealTypeLabel: string; // 用于显示（午餐/晚餐合并）
  category: string; // 分类：大荤一、大荤二、大荤三、小荤一、小荤二、素菜一、素菜二、例汤
  monday: string[];
  tuesday: string[];
  wednesday: string[];
  thursday: string[];
  friday: string[];
  saturday: string[];
  sunday: string[];
}

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

const tableData = computed<TableRow[]>(() => {
  if (!currentMenu.value || !currentMenu.value.items) return [];

  const items = currentMenu.value.items;
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
        const dayKey = dayColumns[day - 1].key as keyof TableRow;
        row[dayKey] = dayItems
          .slice()
          .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
          .map(i => i.dish_name);
      }

      rows.push(row);
    });
  });

  return rows;
});

const arraySpanMethod = ({ row, columnIndex }: { row: TableRow; columnIndex: number }) => {
  const rowIndex = tableData.value.findIndex(r => r === row);
  if (rowIndex === -1) return { rowspan: 1, colspan: 1 };
  
  // 第一列（餐别列）需要把午餐/晚餐分别合并成一个大单元格
  if (columnIndex === 0) {
    if (!row.mealTypeLabel) {
      return { rowspan: 0, colspan: 0 };
    }

    let rowspan = 1;
    for (let i = rowIndex + 1; i < tableData.value.length; i++) {
      const nextRow = tableData.value[i];
      if (nextRow.mealType === row.mealType) {
        rowspan++;
      } else {
        break;
      }
    }
    return { rowspan, colspan: 1 };
  }

  return { rowspan: 1, colspan: 1 };
};

function getCellText(row: TableRow, key: DayKey): string {
  const arr = (row as any)[key] as string[] | undefined;
  if (!arr || arr.length === 0) return '';
  return arr.join('\n');
}

// ------------- 单元格编辑 -------------
const editDialogVisible = ref(false);
const searching = ref(false);
const dishKeyword = ref('');
const dishOptions = ref<DishSearchItem[]>([]);
const selectedDish = ref<DishSearchItem | null>(null);
const editContext = ref<{ day: number; dayLabel: string; mealType: string; category: string; currentDish: string }>(
  { day: 1, dayLabel: '周一', mealType: '午餐', category: '大荤一', currentDish: '' }
);

function openEditCell(row: TableRow, day: number) {
  const dayLabel = dayColumns.find(d => d.day === day)?.label || `周${day}`;
  const key = dayColumns.find(d => d.day === day)?.key as DayKey;
  const currentDish = getCellText(row, key);
  editContext.value = { day, dayLabel, mealType: row.mealType, category: row.category, currentDish };
  dishKeyword.value = '';
  dishOptions.value = [];
  selectedDish.value = null;
  editDialogVisible.value = true;

  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/4b46b970-547e-4662-a3c2-96b8ed9f0e6d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'WeeklyMenu.vue:openEditCell',message:'open edit dialog',data:{day,mealType:row.mealType,category:row.category},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
  // #endregion
}

async function handleSearchDishes() {
  const q = dishKeyword.value.trim();
  if (!q) return;
  searching.value = true;
  try {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/4b46b970-547e-4662-a3c2-96b8ed9f0e6d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'WeeklyMenu.vue:handleSearchDishes',message:'search dishes click',data:{q},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
    // #endregion

    dishOptions.value = await searchDishes(q);
    selectedDish.value = dishOptions.value[0] || null;
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.msg || '搜索失败（菜品库接口可后续接入）');
  } finally {
    searching.value = false;
  }
}

async function handleConfirmReplace() {
  if (!currentMenu.value) return;
  if (!selectedDish.value) return;

  const payload = {
    day_of_week: editContext.value.day,
    meal_type: editContext.value.mealType,
    dish_category: editContext.value.category,
    new_dish_name: selectedDish.value.name,
  };

  try {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/4b46b970-547e-4662-a3c2-96b8ed9f0e6d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'WeeklyMenu.vue:handleConfirmReplace',message:'replace dish confirm',data:{menuId:currentMenu.value.id,...payload},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
    // #endregion

    const res = await replaceWeeklyMenuItem(currentMenu.value.id, payload);
    const updated = res.item;
    if (currentMenu.value.items) {
      const idx = currentMenu.value.items.findIndex(
        it =>
          it.day_of_week === updated.day_of_week &&
          it.meal_type === updated.meal_type &&
          it.dish_category === updated.dish_category
      );
      if (idx >= 0) currentMenu.value.items[idx].dish_name = updated.dish_name;
      else currentMenu.value.items.push(updated);
    }
    ElMessage.success('替换成功');
    editDialogVisible.value = false;
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.msg || '替换失败');
  }
}

const handleGenerate = async () => {
  if (!selectedWeekInfo.value) {
    ElMessage.warning('请选择一个周');
    return;
  }

  generating.value = true;
  try {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/4b46b970-547e-4662-a3c2-96b8ed9f0e6d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'WeeklyMenu.vue:handleGenerate',message:'generate weekly menu',data:{weekYear:selectedWeekInfo.value.weekYear,weekNumber:selectedWeekInfo.value.weekNumber},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    const result = await generateWeeklyMenu(selectedWeekInfo.value.weekYear, selectedWeekInfo.value.weekNumber);
    ElMessage.success('菜单生成成功');
    await loadMenuById(result.id);
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '生成菜单失败');
  } finally {
    generating.value = false;
  }
};

const handleLoadMenu = async () => {
  if (!selectedWeekInfo.value) {
    ElMessage.warning('请选择一个周');
    return;
  }

  loading.value = true;
  try {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/4b46b970-547e-4662-a3c2-96b8ed9f0e6d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'WeeklyMenu.vue:handleLoadMenu',message:'load weekly menu by week',data:{weekYear:selectedWeekInfo.value.weekYear,weekNumber:selectedWeekInfo.value.weekNumber},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    const menus = await fetchWeeklyMenus({
      week_year: selectedWeekInfo.value.weekYear,
      week_number: selectedWeekInfo.value.weekNumber,
    });
    if (menus.length > 0) {
      await loadMenuById(menus[0].id);
    } else {
      ElMessage.warning('未找到该周的菜单，请先生成');
      currentMenu.value = null;
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '加载菜单失败');
  } finally {
    loading.value = false;
  }
};

const loadMenuById = async (id: number) => {
  try {
    const menu = await getWeeklyMenu(id);
    currentMenu.value = menu;
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '加载菜单详情失败');
  }
};

onMounted(() => {
  selectedWeekDate.value = new Date();
});
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.weekly-menu-card {
  height: calc(100vh - 110px);
  display: flex;
  flex-direction: column;
}

.weekly-menu-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.menu-container {
  margin-top: 10px;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.menu-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.menu-table-wrap {
  flex: 1;
  overflow: hidden;
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
}

.menu-table {
  width: 100%;
}

.menu-table :deep(.el-table__cell) {
  padding: 6px 8px;
}

.menu-table :deep(.el-table .cell) {
  white-space: normal;
  line-height: 1.25;
  font-size: clamp(13px, 1.05vw, 16px);
}

.dish-cell-btn {
  width: 100%;
  min-height: 44px;
  padding: 6px 6px;
  text-align: left;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.12s ease, border-color 0.12s ease;
}

.dish-cell-btn:hover {
  background: rgba(64, 158, 255, 0.08);
  border-color: rgba(64, 158, 255, 0.35);
}

.dish-cell-text {
  display: inline-block;
  white-space: pre-wrap;
  word-break: break-word;
}

.edit-meta {
  display: grid;
  gap: 6px;
  margin-bottom: 12px;
  font-size: 14px;
}

.edit-search {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.edit-results {
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  padding: 6px;
}

.dish-option {
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.12s ease;
}

.dish-option:hover {
  background: rgba(64, 158, 255, 0.08);
}

.dish-option.active {
  background: rgba(64, 158, 255, 0.16);
  outline: 1px solid rgba(64, 158, 255, 0.35);
}

.empty-hint {
  padding: 10px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
</style>

