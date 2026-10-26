<!--
  Titelfolie: Im Hintergrund schreibt ein Zählmodell (oder das trainierte Netz) live Märchentext.
  Über dem Cursor sieht man die vier wahrscheinlichsten Kandidaten und welcher gezogen wird.
-->
<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useIsSlideActive } from '@slidev/client'
import type { Eintrag, Zaehler } from '../logik/modell'
import { KONTEXT, ladeModell, verteilung, zeigeZeichen, ziehe } from '../logik/modell'
import type { NetzDaten } from '../logik/netz'
import { ladeNetz, netzVerteilung } from '../logik/netz'

const props = withDefaults(defineProps<{
  kicker?: string
  titel?: string
  untertitel?: string
  reihe?: string[]
  nummer?: number
  quelle?: 'zaehlen' | 'netz'
  legende?: string
}>(), {
  quelle: 'zaehlen',
  legende: `live erzeugt von einem Zählmodell: ${KONTEXT} Zeichen Kontext, gezählt in Grimms Märchen`,
  kicker: 'LLM-Kurs',
  titel: 'Wie schreibt eine Maschine?',
  untertitel: '',
  reihe: () => [],
  nummer: 1,
})

const START = 'es war einmal ein '
const SICHTBAR = 1600
const FRISCH = 60

const text = ref(START)
const kandidaten = ref<Eintrag[]>([])
const gewaehlt = ref(-1)
const flaeche = ref<HTMLElement>()
const cursor = ref<HTMLElement>()
const karte = ref({ x: 0, y: 0, sichtbar: false })

const alt = computed(() => text.value.slice(0, -FRISCH))
const frisch = computed(() => text.value.slice(-FRISCH))

const aktiv = useIsSlideActive()
let modell: Zaehler | null = null
let netz: NetzDaten | null = null

// Die Verteilung für das nächste Zeichen, je nach Quelle aus dem Zählmodell oder aus dem Netz
function verteilen(text: string): Eintrag[] {
  return netz ? netzVerteilung(netz, text) : verteilung(modell!, text)
}
let lauf = 0

const pause = (ms: number) => new Promise(fertig => setTimeout(fertig, ms))

function positioniereKarte() {
  if (!cursor.value || !flaeche.value)
    return
  const breite = flaeche.value.offsetWidth
  const x = Math.min(Math.max(cursor.value.offsetLeft - 70, 0), breite - 170)
  karte.value = { x, y: cursor.value.offsetTop - 12, sichtbar: true }
}

// Damit die Fläche beim Öffnen der Folie schon voll ist, wird der Anfang sofort erzeugt
function vorschreiben(anzahl: number) {
  for (let i = 0; i < anzahl; i++) {
    const eintraege = verteilen(text.value)
    if (!eintraege.length)
      break
    text.value += eintraege[ziehe(eintraege)].zeichen
  }
}

async function schreibe(meinLauf: number) {
  if (!modell && !netz) {
    if (props.quelle === 'netz')
      netz = await ladeNetz()
    else
      modell = await ladeModell()
    vorschreiben(1300)
  }
  while (meinLauf === lauf) {
    let eintraege = verteilen(text.value)
    if (!eintraege.length) {
      text.value = START
      eintraege = verteilen(text.value)
    }
    kandidaten.value = eintraege.slice(0, 4)
    gewaehlt.value = -1
    await nextTick()
    positioniereKarte()
    await pause(140)
    const auswahl = ziehe(eintraege)
    gewaehlt.value = auswahl
    await pause(220)
    if (meinLauf !== lauf)
      return
    text.value = (text.value + eintraege[auswahl].zeichen).slice(-SICHTBAR)
    await pause(40)
  }
}

watch(aktiv, (jetzt) => {
  lauf++
  if (jetzt)
    schreibe(lauf)
}, { immediate: true })

onBeforeUnmount(() => lauf++)
</script>

