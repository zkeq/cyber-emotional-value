<template>
  <div class="stats-component">
    <div class="stats-item" v-for="(stat, index) in stats" :key="index">
      <span class="stats-label">{{ stat.label }}</span>
      <span class="stats-value" :class="stat.class">{{ stat.value }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatsComponent',
  props: {
    sessionDuration: {
      type: Number,
      default: 0
    },
    tokenCount: {
      type: Number,
      default: 0
    },
    messageCount: {
      type: Number,
      default: 0
    },
    emotionType: {
      type: String,
      default: ''
    }
  },
  computed: {
    stats() {
      return [
        {
          label: '已进入网站',
          value: this.formatTime(this.sessionDuration),
          class: ''
        },
        {
          label: '消耗Token',
          value: this.tokenCount,
          class: ''
        },
        {
          label: '收到消息',
          value: this.messageCount,
          class: ''
        },
        {
          label: '情绪类型',
          value: this.emotionType,
          class: 'emotion-type'
        }
      ];
    }
  },
  methods: {
    formatTime(seconds) {
      const mins = Math.floor(seconds / 60);
      const secs = Math.floor(seconds % 60);
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
  }
}
</script>

<style scoped>
.stats-component {
  display: flex;
  justify-content: space-around;
  width: 100%;
}

.stats-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stats-label {
  font-size: 12px;
  color: #888;
  margin-bottom: 5px;
}

.stats-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--primary-color);
}

.emotion-type {
  color: var(--secondary-color);
}

@media (max-width: 768px) {
  .stats-label {
    font-size: 10px;
  }
  
  .stats-value {
    font-size: 14px;
  }
}
</style>
