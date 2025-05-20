<template>
  <div class="bullet-component">
    <div 
      v-for="bullet in bullets" 
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

<style scoped>
.bullet-component {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  overflow: hidden;
  pointer-events: none;
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

@media (max-width: 768px) {
  .bullet-item {
    font-size: 18px;
  }
}
</style>
