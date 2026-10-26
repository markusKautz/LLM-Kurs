<!--
  Das Bigramm-Netz aus Notebook 2 lernt live im Browser auf dem Märchentext.
  Es startet mit lauter Nullen (alle Zeichen gleich wahrscheinlich) und findet die Zählung von selbst.
  Klick 1: Training läuft · Klick 2: Vergleich mit der Zählung
-->
<script setup lang="ts">
import { computed, ref, shallowRef, watch } from 'vue'
import { useIsSlideActive, useSlideContext } from '@slidev/client'
import type { Kennzahlen } from '../logik/modell'
import { ladeKennzahlen, pause, zahl } from '../logik/modell'
import { softmax } from '../logik/netz'

const SCHRITTE = 200
const LERNRATE = 50
const FELD = 7.5

const { $clicks } = useSlideContext()
const aktiv = useIsSlideActive()
const daten = shallowRef<Kennzahlen | null>(null)
const W = shallowRef<number[][]>([])
const verluste = ref<number[]>([])
const schritt = ref(0)
let lauf = 0

const V = computed(() => daten.value?.zeichen.length ?? 0)
const gesamt = computed(() => daten.value?.bigramme.flat().reduce((a, b) => a + b, 0) ?? 1)
const gezaehlt = computed(() => daten.value?.bigramme.map((zeile) => {
  const s = zeile.reduce((a, b) => a + b, 0) || 1
  return zeile.map(v => v / s)
}) ?? [])
const gezaehltVerlust = computed(() => {
  if (!daten.value)
    return 0
  let summe = 0
  daten.value.bigramme.forEach((zeile, a) => zeile.forEach((n, b) => { if (n) summe -= n * Math.log(gezaehlt.value[a][b]) }))
  return summe / gesamt.value
})
const gelernt = computed(() => W.value.map(zeile => softmax(zeile)))

function neu() {
  W.value = Array.from({ length: V.value }, () => Array.from({ length: V.value }, () => 0))
  verluste.value = [Math.log(V.value)]
  schritt.value = 0
}

// Ein Lernschritt über den ganzen Text: Gradient = (Vorhersage − Wahrheit), gewichtet mit den Zählern
function lernschritt() {
  const N = daten.value!.bigramme
  let verlust = 0
  const neuW = W.value.map((zeile, a) => {
    const p = softmax(zeile)
    const na = N[a].reduce((x, y) => x + y, 0)
    N[a].forEach((n, b) => { if (n) verlust -= n * Math.log(p[b]) })
    return zeile.map((w, b) => w - LERNRATE * (na * p[b] - N[a][b]) / gesamt.value)
  })
  W.value = neuW
  verluste.value = [...verluste.value, verlust / gesamt.value]
  schritt.value++
}

ladeKennzahlen().then((d) => {
  daten.value = d
  neu()
})

watch([$clicks, aktiv, daten], async ([klicks, jetzt]) => {
  const meinLauf = ++lauf
  if (!jetzt || !daten.value)
    return
  if (klicks === 0)
    neu()
  if (klicks >= 1 && schritt.value === 0) {
    while (schritt.value < SCHRITTE && meinLauf === lauf) {
      lernschritt()
      await pause(schritt.value < 15 ? 160 : 25)
    }
  }
}, { immediate: true })

// Verlustkurve
const KB = 380
const KH = 200
const kx = (s: number) => 40 + (s / SCHRITTE) * (KB - 50)
const ky = (v: number) => 10 + ((3.8 - v) / (3.8 - 2.0)) * (KH - 40)
const kurve = computed(() => verluste.value.map((v, s) => `${kx(s).toFixed(1)},${ky(v).toFixed(1)}`).join(' '))
const farbe = (p: number) => `rgba(42, 120, 214, ${(0.06 + 0.94 * Math.sqrt(p)).toFixed(3)})`
</script>

<template>
  <div v-if="daten" class="lernt">
    <div class="matrix-block">
      <div class="beschriftung">Das Netz: Softmax(W), Schritt {{ schritt }}</div>
      <svg :width="FELD * V" :height="FELD * V">
        <template v-for="(zeile, a) in gelernt" :key="a">
          <rect v-for="(p, b) in zeile" :key="b" :x="b * FELD" :y="a * FELD" :width="FELD - 0.6" :height="FELD - 0.6" :fill="farbe(p)" />
        </template>
      </svg>
    </div>

    <div class="mitte">
      <div class="beschriftung">Verlust</div>
      <svg :width="KB" :height="KH">
        <line :x1="kx(0)" :x2="kx(SCHRITTE)" :y1="ky(gezaehltVerlust)" :y2="ky(gezaehltVerlust)" class="ziel" :class="{ an: $clicks >= 2 }" />
        <text :x="kx(SCHRITTE)" :y="ky(gezaehltVerlust) + 18" class="ziel-text" :class="{ an: $clicks >= 2 }">Zählen: {{ zahl(gezaehltVerlust, 2) }}</text>
        <line :x1="kx(0)" :x2="kx(0)" :y1="ky(3.8)" :y2="ky(2)" class="achse" />
        <line :x1="kx(0)" :x2="kx(SCHRITTE)" :y1="ky(2)" :y2="ky(2)" class="achse" />
        <text v-for="v in [2, 2.5, 3, 3.5]" :key="v" :x="kx(0) - 8" :y="ky(v) + 4" class="zahl">{{ zahl(v, 1) }}</text>
        <polyline :points="kurve" class="kurve" />
      </svg>
      <div class="stand">
        <span>Schritt <b>{{ schritt }}</b></span>
        <span>Verlust <b class="orange">{{ zahl(verluste[verluste.length - 1] ?? 0, 2) }}</b></span>
      </div>
    </div>

    <div class="matrix-block vergleich" :class="{ an: $clicks >= 2 }">
      <div class="beschriftung">Zum Vergleich: gezählt</div>
      <svg :width="FELD * V" :height="FELD * V">
        <template v-for="(zeile, a) in gezaehlt" :key="a">
          <rect v-for="(p, b) in zeile" :key="b" :x="b * FELD" :y="a * FELD" :width="FELD - 0.6" :height="FELD - 0.6" :fill="farbe(p)" />
        </template>
      </svg>
    </div>
  </div>
</template>

<style scoped>
.lernt {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  margin-top: 1.6rem;
}

.matrix-block {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.matrix-block svg {
  border-radius: 6px;
  box-shadow: 0 0 0 1px var(--linie);
}

.vergleich {
  opacity: 0;
  transition: opacity 0.8s;
}

.vergleich.an {
  opacity: 1;
}

.mitte {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.achse {
  stroke: var(--text-leise);
  stroke-width: 1.2;
}

.zahl {
  font-family: var(--mono);
  font-size: 12px;
  fill: var(--text-leise);
  text-anchor: end;
}

.kurve {
  fill: none;
  stroke: var(--orange);
  stroke-width: 3;
  stroke-linejoin: round;
}

.ziel,
.ziel-text {
  opacity: 0;
  transition: opacity 0.6s;
}

.ziel.an,
.ziel-text.an {
  opacity: 1;
}

.ziel {
  stroke: var(--text);
  stroke-dasharray: 5 5;
}

.ziel-text {
  font-family: var(--mono);
  font-size: 13px;
  fill: var(--text);
  text-anchor: end;
}

.stand {
  display: flex;
  gap: 1.6rem;
  font-family: var(--mono);
  font-size: 1.1rem;
}

.orange {
  color: var(--orange);
}
</style>
