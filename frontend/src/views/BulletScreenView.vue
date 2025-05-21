<template>
  <div class="bullet-screen-container">
    <!-- 弹幕区域 -->
    <div class="bullet-screen" ref="bulletScreen">
      <transition-group name="bullet" tag="div">
        <div 
          v-for="bullet in activeBullets" 
          :key="bullet.id" 
          class="bullet-item"
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
    <div class="stats-panel">
      <div class="stats-item">
        <span class="stats-label">已进入网站</span>
        <span class="stats-value">{{ formatTime(sessionDuration) }}</span>
      </div>
      <div class="stats-item">
        <span class="stats-label">消耗Token</span>
        <span class="stats-value">{{ tokenCount }}</span>
      </div>
      <div class="stats-item">
        <span class="stats-label">收到消息</span>
        <span class="stats-value">{{ messageCount }}</span>
      </div>
      <div class="stats-item">
        <span class="stats-label">情绪类型</span>
        <span class="stats-value emotion-type">{{ emotionType }}</span>
      </div>
    </div>


    <!-- 字数设置面板 -->
    <!-- <div class="settings-panel" :class="{ 'settings-open': settingsOpen }">
      <div class="settings-header" @click="toggleSettings">
        <span class="settings-icon">⚙️</span>
        <span class="settings-title">字数设置</span>
        <span class="settings-toggle">{{ settingsOpen ? '▼' : '▲' }}</span>
      </div>
      
      <div class="settings-content" v-if="settingsOpen">
        <div class="length-sliders">
          <div class="slider-group">
            <label>最小字数: {{ minLength }}</label>
            <input 
              type="range" 
              class="slider" 
              v-model.number="minLength" 
              min="1" 
              max="30" 
              @input="validateLengthRange"
            >
          </div>
          
          <div class="slider-group">
            <label>最大字数: {{ maxLength }}</label>
            <input 
              type="range" 
              class="slider" 
              v-model.number="maxLength" 
              min="1" 
              max="50" 
              @input="validateLengthRange"
            >
          </div>
        </div>
        
        <div class="length-preview">
          当前设置: {{ minLength }}-{{ maxLength }}字
        </div>
        
        <button class="apply-btn" @click="applySettings">
          应用设置
        </button>
      </div>
    </div> -->
    
    <!-- 返回按钮 -->
    <button class="back-btn" @click="goBack">
      <span class="back-icon">←</span> 返回
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
        '#4ecdc4', '#7ee8e1', '#ffe66d', '#ffed8a'
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
      const wsUrl = `wss://emotional-value-api.onmicrosoft.cn/ws/${encodeURIComponent(this.emotionType)}?min_length=${this.minLength}&max_length=${this.maxLength}`;
      
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
        } else if (data.type === 'message') {
          // 弹幕消息
          this.addBullet(data.content);
          
          // 更新统计信息
          this.tokenCount = data.token_count;
          this.messageCount = data.message_count;
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
    addBullet(content) {
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
        duration
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

<style scoped>
.bullet-screen-container {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background-color: var(--background-color);
}

.bullet-screen {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  overflow: hidden;
}

.bullet-item {
  position: absolute;
  white-space: nowrap;
  font-size: 24px;
  font-weight: 500;
  padding: 5px 10px;
  border-radius: 20px;
  background-color: rgba(255, 255, 255, 0.7);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  animation: bulletMove linear;
  transform: translateX(100vw);
}

@keyframes bulletMove {
  from {
    transform: translateX(100vw);
  }
  to {
    transform: translateX(-100%);
  }
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

/* 字数设置面板 */
.settings-panel {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 250px;
  background-color: white;
  border-radius: 15px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 10;
  overflow: hidden;
  transition: all 0.3s ease;
}

.settings-header {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  cursor: pointer;
  background-color: var(--primary-color);
  color: white;
}

.settings-icon {
  margin-right: 8px;
}

.settings-title {
  flex-grow: 1;
  font-weight: 500;
}

.settings-content {
  padding: 15px;
}

.length-sliders {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 10px;
}

.slider-group {
  display: flex;
  flex-direction: column;
}

.slider-group label {
  margin-bottom: 5px;
  font-size: 14px;
  color: #666;
}

.slider {
  width: 100%;
  height: 8px;
  -webkit-appearance: none;
  appearance: none;
  background: #e0e0e0;
  outline: none;
  border-radius: 4px;
  transition: all 0.3s;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--primary-color);
  cursor: pointer;
  transition: all 0.3s;
}

.slider::-webkit-slider-thumb:hover {
  background: var(--secondary-color);
  transform: scale(1.1);
}

.length-preview {
  font-size: 14px;
  color: var(--primary-color);
  font-weight: 500;
  margin: 10px 0;
  text-align: center;
}

.apply-btn {
  width: 100%;
  padding: 8px 0;
  background-color: var(--secondary-color);
  color: white;
  border: none;
  border-radius: 20px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.apply-btn:hover {
  background-color: var(--primary-color);
  transform: translateY(-2px);
}

/* 底部统计面板 */
.stats-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  display: flex;
  justify-content: space-around;
  padding: 15px;
  background-color: rgba(255, 255, 255, 0.9);
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  z-index: 10;
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

.back-btn {
  position: fixed;
  top: 20px;
  left: 20px;
  padding: 8px 15px;
  background-color: white;
  border: none;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  cursor: pointer;
  z-index: 10;
  transition: all 0.3s ease;
}

.back-btn:hover {
  transform: translateX(-3px);
}

.back-icon {
  margin-right: 5px;
}

@media (max-width: 768px) {
  .bullet-item {
    font-size: 18px;
  }
  
  .stats-panel {
    padding: 10px 5px;
  }
  
  .stats-label {
    font-size: 10px;
  }
  
  .stats-value {
    font-size: 14px;
  }
  
  .settings-panel {
    width: 200px;
  }
}
</style>
