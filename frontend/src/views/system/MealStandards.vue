<template>
  <el-card>
    <div class="toolbar">
      <el-input v-model="keyword" placeholder="搜索餐标名称" style="max-width: 200px" />
      <el-select v-model="status" placeholder="状态" clearable style="width: 150px">
        <el-option label="启用" value="enabled" />
        <el-option label="停用" value="disabled" />
      </el-select>
      <el-button type="primary" @click="openEdit()" v-if="canEdit">新增餐标</el-button>
    </div>

    <el-table :data="filteredList" stripe>
      <el-table-column prop="name" label="餐标名称" min-width="150" />
      <el-table-column prop="meal_type" label="餐别" width="100" />
      <el-table-column prop="price" label="单价（元）" width="120">
        <template #default="{ row }">
          ¥{{ row.price?.toFixed(2) || '0.00' }}
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'enabled' ? 'success' : 'info'">
            {{ row.status === 'enabled' ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" v-if="canEdit">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="current?.id ? '编辑餐标' : '新增餐标'" width="500px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="请输入餐标名称" maxlength="128" show-word-limit />
        </el-form-item>
        <el-form-item label="餐别" required>
          <el-select v-model="form.meal_type" placeholder="请选择餐别" style="width: 100%">
            <el-option label="早餐" value="早餐" />
            <el-option label="午餐" value="午餐" />
            <el-option label="晚餐" value="晚餐" />
            <el-option label="夜宵" value="夜宵" />
          </el-select>
        </el-form-item>
        <el-form-item label="单价" required>
          <el-input-number v-model="form.price" :min="0" :precision="2" style="width: 100%" placeholder="请输入单价" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入餐标描述（可选）"
            maxlength="256"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.enabled" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { useAuthStore } from '@/store/auth';
import { createMealStandard, fetchMealStandards, updateMealStandard } from '@/api/mealStandards';

const auth = useAuthStore();
const canEdit = computed(() => ['superadmin', 'admin'].includes(auth.user?.role || ''));

const list = ref<any[]>([]);
const keyword = ref('');
const status = ref<string | undefined>();
const dialogVisible = ref(false);
const current = ref<any | null>(null);
const form = ref({ name: '', meal_type: '午餐', price: 0, description: '', enabled: true });

const filteredList = computed(() => {
  return list.value.filter((item) => {
    const matchKeyword = keyword.value
      ? item.name.toLowerCase().includes(keyword.value.toLowerCase())
      : true;
    const matchStatus = status.value ? item.status === status.value : true;
    return matchKeyword && matchStatus;
  });
});

const loadData = async () => {
  const res = await fetchMealStandards({ status: status.value });
  list.value = res;
};

const openEdit = (row?: any) => {
  if (!canEdit.value) return;
  current.value = row || null;
  if (row) {
    form.value = {
      name: row.name,
      meal_type: row.meal_type,
      price: row.price,
      description: row.description || '',
      enabled: row.status === 'enabled',
    };
  } else {
    form.value = { name: '', meal_type: '午餐', price: 0, description: '', enabled: true };
  }
  dialogVisible.value = true;
};

const save = async () => {
  if (!form.value.name || !form.value.meal_type || form.value.price === null || form.value.price < 0) {
    ElMessage.warning('请填写完整信息');
    return;
  }
  const payload = {
    name: form.value.name.trim(),
    meal_type: form.value.meal_type,
    price: form.value.price,
    description: form.value.description?.trim() || null,
    status: form.value.enabled ? 'enabled' : 'disabled',
  };
  if (current.value?.id) {
    await updateMealStandard(current.value.id, payload);
    ElMessage.success('更新成功');
  } else {
    await createMealStandard(payload);
    ElMessage.success('创建成功');
  }
  dialogVisible.value = false;
  await loadData();
};

onMounted(loadData);
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  align-items: center;
  flex-wrap: wrap;
}
</style>
