<!--
  Minibatches: Statt alle 430.000 Beispiele für jeden Lernschritt zu verwenden, nur eine kleine Zufallsauswahl.
  Klick 1: Zufallsauswahl läuft · Klick 2: die echte Lernkurve (wackelig, aber bergab)
-->
<script setup lang="ts">
import { computed, ref, shallowRef, watch } from 'vue'
import { useIsSlideActive, useSlideContext } from '@slidev/client'
import { pause, zahl } from '../logik/modell'
import { ladeJson } from '../logik/netz'

const PUNKTE = 600
const AUSWAHL = 32

const { $clicks } = useSlideContext()
const aktiv = useIsSlideActive()
const gewaehlt = ref<Set<number>>(new Set())
const runden = ref(0)
const stapel = shallowRef<number[]>([])
const sichtbar = ref(0)
let lauf = 0

ladeJson<{ stapel: number[] }>('netz_karte.json').then(d => stapel.value = d.stapel)

function ziehe() {
  const neu = new Set<number>()
  while (neu.size < AUSWAHL)
    neu.add(Math.floor(Math.random() * PUNKTE))
  gewaehlt.value = neu
  runden.value++
}

// Lernkurve aus dem echten Training: Verlust jedes 10. Minibatches
const KB = 520
const KH = 260
const kurve = computed(() => {
  const werte = stapel.value.slice(0, sichtbar.value)
  return werte.map((v, i) => `${(40 + (i / stapel.value.length) * (KB - 50)).toFixed(1)},${(KH - 30 - ((Math.min(v, 4) - 1) / 3) * (KH - 50)).toFixed(1)}`).join(' ')
})

watch([$clicks, aktiv], async ([klicks, jetzt]) => {
  const meinLauf = ++lauf
  if (!jetzt)
    return
  if (klicks === 0) {
    gewaehlt.value = new Set()
    runden.value = 0
    sichtbar.value = 0
  }
  if (klicks === 1) {
    while (meinLauf === lauf) {
      ziehe()
      await pause(runden.value < 4 ? 1100 : 350)
    }
  }
  if (klicks >= 2) {
    while (sichtbar.value < stapel.value.length && meinLauf === lauf) {
      sichtbar.value = Math.min(sichtbar.value + 25, stapel.value.length)
      ziehe()
      await pause(40)
    }
  }
}, { immediate: true })
</script>

<template>
  <div class="minibatch">
    <div class="links">
      <div class="beschriftung">alle Trainingsbeispiele (jeder Punkt steht für ~700)</div>
      <div class="raster">
        <span v-for="i in PUNKTE" :key="i" class="punkt" :class="{ an: gewaehlt.has(i - 1) }" />
      </div>
      <div class="info">
        <span><b class="orange">{{ AUSWAHL }}</b> zufällige Beispiele pro Lernschritt</span>
        <span v-if="runden">Minibatch Nr. <b>{{ zahl(runden) }}</b></span>
      </div>
    </div>
    <div class="rechts" :class="{ an: $clicks >= 2 }">
      <div class="beschriftung">Verlust pro Minibatch, echtes Training</div>
      <svg :width="KB" :height="KH">
        <line x1="40" :x2="KB - 10" :y1="KH - 30" :y2="KH - 30" class="achse" />
        <line x1="40" x2="40" y1="10" :y2="KH - 30" class="achse" />
        <text v-for="v in [1, 2, 3, 4]" :key="v" x="32" :y="KH - 30 - ((v - 1) / 3) * (KH - 50) + 4" class="zahl">{{ v }}</text>
        <polyline :points="kurve" class="kurve" />
      </svg>
      <div class="klein">wackelt, weil jeder Minibatch andere Beispiele hat, geht aber im Mittel bergab</div>
    </div>
  </div>
</template>

<style scoped>
.minibatch {
  display: grid;
  grid-template-columns: 1fr 540px;
  gap: 2.2rem;
  margin-top: 1.2rem;
}

.links,
.rechts {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}

.raster {
  display: grid;
  grid-template-columns: repeat(30, 1fr);
  gap: 4px;
}

.punkt {
  aspect-ratio: 1;
  border-radius: 50%;
  background: var(--linie);
  transition: background 0.15s, transform 0.15s;
}

.punkt.an {
  background: var(--orange);
  transform: scale(1.4);
}

.info {
  display: flex;
  justify-content: space-between;
  font-size: 1.05rem;
  color: var(--text-leise);
}

.info b {
  font-family: var(--mono);
  color: var(--text);
}

.orange,
.info b.orange {
  color: var(--orange);
}

.rechts {
  opacity: 0;
  transition: opacity 0.6s;
}

.rechts.an {
  opacity: 1;
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

.kurve {
  fill: none;
  stroke: var(--blau);
  stroke-width: 1.2;
  opacity: 0.85;
}

.klein {
  font-size: 0.95rem;
  color: var(--text-leise);
}
</style>
