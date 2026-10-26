<!--
  Markows Experiment von 1913, nachgestellt mit den Märchen:
  Folgt auf einen Vokal eher ein Vokal oder ein Konsonant?

  Klick 1: ein Satz wird Buchstabe für Buchstabe gezählt
  Klick 2: im Zeitraffer der ganze Märchentext
  Klick 3: aus den Zählern werden Anteile
-->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useIsSlideActive, useSlideContext } from '@slidev/client'
import type { Kennzahlen } from '../logik/modell'
import { ladeKennzahlen, pause, zahl } from '../logik/modell'

const SATZ = 'es war einmal ein könig, der hatte drei töchter.'
const VOKALE = new Set('aeiouäöü')

const { $clicks } = useSlideContext()
const aktiv = useIsSlideActive()

const position = ref(-1)
const zaehler = ref({ VV: 0, VK: 0, KV: 0, KK: 0 })
const buchstaben = ref(0)
const leuchtet = ref('')
let daten: Kennzahlen | null = null
let lauf = 0

const art = (z: string) => VOKALE.has(z) ? 'V' : /\p{L}/u.test(z) ? 'K' : ''
// Die Buchstaben des Satzes mit ihrer Position, Satzzeichen und Leerzeichen zählen nicht
const satzBuchstaben = [...SATZ].map((z, i) => ({ z, i, art: art(z) })).filter(b => b.art)

function anteil(von: 'V' | 'K', nach: 'V' | 'K') {
  const zeile = zaehler.value[`${von}V`] + zaehler.value[`${von}K`]
  return zeile ? zaehler.value[`${von}${nach}`] / zeile : 0
}

async function satzZaehlen(meinLauf: number) {
  zaehler.value = { VV: 0, VK: 0, KV: 0, KK: 0 }
  buchstaben.value = 0
  for (let k = 0; k < satzBuchstaben.length; k++) {
    if (meinLauf !== lauf)
      return
    position.value = satzBuchstaben[k].i
    buchstaben.value = k + 1
    if (k > 0) {
      const paar = (satzBuchstaben[k - 1].art + satzBuchstaben[k].art) as keyof typeof zaehler.value
      zaehler.value[paar]++
      leuchtet.value = paar
    }
    await pause(330)
  }
  position.value = -1
  leuchtet.value = ''
}

async function zeitraffer(meinLauf: number) {
  daten ??= await ladeKennzahlen()
  const start = { ...zaehler.value }
  const startBuchstaben = buchstaben.value
  const ziel = daten.markow
  const dauer = 3200
  const anfang = performance.now()
  position.value = -1
  while (meinLauf === lauf) {
    const t = Math.min((performance.now() - anfang) / dauer, 1)
    const f = 1 - (1 - t) ** 3
    for (const paar of ['VV', 'VK', 'KV', 'KK'] as const)
      zaehler.value[paar] = Math.round(start[paar] + (ziel[paar] - start[paar]) * f)
    buchstaben.value = Math.round(startBuchstaben + (ziel.buchstaben - startBuchstaben) * f)
    if (t === 1)
      break
    await pause(30)
  }
}

watch([$clicks, aktiv], async ([klicks, jetzt]) => {
  const meinLauf = ++lauf
  if (!jetzt)
    return
  if (klicks === 0) {
    zaehler.value = { VV: 0, VK: 0, KV: 0, KK: 0 }
    buchstaben.value = 0
    position.value = -1
  }
  else if (klicks === 1) {
    satzZaehlen(meinLauf)
  }
  else {
    zeitraffer(meinLauf)
  }
}, { immediate: true })

const zeigeAnteile = computed(() => $clicks.value >= 3)
</script>

