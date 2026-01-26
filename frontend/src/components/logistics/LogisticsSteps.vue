<template>
  <div class="logistics-steps">
    <el-steps :active="currentStep" finish-status="success" align-center>
      <el-step
        title="备餐装车中"
        :description="stagePrepareLoaded ? `完成时间：${formatTime(timePrepareLoaded)}` : ''"
        :status="getStepStatus(1)"
      />
      <el-step
        title="运输中"
        :description="stageShipping ? `完成时间：${formatTime(timeShipping)}` : ''"
        :status="getStepStatus(2)"
      />
      <el-step
        title="已到达"
        :description="stageArrived ? `完成时间：${formatTime(timeArrived)}` : ''"
        :status="getStepStatus(3)"
      />
      <el-step
        title="已回收"
        :description="stageRecycled ? `完成时间：${formatTime(timeRecycled)}` : ''"
        :status="getStepStatus(4)"
      />
    </el-steps>
    
    <div v-if="showActions" class="actions">
      <div class="action-buttons">
        <el-checkbox
          v-model="selectedStages.prepare_loaded"
          :disabled="stagePrepareLoaded || !canOperateStage('prepare_loaded') || !canUpdateStage('prepare_loaded')"
          @change="handleStageChange"
        >
          确认备餐装车
        </el-checkbox>
        <el-checkbox
          v-model="selectedStages.shipping"
          :disabled="stageShipping || !canOperateStage('shipping') || !canUpdateStage('shipping')"
          @change="handleStageChange"
        >
          确认运输中
        </el-checkbox>
        <el-checkbox
          v-model="selectedStages.arrived"
          :disabled="stageArrived || !canOperateStage('arrived') || !canUpdateStage('arrived')"
          @change="handleStageChange"
        >
          确认已到达
        </el-checkbox>
        <el-checkbox
          v-model="selectedStages.recycled"
          :disabled="stageRecycled || !canOperateStage('recycled') || !canUpdateStage('recycled')"
          @change="handleStageChange"
        >
          确认已回收
        </el-checkbox>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { ElMessage } from 'element-plus';

interface Props {
  orderId: number;
  stagePrepareLoaded: boolean;
  timePrepareLoaded: string | null;
  stageShipping: boolean;
  timeShipping: string | null;
  stageArrived: boolean;
  timeArrived: string | null;
  stageRecycled: boolean;
  timeRecycled: string | null;
  showActions?: boolean;
  userRole?: string;
}

const emit = defineEmits<{
  stageChange: [orderId: number, selectedStage: string | null];
}>();

const props = withDefaults(defineProps<Props>(), {
  showActions: false,
  userRole: '',
});

// #region agent log
// 监听props变化，记录日志
watch(
  () => [
    props.stagePrepareLoaded,
    props.stageShipping,
    props.stageArrived,
    props.stageRecycled,
    props.timePrepareLoaded,
    props.timeShipping,
    props.timeArrived,
    props.timeRecycled,
  ],
  () => {
    fetch('http://127.0.0.1:7242/ingest/afb94993-0489-4bec-ae77-2b991e500ccf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId: 'debug-session',
        runId: 'pre-fix',
        hypothesisId: 'H2',
        location: 'src/components/logistics/LogisticsSteps.vue:props-change',
        message: 'LogisticsSteps props updated',
        data: {
          orderId: props.orderId,
          stage_prepare_loaded: props.stagePrepareLoaded,
          stage_shipping: props.stageShipping,
          stage_arrived: props.stageArrived,
          stage_recycled: props.stageRecycled,
          time_prepare_loaded: props.timePrepareLoaded,
          time_shipping: props.timeShipping,
          time_arrived: props.timeArrived,
          time_recycled: props.timeRecycled,
        },
        timestamp: Date.now(),
      }),
    }).catch(() => {});
  },
  { immediate: true }
);
// #endregion

const selectedStages = ref({
  prepare_loaded: false,
  shipping: false,
  arrived: false,
  recycled: false,
});

const currentStep = computed(() => {
  // 返回当前最高的完成阶段索引（用于el-steps的active属性）
  if (props.stageRecycled) return 3;
  if (props.stageArrived) return 2;
  if (props.stageShipping) return 1;
  if (props.stagePrepareLoaded) return 0;
  return -1;
});

