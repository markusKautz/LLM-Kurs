<!--
  Aus Zählern werden Wahrscheinlichkeiten, am Beispiel einer Zeile der Bigramm-Zählung.
  Klick 1: die Zähler
  Klick 2: die Summe
  Klick 3: jeder Zähler geteilt durch die Summe
-->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { useSlideContext } from '@slidev/client'
import type { Kennzahlen } from '../logik/modell'
import { ladeKennzahlen, zahl, zeigeZeichen } from '../logik/modell'

const props = withDefaults(defineProps<{ zeichen?: string, zeilen?: number }>(), { zeichen: 'h', zeilen: 6 })

const { $clicks } = useSlideContext()
const daten = ref<Kennzahlen | null>(null)
ladeKennzahlen().then(d => daten.value = d)

const zeile = computed(() => {
  if (!daten.value)
    return { eintraege: [], summe: 0 }
  const d = daten.value
  const zaehler = d.bigramme[d.zeichen.indexOf(props.zeichen)]
  const summe = zaehler.reduce((a, b) => a + b, 0)
  const sortiert = zaehler.map((anzahl, i) => ({ z: zeigeZeichen(d.zeichen[i]), anzahl })).sort((a, b) => b.anzahl - a.anzahl)
  const oben = sortiert.slice(0, props.zeilen)
  const rest = sortiert.slice(props.zeilen).reduce((a, b) => a + b.anzahl, 0)
  return { eintraege: [...oben, { z: 'andere', anzahl: rest }], summe }
})
const groesste = computed(() => Math.max(...zeile.value.eintraege.map(e => e.anzahl), 1))
</script>

<template>
  <div v-if="daten" class="normieren">
    <div class="kopf">
      <span class="beschriftung">nach</span><span class="zk gross">{{ zeigeZeichen(props.zeichen) }}</span><span class="beschriftung">kam im Märchentext …</span>
    </div>

    <div class="tabelle">
      <div v-for="(e, i) in zeile.eintraege" :key="i" class="zeile" :class="{ an: $clicks >= 1 }" :style="{ transitionDelay: `${i * 70}ms` }">
        <span class="zk" :class="{ klein: e.z === 'andere' }">{{ e.z }}</span>
        <span class="anzahl">{{ zahl(e.anzahl) }} Mal</span>
        <span class="geteilt" :class="{ an: $clicks >= 3 }" :style="{ transitionDelay: `${i * 90}ms` }">÷ {{ zahl(zeile.summe) }} =</span>
        <span class="ergebnis" :class="{ an: $clicks >= 3 }" :style="{ transitionDelay: `${300 + i * 90}ms` }">
          <span class="spur"><span :style="{ width: $clicks >= 3 ? `${(e.anzahl / groesste) * 100}%` : '0%', transitionDelay: `${400 + i * 90}ms` }" /></span>
          <b>{{ zahl((e.anzahl / zeile.summe) * 100, 1) }} %</b>
        </span>
      </div>
    </div>

    <div class="summe" :class="{ an: $clicks >= 2 }">
      zusammen <b>{{ zahl(zeile.summe) }}</b> Mal
      <span class="pfeil" :class="{ an: $clicks >= 3 }">→ alle Anteile zusammen: <b class="akzent">100 %</b></span>
    </div>
  </div>
</template>

<style scoped>
.normieren {
  margin-top: 1.2rem;
}

.kopf {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-bottom: 1.2rem;
}

.zk.gross {
  min-width: 2.8rem;
  height: 2.8rem;
  font-size: 1.5rem;
  border-color: var(--blau);
  box-shadow: var(--leuchten-blau);
}

.tabelle {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.zeile {
  display: grid;
  grid-template-columns: 4rem 9rem 9rem 1fr;
  align-items: center;
  gap: 1rem;
  font-family: var(--mono);
  font-size: 1.3rem;
  opacity: 0;
  transform: translateX(-12px);
  transition: opacity 0.5s, transform 0.5s;
}

.zeile.an {
  opacity: 1;
  transform: none;
}

.zk.klein {
  font-size: 0.7rem;
  color: var(--text-leise);
}

.anzahl {
  text-align: right;
}

.geteilt {
  color: var(--text-sehr-leise);
  opacity: 0;
  transition: opacity 0.4s;
}

.ergebnis {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: var(--orange);
  opacity: 0;
  transition: opacity 0.4s;
}

.geteilt.an,
.ergebnis.an {
  opacity: 1;
}

.spur {
  width: 14rem;
  height: 0.7rem;
  border-radius: 5px;
  background: var(--flaeche-hell);
  overflow: hidden;
}

.spur span {
  display: block;
  max-width: 100%;
  height: 100%;
  border-radius: 5px;
  background: var(--orange);
  transition: width 0.8s cubic-bezier(.2, .8, .2, 1);
}

.summe {
  margin-top: 1.4rem;
  padding-top: 1rem;
  border-top: 2px solid var(--linie);
  font-family: var(--mono);
  font-size: 1.3rem;
  opacity: 0;
  transition: opacity 0.5s;
}

.summe.an {
  opacity: 1;
}

.pfeil {
  margin-left: 2rem;
  opacity: 0;
  transition: opacity 0.5s 1.2s;
}

.pfeil.an {
  opacity: 1;
}
</style>
