<template>
  <div class="absolute w-full h-full top-0 left-0 overflow-hidden pointer-events-none">
    <div 
      v-for="bullet in bullets" 
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
  </div>
</template>

<script>
export default {
  name: 'BulletComponent',
  props: {
    bullets: {
      type: Array,
      required: true
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
</style>
