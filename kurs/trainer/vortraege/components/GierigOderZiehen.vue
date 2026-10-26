<!--
  Warum ziehen? Links nimmt das Modell immer das wahrscheinlichste Zeichen, rechts zieht es.
  Klick 1: links schreibt "gierig" und gerät in eine Schleife
  Klick 2: rechts schreibt mit Ziehen
-->
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useIsSlideActive, useSlideContext } from '@slidev/client'
import type { Zaehler } from '../logik/modell'
import { erzeuge, ladeModell, pause } from '../logik/modell'

const props = withDefaults(defineProps<{ start?: string, n?: number, laenge?: number }>(), {
  start: 'es war einmal ',
  n: 4,
  laenge: 150,
})

const { $clicks } = useSlideContext()
const aktiv = useIsSlideActive()
const links = ref('')
const rechts = ref('')
const schleife = ref('')
let modell: Zaehler | null = null
let lauf = 0

// Das kürzeste Stück am Ende, das sich direkt davor schon einmal wiederholt hat
function findeSchleife(text: string) {
  for (let laenge = 3; laenge < text.length / 2; laenge++) {
    const ende = text.slice(-laenge)
    if (text.slice(-2 * laenge, -laenge) === ende)
      return ende
  }
  return ''
}

async function tippe(ziel: typeof links, text: string, meinLauf: number) {
  ziel.value = props.start
  for (let i = props.start.length; i <= text.length; i++) {
    if (meinLauf !== lauf)
      return
    ziel.value = text.slice(0, i)
    await pause(38)
  }
}

watch([$clicks, aktiv], async ([klicks, jetzt]) => {
  const meinLauf = ++lauf
  if (!jetzt)
    return
  modell ??= await ladeModell(props.n)
  if (klicks === 0) {
    links.value = ''
    rechts.value = ''
    schleife.value = ''
  }
  if (klicks === 1) {
    rechts.value = ''
    const text = erzeuge(modell, props.start, props.laenge, props.n, true)
    schleife.value = ''
    await tippe(links, text, meinLauf)
    if (meinLauf === lauf)
      schleife.value = findeSchleife(text.trimEnd())
  }
  if (klicks === 2)
    await tippe(rechts, erzeuge(modell, props.start, props.laenge, props.n).replace(/\n/g, ' '), meinLauf)
}, { immediate: true })

// Text in Stücke teilen, damit die Wiederholungen markiert werden können
function teile(text: string) {
  if (!schleife.value)
    return [{ text, markiert: false }]
  return text.split(schleife.value).flatMap((stueck, i) => i === 0 ? [{ text: stueck, markiert: false }] : [{ text: schleife.value, markiert: true }, { text: stueck, markiert: false }])
}
</script>

<template>
  <div class="vergleich">
    <div class="spalte karte" :class="{ an: $clicks >= 1 }">
      <div class="titel">Immer das Wahrscheinlichste</div>
      <div class="text"><template v-for="(t, i) in teile(links)" :key="i"><span :class="{ markiert: t.markiert }">{{ t.text }}</span></template><span v-if="$clicks === 1" class="cursor" /></div>
      <div class="fazit schlecht" :class="{ an: schleife }">Es dreht sich im Kreis.</div>
    </div>
    <div class="spalte karte" :class="{ an: $clicks >= 2 }">
      <div class="titel">Ziehen nach Wahrscheinlichkeit</div>
      <div class="text">{{ rechts }}<span v-if="$clicks === 2" class="cursor" /></div>
      <div class="fazit gut" :class="{ an: $clicks >= 3 }">Abwechslungsreich, jedes Mal anders.</div>
    </div>
  </div>
</template>

<style scoped>
.vergleich {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-top: 1.6rem;
}

.spalte {
  display: flex;
  flex-direction: column;
  padding: 1.3rem 1.5rem;
  min-height: 23rem;
  opacity: 0.25;
  transition: opacity 0.6s;
}

.spalte.an {
  opacity: 1;
}

.titel {
  font-size: 1.25rem;
  font-weight: 650;
  margin-bottom: 1rem;
}

.text {
  font-family: var(--mono);
  font-size: 1.15rem;
  line-height: 1.65;
  white-space: pre-wrap;
}

.markiert {
  border-radius: 4px;
  background: var(--orange-hauch);
  box-shadow: inset 0 -2px 0 var(--orange);
}

.cursor {
  display: inline-block;
  width: 0.55em;
  height: 1em;
  vertical-align: -0.15em;
  background: var(--orange);
  border-radius: 2px;
}

.fazit {
  margin-top: auto;
  padding-top: 1rem;
  font-size: 1.15rem;
  font-weight: 600;
  opacity: 0;
  transition: opacity 0.6s;
}

.fazit.an {
  opacity: 1;
}

.schlecht {
  color: var(--orange);
}

.gut {
  color: var(--blau);
}
</style>
