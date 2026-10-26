<!--
  Shannons Experiment von 1948, nachgebaut mit den Märchen:
  Je mehr Zeichen das Modell zurückschaut, desto mehr klingt der Text nach Deutsch.
  Jeder Klick zeigt eine weitere Zeile mit einem Zeichen mehr Kontext.
-->
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useIsSlideActive, useSlideContext } from '@slidev/client'
import { erzeuge, ladeModell, pause } from '../logik/modell'

const props = withDefaults(defineProps<{ bis?: number, laenge?: number }>(), { bis: 5, laenge: 62 })

const stufen = Array.from({ length: props.bis + 1 }, (_, n) => n)
const BESCHREIBUNG = ['nur Häufigkeit', '1 Zeichen zurück', '2 Zeichen zurück', '3 Zeichen zurück', '4 Zeichen zurück', '5 Zeichen zurück', '6 Zeichen zurück']

const { $clicks } = useSlideContext()
const aktiv = useIsSlideActive()
const texte = ref<string[]>(stufen.map(() => ''))
const fertig = ref<boolean[]>(stufen.map(() => false))
let lauf = 0

async function schreibe(n: number, meinLauf: number) {
  if (fertig.value[n])
    return
  const modell = await ladeModell(n)
  // Der Start gibt dem Modell genug Kontext. Bei n = 0 gibt es keinen Kontext.
  const start = 'es war einmal '
  const ganz = erzeuge(modell, start, props.laenge, n).replace(/\n/g, ' ').slice(start.length)
  for (let i = 1; i <= ganz.length; i++) {
    if (meinLauf !== lauf)
      return
    texte.value[n] = ganz.slice(0, i)
    await pause(22)
  }
  fertig.value[n] = true
}

watch([$clicks, aktiv], async ([klicks, jetzt]) => {
  const meinLauf = ++lauf
  if (!jetzt)
    return
  for (const n of stufen) {
    if (n < klicks)
      await schreibe(n, meinLauf)
    else {
      texte.value[n] = ''
      fertig.value[n] = false
    }
  }
}, { immediate: true })
</script>

<template>
  <div class="treppe">
    <div v-for="n in stufen" :key="n" class="stufe" :class="{ an: n < $clicks }">
      <div class="links">
        <div class="n">n = {{ n }}</div>
        <div class="was">{{ BESCHREIBUNG[n] }}</div>
      </div>
      <div class="text">{{ texte[n] }}</div>
    </div>
  </div>
</template>

<style scoped>
.treppe {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  margin-top: 1.3rem;
}

.stufe {
  display: grid;
  grid-template-columns: 11rem 1fr;
  align-items: center;
  gap: 1.2rem;
  min-height: 3.7rem;
  padding: 0.5rem 1.1rem;
  border-radius: 12px;
  background: var(--flaeche);
  border: 1px solid var(--linie);
  opacity: 0.3;
  transition: opacity 0.5s, box-shadow 0.5s;
}

.stufe.an {
  opacity: 1;
  box-shadow: var(--schatten);
}

.n {
  font-family: var(--mono);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--blau);
}

.was {
  font-size: 0.85rem;
  color: var(--text-leise);
}

.text {
  font-family: var(--mono);
  font-size: 1.15rem;
  white-space: pre;
  overflow: hidden;
}
</style>
