<template>
  <div class="dashboard">
    <el-row :gutter="16">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="card">
          <div class="card-title">今日订单总数</div>
          <div class="card-value">--</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="card">
          <div class="card-title">已到达订单</div>
          <div class="card-value">--</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="card">
          <div class="card-title">已回收订单</div>
          <div class="card-value">--</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
// 后续可在此调用后端统计接口，填充卡片数据
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.card {
  text-align: center;
}
.card-title {
  font-size: 14px;
  color: #909399;
}
.card-value {
  margin-top: 8px;
  font-size: 24px;
  font-weight: 600;
  color: #27ae60;
}
</style>
