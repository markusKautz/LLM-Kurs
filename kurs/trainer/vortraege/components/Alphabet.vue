<!--
  Alle Zeichen der Märchen mit ihrer Nummer.
  Klick 1: jedes Zeichen bekommt seine Nummer (ID)
  Klick 2: wie oft kommt jedes Zeichen vor?
  Klick 3: Text, der nur nach Häufigkeit gezogen wird
-->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useIsSlideActive, useSlideContext } from '@slidev/client'
import type { Kennzahlen, Zaehler } from '../logik/modell'
import { erzeuge, ladeKennzahlen, ladeModell, zahl, zeigeZeichen } from '../logik/modell'

const { $clicks } = useSlideContext()
const aktiv = useIsSlideActive()
const daten = ref<Kennzahlen | null>(null)
const beispiel = ref('')
let modell0: Zaehler | null = null

ladeKennzahlen().then(d => daten.value = d)

const groesste = computed(() => Math.max(...(daten.value?.haeufigkeit ?? [1])))
const oben = computed(() => {
  if (!daten.value)
    return []
  const d = daten.value
  return d.zeichen.map((z, i) => ({ z, anteil: d.haeufigkeit[i] / d.laenge }))
    .sort((a, b) => b.anteil - a.anteil).slice(0, 4)
})

watch([$clicks, aktiv], async ([klicks, jetzt]) => {
  if (jetzt && klicks >= 3) {
    modell0 ??= await ladeModell(0)
    beispiel.value = erzeuge(modell0, '', 90, 0).replace(/\n/g, ' ')
  }
}, { immediate: true })
</script>

<template>
  <div v-if="daten" class="alphabet">
    <div class="raster">
      <div
        v-for="(z, i) in daten.zeichen" :key="i" class="feld"
        :style="{ transitionDelay: `${i * 18}ms` }"
      >
        <div class="fuellung" :style="{ height: $clicks >= 2 ? `${(daten.haeufigkeit[i] / groesste) * 100}%` : '0%', transitionDelay: `${i * 18}ms` }" />
        <span class="z">{{ zeigeZeichen(z) }}</span>
        <span class="id" :class="{ an: $clicks >= 1 }" :style="{ transitionDelay: `${i * 25}ms` }">{{ i }}</span>
      </div>
    </div>

    <div class="unten">
      <div class="haeufig" :class="{ an: $clicks >= 2 }">
        <span class="beschriftung">am häufigsten</span>
        <span v-for="o in oben" :key="o.z" class="eintrag"><span class="zk">{{ zeigeZeichen(o.z) }}</span>{{ zahl(o.anteil * 100, 1) }} %</span>
        <span class="leise">bei {{ zahl(daten.laenge) }} Zeichen</span>
      </div>
      <div class="beispiel karte" :class="{ an: $clicks >= 3 }">
        <span class="beschriftung">nur nach Häufigkeit gezogen</span>
        <div class="text">{{ beispiel }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.alphabet {
  margin-top: 1.4rem;
}

.raster {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 0.6rem;
}

.feld {
  position: relative;
  height: 4.2rem;
  border-radius: 10px;
  background: var(--flaeche);
  border: 1px solid var(--linie);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fuellung {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to top, rgba(42, 120, 214, 0.35), rgba(42, 120, 214, 0.12));
  transition: height 0.9s cubic-bezier(.2, .8, .2, 1);
}

.z {
  position: relative;
  font-family: var(--mono);
  font-size: 1.6rem;
}

.id {
  position: absolute;
  right: 0.4rem;
  bottom: 0.25rem;
  font-family: var(--mono);
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--orange);
  opacity: 0;
  transform: translateY(6px);
  transition: opacity 0.4s, transform 0.4s;
}

.id.an {
  opacity: 1;
  transform: none;
}

.unten {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1.3rem;
}

.haeufig {
  display: flex;
  align-items: center;
  gap: 1.3rem;
  font-family: var(--mono);
  font-size: 1.05rem;
  opacity: 0;
  transition: opacity 0.6s 0.6s;
}

.haeufig.an {
  opacity: 1;
}

.eintrag {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.leise {
  font-size: 0.85rem;
  color: var(--text-sehr-leise);
}

.beispiel {
  padding: 0.8rem 1.1rem;
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.6s, transform 0.6s;
}

.beispiel.an {
  opacity: 1;
  transform: none;
}

.beispiel .text {
  margin-top: 0.4rem;
  font-family: var(--mono);
  font-size: 1.2rem;
  white-space: pre-wrap;
}
</style>
