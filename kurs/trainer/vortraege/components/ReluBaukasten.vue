<!--
  Warum der Knick so wichtig ist: Aus vielen ReLU-Knicken lässt sich jede Kurve zusammensetzen.
  Jeder Klick nimmt mehr Neuronen (Knicke) dazu.
-->
<script setup lang="ts">
import { computed } from 'vue'
import { useSlideContext } from '@slidev/client'

const STUFEN = [0, 1, 3, 6, 24]
const ziel = (x: number) => 3 + 1.6 * Math.sin(x * 0.9) + 0.9 * Math.sin(x * 2.3 + 1) + 0.25 * x

const B = 760
const H = 340
const px = (x: number) => 30 + (x / 10) * (B - 50)
const py = (y: number) => H - 30 - (y / 8) * (H - 50)

const { $clicks } = useSlideContext()
const neuronen = computed(() => STUFEN[Math.min($clicks.value, STUFEN.length - 1)])

const zielPfad = (() => {
  const teile: string[] = []
  for (let i = 0; i <= 200; i++) {
    const x = (i / 200) * 10
    teile.push(`${px(x).toFixed(1)},${py(ziel(x)).toFixed(1)}`)
  }
  return `M${teile.join(' L')}`
})()

// Gerade Stücke zwischen gleichmäßig verteilten Punkten. Jeder Knick ist genau ein ReLU-Neuron.
const naeherung = computed(() => {
  const k = neuronen.value
  if (k === 0)
    return { punkte: '', knicke: [] as number[][] }
  const xs = Array.from({ length: k + 2 }, (_, i) => (i / (k + 1)) * 10)
  const pts = xs.map(x => [x, ziel(x)])
  return {
    punkte: pts.map(([x, y]) => `${px(x).toFixed(1)},${py(y).toFixed(1)}`).join(' '),
    knicke: pts.slice(1, -1),
  }
})
</script>

<template>
  <div class="baukasten">
    <svg :width="B" :height="H">
      <line :x1="px(0)" :x2="px(10)" :y1="py(0)" :y2="py(0)" class="achse" />
      <path :d="zielPfad" class="ziel" />
      <polyline v-if="neuronen" :points="naeherung.punkte" class="naeherung" />
      <circle v-for="(p, i) in naeherung.knicke" :key="`${neuronen}-${i}`" :cx="px(p[0])" :cy="py(p[1])" r="5" class="knick" />
    </svg>
    <div class="seite">
      <div class="anzahl"><b>{{ neuronen }}</b> {{ neuronen === 1 ? 'Neuron' : 'Neuronen' }}</div>
      <div class="legende"><span class="strich grau" /> was das Netz lernen soll</div>
      <div class="legende"><span class="strich orange" /> was die Neuronen zusammen können</div>
      <div class="relu-bild">
        <svg width="120" height="70"><polyline points="10,55 60,55 110,10" /></svg>
        <span>ein Neuron = ein Knick</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.baukasten {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-top: 1.4rem;
}

.achse {
  stroke: var(--text-leise);
}

.ziel {
  fill: none;
  stroke: var(--text-sehr-leise);
  stroke-width: 4;
  stroke-dasharray: 8 6;
}

.naeherung {
  fill: none;
  stroke: var(--orange);
  stroke-width: 4;
  stroke-linejoin: round;
}

.knick {
  fill: var(--flaeche);
  stroke: var(--orange);
  stroke-width: 2.5;
  animation: auf 0.4s ease;
}

@keyframes auf {
  from { r: 0; }
}

.seite {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.anzahl {
  font-size: 1.5rem;
}

.anzahl b {
  font-family: var(--mono);
  font-size: 3rem;
  color: var(--orange);
}

.legende {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 1rem;
  color: var(--text-leise);
}

.strich {
  width: 2rem;
  height: 4px;
  border-radius: 2px;
}

.strich.grau {
  background: var(--text-sehr-leise);
}

.strich.orange {
  background: var(--orange);
}

.relu-bild {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-top: 1rem;
  font-size: 1rem;
  color: var(--text-leise);
}

.relu-bild polyline {
  fill: none;
  stroke: var(--orange);
  stroke-width: 4;
  stroke-linecap: round;
}
</style>
