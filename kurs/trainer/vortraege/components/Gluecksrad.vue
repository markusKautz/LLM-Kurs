<!--
  Ziehen als Glücksrad: Jedes Zeichen bekommt ein Stück, so groß wie seine Wahrscheinlichkeit.
  Klick 1: einmal drehen
  Klick 2: zehnmal drehen
  Klick 3: 1000-mal drehen, die Strichliste nähert sich den Wahrscheinlichkeiten
-->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useIsSlideActive, useSlideContext } from '@slidev/client'
import type { Eintrag } from '../logik/modell'
import { ladeModell, pause, verteilung, zahl, zeigeZeichen, ziehe } from '../logik/modell'

const props = withDefaults(defineProps<{ kontext?: string, stuecke?: number }>(), { kontext: ' ein', stuecke: 5 })

const FARBEN = ['#2a78d6', '#eb6834', '#2ea37a', '#8a5cd6', '#d6a12a', '#b5b9c2']
const R = 170

const { $clicks } = useSlideContext()
const aktiv = useIsSlideActive()
const felder = ref<(Eintrag & { label: string })[]>([])
const drehung = ref(0)
const dauer = ref(0)
const treffer = ref<number[]>([])
const letzter = ref(-1)
let lauf = 0

ladeModell().then((modell) => {
  const alle = verteilung(modell, props.kontext)
  const oben = alle.slice(0, props.stuecke).map(e => ({ ...e, label: zeigeZeichen(e.zeichen) }))
  const rest = alle.slice(props.stuecke).reduce((a, b) => a + b.p, 0)
  felder.value = [...oben, { zeichen: '', p: rest, label: 'andere' }]
  treffer.value = felder.value.map(() => 0)
})

// Start- und Endwinkel jedes Stücks, 0 Grad ist oben
const stuecke = computed(() => {
  let winkel = 0
  return felder.value.map((f, i) => {
    const von = winkel
    winkel += f.p * 360
    return { ...f, von, bis: winkel, farbe: FARBEN[i % FARBEN.length] }
  })
})

function punkt(winkel: number, radius = R) {
  const rad = (winkel - 90) * Math.PI / 180
  return [Math.cos(rad) * radius, Math.sin(rad) * radius]
}

function pfad(von: number, bis: number) {
  const [x1, y1] = punkt(von)
  const [x2, y2] = punkt(bis)
  return `M0 0 L${x1} ${y1} A${R} ${R} 0 ${bis - von > 180 ? 1 : 0} 1 ${x2} ${y2} Z`
}

const gesamt = computed(() => treffer.value.reduce((a, b) => a + b, 0))

async function drehe(meinLauf: number, ms: number) {
  const nummer = ziehe(felder.value)
  const s = stuecke.value[nummer]
  // Der Zeiger steht oben: das Rad so weit drehen, dass eine zufällige Stelle des Stücks oben landet
  const ziel = s.von + (0.15 + Math.random() * 0.7) * (s.bis - s.von)
  const jetzt = ((drehung.value % 360) + 360) % 360
  dauer.value = ms
  drehung.value += (ms > 300 ? 3 * 360 : 360) + ((360 - ziel) - jetzt + 720) % 360
  await pause(ms + 60)
  if (meinLauf !== lauf)
    return
  treffer.value[nummer]++
  letzter.value = nummer
}

watch([$clicks, aktiv, felder], async ([klicks, jetzt]) => {
  const meinLauf = ++lauf
  if (!jetzt || !felder.value.length)
    return
  if (klicks <= 1) {
    treffer.value = felder.value.map(() => 0)
    letzter.value = -1
  }
  if (klicks === 1)
    await drehe(meinLauf, 3800)
  if (klicks === 2) {
    for (let i = 0; i < 10 && meinLauf === lauf; i++)
      await drehe(meinLauf, 650)
  }
  if (klicks === 3) {
    // Ohne Animation weiterdrehen, aber die Strichliste sichtbar wachsen lassen
    for (let runde = 0; runde < 50 && meinLauf === lauf; runde++) {
      for (let i = 0; i < 20; i++)
        treffer.value[ziehe(felder.value)]++
      drehung.value += 137
      dauer.value = 60
      await pause(60)
    }
  }
}, { immediate: true })
</script>