<template>
  <div class="markow">
    <div class="satz karte">
      <div class="beschriftung">Text</div>
      <div class="zeichen">
        <span
          v-for="(z, i) in SATZ" :key="i"
          :class="[art(z) === 'V' ? 'vokal' : art(z) === 'K' ? 'konsonant' : 'sonst', { aktiv: i === position, gesehen: $clicks >= 2 || (position >= 0 && i <= position) }]"
        >{{ z }}</span>
      </div>
      <div class="legende">
        <span class="vokal">Vokal</span>
        <span class="konsonant">Konsonant</span>
        <span class="leise">Leer- und Satzzeichen überspringt Markow</span>
      </div>
      <div class="anzahl">{{ zahl(buchstaben) }} Buchstaben gezählt</div>
    </div>

    <div class="tabelle karte">
      <div class="beschriftung ecke">danach →<br>vorher ↓</div>
      <div class="kopf vokal">Vokal</div>
      <div class="kopf konsonant">Konsonant</div>
      <template v-for="von in (['V', 'K'] as const)" :key="von">
        <div class="kopf" :class="von === 'V' ? 'vokal' : 'konsonant'">{{ von === 'V' ? 'Vokal' : 'Konsonant' }}</div>
        <div
          v-for="nach in (['V', 'K'] as const)" :key="nach"
          class="zelle" :class="{ leuchtet: leuchtet === von + nach }"
        >
          <div class="wert">{{ zahl(zaehler[`${von}${nach}`]) }}</div>
          <div class="anteil" :class="{ an: zeigeAnteile }">
            <div class="balken"><span :style="{ width: zeigeAnteile ? `${anteil(von, nach) * 100}%` : '0%' }" /></div>
            {{ Math.round(anteil(von, nach) * 100) }} %
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.markow {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-top: 1.4rem;
}

.satz {
  padding: 1.4rem 1.6rem;
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.zeichen {
  font-family: var(--mono);
  font-size: 1.9rem;
  line-height: 1.7;
  word-break: break-all;
}

.zeichen span {
  border-radius: 5px;
  padding: 0 1px;
  color: var(--text-sehr-leise);
  transition: color 0.25s, background 0.25s;
}

.zeichen span.gesehen.vokal {
  color: var(--orange);
}

.zeichen span.gesehen.konsonant {
  color: var(--blau);
}

.zeichen span.aktiv {
  background: var(--text);
  color: #fff !important;
}

.legende {
  display: flex;
  flex-wrap: wrap;
  gap: 1.2rem;
  font-size: 0.9rem;
}

.legende .vokal::before,
.legende .konsonant::before {
  content: "";
  display: inline-block;
  width: 0.7rem;
  height: 0.7rem;
  margin-right: 0.4rem;
  border-radius: 3px;
  background: currentColor;
}

.vokal {
  color: var(--orange);
}

.konsonant {
  color: var(--blau);
}

.leise {
  color: var(--text-sehr-leise);
}

.anzahl {
  margin-top: auto;
  font-family: var(--mono);
  font-size: 1rem;
  color: var(--text-leise);
}

.tabelle {
  display: grid;
  grid-template-columns: 7.5rem 1fr 1fr;
  grid-template-rows: 3rem 1fr 1fr;
  gap: 0.6rem;
  padding: 1.2rem;
}

.ecke {
  align-self: end;
  line-height: 1.5;
}

.kopf {
  display: grid;
  place-items: center;
  font-weight: 650;
  font-size: 1.05rem;
}

.zelle {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 0.6rem;
  border-radius: 12px;
  background: var(--flaeche-hell);
  transition: background 0.2s, box-shadow 0.2s;
}

.zelle.leuchtet {
  background: var(--orange-hauch);
  box-shadow: inset 0 0 0 2px var(--orange);
}

.wert {
  font-family: var(--mono);
  font-size: 1.7rem;
  font-weight: 650;
}

.anteil {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-family: var(--mono);
  font-size: 1.15rem;
  color: var(--orange);
  opacity: 0;
  transition: opacity 0.5s;
}

.anteil.an {
  opacity: 1;
}

.balken {
  width: 5.5rem;
  height: 0.6rem;
  border-radius: 4px;
  background: var(--flaeche);
  overflow: hidden;
}

.balken span {
  display: block;
  height: 100%;
  background: var(--orange);
  transition: width 0.9s ease;
}
</style>
