<template>
  <div class="relative w-full h-screen overflow-hidden bg-gradient-to-br from-primary-50 to-secondary-50">
    <!-- 弹幕区域 -->
    <div class="absolute w-full h-full top-0 left-0 overflow-hidden" ref="bulletScreen">
      <transition-group name="bullet" tag="div">
        <div 
          v-for="bullet in activeBullets" 
          :key="bullet.id" 
          class="absolute whitespace-nowrap text-xl md:text-2xl font-medium py-2 px-4 rounded-full bg-opacity-80 shadow-md transform transition-all duration-500"
          :class="bullet.isSystem ? 'bg-white text-primary-600' : 'bg-gradient-to-r from-primary-100 to-secondary-100'"
          :style="{ 
            top: bullet.top + '%', 
            animationDuration: bullet.duration + 's',
            color: bullet.color
          }"
        >
          {{ bullet.content }}
        </div>
      </transition-group>
    </div>
    
    <!-- 底部统计信息 -->
    <div class="fixed bottom-0 left-0 w-full flex justify-around items-center py-3 px-4 bg-white bg-opacity-90 backdrop-blur-sm shadow-lg z-10 rounded-t-xl">
      <div class="flex flex-col items-center">
        <span class="text-xs text-gray-500 mb-1">已进入网站</span>
        <span class="text-base md:text-lg font-bold text-primary-600">{{ formatTime(sessionDuration) }}</span>
      </div>
      <div class="flex flex-col items-center">
        <span class="text-xs text-gray-500 mb-1">消耗Token</span>
        <span class="text-base md:text-lg font-bold text-primary-600">{{ tokenCount }}</span>
      </div>
      <div class="flex flex-col items-center">
        <span class="text-xs text-gray-500 mb-1">收到消息</span>
        <span class="text-base md:text-lg font-bold text-primary-600">{{ messageCount }}</span>
      </div>
      <div class="flex flex-col items-center">
        <span class="text-xs text-gray-500 mb-1">情绪类型</span>
        <span class="text-base md:text-lg font-bold text-secondary-600">{{ emotionType }}</span>
      </div>
    </div>
    
    <!-- 字数设置面板 -->
    <div 
      class="fixed top-5 right-5 w-64 md:w-72 bg-white rounded-2xl shadow-cute overflow-hidden transition-all duration-300 transform z-20"
      :class="settingsOpen ? 'translate-y-0' : 'translate-y-[-85%]'"
    >
      <div 
        class="flex items-center px-4 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white cursor-pointer"
        @click="toggleSettings"
      >
        <span class="mr-2 text-lg">⚙️</span>
        <span class="flex-grow font-medium">字数设置</span>
        <span class="transform transition-transform duration-300" :class="settingsOpen ? 'rotate-180' : ''">▼</span>
      </div>
      
      <div class="p-4" v-if="settingsOpen">
        <div class="space-y-4">
          <div class="space-y-2">
            <div class="flex justify-between items-center">
              <label class="text-sm text-gray-600">最小字数</label>
              <span class="text-sm bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full font-medium">{{ minLength }}</span>
            </div>
            <input 
              type="range" 
              class="w-full h-2 bg-primary-100 rounded-lg appearance-none cursor-pointer accent-primary-500" 
              v-model.number="minLength" 
              min="1" 
              max="30" 
              @input="validateLengthRange"
            >
          </div>
          
          <div class="space-y-2">
            <div class="flex justify-between items-center">
              <label class="text-sm text-gray-600">最大字数</label>
              <span class="text-sm bg-secondary-100 text-secondary-700 px-2 py-0.5 rounded-full font-medium">{{ maxLength }}</span>
            </div>
            <input 
              type="range" 
              class="w-full h-2 bg-secondary-100 rounded-lg appearance-none cursor-pointer accent-secondary-500" 
              v-model.number="maxLength" 
              min="1" 
              max="50" 
              @input="validateLengthRange"
            >
          </div>
        </div>
        
        <div class="mt-3 text-center">
          <span class="inline-block bg-gray-100 px-3 py-1 rounded-full text-sm font-medium text-primary-600">
            当前设置: {{ minLength }}-{{ maxLength }}字
          </span>
        </div>
        
        <button 
          class="w-full mt-4 bg-gradient-to-r from-primary-500 to-secondary-500 text-white py-2 px-4 rounded-xl font-medium transition-all duration-300 hover:shadow-md hover:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-primary-400"
          @click="applySettings"
        >
          应用设置
        </button>
      </div>
    </div>
    
    <!-- 返回按钮 -->
    <button 
      class="fixed top-5 left-5 py-2 px-4 bg-white rounded-full shadow-md flex items-center z-20 transition-all duration-300 hover:shadow-lg hover:translate-x-[-3px] focus:outline-none focus:ring-2 focus:ring-primary-400"
      @click="goBack"
    >
      <span class="mr-1 text-primary-500">←</span> 
      <span class="font-medium text-gray-700">返回</span>
    </button>
  </div>
</template>

