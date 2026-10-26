<!--
  Die Karte der Zeichen entsteht beim Training (echte Zwischenstände, Netz mit 2 Koordinaten).
  Klick 1: das Training läuft ab · Klick 2: Vokale markieren · Klick 3: Satzzeichen markieren
-->
<script setup lang="ts">
import { computed, ref, shallowRef, watch } from 'vue'
import { useIsSlideActive, useSlideContext } from '@slidev/client'
import { pause, zahl, zeigeZeichen } from '../logik/modell'
import { ladeJson } from '../logik/netz'

type Karte = { zeichen: string[], staende: number[][][], messungen: { schritt: number, training: number, test: number }[] }

const VOKALE = new Set('aeiouäöü')
const SATZZEICHEN = new Set('.,:;!?-')
const B = 620
const H = 470

const { $clicks } = useSlideContext()
const aktiv = useIsSlideActive()
const karte = shallowRef<Karte | null>(null)
const stand = ref(0)
let lauf = 0

ladeJson<Karte>('netz_karte.json').then(d => karte.value = d)

// Feste Achsen aus dem letzten Stand, damit die Karte am Ende den Platz gut nutzt
const grenzen = computed(() => {
  if (!karte.value)
    return { x: [-1, 1], y: [-1, 1] }
  const ende = karte.value.staende[karte.value.staende.length - 1]
  const xs = ende.map(p => p[0])
  const ys = ende.map(p => p[1])
  return { x: [Math.min(...xs) - 0.4, Math.max(...xs) + 0.4], y: [Math.min(...ys) - 0.4, Math.max(...ys) + 0.4] }
})
const px = (x: number) => 20 + ((x - grenzen.value.x[0]) / (grenzen.value.x[1] - grenzen.value.x[0])) * (B - 40)
const py = (y: number) => H - 20 - ((y - grenzen.value.y[0]) / (grenzen.value.y[1] - grenzen.value.y[0])) * (H - 40)

const punkte = computed(() => {
  if (!karte.value)
    return []
  return karte.value.staende[stand.value].map((p, i) => {
    const z = karte.value!.zeichen[i]
    return { z, x: px(p[0]), y: py(p[1]), art: VOKALE.has(z) ? 'vokal' : SATZZEICHEN.has(z) ? 'satz' : 'sonst' }
  })
})
const messung = computed(() => karte.value?.messungen[stand.value])

watch([$clicks, aktiv, karte], async ([klicks, jetzt]) => {
  const meinLauf = ++lauf
  if (!jetzt || !karte.value)
    return
  if (klicks === 0) {
    stand.value = 0
    return
  }
  if (klicks >= 1 && stand.value < karte.value.staende.length - 1) {
    while (stand.value < karte.value.staende.length - 1 && meinLauf === lauf) {
      stand.value++
      await pause(stand.value < 20 ? 220 : 90)
    }
  }
}, { immediate: true })
</script>

<template>
  <div v-if="karte" class="karte-entsteht">
    <svg :width="B" :height="H" class="flaeche">
      <g
        v-for="p in punkte" :key="p.z" class="zeichen"
        :class="[p.art, { hervor: ($clicks >= 2 && p.art === 'vokal') || ($clicks >= 3 && p.art === 'satz'), leise: $clicks >= 2 && !(($clicks >= 2 && p.art === 'vokal') || ($clicks >= 3 && p.art === 'satz')) }]"
        :style="{ transform: `translate(${p.x}px, ${p.y}px)` }"
      >
        <rect x="-15" y="-15" width="30" height="30" rx="7" />
        <text y="6">{{ zeigeZeichen(p.z) }}</text>
      </g>
    </svg>
    <div class="seite">
      <div class="beschriftung">Training</div>
      <div class="zahl-gross">{{ zahl(messung?.schritt ?? 0) }}</div>
      <div class="klein">Lernschritte</div>
      <div class="beschriftung mt">Verlust</div>
      <div class="zahl-gross orange">{{ zahl(messung?.training ?? 0, 2) }}</div>
      <div class="legende">
        <span class="vokal-farbe" :class="{ an: $clicks >= 2 }">Vokale</span>
        <span class="satz-farbe" :class="{ an: $clicks >= 3 }">Satzzeichen</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.karte-entsteht {
  display: flex;
  gap: 2rem;
  align-items: center;
  margin-top: 0.6rem;
}

.flaeche {
  border-radius: 16px;
  background: var(--flaeche);
  box-shadow: 0 0 0 1px var(--linie), var(--schatten);
}

.zeichen {
  transition: transform 0.25s linear, opacity 0.5s;
}

.zeichen rect {
  fill: var(--flaeche-hell);
  stroke: var(--linie);
  stroke-width: 1.5;
  transition: fill 0.5s, stroke 0.5s;
}

.zeichen text {
  font-family: var(--mono);
  font-size: 17px;
  text-anchor: middle;
}

.zeichen.leise {
  opacity: 0.3;
}

.zeichen.vokal.hervor rect {
  fill: var(--orange);
  stroke: var(--orange);
}

.zeichen.satz.hervor rect {
  fill: var(--blau);
  stroke: var(--blau);
}

.zeichen.hervor text {
  fill: #fff;
  font-weight: 700;
}

.seite {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.mt {
  margin-top: 1.2rem;
}

.zahl-gross {
  font-family: var(--mono);
  font-size: 2.6rem;
  font-weight: 700;
}

.orange {
  color: var(--orange);
}

.klein {
  color: var(--text-leise);
}

.legende {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1.6rem;
  font-size: 1.1rem;
  font-weight: 650;
}

.legende span {
  opacity: 0;
  transition: opacity 0.5s;
}

.legende span.an {
  opacity: 1;
}

.vokal-farbe {
  color: var(--orange);
}

.satz-farbe {
  color: var(--blau);
}
</style>
