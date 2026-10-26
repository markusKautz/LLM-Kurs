<!--
  Die Grundidee in drei Schritten: vorhersagen, ziehen, anhängen.

  Klick 1: Kontext markieren und die Verteilung für das nächste Zeichen zeigen
  Klick 2: ein Zeichen ziehen (Glücksrad über den Balken) und anhängen
  Klick 3: die Schleife läuft von allein weiter
-->
<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useIsSlideActive, useSlideContext } from '@slidev/client'
import type { Eintrag, Zaehler } from '../logik/modell'
import { KONTEXT, ladeModell, verteilung, zeigeZeichen, ziehe } from '../logik/modell'

const props = withDefaults(defineProps<{ start?: string }>(), { start: 'es war einmal ein' })

const ZEILEN = 7
const SCHRITTE = ['Vorhersagen', 'Ziehen', 'Anhängen']

const { $clicks } = useSlideContext()
const aktiv = useIsSlideActive()

const text = ref(props.start)
const eintraege = ref<Eintrag[]>([])
const balkenSichtbar = ref(false)
const kontextSichtbar = ref(false)
const markiert = ref(-1)
const schritt = ref(-1)
const erzeugt = ref(0)

const wurzel = ref<HTMLElement>()
const cursor = ref<HTMLElement>()
const zeilenElemente = ref<HTMLElement[]>([])
const flieger = ref<HTMLElement>()
const fliegerZeichen = ref('')

let modell: Zaehler | null = null
let lauf = 0
const pause = (ms: number) => new Promise(fertig => setTimeout(fertig, ms))

// Die obersten Zeilen der Verteilung, der Rest wird zu "andere" zusammengefasst
const zeilen = computed(() => {
  const oben = eintraege.value.slice(0, ZEILEN).map(e => ({ ...e, label: zeigeZeichen(e.zeichen), rest: false }))
  const rest = eintraege.value.slice(ZEILEN).reduce((summe, e) => summe + e.p, 0)
  if (rest > 0.001)
    oben.push({ zeichen: '', p: rest, label: 'andere', rest: true })
  return oben
})
const groesste = computed(() => Math.max(...zeilen.value.map(z => z.p), 0.01))

// Nur das Ende des Texts zeigen, damit er auf die Folie passt
const sichtbar = computed(() => {
  const ende = text.value.slice(-34)
  return { vorne: ende.slice(0, -KONTEXT), kontext: [...ende.slice(-KONTEXT)], abgeschnitten: text.value.length > 34 }
})

function prozent(p: number) {
  return p < 0.01 ? '<1 %' : `${Math.round(p * 100)} %`
}

function vorhersagen() {
  if (!modell)
    return
  eintraege.value = verteilung(modell, text.value)
  if (!eintraege.value.length) {
    text.value = props.start
    eintraege.value = verteilung(modell, text.value)
  }
}

// Position eines Elements relativ zur Komponente, unabhängig von der Skalierung der Folie
function lage(element: HTMLElement) {
  const basis = wurzel.value!.getBoundingClientRect()
  const massstab = basis.width / wurzel.value!.offsetWidth
  const r = element.getBoundingClientRect()
  return { x: (r.left - basis.left) / massstab, y: (r.top - basis.top) / massstab }
}

async function ziehen(meinLauf: number, schnell: boolean) {
  schritt.value = 1
  const auswahl = ziehe(eintraege.value)
  const ziel = Math.min(auswahl, zeilen.value.length - 1)

  // Glücksrad: die Markierung läuft über die Balken und wird langsamer
  const runden = schnell ? 1 : 2
  const spruenge = runden * zeilen.value.length + ziel
  for (let i = 0; i <= spruenge; i++) {
    if (meinLauf !== lauf)
      return
    markiert.value = i % zeilen.value.length
    const rest = spruenge - i
    await pause(schnell ? 28 + 90 / (rest + 1) : 45 + 420 / (rest + 1))
  }
  await pause(schnell ? 120 : 450)

  // Anhängen: das gezogene Zeichen fliegt an das Ende des Texts
  schritt.value = 2
  const zeichen = eintraege.value[auswahl].zeichen
  fliegerZeichen.value = zeigeZeichen(zeichen)
  await nextTick()
  const von = lage(zeilenElemente.value[ziel].querySelector('.kachel') as HTMLElement)
  const nach = lage(cursor.value!)
  const dauer = schnell ? 380 : 750
  flieger.value!.animate([
    { transform: `translate(${von.x}px, ${von.y}px) scale(1)`, opacity: 1 },
    { transform: `translate(${(von.x + nach.x) / 2}px, ${Math.min(von.y, nach.y) - 70}px) scale(1.5)`, opacity: 1, offset: 0.5 },
    { transform: `translate(${nach.x}px, ${nach.y}px) scale(1.2)`, opacity: 1 },
  ], { duration: dauer, easing: 'cubic-bezier(.5,0,.3,1)' })
  await pause(dauer)
  if (meinLauf !== lauf)
    return
  fliegerZeichen.value = ''
  markiert.value = -1
  text.value += zeichen
  erzeugt.value++

  schritt.value = 0
  vorhersagen()
}

