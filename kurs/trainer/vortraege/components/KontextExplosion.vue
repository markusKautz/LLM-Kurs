<!--
  Der Haken an mehr Kontext: Die Zahl der möglichen Kontexte explodiert.
  Jeder Klick zeigt eine weitere Zeile. Die Zahlen zählen dabei hoch.
  Klick nach der letzten Zeile: die Spalte "im Test unbekannt" leuchtet auf.
-->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useSlideContext } from '@slidev/client'
import type { Kennzahlen } from '../logik/modell'
import { ladeKennzahlen, zahl } from '../logik/modell'

const { $clicks } = useSlideContext()
const daten = ref<Kennzahlen | null>(null)
ladeKennzahlen().then(d => daten.value = d)

const zeilen = computed(() => daten.value?.explosion.filter(e => e.n >= 1) ?? [])
const angezeigt = ref<number[]>([])

// Zahlen hochzählen lassen, wenn eine Zeile erscheint
watch([$clicks, zeilen], () => {
  zeilen.value.forEach((z, i) => {
    if (i >= $clicks.value) {
      angezeigt.value[i] = 0
      return
    }
    if (angezeigt.value[i] === z.moeglich)
      return
    const anfang = performance.now()
    const schritt = () => {
      const t = Math.min((performance.now() - anfang) / 1200, 1)
      angezeigt.value[i] = Math.round(z.moeglich ** (1 - (1 - t) ** 2))
      if (t < 1)
        requestAnimationFrame(schritt)
      else
        angezeigt.value[i] = z.moeglich
    }
    requestAnimationFrame(schritt)
  })
}, { immediate: true })

const testSichtbar = computed(() => $clicks.value > zeilen.value.length)
</script>

<template>
  <div v-if="daten" class="explosion">
    <div class="kopf">
      <span>Kontext</span>
      <span class="rechts">mögliche Kontexte</span>
      <span class="rechts">kommen im Text vor</span>
      <span class="rechts" :class="{ hervor: testSichtbar }">im Test nie gesehen</span>
    </div>
    <div v-for="(z, i) in zeilen" :key="z.n" class="zeile" :class="{ an: i < $clicks }">
      <span class="n">{{ z.n }} Zeichen</span>
      <span class="rechts moeglich">{{ zahl(angezeigt[i] ?? 0) }}</span>
      <span class="rechts gesehen">
        {{ zahl(z.gesehen) }}
        <small>{{ z.gesehen / z.moeglich >= 0.01 ? zahl((z.gesehen / z.moeglich) * 100, 0) : zahl((z.gesehen / z.moeglich) * 100, z.n > 5 ? 4 : 2) }} %</small>
      </span>
      <span class="rechts test" :class="{ an: testSichtbar }">
        <span class="spur"><span :style="{ width: testSichtbar ? `${Math.min(z.unbekannt / 0.2, 1) * 100}%` : '0%' }" /></span>
        {{ zahl(z.unbekannt * 100, z.unbekannt < 0.001 ? 2 : 1) }} %
      </span>
    </div>
    <div class="fuss">
      {{ daten.zeichen.length }} verschiedene Zeichen, Kontexte gezählt im Märchentext ({{ zahl(daten.laenge * 0.9) }} Zeichen Training)
    </div>
  </div>
</template>

<style scoped>
.explosion {
  margin-top: 1.3rem;
}

.kopf,
.zeile {
  display: grid;
  grid-template-columns: 10rem 1.4fr 1.2fr 1.3fr;
  align-items: center;
  gap: 1.5rem;
}

.kopf {
  padding: 0 1.2rem 0.7rem;
  font-size: 0.95rem;
  color: var(--text-leise);
  border-bottom: 2px solid var(--linie);
}

.kopf .hervor {
  color: var(--orange);
  font-weight: 650;
}

.rechts {
  text-align: right;
  justify-self: end;
}

.zeile {
  padding: 0.75rem 1.2rem;
  border-bottom: 1px solid var(--linie);
  font-family: var(--mono);
  font-size: 1.35rem;
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.5s, transform 0.5s;
}

.zeile.an {
  opacity: 1;
  transform: none;
}

.n {
  font-family: var(--sans);
  font-size: 1.1rem;
  font-weight: 600;
}

.moeglich {
  font-weight: 700;
  color: var(--blau);
}

.gesehen small {
  display: block;
  font-size: 0.75rem;
  color: var(--text-leise);
}

.test {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  color: var(--orange);
  opacity: 0;
  transition: opacity 0.6s;
}

.test.an {
  opacity: 1;
}

.spur {
  width: 7rem;
  height: 0.65rem;
  border-radius: 5px;
  background: var(--flaeche-hell);
  overflow: hidden;
}

.spur span {
  display: block;
  height: 100%;
  border-radius: 5px;
  background: var(--orange);
  transition: width 0.9s ease;
}

.fuss {
  margin-top: 1rem;
  font-size: 0.85rem;
  color: var(--text-sehr-leise);
}
</style>
