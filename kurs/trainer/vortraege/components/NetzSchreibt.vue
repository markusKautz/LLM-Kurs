<!--
  Das Netz schreibt, live mit den trainierten Gewichten. Dazu die Testverluste aller Modelle.
  Klick 1: das Netz schreibt · Klick 2: Vergleich der Testverluste
-->
<script setup lang="ts">
import { ref, shallowRef, watch } from 'vue'
import { useIsSlideActive, useSlideContext } from '@slidev/client'
import { pause, zahl } from '../logik/modell'
import type { NetzDaten } from '../logik/netz'
import { ladeJson, ladeNetz, netzErzeuge } from '../logik/netz'

const { $clicks } = useSlideContext()
const aktiv = useIsSlideActive()
const netz = shallowRef<NetzDaten | null>(null)
const text = ref('')
const verluste = ref<{ name: string, test: number | null }[]>([])
let lauf = 0

ladeNetz().then(n => netz.value = n)
ladeJson<{ verluste: { name: string, test: number | null }[] }>('vergleich.json').then(d => verluste.value = d.verluste)

watch([$clicks, aktiv, netz], async ([klicks, jetzt]) => {
  const meinLauf = ++lauf
  if (!jetzt || !netz.value)
    return
  if (klicks === 0)
    text.value = ''
  if (klicks === 1) {
    const ganz = netzErzeuge(netz.value, 'es war einmal ', 330).replace(/\n/g, ' ')
    for (let i = 14; i <= ganz.length && meinLauf === lauf; i++) {
      text.value = ganz.slice(0, i)
      await pause(24)
    }
  }
}, { immediate: true })

const MAX = 3
</script>

<template>
  <div class="schreibt">
    <div class="text karte" :class="{ an: $clicks >= 1 }">
      <div class="beschriftung">live erzeugt vom Netz: 3 Zeichen Kontext, 10 Koordinaten, 200 Neuronen</div>
      <div class="inhalt">{{ text }}<span v-if="$clicks === 1" class="cursor" /></div>
    </div>
    <div class="tabelle karte" :class="{ an: $clicks >= 2 }">
      <div class="beschriftung">Verlust auf dem Testtext der Märchen</div>
      <div v-for="(v, i) in verluste" :key="i" class="zeile">
        <span class="name">{{ v.name }}</span>
        <span v-if="v.test !== null" class="spur"><span :style="{ width: $clicks >= 2 ? `${(v.test / MAX) * 100}%` : '0%', transitionDelay: `${i * 200}ms` }" :class="{ bestes: i === verluste.length - 1 }" /></span>
        <span v-else class="spur unendlich-spur" />
        <b :class="{ unendlich: v.test === null, bestes: i === verluste.length - 1 }">{{ v.test === null ? 'unendlich' : zahl(v.test, 2) }}</b>
      </div>
      <div class="klein">Das Bigramm-Netz lernt dasselbe wie das Zählen, gibt aber nie 0. Das Zeichen-Netz sieht 3 Zeichen und ist klar besser.</div>
    </div>
  </div>
</template>

<style scoped>
.schreibt {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 1.6rem;
  margin-top: 1.2rem;
}

.text,
.tabelle {
  padding: 1.1rem 1.4rem;
  opacity: 0.15;
  transition: opacity 0.6s;
}

.text.an,
.tabelle.an {
  opacity: 1;
}

.inhalt {
  margin-top: 0.6rem;
  font-family: var(--mono);
  font-size: 1.15rem;
  line-height: 1.65;
  min-height: 18rem;
}

.cursor {
  display: inline-block;
  width: 0.55em;
  height: 1em;
  vertical-align: -0.15em;
  background: var(--orange);
  border-radius: 2px;
}

.zeile {
  display: grid;
  grid-template-columns: 11rem 1fr 6rem;
  align-items: center;
  gap: 0.8rem;
  margin-top: 1rem;
}

.name {
  font-size: 1.05rem;
}

.spur {
  height: 0.8rem;
  border-radius: 5px;
  background: var(--flaeche-hell);
  overflow: hidden;
}

.spur span {
  display: block;
  height: 100%;
  border-radius: 5px;
  background: var(--text-sehr-leise);
  transition: width 0.9s cubic-bezier(.2, .8, .2, 1);
}

.spur span.bestes {
  background: var(--blau);
}

.unendlich-spur {
  background: repeating-linear-gradient(90deg, var(--orange-hauch) 0 8px, transparent 8px 14px);
}

b {
  font-family: var(--mono);
  font-size: 1.15rem;
  text-align: right;
}

.unendlich {
  color: var(--orange);
}

b.bestes {
  color: var(--blau);
}

.klein {
  margin-top: 1.2rem;
  font-size: 0.95rem;
  line-height: 1.45;
  color: var(--text-leise);
}
</style>