async function zustand(klicks: number) {
  const meinLauf = ++lauf
  modell ??= await ladeModell()
  if (meinLauf !== lauf)
    return

  if (klicks === 0) {
    text.value = props.start
    erzeugt.value = 0
    vorhersagen()
    kontextSichtbar.value = false
    balkenSichtbar.value = false
    schritt.value = -1
    markiert.value = -1
    return
  }

  kontextSichtbar.value = true
  if (klicks === 1) {
    text.value = props.start
    erzeugt.value = 0
    markiert.value = -1
    vorhersagen()
    balkenSichtbar.value = false
    await nextTick()
    await pause(30)
    balkenSichtbar.value = true
    schritt.value = 0
    return
  }

  balkenSichtbar.value = true
  if (!eintraege.value.length)
    vorhersagen()
  if (klicks === 2) {
    await ziehen(meinLauf, false)
    return
  }

  // Ab Klick 3 läuft die Schleife von selbst
  while (meinLauf === lauf) {
    await pause(650)
    if (meinLauf !== lauf)
      return
    await ziehen(meinLauf, true)
  }
}

watch([$clicks, aktiv], ([klicks, jetzt]) => {
  if (jetzt)
    zustand(klicks)
  else
    lauf++
}, { immediate: true })

onBeforeUnmount(() => lauf++)
</script>

<template>
  <div ref="wurzel" class="wurzel">
    <div class="buehne">
      <!-- Links: der Text -->
      <div class="textfeld">
        <div class="beschriftung">Text bisher</div>
        <div class="text">
          <span v-if="sichtbar.abgeschnitten" class="leise">…</span>{{ sichtbar.vorne }}<span class="kontext" :class="{ an: kontextSichtbar }"><span v-for="(z, i) in sichtbar.kontext" :key="i" :class="{ leer: z === ' ' }">{{ kontextSichtbar && z === ' ' ? '␣' : z }}</span><span class="kontext-label">Kontext: die letzten {{ KONTEXT }} Zeichen</span></span><span ref="cursor" class="cursor" />
        </div>
        <div class="zaehler" :class="{ an: erzeugt > 0 }">{{ erzeugt }} Zeichen erzeugt</div>
      </div>

      <!-- Rechts: die Verteilung -->
      <div class="verteilung" :class="{ an: balkenSichtbar }">
        <div class="beschriftung">Was kommt als Nächstes?</div>
        <div
          v-for="(zeile, i) in zeilen" :key="i" ref="zeilenElemente"
          class="zeile" :class="{ markiert: i === markiert, rest: zeile.rest }"
          :style="{ transitionDelay: `${i * 45}ms` }"
        >
          <span class="kachel">{{ zeile.label }}</span>
          <span class="spur"><span class="fuellung" :style="{ width: balkenSichtbar ? `${(zeile.p / groesste) * 100}%` : '0%', transitionDelay: `${i * 45}ms` }" /></span>
          <span class="prozent">{{ prozent(zeile.p) }}</span>
        </div>
      </div>
    </div>

    <!-- Unten: die Schleife -->
    <div class="schleife">
      <template v-for="(name, i) in SCHRITTE" :key="name">
        <div class="schritt" :class="{ an: schritt === i }">
          <span class="nr">{{ i + 1 }}</span>{{ name }}
        </div>
        <svg v-if="i < SCHRITTE.length - 1" class="pfeil" viewBox="0 0 40 12"><path d="M0 6h34m-6-5 6 5-6 5" /></svg>
      </template>
      <svg class="zurueck" viewBox="0 0 60 12"><path d="M58 6H6m6-5L6 6l6 5" /></svg>
      <span class="wieder">und wieder von vorn</span>
    </div>

    <div ref="flieger" class="flieger" :class="{ an: fliegerZeichen }">{{ fliegerZeichen }}</div>
  </div>
</template>

<style scoped>
.wurzel {
  position: relative;
  height: calc(100% - 6.4rem);
  display: flex;
  flex-direction: column;
}

.buehne {
  flex: 1;
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 2.5rem;
  margin-top: 1.4rem;
}

.beschriftung {
  font-family: var(--mono);
  font-size: 0.78rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-sehr-leise);
  margin-bottom: 1rem;
}

