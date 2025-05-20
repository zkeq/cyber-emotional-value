<template>
  <div id="app">
    <router-view />
    <div class="bubbles">
      <div class="bubble" v-for="n in 10" :key="n" 
           :style="{ 
             width: 20 + Math.random() * 60 + 'px', 
             height: 20 + Math.random() * 60 + 'px',
             left: Math.random() * 100 + '%',
             top: Math.random() * 100 + '%',
             animationDuration: 3 + Math.random() * 7 + 's',
             animationDelay: Math.random() * 5 + 's'
           }">
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

.bubbles {
  position: fixed;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: -1;
  pointer-events: none;
}

.bubble {
  position: absolute;
  animation: float infinite ease-in-out;
}
</style>
