<template>
  <div class="min-h-screen w-full bg-gradient-to-br from-primary-50 to-secondary-50 flex justify-center items-center p-4 md:p-6">
    <div class="w-full max-w-md bg-white rounded-3xl shadow-cute p-6 md:p-8 transform transition-all duration-500 hover:scale-[1.02] animate-fadeIn">
      <!-- 标题区域 -->
      <div class="mb-6 animate-float">
        <div class="flex justify-center mb-2">
          <div class="h-16 w-16 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center shadow-lg">
            <span class="text-3xl">💖</span>
          </div>
        </div>
        <h1 class="text-4xl font-bold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent mb-1">夸夸网站</h1>
        <h2 class="text-xl text-gray-600 font-medium">今天想要怎样的情绪价值？</h2>
      </div>
      
      <!-- 输入区域 -->
      <div class="space-y-6">
        <div class="relative group">
          <input 
            type="text" 
            class="input-cute text-center text-lg placeholder-primary-300"
            v-model="emotionType"
            placeholder="例如：鼓励、温暖、治愈、自信..."
            @keyup.enter="startBulletScreen"
          >
          <div class="absolute inset-0 rounded-xl border-2 border-primary-200 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
        </div>
        
        <!-- 字数范围选择 -->
        <div class="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-2xl p-5 shadow-sm">
          <h3 class="text-primary-700 font-medium text-lg mb-4 flex items-center">
            <span class="mr-2">✨</span>
            自定义字数范围
          </h3>
          
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
            <span class="inline-block bg-white px-3 py-1 rounded-full text-sm font-medium text-primary-600 shadow-sm">
              当前设置: {{ minLength }}-{{ maxLength }}字
            </span>
          </div>
        </div>
        
        <button 
          class="w-full bg-gradient-to-r from-primary-500 to-secondary-500 text-white py-4 px-6 rounded-xl font-medium text-lg transition-all duration-300 transform hover:scale-[1.03] hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
          @click="startBulletScreen"
        >
          开始夸夸
          <span class="ml-2 inline-block animate-bounce-slow">❤️</span>
        </button>
      </div>
      
      <div class="mt-6 text-center text-gray-500 text-sm">
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