const getStepStatus = (step: number) => {
  // 已完成的状态显示为success
  if (step === 1 && props.stagePrepareLoaded) return 'success';
  if (step === 2 && props.stageShipping) return 'success';
  if (step === 3 && props.stageArrived) return 'success';
  if (step === 4 && props.stageRecycled) return 'success';
  
  // 当前进行中的状态显示为process（下一个要执行的步骤）
  if (step === 1 && !props.stagePrepareLoaded && currentStep.value === -1) {
    return 'process';
  }
  if (step === 2 && !props.stageShipping && props.stagePrepareLoaded) {
    return 'process';
  }
  if (step === 3 && !props.stageArrived && props.stageShipping) {
    return 'process';
  }
  if (step === 4 && !props.stageRecycled && props.stageArrived) {
    return 'process';
  }
  
  return 'wait';
};

const formatTime = (timeStr: string | null) => {
  if (!timeStr) return '';
  try {
    const date = new Date(timeStr);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  } catch {
    return timeStr;
  }
};

const canOperateStage = (stage: string) => {
  const role = props.userRole;
  if (stage === 'prepare_loaded' || stage === 'shipping') {
    return role === 'admin' || role === 'superadmin';
  }
  if (stage === 'arrived' || stage === 'recycled') {
    return role === 'admin' || role === 'superadmin' || role === 'user';
  }
  return false;
};

// 检查是否可以更新到该阶段（必须按顺序，且前置阶段已完成）
const canUpdateStage = (stage: string) => {
  // 如果阶段已完成，不能再次更新
  if (stage === 'prepare_loaded' && props.stagePrepareLoaded) return false;
  if (stage === 'shipping' && props.stageShipping) return false;
  if (stage === 'arrived' && props.stageArrived) return false;
  if (stage === 'recycled' && props.stageRecycled) return false;
  
  // 检查前置阶段是否完成
  if (stage === 'prepare_loaded') {
    // 备餐装车是第一阶段，可以直接更新
    return true;
  }
  if (stage === 'shipping') {
    // 运输中需要备餐装车已完成
    return props.stagePrepareLoaded;
  }
  if (stage === 'arrived') {
    // 已到达需要运输中已完成
    return props.stageShipping;
  }
  if (stage === 'recycled') {
    // 已回收需要已到达已完成
    return props.stageArrived;
  }
  
  return false;
};

const handleStageChange = () => {
  // 确定选中的下一个阶段（只能选择一个）
  let selectedStage: string | null = null;
  
  // 按优先级检查：找到第一个选中的有效状态
  if (selectedStages.value.prepare_loaded && !props.stagePrepareLoaded && canUpdateStage('prepare_loaded')) {
    selectedStage = 'prepare_loaded';
    // 取消其他选择
    selectedStages.value.shipping = false;
    selectedStages.value.arrived = false;
    selectedStages.value.recycled = false;
  } else if (selectedStages.value.shipping && !props.stageShipping && canUpdateStage('shipping')) {
    selectedStage = 'shipping';
    selectedStages.value.prepare_loaded = false;
    selectedStages.value.arrived = false;
    selectedStages.value.recycled = false;
  } else if (selectedStages.value.arrived && !props.stageArrived && canUpdateStage('arrived')) {
    selectedStage = 'arrived';
    selectedStages.value.prepare_loaded = false;
    selectedStages.value.shipping = false;
    selectedStages.value.recycled = false;
  } else if (selectedStages.value.recycled && !props.stageRecycled && canUpdateStage('recycled')) {
    selectedStage = 'recycled';
    selectedStages.value.prepare_loaded = false;
    selectedStages.value.shipping = false;
    selectedStages.value.arrived = false;
  } else {
    // 如果所有勾选框都被取消或无效，重置为null
    if (!selectedStages.value.prepare_loaded && 
        !selectedStages.value.shipping && 
        !selectedStages.value.arrived && 
        !selectedStages.value.recycled) {
      selectedStage = null;
    } else {
      // 如果有勾选但无效，清除所有勾选
      selectedStages.value = {
        prepare_loaded: false,
        shipping: false,
        arrived: false,
        recycled: false,
      };
      selectedStage = null;
    }
  }
  
  // 通知父组件状态变化
  emit('stageChange', props.orderId, selectedStage);
};

// 监听阶段变化，重置选中状态
watch(
  () => [
    props.stagePrepareLoaded,
    props.stageShipping,
    props.stageArrived,
    props.stageRecycled,
  ],
  () => {
    selectedStages.value = {
      prepare_loaded: false,
      shipping: false,
      arrived: false,
      recycled: false,
    };
    // 通知父组件状态已重置
    emit('stageChange', props.orderId, null);
  }
);
</script>

<style scoped>
.logistics-steps {
  padding: 20px;
}

.actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.action-buttons {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}
</style>

