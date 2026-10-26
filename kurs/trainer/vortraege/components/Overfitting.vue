<!--
  Größer ist nicht immer besser: Training und Test für ein kleines und ein riesiges Netz (echte Messungen).
  Klick 1: kleines Netz · Klick 2: riesiges Netz · Klick 3: die Lücke markieren
-->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { useSlideContext } from '@slidev/client'
import { zahl } from '../logik/modell'
import { ladeJson } from '../logik/netz'

type Messung = { schritt: number, training: number, test: number }
type Lauf = { kontext: number, koordinaten: number, neuronen: number, gewichte: number, messungen: Messung[] }

const { $clicks } = useSlideContext()
const daten = ref<{ klein: Lauf, riesig: Lauf, zeichen_im_text: number } | null>(null)
ladeJson<{ klein: Lauf, riesig: Lauf, zeichen_im_text: number }>('overfitting.json').then(d => daten.value = d)

const B = 520
const H = 330
const px = (s: number) => 46 + (s / 12000) * (B - 60)
const py = (v: number) => H - 34 - (Math.min(v, 3.6) / 3.6) * (H - 50)
const linie = (m: Messung[], art: 'training' | 'test') => m.map(p => `${px(p.schritt).toFixed(1)},${py(p[art]).toFixed(1)}`).join(' ')

const laeufe = computed(() => daten.value ? [
  { name: 'Kleines Netz', lauf: daten.value.klein, an: $clicks.value >= 1 },
  { name: 'Riesiges Netz', lauf: daten.value.riesig, an: $clicks.value >= 2 },
] : [])
</script>

<template>
  <div v-if="daten" class="overfitting">
    <div v-for="(l, i) in laeufe" :key="i" class="fall karte" :class="{ an: l.an }">
      <div class="kopf">
        <span class="titel">{{ l.name }}</span>
        <span class="details">{{ l.lauf.kontext }} Zeichen · {{ l.lauf.neuronen }} Neuronen · {{ zahl(l.lauf.gewichte) }} Gewichte</span>
      </div>
      <svg :width="B" :height="H">
        <line :x1="px(0)" :x2="px(12000)" :y1="py(0)" :y2="py(0)" class="achse" />
        <line :x1="px(0)" :x2="px(0)" :y1="py(0)" :y2="py(3.6)" class="achse" />
        <text v-for="v in [0, 1, 2, 3]" :key="v" :x="px(0) - 8" :y="py(v) + 4" class="zahl">{{ v }}</text>
        <text :x="(px(0) + px(12000)) / 2" :y="H - 6" class="achsentitel">Lernschritte</text>
        <polygon
          v-if="i === 1 && $clicks >= 3" class="luecke"
          :points="`${linie(l.lauf.messungen, 'training')} ${linie([...l.lauf.messungen].reverse(), 'test')}`"
        />
        <polyline :points="linie(l.lauf.messungen, 'training')" class="kurve training" pathLength="1" />
        <polyline :points="linie(l.lauf.messungen, 'test')" class="kurve test" pathLength="1" />
      </svg>
      <div class="werte">
        <span class="training-farbe">Training {{ zahl(l.lauf.messungen[l.lauf.messungen.length - 1].training, 2) }}</span>
        <span class="test-farbe">Test {{ zahl(l.lauf.messungen[l.lauf.messungen.length - 1].test, 2) }}</span>
      </div>
    </div>
  </div>
  <div class="merksatz text-center mt-5 schluss" :class="{ an: $clicks >= 3 }">
    Das riesige Netz lernt den Trainingstext <span class="akzent">auswendig</span>. Auf neuem Text wird es schlechter.
  </div>
</template>

<style scoped>
.schluss {
  opacity: 0;
  transition: opacity 0.6s;
}

.schluss.an {
  opacity: 1;
}

.overfitting {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.6rem;
  margin-top: 1rem;
}

.fall {
  padding: 1rem 1.2rem;
  opacity: 0.15;
  transition: opacity 0.6s;
}

.fall.an {
  opacity: 1;
}

.kopf {
  display: flex;
  flex-direction: column;
}

.titel {
  font-size: 1.25rem;
  font-weight: 700;
}

.details {
  font-size: 0.9rem;
  color: var(--text-leise);
}

.achse {
  stroke: var(--text-leise);
}

.zahl {
  font-family: var(--mono);
  font-size: 12px;
  fill: var(--text-leise);
  text-anchor: end;
}

.achsentitel {
  font-size: 13px;
  fill: var(--text-leise);
  text-anchor: middle;
}

.kurve {
  fill: none;
  stroke-width: 3.5;
  stroke-linejoin: round;
  stroke-dasharray: 1;
  stroke-dashoffset: 1;
  transition: stroke-dashoffset 2.4s ease;
}

.fall.an .kurve {
  stroke-dashoffset: 0;
}

.training {
  stroke: var(--blau);
}

.test {
  stroke: var(--orange);
}

.luecke {
  fill: rgba(235, 104, 52, 0.12);
  animation: auf 0.8s ease;
}

@keyframes auf {
  from { opacity: 0; }
}

.werte {
  display: flex;
  gap: 1.5rem;
  font-family: var(--mono);
  font-size: 1.05rem;
  font-weight: 700;
}

.training-farbe {
  color: var(--blau);
}

.test-farbe {
  color: var(--orange);
}
</style>
