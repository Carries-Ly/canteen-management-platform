<template>
  <el-card>
    <div class="header">
      <div>
        <div class="title">订单详情（ID：{{ orderId }}）</div>
        <div class="subtitle">此处后续可展示公司名称、订餐日期和状态等信息</div>
      </div>
    </div>
    <el-divider />
    <el-empty description="订单详情页面待实现" />
  </el-card>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router';

const route = useRoute();
const orderId = route.params.id;
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.title {
  font-size: 18px;
  font-weight: 600;
}
.subtitle {
  margin-top: 4px;
  font-size: 13px;
  color: #909399;
}
</style>