<template>
  <div class="titel">
    <div class="links">
      <div class="kicker">{{ props.kicker }}</div>
      <h1>{{ props.titel }}</h1>
      <p class="untertitel">{{ props.untertitel }}</p>

      <ol v-if="props.reihe.length" class="reihe">
        <li v-for="(teil, i) in props.reihe" :key="teil" :class="{ aktuell: i + 1 === props.nummer }">
          <span class="nr">{{ i + 1 }}</span>{{ teil }}
        </li>
      </ol>
    </div>

    <div class="rechts">
      <div ref="flaeche" class="flaeche">
        <div class="text"><span class="alt">{{ alt }}</span><span class="frisch">{{ frisch }}</span><span ref="cursor" class="cursor" /></div>

        <div v-if="karte.sichtbar" class="karte" :style="{ transform: `translate(${karte.x}px, ${karte.y}px) translateY(-100%)` }">
          <div v-for="(k, i) in kandidaten" :key="i" class="kandidat" :class="{ gewaehlt: i === gewaehlt }">
            <span class="zeichen">{{ zeigeZeichen(k.zeichen) }}</span>
            <span class="balken"><span :style="{ width: `${(k.p / kandidaten[0].p) * 100}%` }" /></span>
            <span class="prozent">{{ Math.round(k.p * 100) }}%</span>
          </div>
        </div>
      </div>
      <div class="legende">
        {{ props.legende }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.titel {
  position: absolute;
  inset: 0;
  display: grid;
  grid-template-columns: 46% 54%;
  grid-template-rows: minmax(0, 1fr);
  background:
    radial-gradient(ellipse at 12% 45%, rgba(42, 120, 214, 0.07), transparent 55%),
    radial-gradient(ellipse at 88% 95%, rgba(235, 104, 52, 0.07), transparent 50%),
    var(--hintergrund);
  overflow: hidden;
}

.links {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 2rem 0 4.5rem;
  z-index: 1;
}

.links h1 {
  font-size: 4.1rem;
  font-weight: 750;
  line-height: 1.02;
  letter-spacing: -0.035em;
  margin: 0.9rem 0 1.1rem;
  background: linear-gradient(100deg, var(--text) 35%, #3b5683);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.untertitel {
  font-size: 1.45rem;
  color: var(--text-leise);
  margin: 0;
}

.reihe {
  list-style: none;
  padding: 0;
  margin: 3.2rem 0 0;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  font-size: 1rem;
  color: var(--text-sehr-leise);
}

.reihe li {
  display: flex;
  align-items: center;
  gap: 0.7rem;
}

.reihe .nr {
  display: inline-grid;
  place-items: center;
  width: 1.6rem;
  height: 1.6rem;
  border-radius: 50%;
  border: 1.5px solid var(--linie);
  font-family: var(--mono);
  font-size: 0.8rem;
}

.reihe li.aktuell {
  color: var(--text);
}

.reihe li.aktuell .nr {
  border-color: var(--orange);
  background: var(--orange);
  color: #fff;
  box-shadow: var(--leuchten-orange);
}

.rechts {
  position: relative;
  padding: 2.5rem 3.5rem 2.5rem 1rem;
  display: flex;
  flex-direction: column;
}

.flaeche {
  position: relative;
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  overflow: hidden;
  mask-image: linear-gradient(to bottom, transparent 0%, black 45%);
}

.text {
  font-family: var(--mono);
  font-size: 1.05rem;
  line-height: 1.75;
  white-space: pre-wrap;
  word-break: break-word;
}

.alt {
  color: #b9bcc4;
}

.frisch {
  color: var(--text-leise);
}

.cursor {
  display: inline-block;
  width: 0.6em;
  height: 1.2em;
  margin-left: 1px;
  vertical-align: -0.2em;
  background: var(--orange);
  border-radius: 2px;
  box-shadow: var(--leuchten-orange);
}

.karte {
  position: absolute;
  left: 0;
  top: 0;
  width: 170px;
  padding: 0.5rem 0.6rem;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid var(--linie);
  box-shadow: var(--schatten);
  backdrop-filter: blur(6px);
  transition: transform 0.18s ease-out;
}

.kandidat {
  display: grid;
  grid-template-columns: 1.4rem 1fr 2.6rem;
  align-items: center;
  gap: 0.45rem;
  height: 1.45rem;
  font-family: var(--mono);
  font-size: 0.8rem;
  color: var(--text-leise);
  border-radius: 5px;
  padding: 0 0.25rem;
  transition: background 0.12s, color 0.12s;
}

.kandidat .zeichen {
  text-align: center;
  color: var(--text);
}

.kandidat .balken {
  height: 6px;
  border-radius: 3px;
  background: var(--flaeche-hell);
  overflow: hidden;
}

.kandidat .balken span {
  display: block;
  height: 100%;
  background: var(--blau);
  border-radius: 3px;
  transition: width 0.2s;
}

.kandidat .prozent {
  text-align: right;
}

.kandidat.gewaehlt {
  background: var(--orange-hauch);
  color: var(--orange);
}

.kandidat.gewaehlt .balken span {
  background: var(--orange);
  box-shadow: var(--leuchten-orange);
}

.legende {
  margin-top: 1rem;
  font-family: var(--mono);
  font-size: 0.72rem;
  letter-spacing: 0.04em;
  color: var(--text-sehr-leise);
}
</style>
