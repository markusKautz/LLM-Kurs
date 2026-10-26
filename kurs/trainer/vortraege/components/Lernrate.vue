<!--
  Drei Lernraten auf derselben Kurve: zu klein, gut, zu groß.
  Klick 1: alle drei laufen gleichzeitig los
-->
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useIsSlideActive, useSlideContext } from '@slidev/client'
import { pause, zahl } from '../logik/modell'

// Dieselbe Kurve wie in Notebook 2: Tal bei w = 3
const f = (w: number) => (w - 3) ** 2 + 1
const steigung = (w: number) => 2 * (w - 3)
const START = 0.3

const FAELLE = [
  { titel: 'Zu klein', lernrate: 0.03, text: 'Kommt an, aber sehr langsam.', farbe: 'var(--text-leise)' },
  { titel: 'Gut', lernrate: 0.3, text: 'Schnell und sicher im Tal.', farbe: 'var(--blau)' },
  { titel: 'Zu groß', lernrate: 1.04, text: 'Springt über das Tal hinaus, immer weiter weg.', farbe: 'var(--orange)' },
]

const B = 340
const H = 250
const x = (w: number) => 20 + ((w + 0.5) / 7) * (B - 40)
const y = (v: number) => H - 20 - (Math.min(v, 14) / 14) * (H - 40)
const kurve = (() => {
  const teile: string[] = []
  for (let i = 0; i <= 100; i++) {
    const w = -0.5 + (i / 100) * 7
    teile.push(`${x(w).toFixed(1)},${y(f(w)).toFixed(1)}`)
  }
  return `M${teile.join(' L')}`
})()

const { $clicks } = useSlideContext()
const aktiv = useIsSlideActive()
const wege = ref<number[][]>(FAELLE.map(() => [START]))
let lauf = 0

watch([$clicks, aktiv], async ([klicks, jetzt]) => {
  const meinLauf = ++lauf
  wege.value = FAELLE.map(() => [START])
  if (!jetzt || klicks < 1)
    return
  for (let schritt = 0; schritt < 14 && meinLauf === lauf; schritt++) {
    await pause(650)
    wege.value = wege.value.map((weg, i) => {
      const w = weg[weg.length - 1]
      const neu = w - FAELLE[i].lernrate * steigung(w)
      return [...weg, Math.max(Math.min(neu, 6.4), -0.4)]
    })
  }
}, { immediate: true })
</script>

<template>
  <div class="lernraten">
    <div v-for="(fall, i) in FAELLE" :key="i" class="fall karte">
      <div class="kopf">
        <span class="titel" :style="{ color: fall.farbe }">{{ fall.titel }}</span>
        <span class="rate">Lernrate {{ zahl(fall.lernrate, 2) }}</span>
      </div>
      <svg :width="B" :height="H">
        <path :d="kurve" class="kurve" />
        <line :x1="x(3)" :x2="x(3)" :y1="y(0)" :y2="y(1)" class="tal" />
        <polyline
          :points="wege[i].map(w => `${x(w).toFixed(1)},${y(f(w)).toFixed(1)}`).join(' ')"
          class="weg" :style="{ stroke: fall.farbe }"
        />
        <circle
          v-for="(w, k) in wege[i].slice(0, -1)" :key="k"
          :cx="x(w)" :cy="y(f(w))" r="4" :style="{ fill: fall.farbe }" class="spur"
        />
        <circle :cx="x(wege[i][wege[i].length - 1])" :cy="y(f(wege[i][wege[i].length - 1]))" r="10" class="ball" :style="{ fill: fall.farbe }" />
      </svg>
      <div class="text" :class="{ an: $clicks >= 1 && wege[i].length > 8 }">{{ fall.text }}</div>
    </div>
  </div>
  <div class="formel" :class="{ an: $clicks >= 2 }">
    neuer Wert = alter Wert − <b>Lernrate</b> × Steigung
  </div>
</template>

<style scoped>
.lernraten {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.2rem;
  margin-top: 1.2rem;
}

.fall {
  padding: 1rem 1.1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.kopf {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.titel {
  font-size: 1.3rem;
  font-weight: 700;
}

.rate {
  font-family: var(--mono);
  font-size: 0.95rem;
  color: var(--text-leise);
}

.kurve {
  fill: none;
  stroke: var(--text);
  stroke-width: 2.5;
}

.tal {
  stroke: var(--text-sehr-leise);
  stroke-dasharray: 4 4;
}

.weg {
  fill: none;
  stroke-width: 1.5;
  stroke-dasharray: 4 3;
  opacity: 0.7;
}

.spur {
  opacity: 0.45;
}

.ball {
  stroke: #fff;
  stroke-width: 3;
  transition: cx 0.5s ease, cy 0.5s ease;
}

.text {
  min-height: 1.5rem;
  font-size: 1.05rem;
  color: var(--text-leise);
  opacity: 0;
  transition: opacity 0.5s;
}

.text.an {
  opacity: 1;
}

.formel {
  margin-top: 1.5rem;
  text-align: center;
  font-family: var(--mono);
  font-size: 1.5rem;
  opacity: 0;
  transition: opacity 0.6s;
}

.formel.an {
  opacity: 1;
}

.formel b {
  color: var(--orange);
}
</style>
