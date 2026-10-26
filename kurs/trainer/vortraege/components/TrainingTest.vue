<!--
  Training und Test: Der Text wird geteilt, geprüft wird mit dem Teil, den das Modell nie gesehen hat.
  Klick 1: der Text wird geteilt
  Klick 2: Verlust auf dem Training für jedes n
  Klick 3: Verlust auf dem Test
-->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { useSlideContext } from '@slidev/client'
import type { Kennzahlen } from '../logik/modell'
import { ladeKennzahlen, zahl } from '../logik/modell'

const { $clicks } = useSlideContext()
const daten = ref<Kennzahlen | null>(null)
ladeKennzahlen().then(d => daten.value = d)

const zeilen = computed(() => daten.value?.verluste ?? [])
const MAX = 3.2
</script>

<template>
  <div v-if="daten" class="tt">
    <div class="teilung" :class="{ an: $clicks >= 1 }">
      <div class="teil teil-training"><b>Training</b> 90 %: daraus wird gezählt</div>
      <div class="teil teil-test"><b>Test</b> 10 %</div>
    </div>
    <div class="teilung-text" :class="{ an: $clicks >= 1 }">
      Wie in der Prüfung: Spannend sind nicht die Übungsaufgaben, sondern neue Aufgaben.
    </div>

    <div class="tabelle" :class="{ an: $clicks >= 2 }">
      <div class="kopf">
        <span>Kontext</span>
        <span>Verlust Training</span>
        <span :class="{ hervor: $clicks >= 3 }">Verlust Test</span>
      </div>
      <div v-for="(z, i) in zeilen" :key="z.n" class="zeile">
        <span class="n">n = {{ z.n }}</span>
        <span class="wert">
          <span class="spur"><span class="blau" :style="{ width: $clicks >= 2 ? `${(z.training / MAX) * 100}%` : '0%', transitionDelay: `${i * 90}ms` }" /></span>
          <b>{{ zahl(z.training, 2) }}</b>
        </span>
        <span class="wert test" :class="{ an: $clicks >= 3 }" :style="{ transitionDelay: `${i * 160}ms` }">
          <template v-if="z.test !== null">
            <span class="spur"><span class="blau" :style="{ width: `${(z.test / MAX) * 100}%` }" /></span>
            <b>{{ zahl(z.test, 2) }}</b>
          </template>
          <template v-else>
            <b class="unendlich">unendlich</b>
            <small>{{ zahl(z.nullen * 100, z.nullen < 0.01 ? 2 : 1) }} % der Stellen „unmöglich“</small>
          </template>
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tt {
  margin-top: 1.2rem;
}

.teilung {
  display: flex;
  height: 2.8rem;
  border-radius: 10px;
  overflow: hidden;
  font-size: 1.05rem;
  opacity: 0;
  transform: scaleX(0.9);
  transition: opacity 0.6s, transform 0.6s;
}

.teilung.an {
  opacity: 1;
  transform: none;
}

.teil {
  display: flex;
  align-items: center;
  padding: 0 1rem;
  gap: 0.4rem;
  color: #fff;
}

.teil-training {
  flex: 9;
  background: var(--blau);
}

.teil-test {
  flex: 1;
  background: var(--orange);
  justify-content: center;
}

.teilung-text {
  margin-top: 0.6rem;
  font-size: 1rem;
  color: var(--text-leise);
  opacity: 0;
  transition: opacity 0.6s 0.4s;
}

.teilung-text.an {
  opacity: 1;
}

.tabelle {
  margin-top: 1.3rem;
  opacity: 0;
  transition: opacity 0.6s;
}

.tabelle.an {
  opacity: 1;
}

.kopf,
.zeile {
  display: grid;
  grid-template-columns: 6rem 1fr 1.25fr;
  align-items: center;
  gap: 2rem;
}

.kopf {
  padding-bottom: 0.4rem;
  border-bottom: 2px solid var(--linie);
  font-size: 0.95rem;
  color: var(--text-leise);
}

.kopf .hervor {
  color: var(--orange);
  font-weight: 650;
}

.zeile {
  height: 2.45rem;
  border-bottom: 1px solid var(--linie);
}

.n {
  font-family: var(--mono);
  font-weight: 700;
  color: var(--blau);
}

.wert {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  font-family: var(--mono);
  font-size: 1.05rem;
}

.spur {
  flex: 0 0 13rem;
  height: 0.65rem;
  border-radius: 5px;
  background: var(--flaeche-hell);
  overflow: hidden;
}

.spur .blau {
  display: block;
  height: 100%;
  border-radius: 5px;
  background: var(--blau);
  transition: width 0.8s cubic-bezier(.2, .8, .2, 1);
}

.test {
  opacity: 0;
  transform: translateX(10px);
  transition: opacity 0.5s, transform 0.5s;
}

.test.an {
  opacity: 1;
  transform: none;
}

.unendlich {
  color: var(--orange);
}

.test small {
  font-family: var(--sans);
  font-size: 0.85rem;
  color: var(--text-leise);
}
</style>
