<template>
  <div class="welcome-container">
    <div class="welcome-card">
      <div class="logo">
        <h1 class="logo-text">夸夸网站</h1>
      </div>
      <h2 class="welcome-title">今天想要怎样的情绪价值？</h2>
      <div class="input-container">
        <input 
          type="text" 
          class="input emotion-input" 
          v-model="emotionType"
          placeholder="例如：鼓励、温暖、治愈、自信..."
          @keyup.enter="startBulletScreen"
        >
        
        <!-- 字数范围选择 -->
        <div class="length-settings">
          <h3 class="settings-title">自定义字数范围</h3>
          
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
        </div>
        
        <button class="btn start-btn" @click="startBulletScreen">
          开始夸夸
          <span class="btn-icon">❤️</span>
        </button>
      </div>
      <div class="welcome-footer">
        <p>每天都需要一些情绪价值，让我们来夸夸你吧~</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WelcomeView',
  data() {
    return {
      emotionType: '',
      minLength: 5,
      maxLength: 15
    }
  },
  methods: {
    validateLengthRange() {
      // 确保最小值不大于最大值
      if (this.minLength > this.maxLength) {
        this.maxLength = this.minLength;
      }
    },
    startBulletScreen() {
      if (!this.emotionType.trim()) {
        this.emotionType = '鼓励'; // 默认情绪类型
      }
      
      // 传递字数范围参数
      this.$router.push({ 
        name: 'bullets', 
        params: { 
          emotionType: this.emotionType.trim() 
        },
        query: {
          min_length: this.minLength,
          max_length: this.maxLength
        }
      });
    }
  }
}
</script>

<style scoped>
.welcome-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
}

.welcome-card {
  background-color: white;
  border-radius: 20px;
  padding: 40px;
  width: 100%;
  max-width: 500px;
  text-align: center;
  box-shadow: 0 10px 30px var(--shadow-color);
  animation: pulse 3s infinite ease-in-out;
}

.logo {
  margin-bottom: 20px;
}

.logo-text {
  font-size: 2.5rem;
  color: var(--primary-color);
  margin-bottom: 10px;
  font-weight: 700;
}

.welcome-title {
  font-size: 1.5rem;
  margin-bottom: 30px;
  color: var(--text-color);
}

.input-container {
  margin-bottom: 30px;
}

.emotion-input {
  margin-bottom: 15px;
  text-align: center;
  font-size: 18px;
}

/* 字数范围设置样式 */
.length-settings {
  background-color: #f9f9f9;
  border-radius: 15px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.settings-title {
  font-size: 16px;
  margin-bottom: 15px;
  color: var(--secondary-color);
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
  align-items: center;
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
  margin-top: 5px;
}

.start-btn {
  width: 100%;
  font-size: 18px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.btn-icon {
  margin-left: 8px;
  font-size: 20px;
}

.welcome-footer {
  font-size: 14px;
  color: #888;
}

@media (max-width: 768px) {
  .welcome-card {
    padding: 30px 20px;
  }
  
  .logo-text {
    font-size: 2rem;
  }
  
  .welcome-title {
    font-size: 1.2rem;
  }
  
  .length-settings {
    padding: 10px;
  }
}
</style>
