<template>
  <el-card>
    <div class="toolbar">
      <el-input
        v-model="keyword"
        placeholder="搜索公司名称、联系人、联系方式"
        style="max-width: 300px"
        clearable
        @clear="loadData"
        @keyup.enter="loadData"
      />
      <el-button type="primary" @click="openEdit()" v-if="canAdd">新增客户</el-button>
    </div>

    <el-table :data="list" stripe v-loading="loading">
      <el-table-column prop="name" label="公司名称" min-width="150" />
      <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip />
      <el-table-column prop="contact_person" label="联系人" width="120" />
      <el-table-column prop="contact_phone" label="联系方式" width="150" />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ row.created_at ? formatDate(row.created_at) : '--' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" v-if="canEdit || canDelete">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)" v-if="canEdit">编辑</el-button>
          <el-button
            size="small"
            type="danger"
            @click="handleDelete(row)"
            v-if="canDelete"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="dialogVisible"
      :title="current?.id ? '编辑客户' : '新增客户'"
      width="500px"
    >
      <el-form :model="form" label-width="100px">
        <el-form-item label="公司名称" :required="!current?.id">
          <el-input
            v-model="form.name"
            :disabled="!canEditAllFields && !!current?.id"
            placeholder="请输入公司名称"
            maxlength="128"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="地址">
          <el-input
            v-model="form.address"
            type="textarea"
            :rows="2"
            :disabled="!canEditAllFields && !!current?.id"
            placeholder="请输入配送地址/企业地址"
            maxlength="256"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="联系人">
          <el-input 
            v-model="form.contact_person" 
            placeholder="请输入联系人姓名"
            maxlength="64"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="联系方式">
          <el-input 
            v-model="form.contact_phone" 
            placeholder="请输入联系方式（手机号/座机）"
            maxlength="32"
            show-word-limit
          />
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
import { ElMessage, ElMessageBox } from 'element-plus';
import { useAuthStore } from '@/store/auth';
import {
  fetchCompanies,
  createCompany,
  updateCompany,
  deleteCompany,
  type Company,
} from '@/api/companies';

// #region agent log
const logDebug = (location: string, message: string, data: any) => {
  fetch('http://127.0.0.1:7242/ingest/afb94993-0489-4bec-ae77-2b991e500ccf', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      sessionId: 'debug-session',
      runId: 'pre-fix',
      hypothesisId: 'H1',
      location,
      message,
      data,
      timestamp: Date.now(),
    }),
  }).catch(() => {});
};
// #endregion

const auth = useAuthStore();
const role = computed(() => auth.user?.role || '');
// 根据设计文档：admin/superadmin 都可以进行 CRUD 操作
const canAdd = computed(() => ['superadmin', 'admin'].includes(role.value));
const canEdit = computed(() => ['superadmin', 'admin'].includes(role.value));
const canDelete = computed(() => ['superadmin', 'admin'].includes(role.value));
// admin 和 superadmin 都可以编辑所有字段
const canEditAllFields = computed(() => ['superadmin', 'admin'].includes(role.value));

const list = ref<Company[]>([]);
const keyword = ref('');
const loading = ref(false);
const dialogVisible = ref(false);
const current = ref<Company | null>(null);
const form = ref({
  name: '',
  address: '',
  contact_person: '',
  contact_phone: '',
});

const formatDate = (dateStr: string) => {
  if (!dateStr) return '--';
  try {
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateStr;
  }
};

const loadData = async () => {
  loading.value = true;
  // #region agent log
  logDebug('src/views/system/Companies.vue:loadData', 'loadData start', {
    keyword: keyword.value,
    role: role.value,
    hasToken: !!auth.token,
  });
  // #endregion
  try {
    const res = await fetchCompanies({ keyword: keyword.value || undefined });
    list.value = res;
    // #region agent log
    logDebug('src/views/system/Companies.vue:loadData', 'loadData success', {
      count: res.length,
    });
    // #endregion
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '加载客户列表失败');
    // #region agent log
    logDebug('src/views/system/Companies.vue:loadData', 'loadData error', {
      errorName: error.name,
      errorMsg: error.message,
      status: error.response?.status,
      errorData: error.response?.data,
    });
    // #endregion
  } finally {
    loading.value = false;
  }
};

const openEdit = (row?: Company) => {
  if (!canEdit.value) return;
  current.value = row || null;
  if (row) {
    form.value = {
      name: row.name || '',
      address: row.address || '',
      contact_person: row.contact_person || '',
      contact_phone: row.contact_phone || '',
    };
  } else {
    form.value = {
      name: '',
      address: '',
      contact_person: '',
      contact_phone: '',
    };
  }
  // #region agent log
  logDebug('src/views/system/Companies.vue:openEdit', 'openEdit', {
    isEdit: !!row,
    canEditAllFields: canEditAllFields.value,
    role: role.value,
  });
  // #endregion
  dialogVisible.value = true;
};

const save = async () => {
  if (!form.value.name.trim()) {
    ElMessage.warning('公司名称不能为空');
    return;
  }
  // #region agent log
  logDebug('src/views/system/Companies.vue:save', 'save start', {
    isEdit: !!current.value,
    formData: {
      hasName: !!form.value.name,
      hasAddress: !!form.value.address,
      hasContactPerson: !!form.value.contact_person,
      hasContactPhone: !!form.value.contact_phone,
    },
    canEditAllFields: canEditAllFields.value,
  });
  // #endregion
  try {
    if (current.value?.id) {
      const payload: any = {
        contact_person: form.value.contact_person || null,
        contact_phone: form.value.contact_phone || null,
      };
      if (canEditAllFields.value) {
        payload.name = form.value.name;
        payload.address = form.value.address || null;
      }
      await updateCompany(current.value.id, payload);
      ElMessage.success('更新成功');
    } else {
      await createCompany({
        name: form.value.name,
        address: form.value.address || null,
        contact_person: form.value.contact_person || null,
        contact_phone: form.value.contact_phone || null,
      });
      ElMessage.success('创建成功');
    }
    // #region agent log
    logDebug('src/views/system/Companies.vue:save', 'save success', {});
    // #endregion
    dialogVisible.value = false;
    await loadData();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.msg || '保存失败');
    // #region agent log
    logDebug('src/views/system/Companies.vue:save', 'save error', {
      errorName: error.name,
      errorMsg: error.message,
      status: error.response?.status,
      errorData: error.response?.data,
    });
    // #endregion
  }
};

const handleDelete = async (row: Company) => {
  if (!canDelete.value) return;
  try {
    await ElMessageBox.confirm(
      `确定要删除客户"${row.name}"吗？删除后将无法恢复。`,
      '删除确认',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
      }
    );
    // #region agent log
    logDebug('src/views/system/Companies.vue:handleDelete', 'handleDelete start', {
      companyId: row.id,
      companyName: row.name,
    });
    // #endregion
    await deleteCompany(row.id);
    ElMessage.success('删除成功');
    // #region agent log
    logDebug('src/views/system/Companies.vue:handleDelete', 'handleDelete success', {});
    // #endregion
    await loadData();
  } catch (error: any) {
    if (error !== 'cancel') {
      const errorMsg = error.response?.data?.msg || '删除失败';
      ElMessage.error(errorMsg);
      // #region agent log
      logDebug('src/views/system/Companies.vue:handleDelete', 'handleDelete error', {
        errorName: error.name,
        errorMsg: error.message,
        status: error.response?.status,
        errorData: error.response?.data,
      });
      // #endregion
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
