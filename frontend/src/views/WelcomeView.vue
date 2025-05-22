<template>
  <div class="min-h-screen bg-gradient-to-br from-pink-100 to-rose-100 flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl p-8 md:p-12 w-full max-w-md shadow-xl transform transition-all hover:scale-[1.02] duration-300">
      <!-- Logo Section -->
      <div class="text-center mb-8">
        <h1 class="text-4xl md:text-5xl font-bold bg-gradient-to-r from-pink-500 to-rose-400 bg-clip-text text-transparent">
          夸夸网站
        </h1>
      </div>

      <!-- Title -->
      <h2 class="text-2xl font-semibold text-gray-700 text-center mb-8">
        今天想要怎样的情绪价值？
      </h2>

      <!-- Input Container -->
      <div class="space-y-6">
        <!-- Emotion Input -->
        <input 
          type="text" 
          class="w-full px-4 py-3 rounded-xl border-2 border-pink-200 focus:border-pink-400 focus:ring-2 focus:ring-pink-200 outline-none transition-all text-center text-lg placeholder-gray-400"
          v-model="emotionType"
          placeholder="例如：鼓励、温暖、治愈、自信..."
          @keyup.enter="startBulletScreen"
        >
        
        <!-- Length Settings -->
        <div class="bg-pink-50 rounded-2xl p-6 space-y-4">
          <h3 class="text-lg font-medium text-pink-600 text-center">
            自定义字数范围
          </h3>
          
          <!-- Sliders -->
          <div class="space-y-6">
            <div class="space-y-2">
              <label class="text-sm text-gray-600 block text-center">
                最小字数: {{ minLength }}
              </label>
              <input 
                type="range" 
                class="w-full h-2 bg-pink-200 rounded-lg appearance-none cursor-pointer accent-pink-500"
                v-model.number="minLength" 
                min="1" 
                max="30" 
                @input="validateLengthRange"
              >
            </div>
            
            <div class="space-y-2">
              <label class="text-sm text-gray-600 block text-center">
                最大字数: {{ maxLength }}
              </label>
              <input 
                type="range" 
                class="w-full h-2 bg-pink-200 rounded-lg appearance-none cursor-pointer accent-pink-500"
                v-model.number="maxLength" 
                min="1" 
                max="50" 
                @input="validateLengthRange"
              >
            </div>
          </div>
          
          <!-- Length Preview -->
          <div class="text-center text-pink-600 font-medium">
            当前设置: {{ minLength }}-{{ maxLength }}字
          </div>
        </div>
        
        <!-- Start Button -->
        <button 
          @click="startBulletScreen"
          class="w-full bg-gradient-to-r from-pink-500 to-rose-400 text-white py-4 rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl transform transition-all hover:-translate-y-0.5 flex items-center justify-center gap-2"
        >
          开始夸夸
          <span class="animate-bounce">❤️</span>
        </button>
      </div>

      <!-- Footer -->
      <div class="mt-8 text-center">
        <p class="text-gray-500 text-sm">
          每天都需要一些情绪价值，让我们来夸夸你吧~
        </p>
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