<script>
export default {
  name: 'BulletScreenView',
  props: {
    emotionType: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      // WebSocket连接
      socket: null,
      // 会话信息
      sessionId: '',
      sessionStartTime: 0,
      sessionDuration: 0,
      tokenCount: 0,
      messageCount: 0,
      // 弹幕相关
      bulletId: 0,
      activeBullets: [],
      // 字数设置
      minLength: 5,
      maxLength: 15,
      settingsOpen: false,
      // 颜色列表
      colors: [
        '#ff6b6b', '#ff8e8e', '#ff9e7d', '#ffb88c', 
        '#4ecdc4', '#7ee8e1', '#ffe66d', '#ffed8a',
        '#f472b6', '#ec4899', '#db2777', '#be185d',
        '#2dd4bf', '#14b8a6', '#0d9488', '#0f766e'
      ]
    }
  },
  created() {
    // 从URL查询参数获取字数范围
    const { min_length, max_length } = this.$route.query;
    if (min_length) {
      this.minLength = parseInt(min_length);
    }
    if (max_length) {
      this.maxLength = parseInt(max_length);
    }
    
    // 确保参数有效
    this.validateLengthRange();
  },
  mounted() {
    // 初始化WebSocket连接
    this.initWebSocket();
    
    // 启动会话计时器
    this.sessionStartTime = Date.now();
    this.timerInterval = setInterval(() => {
      this.sessionDuration = (Date.now() - this.sessionStartTime) / 1000;
    }, 100);
  },
  beforeUnmount() {
    // 清理资源
    if (this.socket) {
      this.socket.close();
    }
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
    }
  },
  methods: {
    initWebSocket() {
      // 构建WebSocket URL，包含字数范围参数
      const wsUrl = `ws://localhost:8000/ws/${encodeURIComponent(this.emotionType)}?min_length=${this.minLength}&max_length=${this.maxLength}`;
      
      // 创建WebSocket连接
      this.socket = new WebSocket(wsUrl);
      
      // 连接建立时的处理
      this.socket.onopen = () => {
        console.log('WebSocket连接已建立');
      };
      
      // 接收消息的处理
      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'session_start') {
          // 会话开始消息
          this.sessionId = data.session_id;
          console.log('会话已开始:', this.sessionId);
          
          // 如果是参数更新后的新会话，显示提示
          if (data.is_update) {
            console.log('字数设置已更新:', data.min_length, '-', data.max_length);
            // 可以添加一个临时提示
            this.addBullet(`字数已更新为 ${data.min_length}-${data.max_length} 字`, true);
          }
        } else if (data.type === 'message') {
          // 弹幕消息
          this.addBullet(data.content);
          
          // 更新统计信息
          this.tokenCount = data.token_count;
          this.messageCount = data.message_count;
        } else if (data.type === 'params_updated') {
          // 参数更新确认消息
          console.log('参数更新已确认:', data.min_length, '-', data.max_length);
          // 可以在UI上显示更新成功的提示
          this.addBullet(`字数设置已成功应用: ${data.min_length}-${data.max_length} 字`, true);
        }
      };
      
      // 连接关闭的处理
      this.socket.onclose = () => {
        console.log('WebSocket连接已关闭');
      };
      
      // 连接错误的处理
      this.socket.onerror = (error) => {
        console.error('WebSocket错误:', error);
      };
    },
    
    // 添加一条新弹幕
    addBullet(content, isSystem = false) {
      // 生成随机高度（避免顶部和底部）
      const top = 10 + Math.random() * 60;
      
      // 随机选择一个颜色
      const color = this.colors[Math.floor(Math.random() * this.colors.length)];
      
      // 随机生成动画持续时间（秒），增加持续时间使弹幕不那么密集
      const duration = 12 + Math.random() * 6;
      
      // 创建新弹幕对象
      const newBullet = {
        id: this.bulletId++,
        content,
        top,
        color,
        duration,
        isSystem
      };
      
      // 添加到活动弹幕列表
      this.activeBullets.push(newBullet);
      
      // 设置定时器，在动画结束后移除弹幕
      setTimeout(() => {
        const index = this.activeBullets.findIndex(b => b.id === newBullet.id);
        if (index !== -1) {
          this.activeBullets.splice(index, 1);
        }
      }, duration * 1000);
    },
    
    // 验证字数范围
    validateLengthRange() {
      // 确保最小值不大于最大值
      if (this.minLength > this.maxLength) {
        this.maxLength = this.minLength;
      }
    },
    
    // 应用新的字数设置
    applySettings() {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        // 发送更新参数请求
        this.socket.send(JSON.stringify({
          type: 'update_params',
          min_length: this.minLength,
          max_length: this.maxLength
        }));
        
        // 关闭设置面板
        this.settingsOpen = false;
      }
    },
    
    // 切换设置面板显示状态
    toggleSettings() {
      this.settingsOpen = !this.settingsOpen;
    },
    
    // 格式化时间（秒 -> mm:ss）
    formatTime(seconds) {
      const mins = Math.floor(seconds / 60);
      const secs = Math.floor(seconds % 60);
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    },
    
    // 返回首页
    goBack() {
      this.$router.push('/');
    }
  }
}
</script>

<style>
@keyframes bulletMove {
  from {
    transform: translateX(100vw);
  }
  to {
    transform: translateX(-100%);
  }
}

.bullet-item {
  animation: bulletMove linear;
  transform: translateX(100vw);
}

.bullet-enter-active {
  transition: all 0.5s;
}

.bullet-leave-active {
  transition: all 0.5s;
}

.bullet-enter-from, .bullet-leave-to {
  opacity: 0;
}
</style>
