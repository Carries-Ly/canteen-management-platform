<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>一周总菜单</span>
        <div>
          <el-select v-model="selectedWeekYear" placeholder="选择年份" style="width: 120px; margin-right: 10px">
            <el-option
              v-for="year in years"
              :key="year"
              :label="year"
              :value="year"
            />
          </el-select>
          <el-input-number
            v-model="selectedWeekNumber"
            :min="1"
            :max="53"
            placeholder="周数"
            style="width: 120px; margin-right: 10px"
          />
          <el-button type="primary" @click="handleGenerate" :loading="generating">生成菜单</el-button>
          <el-button @click="handleLoadMenu" :loading="loading">查看菜单</el-button>
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

      <el-table
        :data="tableData"
        border
        stripe
        style="width: 100%; margin-top: 20px"
        :span-method="arraySpanMethod"
      >
        <el-table-column prop="category" label="分类" width="120" fixed="left" />
        <el-table-column prop="monday" label="周一" min-width="150">
          <template #default="{ row }">
            <div v-for="(dish, idx) in row.monday" :key="idx" class="dish-item">{{ dish }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="tuesday" label="周二" min-width="150">
          <template #default="{ row }">
            <div v-for="(dish, idx) in row.tuesday" :key="idx" class="dish-item">{{ dish }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="wednesday" label="周三" min-width="150">
          <template #default="{ row }">
            <div v-for="(dish, idx) in row.wednesday" :key="idx" class="dish-item">{{ dish }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="thursday" label="周四" min-width="150">
          <template #default="{ row }">
            <div v-for="(dish, idx) in row.thursday" :key="idx" class="dish-item">{{ dish }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="friday" label="周五" min-width="150">
          <template #default="{ row }">
            <div v-for="(dish, idx) in row.friday" :key="idx" class="dish-item">{{ dish }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="saturday" label="周六" min-width="150">
          <template #default="{ row }">
            <div v-for="(dish, idx) in row.saturday" :key="idx" class="dish-item">{{ dish }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="sunday" label="周日" min-width="150">
          <template #default="{ row }">
            <div v-for="(dish, idx) in row.sunday" :key="idx" class="dish-item">{{ dish }}</div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-empty v-else description="请选择年份和周数，生成或查看菜单" />
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { fetchWeeklyMenus, getWeeklyMenu, generateWeeklyMenu, type WeeklyMenu, type WeeklyMenuItem } from '@/api/weeklyMenu';

const loading = ref(false);
const generating = ref(false);
const selectedWeekYear = ref(new Date().getFullYear());
const selectedWeekNumber = ref(1);
const currentMenu = ref<WeeklyMenu | null>(null);

const years = computed(() => {
  const currentYear = new Date().getFullYear();
  return Array.from({ length: 3 }, (_, i) => currentYear - 1 + i);
});

interface TableRow {
  category: string;
  mealType: string;
  monday: string[];
  tuesday: string[];
  wednesday: string[];
  thursday: string[];
  friday: string[];
  saturday: string[];
  sunday: string[];
}

const tableData = computed<TableRow[]>(() => {
  if (!currentMenu.value || !currentMenu.value.items) return [];

  const items = currentMenu.value.items;
  const rows: TableRow[] = [];

  // 菜品分类顺序
  const categories = ['大荤一', '大荤二', '大荤三', '小荤一', '小荤二', '素菜一', '素菜二', '例汤'];
  const mealTypes = ['午餐', '晚餐'];

  // 初始化数据结构
  mealTypes.forEach(mealType => {
    categories.forEach(category => {
      // 晚餐没有大荤三
      if (mealType === '晚餐' && category === '大荤三') return;

      const row: TableRow = {
        category: mealType === '午餐' ? category : '',
        mealType,
        monday: [],
        tuesday: [],
        wednesday: [],
        thursday: [],
        friday: [],
        saturday: [],
        sunday: [],
      };

      // 填充每一天的菜品
      for (let day = 1; day <= 7; day++) {
        const dayItems = items.filter(
          item => item.day_of_week === day &&
          item.meal_type === mealType &&
          item.dish_category === category
        );
        const dayKey = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][day - 1] as keyof TableRow;
        row[dayKey] = dayItems.map(item => item.dish_name).sort((a, b) => {
          const itemA = dayItems.find(i => i.dish_name === a);
          const itemB = dayItems.find(i => i.dish_name === b);
          return (itemA?.sort_order || 0) - (itemB?.sort_order || 0);
        });
      }

      rows.push(row);
    });
  });

  return rows;
});

const arraySpanMethod = ({ row, columnIndex }: { row: TableRow; columnIndex: number }) => {
  // 第一列（分类列）需要合并相同餐别的行
  if (columnIndex === 0) {
    const categoryIndex = tableData.value.findIndex(r => r === row);
    if (categoryIndex === 0 || tableData.value[categoryIndex - 1].mealType !== row.mealType) {
      // 计算相同餐别的行数
      let rowspan = 1;
      for (let i = categoryIndex + 1; i < tableData.value.length; i++) {
        if (tableData.value[i].mealType === row.mealType) {
          rowspan++;
        } else {
          break;
        }
      }
      return { rowspan, colspan: 1 };
    } else {
      return { rowspan: 0, colspan: 0 };
    }
  }
  return { rowspan: 1, colspan: 1 };
};

const handleGenerate = async () => {
  if (!selectedWeekYear.value || !selectedWeekNumber.value) {
    ElMessage.warning('请选择年份和周数');
    return;
  }

  generating.value = true;
  try {
    const result = await generateWeeklyMenu(selectedWeekYear.value, selectedWeekNumber.value);
    ElMessage.success('菜单生成成功');
    await loadMenuById(result.id);
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '生成菜单失败');
  } finally {
    generating.value = false;
  }
};

const handleLoadMenu = async () => {
  if (!selectedWeekYear.value || !selectedWeekNumber.value) {
    ElMessage.warning('请选择年份和周数');
    return;
  }

  loading.value = true;
  try {
    const menus = await fetchWeeklyMenus({
      week_year: selectedWeekYear.value,
      week_number: selectedWeekNumber.value,
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
  // 计算当前周数
  const now = new Date();
  const start = new Date(now.getFullYear(), 0, 1);
  const days = Math.floor((now.getTime() - start.getTime()) / (24 * 60 * 60 * 1000));
  const weekNumber = Math.ceil((days + start.getDay() + 1) / 7);
  selectedWeekNumber.value = weekNumber;
});
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.menu-container {
  margin-top: 20px;
}

.menu-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.dish-item {
  padding: 4px 0;
  font-size: 13px;
}
</style>

