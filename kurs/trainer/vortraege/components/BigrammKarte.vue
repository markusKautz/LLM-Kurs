<!--
  Die ganze Bigramm-Zählung der Märchen als Bild: 40 mal 40 Felder.
  Klick 1: die Karte baut sich auf
  Ab Klick 2: jeweils eine Zeile wird hervorgehoben (aus der Prop "zeilen")
-->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { useSlideContext } from '@slidev/client'
import type { Kennzahlen } from '../logik/modell'
import { ladeKennzahlen, zahl, zeigeZeichen } from '../logik/modell'

const props = withDefaults(defineProps<{ zeilen?: string[] }>(), { zeilen: () => ['q', ' ', 'e'] })

const FELD = 11
const RAND = 22

const { $clicks } = useSlideContext()
const daten = ref<Kennzahlen | null>(null)
ladeKennzahlen().then(d => daten.value = d)

// Jede Zeile durch ihre Summe teilen: aus Zählern werden Wahrscheinlichkeiten
const wahrscheinlichkeiten = computed(() => daten.value?.bigramme.map((zeile) => {
  const summe = zeile.reduce((a, b) => a + b, 0) || 1
  return zeile.map(anzahl => anzahl / summe)
}) ?? [])

const hervor = computed(() => {
  const nummer = $clicks.value - 2
  if (!daten.value || nummer < 0 || nummer >= props.zeilen.length)
    return -1
  return daten.value.zeichen.indexOf(props.zeilen[nummer])
})

const auswahl = computed(() => {
  if (hervor.value < 0 || !daten.value)
    return []
  const d = daten.value
  return wahrscheinlichkeiten.value[hervor.value]
    .map((p, i) => ({ z: d.zeichen[i], p, anzahl: d.bigramme[hervor.value][i] }))
    .sort((a, b) => b.p - a.p).slice(0, 6)
})
const summe = computed(() => hervor.value < 0 ? 0 : daten.value!.bigramme[hervor.value].reduce((a, b) => a + b, 0))
</script>

<template>
  <div v-if="daten" class="karte-bigramm">
    <svg
      :width="RAND + FELD * daten.zeichen.length" :height="RAND + FELD * daten.zeichen.length"
      class="matrix" :class="{ an: $clicks >= 1, fokus: hervor >= 0 }"
    >
      <text
        v-for="(z, i) in daten.zeichen" :key="`o${i}`"
        :x="RAND + FELD * i + FELD / 2" :y="RAND - 7" class="achse"
      >{{ zeigeZeichen(z) }}</text>
      <text
        v-for="(z, i) in daten.zeichen" :key="`l${i}`"
        :x="RAND - 8" :y="RAND + FELD * i + FELD / 2 + 3" class="achse" :class="{ hervor: i === hervor }"
      >{{ zeigeZeichen(z) }}</text>
      <g v-for="(zeile, a) in wahrscheinlichkeiten" :key="a" class="zeile" :class="{ hervor: a === hervor }" :style="{ transitionDelay: `${a * 25}ms` }">
        <rect
          v-for="(p, b) in zeile" :key="b"
          :x="RAND + FELD * b + 0.5" :y="RAND + FELD * a + 0.5" :width="FELD - 1" :height="FELD - 1" rx="2"
          :fill="p > 0 ? `rgba(42, 120, 214, ${0.08 + 0.92 * Math.sqrt(p)})` : '#f1efea'"
        />
      </g>
      <rect
        v-if="hervor >= 0" class="rahmen"
        :x="RAND - 1" :y="RAND + FELD * hervor - 1" :width="FELD * daten.zeichen.length + 2" :height="FELD + 2" rx="3"
      />
    </svg>

    <div class="seite">
      <div class="erklaerung" :class="{ an: $clicks >= 1 }">
        <div><b>Zeile</b> = das Zeichen jetzt</div>
        <div><b>Spalte</b> = das Zeichen danach</div>
        <div>je <b class="blau">dunkler</b>, desto häufiger</div>
      </div>

      <div v-if="hervor >= 0" :key="hervor" class="auswahl karte">
        <div class="beschriftung">nach „{{ zeigeZeichen(daten.zeichen[hervor]) }}“ kam im Text …</div>
        <div v-for="e in auswahl" :key="e.z" class="eintrag">
          <span class="zk">{{ zeigeZeichen(e.z) }}</span>
          <span class="spur"><span :style="{ width: `${e.p * 100}%` }" /></span>
          <span class="prozent">{{ zahl(e.p * 100, e.p < 0.1 ? 1 : 0) }} %</span>
        </div>
        <div class="summe">{{ zahl(summe) }} Mal gezählt</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.karte-bigramm {
  display: flex;
  gap: 2.5rem;
  margin-top: 0.8rem;
  align-items: flex-start;
}

.matrix {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.4s;
}

.matrix.an {
  opacity: 1;
}

.achse {
  font-family: var(--mono);
  font-size: 9px;
  fill: var(--text-leise);
  text-anchor: middle;
}

.achse.hervor {
  fill: var(--orange);
  font-weight: 700;
  font-size: 11px;
}

.zeile {
  opacity: 0;
  transition: opacity 0.5s;
}

.matrix.an .zeile {
  opacity: 1;
}

.matrix.fokus .zeile:not(.hervor) {
  opacity: 0.22;
  transition-delay: 0s !important;
}

.rahmen {
  fill: none;
  stroke: var(--orange);
  stroke-width: 2;
}

.seite {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.4rem;
  padding-top: 1.4rem;
}

.erklaerung {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  font-size: 1.15rem;
  color: var(--text-leise);
  opacity: 0;
  transition: opacity 0.6s 0.8s;
}

.erklaerung.an {
  opacity: 1;
}

.blau {
  color: var(--blau);
}

.auswahl {
  padding: 1.1rem 1.3rem;
  animation: herein 0.5s ease;
}

@keyframes herein {
  from { opacity: 0; transform: translateY(10px); }
}

.eintrag {
  display: grid;
  grid-template-columns: 2.4rem 1fr 4rem;
  align-items: center;
  gap: 0.8rem;
  margin-top: 0.6rem;
}

.spur {
  height: 0.65rem;
  border-radius: 5px;
  background: var(--flaeche-hell);
  overflow: hidden;
}

.spur span {
  display: block;
  height: 100%;
  border-radius: 5px;
  background: var(--blau);
  transform-origin: left;
  animation: wachsen 0.8s cubic-bezier(.2, .8, .2, 1);
}

@keyframes wachsen {
  from { transform: scaleX(0); }
}

.prozent {
  font-family: var(--mono);
  text-align: right;
  color: var(--text-leise);
}

.summe {
  margin-top: 0.8rem;
  font-family: var(--mono);
  font-size: 0.85rem;
  color: var(--text-sehr-leise);
}
</style>
