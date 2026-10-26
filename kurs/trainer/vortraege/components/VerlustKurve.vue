<!--
  Der Verlust -log(p) als Kurve: Wie überrascht ist das Modell vom richtigen Zeichen?
  Klick 1: die Kurve
  Klick 2 bis 6: Beispiele von "fast sicher" bis "für unmöglich gehalten"
-->
<script setup lang="ts">
import { computed } from 'vue'
import { useSlideContext } from '@slidev/client'
import { zahl } from '../logik/modell'

const BREITE = 560
const HOEHE = 380
const RAND = { links: 56, rechts: 20, oben: 24, unten: 52 }
const Y_MAX = 5

const BEISPIELE = [
  { p: 0.9, text: 'fast sicher, und es stimmt', farbe: 'var(--blau)' },
  { p: 0.5, text: 'eine von zwei Möglichkeiten', farbe: 'var(--blau)' },
  { p: 0.1, text: 'hat es kaum erwartet', farbe: 'var(--orange)' },
  { p: 0.01, text: 'sehr überrascht', farbe: 'var(--orange)' },
  { p: 0, text: 'hielt es für unmöglich', farbe: 'var(--orange)' },
]

const { $clicks } = useSlideContext()

const x = (p: number) => RAND.links + p * (BREITE - RAND.links - RAND.rechts)
const y = (v: number) => RAND.oben + (1 - Math.min(v, Y_MAX) / Y_MAX) * (HOEHE - RAND.oben - RAND.unten)

const kurve = computed(() => {
  const punkte: string[] = []
  for (let i = 0; i <= 200; i++) {
    const p = Math.exp(-Y_MAX) + (1 - Math.exp(-Y_MAX)) * (i / 200) ** 2
    punkte.push(`${x(p).toFixed(1)},${y(-Math.log(p)).toFixed(1)}`)
  }
  return `M${punkte.join(' L')}`
})

const verlust = (p: number) => p === 0 ? '∞' : zahl(-Math.log(p), 2)
</script>

<template>
  <div class="verlust">
    <svg :width="BREITE" :height="HOEHE" class="diagramm">
      <!-- Achsen und Raster -->
      <g class="raster">
        <line v-for="v in [1, 2, 3, 4, 5]" :key="v" :x1="RAND.links" :x2="BREITE - RAND.rechts" :y1="y(v)" :y2="y(v)" />
      </g>
      <line :x1="RAND.links" :x2="BREITE - RAND.rechts" :y1="y(0)" :y2="y(0)" class="achse" />
      <line :x1="RAND.links" :x2="RAND.links" :y1="y(0)" :y2="RAND.oben - 10" class="achse" />
      <text v-for="v in [0, 1, 2, 3, 4, 5]" :key="`y${v}`" :x="RAND.links - 12" :y="y(v) + 5" class="zahl rechtsbuendig">{{ v }}</text>
      <text v-for="p in [0, 0.25, 0.5, 0.75, 1]" :key="`x${p}`" :x="x(p)" :y="HOEHE - RAND.unten + 22" class="zahl mitte">{{ p * 100 }} %</text>
      <text :x="(BREITE + RAND.links) / 2" :y="HOEHE - 6" class="titel mitte">Wahrscheinlichkeit für das richtige Zeichen</text>
      <text :x="14" :y="HOEHE / 2" class="titel mitte" :transform="`rotate(-90 14 ${HOEHE / 2})`">Verlust</text>

      <path :d="kurve" class="kurve" :class="{ an: $clicks >= 1 }" pathLength="1" />

      <!-- Beispiele -->
      <g v-for="(b, i) in BEISPIELE" :key="i" class="beispiel" :class="{ an: $clicks >= i + 2 }">
        <template v-if="b.p > 0">
          <line :x1="x(b.p)" :x2="x(b.p)" :y1="y(0)" :y2="y(-Math.log(b.p))" class="hilfslinie" />
          <circle :cx="x(b.p)" :cy="y(-Math.log(b.p))" r="8" :fill="b.farbe" />
        </template>
        <template v-else>
          <line :x1="x(0) + 4" :x2="x(0) + 4" :y1="y(0)" :y2="RAND.oben - 6" class="unendlich" />
          <path :d="`M${x(0) - 4} ${RAND.oben + 4} L${x(0) + 4} ${RAND.oben - 10} L${x(0) + 12} ${RAND.oben + 4}`" class="unendlich" />
        </template>
      </g>
    </svg>

    <div class="liste">
      <div v-for="(b, i) in BEISPIELE" :key="i" class="zeile" :class="{ an: $clicks >= i + 2 }">
        <span class="p">{{ zahl(b.p * 100) }} %</span>
        <span class="pfeil">→</span>
        <span class="wert" :style="{ color: b.farbe }">{{ verlust(b.p) }}</span>
        <span class="text">{{ b.text }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.verlust {
  display: grid;
  grid-template-columns: 560px 1fr;
  gap: 2.5rem;
  align-items: center;
  margin-top: 0.8rem;
}

.raster line {
  stroke: var(--linie);
  stroke-dasharray: 3 5;
}

.achse {
  stroke: var(--text-leise);
  stroke-width: 1.5;
}

.zahl {
  font-family: var(--mono);
  font-size: 13px;
  fill: var(--text-leise);
}

.titel {
  font-size: 14px;
  fill: var(--text-leise);
}

.rechtsbuendig {
  text-anchor: end;
}

.mitte {
  text-anchor: middle;
}

.kurve {
  fill: none;
  stroke: var(--text);
  stroke-width: 3.5;
  stroke-linecap: round;
  stroke-dasharray: 1;
  stroke-dashoffset: 1;
  transition: stroke-dashoffset 1.6s ease;
}

.kurve.an {
  stroke-dashoffset: 0;
}

.beispiel {
  opacity: 0;
  transition: opacity 0.5s;
}

.beispiel.an {
  opacity: 1;
}

.hilfslinie {
  stroke: var(--text-sehr-leise);
  stroke-dasharray: 4 4;
}

.unendlich {
  fill: none;
  stroke: var(--orange);
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.liste {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.zeile {
  display: grid;
  grid-template-columns: 3.8rem 1.4rem 3.6rem 1fr;
  align-items: baseline;
  gap: 0.6rem;
  font-size: 1.2rem;
  opacity: 0;
  transform: translateX(10px);
  transition: opacity 0.5s, transform 0.5s;
}

.zeile.an {
  opacity: 1;
  transform: none;
}

.p,
.wert {
  font-family: var(--mono);
  text-align: right;
}

.wert {
  font-weight: 700;
  font-size: 1.35rem;
}

.pfeil {
  color: var(--text-sehr-leise);
  text-align: center;
}

.text {
  color: var(--text-leise);
}
</style>
