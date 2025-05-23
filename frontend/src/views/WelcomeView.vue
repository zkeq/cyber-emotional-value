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
      <div class="mt-8 text-center space-y-3">
        <p class="text-gray-500 text-sm">
          每天都需要一些情绪价值，让我们来夸夸你吧~
        </p>
        <a 
          href="https://github.com/zkeq/cyber-emotional-value" 
          target="_blank"
          class="inline-flex items-center gap-2 text-gray-600 hover:text-pink-500 transition-colors"
        >
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd" />
          </svg>
          <span class="text-sm">喜欢这个项目？ - 欢迎 Star ⭐</span>
        </a>
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