<template>
  <div class="gluecksrad">
    <div class="rad">
      <svg :viewBox="`${-R - 20} ${-R - 30} ${2 * R + 40} ${2 * R + 50}`" width="420" height="440">
        <g :style="{ transform: `rotate(${drehung}deg)`, transition: `transform ${dauer}ms cubic-bezier(.15, .7, .2, 1)` }">
          <path v-for="(s, i) in stuecke" :key="i" :d="pfad(s.von, s.bis)" :fill="s.farbe" stroke="#fff" stroke-width="3" />
          <template v-for="(s, i) in stuecke" :key="`t${i}`">
            <!-- Gegen die Drehung des Rads gedreht, damit die Schrift am Ende aufrecht steht -->
            <text
              v-if="s.bis - s.von > 14"
              :x="punkt((s.von + s.bis) / 2, R * 0.68)[0]" :y="punkt((s.von + s.bis) / 2, R * 0.68)[1]"
              :transform="`rotate(${-drehung} ${punkt((s.von + s.bis) / 2, R * 0.68)[0]} ${punkt((s.von + s.bis) / 2, R * 0.68)[1]})`"
              dominant-baseline="central"
              class="beschriftung-rad" :class="{ klein: s.label === 'andere' }"
            >{{ s.label }}</text>
          </template>
        </g>
        <circle r="26" fill="#fff" stroke="var(--linie)" stroke-width="2" />
        <path :d="`M-14 ${-R - 26} L14 ${-R - 26} L0 ${-R + 8} Z`" class="zeiger" />
      </svg>
      <div class="kontext">nach „<span>{{ props.kontext.replace(/ /g, '␣') }}</span>“</div>
    </div>

    <div class="liste karte">
      <div class="kopf">
        <span class="beschriftung">Strichliste</span>
        <span class="gedreht">{{ zahl(gesamt) }}-mal gedreht</span>
      </div>
      <div v-for="(s, i) in stuecke" :key="i" class="eintrag" :class="{ neu: i === letzter && $clicks < 3 }">
        <span class="farbe" :style="{ background: s.farbe }" />
        <span class="zeichen" :class="{ klein: s.label === 'andere' }">{{ s.label }}</span>
        <span class="spur">
          <span class="ist" :style="{ width: gesamt ? `${(treffer[i] / gesamt) * 100}%` : '0%', background: s.farbe }" />
          <span class="soll" :style="{ left: `${s.p * 100}%` }" />
        </span>
        <span class="zahlen">{{ treffer[i] }}<small>{{ gesamt ? ` · ${Math.round((treffer[i] / gesamt) * 100)} %` : '' }}</small></span>
      </div>
      <div class="legende"><span class="soll-muster" /> Wahrscheinlichkeit laut Modell</div>
    </div>
  </div>
</template>

<style scoped>
.gluecksrad {
  display: grid;
  grid-template-columns: 440px 1fr;
  gap: 2rem;
  align-items: center;
  margin-top: 0.4rem;
}

.rad {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.beschriftung-rad {
  fill: #fff;
  font-family: var(--mono);
  font-size: 26px;
  font-weight: 700;
  text-anchor: middle;
}

.beschriftung-rad.klein {
  font-size: 13px;
}

.zeiger {
  fill: var(--text);
  filter: drop-shadow(0 2px 3px rgba(0, 0, 0, 0.25));
}

.kontext {
  margin-top: -0.5rem;
  font-size: 1.1rem;
  color: var(--text-leise);
}

.kontext span {
  font-family: var(--mono);
  color: var(--text);
}

.liste {
  padding: 1.2rem 1.4rem;
}

.kopf {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 0.8rem;
}

.gedreht {
  font-family: var(--mono);
  font-size: 1rem;
  color: var(--text-leise);
}

.eintrag {
  display: grid;
  grid-template-columns: 0.8rem 3.6rem 1fr 6.5rem;
  align-items: center;
  gap: 0.8rem;
  height: 2.6rem;
  padding: 0 0.4rem;
  margin: 0 -0.4rem;
  border-radius: 8px;
  transition: background 0.3s;
}

.eintrag.neu {
  background: var(--orange-hauch);
}

.farbe {
  width: 0.8rem;
  height: 0.8rem;
  border-radius: 3px;
}

.zeichen {
  font-family: var(--mono);
  font-size: 1.3rem;
}

.zeichen.klein {
  font-size: 0.8rem;
  color: var(--text-leise);
}

.spur {
  position: relative;
  height: 0.8rem;
  border-radius: 5px;
  background: var(--flaeche-hell);
}

.ist {
  display: block;
  height: 100%;
  border-radius: 5px;
  transition: width 0.3s;
}

.soll {
  position: absolute;
  top: -5px;
  bottom: -5px;
  width: 3px;
  margin-left: -1.5px;
  border-radius: 2px;
  background: var(--text);
}

.zahlen {
  font-family: var(--mono);
  font-size: 1.05rem;
  text-align: right;
}

.zahlen small {
  color: var(--text-leise);
}

.legende {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-top: 0.9rem;
  font-size: 0.85rem;
  color: var(--text-leise);
}

.soll-muster {
  width: 3px;
  height: 1rem;
  border-radius: 2px;
  background: var(--text);
}
</style>
