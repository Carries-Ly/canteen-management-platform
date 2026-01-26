<template>
  <el-card>
    <div class="toolbar">
      <el-input
        v-model="keyword"
        placeholder="搜索用户名"
        style="max-width: 300px"
        clearable
        @clear="loadData"
        @keyup.enter="loadData"
      />
      <el-select
        v-model="roleFilter"
        placeholder="筛选角色"
        style="width: 150px"
        clearable
        @change="loadData"
      >
        <el-option label="管理员" value="admin" />
        <el-option label="普通员工" value="user" />
      </el-select>
      <el-button type="primary" @click="openEdit()">新增员工</el-button>
    </div>

    <el-table :data="list" stripe v-loading="loading">
      <el-table-column prop="username" label="用户名" min-width="150" />
      <el-table-column prop="role" label="角色" width="120">
        <template #default="{ row }">
          <el-tag :type="row.role === 'admin' ? 'warning' : 'info'">
            {{ row.role === 'admin' ? '管理员' : '普通员工' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="warning" @click="handleResetPassword(row)">
            重置密码
          </el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="dialogVisible"
      :title="current?.id ? '编辑员工' : '新增员工'"
      width="500px"
    >
      <el-form :model="form" label-width="100px">
        <el-form-item label="用户名" required>
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            maxlength="64"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="密码" :required="!current?.id">
          <el-input
            v-model="form.password"
            type="password"
            :placeholder="current?.id ? '留空则不修改密码' : '请输入密码'"
            show-password
          />
        </el-form-item>
        <el-form-item label="角色" required>
          <el-select v-model="form.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="普通员工" value="user" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="passwordDialogVisible"
      title="密码重置成功"
      width="400px"
    >
      <div style="margin-bottom: 16px">
        <p>新密码已生成，请妥善保管：</p>
        <el-input
          v-model="newPassword"
          readonly
          style="margin-top: 8px"
        >
          <template #append>
            <el-button @click="copyPassword">复制</el-button>
          </template>
        </el-input>
      </div>
      <template #footer>
        <el-button type="primary" @click="passwordDialogVisible = false">确定</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useAuthStore } from '@/store/auth';
import {
  fetchStaff,
  createStaff,
  updateStaff,
  deleteStaff,
  resetStaffPassword,
  type Staff,
} from '@/api/staff';

const auth = useAuthStore();
const role = computed(() => auth.user?.role || '');

const list = ref<Staff[]>([]);
const keyword = ref('');
const roleFilter = ref<'admin' | 'user' | ''>('');
const loading = ref(false);
const dialogVisible = ref(false);
const passwordDialogVisible = ref(false);
const newPassword = ref('');
const current = ref<Staff | null>(null);
const form = ref({
  username: '',
  password: '',
  role: 'user' as 'admin' | 'user',
});

const loadData = async () => {
  loading.value = true;
  try {
    const params: any = {};
    if (keyword.value) {
      params.keyword = keyword.value;
    }
    if (roleFilter.value) {
      params.role = roleFilter.value;
    }
    const res = await fetchStaff(params);
    list.value = res;
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '加载员工列表失败');
  } finally {
    loading.value = false;
  }
};

const openEdit = (row?: Staff) => {
  current.value = row || null;
  if (row) {
    form.value = {
      username: row.username || '',
      password: '',
      role: row.role,
    };
  } else {
    form.value = {
      username: '',
      password: '',
      role: 'user',
    };
  }
  dialogVisible.value = true;
};

const save = async () => {
  if (!form.value.username.trim()) {
    ElMessage.warning('用户名不能为空');
    return;
  }
  if (!current.value?.id && !form.value.password.trim()) {
    ElMessage.warning('创建员工时密码不能为空');
    return;
  }
  if (!form.value.role) {
    ElMessage.warning('请选择角色');
    return;
  }

  try {
    if (current.value?.id) {
      const payload: any = {
        role: form.value.role,
      };
      if (form.value.username !== current.value.username) {
        payload.username = form.value.username;
      }
      await updateStaff(current.value.id, payload);
      ElMessage.success('更新成功');
    } else {
      await createStaff({
        username: form.value.username,
        password: form.value.password,
        role: form.value.role,
      });
      ElMessage.success('创建成功');
    }
    dialogVisible.value = false;
    await loadData();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '保存失败');
  }
};

const handleResetPassword = async (row: Staff) => {
  try {
    await ElMessageBox.confirm(
      `确定要重置员工"${row.username}"的密码吗？`,
      '重置密码确认',
      {
        type: 'warning',
        confirmButtonText: '确定重置',
        cancelButtonText: '取消',
      }
    );
    const res = await resetStaffPassword(row.id);
    newPassword.value = res.new_password || '';
    passwordDialogVisible.value = true;
    ElMessage.success('密码重置成功');
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.msg || '重置密码失败');
    }
  }
};

const copyPassword = async () => {
  try {
    await navigator.clipboard.writeText(newPassword.value);
    ElMessage.success('密码已复制到剪贴板');
  } catch (error) {
    ElMessage.error('复制失败，请手动复制');
  }
};

const handleDelete = async (row: Staff) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除员工"${row.username}"吗？删除后将无法恢复。`,
      '删除确认',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
      }
    );
    await deleteStaff(row.id);
    ElMessage.success('删除成功');
    await loadData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.msg || '删除失败');
    }
  }
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

