<!--
  Pausenfolie mit Countdown. Startet, sobald die Folie erscheint.
-->
<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useIsSlideActive } from '@slidev/client'

const props = withDefaults(defineProps<{ minuten?: number }>(), { minuten: 10 })

const aktiv = useIsSlideActive()
const rest = ref(props.minuten * 60)
let uhr = 0

watch(aktiv, (jetzt) => {
  clearInterval(uhr)
  if (!jetzt)
    return
  rest.value = props.minuten * 60
  uhr = window.setInterval(() => {
    rest.value = Math.max(rest.value - 1, 0)
  }, 1000)
}, { immediate: true })
onBeforeUnmount(() => clearInterval(uhr))

const anzeige = computed(() => `${Math.floor(rest.value / 60)}:${String(rest.value % 60).padStart(2, '0')}`)
const anteil = computed(() => rest.value / (props.minuten * 60))
</script>

<template>
  <div class="pause">
    <svg viewBox="0 0 220 220" class="uhr-ring">
      <circle cx="110" cy="110" r="96" class="hinten" />
      <circle cx="110" cy="110" r="96" class="vorne" :style="{ strokeDashoffset: `${(1 - anteil) * 603.2}` }" />
    </svg>
    <div class="zeit">{{ anzeige }}</div>
  </div>
</template>

<style scoped>
.pause {
  position: relative;
  width: 300px;
  height: 300px;
  margin: 1.5rem auto 0;
}

.uhr-ring {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.hinten,
.vorne {
  fill: none;
  stroke-width: 12;
}

.hinten {
  stroke: var(--linie);
}

.vorne {
  stroke: var(--orange);
  stroke-linecap: round;
  stroke-dasharray: 603.2;
  transition: stroke-dashoffset 1s linear;
}

.zeit {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  font-family: var(--mono);
  font-size: 4rem;
  font-weight: 700;
}
</style>