/* ---------- Text ---------- */
.textfeld {
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.text {
  font-family: var(--mono);
  font-size: 2.5rem;
  line-height: 1.5;
  color: var(--text);
  padding-bottom: 2.2rem;
  white-space: pre-wrap;
  word-break: break-all;
}

.kontext {
  position: relative;
  display: inline-block;
  white-space: nowrap;
  line-height: 1.25;
  border-radius: 8px;
  padding: 0.05em 0;
  transition: background 0.4s, box-shadow 0.4s;
}

.kontext.an {
  background: var(--orange-hauch);
  box-shadow: inset 0 0 0 2px var(--orange), var(--leuchten-orange);
}

.kontext .leer {
  color: var(--text-sehr-leise);
}

.kontext-label {
  position: absolute;
  left: 0;
  top: 100%;
  margin-top: 0.5rem;
  white-space: nowrap;
  font-family: var(--mono);
  font-size: 0.75rem;
  color: var(--orange);
  opacity: 0;
  transform: translateY(6px);
  transition: opacity 0.4s, transform 0.4s;
}

.kontext.an .kontext-label {
  opacity: 1;
  transform: none;
}

.cursor {
  display: inline-block;
  width: 0.55em;
  height: 1.05em;
  vertical-align: -0.15em;
  margin-left: 3px;
  background: var(--text);
  border-radius: 3px;
  animation: blinken 1.1s steps(1) infinite;
}

@keyframes blinken {
  50% { opacity: 0; }
}

.zaehler {
  margin-top: auto;
  font-family: var(--mono);
  font-size: 0.85rem;
  color: var(--text-leise);
  opacity: 0;
  transition: opacity 0.3s;
}

.zaehler.an {
  opacity: 1;
}

/* ---------- Verteilung ---------- */
.verteilung {
  align-self: start;
  padding: 1.3rem 1.5rem;
  border-radius: 16px;
  background: var(--flaeche);
  border: 1px solid var(--linie);
  box-shadow: var(--schatten);
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 0.5s, transform 0.5s;
}

.verteilung.an {
  opacity: 1;
  transform: none;
}

.zeile {
  display: grid;
  grid-template-columns: 2.3rem 1fr 3.4rem;
  align-items: center;
  gap: 0.8rem;
  height: 2.55rem;
  padding: 0 0.4rem;
  margin: 0 -0.4rem;
  border-radius: 8px;
  transition: background 0.08s;
}

.kachel {
  display: grid;
  place-items: center;
  height: 2rem;
  border-radius: 7px;
  background: var(--flaeche-hell);
  border: 1px solid var(--linie);
  font-family: var(--mono);
  font-size: 1.1rem;
  transition: border-color 0.08s, color 0.08s;
}

.zeile.rest .kachel {
  font-size: 0.65rem;
  color: var(--text-leise);
}

.spur {
  height: 0.75rem;
  border-radius: 6px;
  background: var(--flaeche-hell);
  overflow: hidden;
}

.fuellung {
  display: block;
  height: 100%;
  border-radius: 6px;
  background: linear-gradient(90deg, var(--blau-tief), var(--blau));
  transition: width 0.6s cubic-bezier(.2, .8, .2, 1);
}

.zeile.rest .fuellung {
  background: var(--text-sehr-leise);
}

.prozent {
  font-family: var(--mono);
  font-size: 0.9rem;
  text-align: right;
  color: var(--text-leise);
}

.zeile.markiert {
  background: var(--orange-hauch);
}

.zeile.markiert .kachel {
  border-color: var(--orange);
  color: var(--orange);
  box-shadow: var(--leuchten-orange);
}

.zeile.markiert .fuellung {
  background: linear-gradient(90deg, var(--orange-tief), var(--orange));
}

.zeile.markiert .prozent {
  color: var(--orange);
}

/* ---------- Schleife ---------- */
.schleife {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  margin-top: 1.4rem;
  font-size: 1rem;
  color: var(--text-sehr-leise);
}

.schritt {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.45rem 1rem 0.45rem 0.5rem;
  border-radius: 999px;
  border: 1px solid var(--linie);
  transition: all 0.25s;
}

.schritt .nr {
  display: grid;
  place-items: center;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  background: var(--flaeche-hell);
  font-family: var(--mono);
  font-size: 0.8rem;
}

.schritt.an {
  color: var(--text);
  border-color: var(--orange);
  box-shadow: var(--leuchten-orange);
}

.schritt.an .nr {
  background: var(--orange);
  color: #fff;
}

.pfeil, .zurueck {
  width: 2.2rem;
  height: 0.8rem;
  fill: none;
  stroke: var(--text-sehr-leise);
  stroke-width: 1.5;
}

.zurueck {
  width: 3rem;
  margin-left: 0.6rem;
}

.wieder {
  font-size: 0.85rem;
}

/* ---------- Fliegendes Zeichen ---------- */
.flieger {
  position: absolute;
  left: 0;
  top: 0;
  display: grid;
  place-items: center;
  width: 2.3rem;
  height: 2rem;
  border-radius: 7px;
  background: var(--orange);
  color: #fff;
  font-family: var(--mono);
  font-size: 1.1rem;
  font-weight: 700;
  box-shadow: var(--leuchten-orange);
  pointer-events: none;
  opacity: 0;
}

.flieger.an {
  opacity: 1;
}
</style>
