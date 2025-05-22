<template>
  <div class="flex justify-around items-center w-full">
    <div class="flex flex-col items-center" v-for="(stat, index) in stats" :key="index">
      <span class="text-xs md:text-sm text-gray-500 mb-1">{{ stat.label }}</span>
      <span 
        class="text-base md:text-lg font-bold transition-all duration-300"
        :class="stat.class === 'emotion-type' ? 'text-secondary-600' : 'text-primary-600'"
      >
        {{ stat.value }}
      </span>
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
