<!--
  Das ganze Zeichen-Netz, live gerechnet mit den trainierten Gewichten.
  Jeder Klick schickt einen anderen Kontext durch das Netz.
-->
<script setup lang="ts">
import { computed, shallowRef } from 'vue'
import { useSlideContext } from '@slidev/client'
import { zahl, zeigeZeichen } from '../logik/modell'
import type { NetzDaten } from '../logik/netz'
import { durchlauf, ladeNetz } from '../logik/netz'

const props = withDefaults(defineProps<{ kontexte?: string[] }>(), { kontexte: () => ['kön', 'er ', 'sch', 'hnc'] })

const { $clicks } = useSlideContext()
const netz = shallowRef<NetzDaten | null>(null)
ladeNetz().then(n => netz.value = n)

const kontext = computed(() => props.kontexte[Math.min(Math.max($clicks.value - 1, 0), props.kontexte.length - 1)])
const lauf = computed(() => netz.value ? durchlauf(netz.value, kontext.value) : null)
const oben = computed(() => {
  if (!lauf.value || !netz.value)
    return []
  return lauf.value.wahrscheinlichkeiten.map((p, i) => ({ z: netz.value!.zeichen[i], p })).sort((a, b) => b.p - a.p).slice(0, 6)
})
const groessteAktivitaet = computed(() => Math.max(...(lauf.value?.neuronen ?? [1]), 0.01))
const aktive = computed(() => lauf.value?.neuronen.filter(v => v > 0).length ?? 0)
const fuellung = (v: number, max: number) => `rgba(42, 120, 214, ${(Math.min(Math.abs(v) / max, 1) * 0.9 + 0.08).toFixed(3)})`
</script>

<template>
  <div v-if="netz && lauf" class="fluss" :class="{ an: $clicks >= 1 }">
    <!-- 1. Kontext -->
    <div class="stufe">
      <div class="beschriftung">3 Zeichen</div>
      <div class="kontext">
        <span v-for="(z, i) in kontext" :key="`${kontext}-${i}`" class="zk gross">{{ zeigeZeichen(z) }}</span>
      </div>
    </div>
    <div class="pfeil">→</div>

    <!-- 2. Einbettung -->
    <div class="stufe">
      <div class="beschriftung">Koordinaten</div>
      <div class="einbettung">
        <div v-for="g in 3" :key="g" class="gruppe">
          <span v-for="k in 10" :key="k" class="zelle" :style="{ background: fuellung(lauf.eingabe[(g - 1) * 10 + k - 1], 2) }" />
        </div>
      </div>
      <div class="klein">3 × 10 Zahlen</div>
    </div>
    <div class="pfeil">→</div>

    <!-- 3. Neuronen -->
    <div class="stufe">
      <div class="beschriftung">200 Neuronen mit ReLU</div>
      <div class="neuronen">
        <span
          v-for="(v, i) in lauf.neuronen" :key="i" class="neuron"
          :class="{ aus: v === 0 }" :style="{ background: v > 0 ? fuellung(v, groessteAktivitaet) : undefined }"
        />
      </div>
      <div class="klein"><b>{{ aktive }}</b> aktiv, der Rest durch ReLU auf 0</div>
    </div>
    <div class="pfeil">→</div>

    <!-- 4. Ausgabe -->
    <div class="stufe">
      <div class="beschriftung">Softmax: nächstes Zeichen</div>
      <div class="ausgabe">
        <div v-for="(e, i) in oben" :key="`${kontext}-${e.z}`" class="eintrag" :style="{ animationDelay: `${i * 60}ms` }">
          <span class="zk">{{ zeigeZeichen(e.z) }}</span>
          <span class="spur"><span :style="{ width: `${e.p * 100}%` }" /></span>
          <span class="prozent">{{ zahl(e.p * 100) }} %</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.fluss {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
  margin-top: 2rem;
  opacity: 0.2;
  transition: opacity 0.6s;
}

.fluss.an {
  opacity: 1;
}

.stufe {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.6rem;
}

.pfeil {
  font-size: 2rem;
  color: var(--text-sehr-leise);
}

.kontext {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.zk.gross {
  min-width: 3rem;
  height: 3rem;
  font-size: 1.6rem;
  animation: herein 0.5s ease;
}

@keyframes herein {
  from { opacity: 0; transform: scale(0.7); }
}

.einbettung {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.gruppe {
  display: flex;
  gap: 2px;
}

.zelle {
  width: 14px;
  height: 36px;
  border-radius: 3px;
  transition: background 0.6s;
}

.klein {
  font-size: 0.85rem;
  color: var(--text-leise);
  text-align: center;
}

.neuronen {
  display: grid;
  grid-template-columns: repeat(20, 12px);
  gap: 3px;
}

.neuron {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  transition: background 0.6s;
}

.neuron.aus {
  background: var(--flaeche-hell);
}

.ausgabe {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  width: 17rem;
}

.eintrag {
  display: grid;
  grid-template-columns: 2.4rem 1fr 3.6rem;
  align-items: center;
  gap: 0.6rem;
  animation: herein 0.5s ease backwards;
}

.spur {
  height: 0.7rem;
  border-radius: 5px;
  background: var(--flaeche-hell);
  overflow: hidden;
}

.spur span {
  display: block;
  height: 100%;
  border-radius: 5px;
  background: var(--orange);
}

.prozent {
  font-family: var(--mono);
  text-align: right;
  color: var(--text-leise);
}
</style>
