<!--
  Der Verlust für jedes Zeichen eines Satzes, mit einem Modell, das 2 Zeichen zurückschaut.
  Klick 1: die Balken erscheinen Zeichen für Zeichen
  Klick 2: der Durchschnitt
-->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { useSlideContext } from '@slidev/client'
import type { Zaehler } from '../logik/modell'
import { ladeModell, zahl, zeigeZeichen } from '../logik/modell'

const props = withDefaults(defineProps<{ satz?: string, n?: number }>(), { satz: 'der könig sprach', n: 2 })

const HOEHE = 210
const Y_MAX = 3.5

const { $clicks } = useSlideContext()
const modell = ref<Zaehler | null>(null)
ladeModell(props.n).then(m => modell.value = m)

const spalten = computed(() => {
  if (!modell.value)
    return []
  return [...props.satz].map((z, i) => {
    if (i < props.n)
      return { z, kontext: '', p: null as number | null, verlust: 0 }
    const zaehler = modell.value![props.satz.slice(i - props.n, i)] ?? {}
    const summe = Object.values(zaehler).reduce((a, b) => a + b, 0)
    const p = summe ? (zaehler[z] ?? 0) / summe : 0
    return { z, kontext: props.satz.slice(i - props.n, i), p, verlust: -Math.log(p) }
  })
})
const gewertet = computed(() => spalten.value.filter(s => s.p !== null))
const durchschnitt = computed(() => gewertet.value.reduce((a, s) => a + s.verlust, 0) / (gewertet.value.length || 1))
const hoehe = (v: number) => Math.min(v / Y_MAX, 1) * HOEHE
</script>

<template>
  <div class="beispiel">
    <div class="diagramm" :style="{ height: `${HOEHE}px` }">
      <div class="mittel" :class="{ an: $clicks >= 2 }" :style="{ bottom: `${hoehe(durchschnitt)}px` }">
        <span>Durchschnitt: {{ zahl(durchschnitt, 2) }}</span>
      </div>
      <div v-for="(s, i) in spalten" :key="i" class="spalte">
        <div
          v-if="s.p !== null" class="balken" :class="{ hoch: s.verlust > 2 }"
          :style="{ height: $clicks >= 1 ? `${hoehe(s.verlust)}px` : '0px', transitionDelay: `${i * 150}ms` }"
        >
          <span class="wert" :class="{ an: $clicks >= 1 }" :style="{ transitionDelay: `${i * 150 + 300}ms` }">{{ zahl(s.verlust, 1) }}</span>
        </div>
      </div>
    </div>
    <div class="zeichen">
      <div v-for="(s, i) in spalten" :key="i" class="spalte">
        <span class="zk" :class="{ start: s.p === null }">{{ zeigeZeichen(s.z) }}</span>
        <span v-if="s.p !== null" class="p" :class="{ an: $clicks >= 1 }" :style="{ transitionDelay: `${i * 150 + 300}ms` }">{{ zahl(s.p * 100) }} %</span>
        <span v-else class="p an leise">Start</span>
      </div>
    </div>
    <div class="legende">
      <span><b>oben:</b> Verlust</span>
      <span><b>unten:</b> Wahrscheinlichkeit, die das Modell dem richtigen Zeichen gab</span>
      <span class="leise">Modell: {{ props.n }} Zeichen zurück</span>
    </div>
  </div>
</template>

<style scoped>
.beispiel {
  margin-top: 2.2rem;
}

.diagramm,
.zeichen {
  position: relative;
  display: flex;
  gap: 0.4rem;
}

.diagramm {
  align-items: flex-end;
  border-bottom: 2px solid var(--linie);
}

.spalte {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.balken {
  position: relative;
  width: 100%;
  border-radius: 6px 6px 0 0;
  background: linear-gradient(to top, var(--blau-tief), var(--blau));
  transition: height 0.7s cubic-bezier(.2, .8, .2, 1);
}

.balken.hoch {
  background: linear-gradient(to top, var(--orange-tief), var(--orange));
}

.wert {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  margin-bottom: 0.3rem;
  text-align: center;
  font-family: var(--mono);
  font-size: 0.9rem;
  color: var(--text-leise);
  opacity: 0;
  transition: opacity 0.4s;
}

.zeichen {
  margin-top: 0.6rem;
}

.zk {
  width: 100%;
  font-size: 1.35rem;
}

.zk.start {
  color: var(--text-sehr-leise);
  border-style: dashed;
  background: transparent;
}

.p {
  margin-top: 0.4rem;
  font-family: var(--mono);
  font-size: 0.8rem;
  color: var(--text-leise);
  opacity: 0;
  transition: opacity 0.4s;
}

.wert.an,
.p.an {
  opacity: 1;
}

.leise {
  color: var(--text-sehr-leise);
}

.mittel {
  position: absolute;
  left: 0;
  right: 0;
  border-top: 2.5px dashed var(--orange);
  opacity: 0;
  z-index: 1;
  transition: opacity 0.6s;
}

.mittel.an {
  opacity: 1;
}

.mittel span {
  position: absolute;
  right: 0;
  bottom: 0.3rem;
  padding: 0.15rem 0.6rem;
  border-radius: 6px;
  background: var(--orange);
  color: #fff;
  font-family: var(--mono);
  font-size: 1rem;
  font-weight: 700;
}

.legende {
  display: flex;
  gap: 2rem;
  margin-top: 1.4rem;
  font-size: 0.95rem;
  color: var(--text-leise);
}
</style>
