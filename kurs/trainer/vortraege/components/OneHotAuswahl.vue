<!--
  Der Aha-Moment aus Notebook 2: Ein One-Hot-Vektor mal eine Matrix wählt genau eine Zeile aus.
  Die Matrix enthält die gezählten Wahrscheinlichkeiten für fünf häufige Zeichen.
  Klick 1: One-Hot für "e" · Klick 2: jede Zeile wird mit 0 oder 1 malgenommen · Klick 3: übrig bleibt die Zeile von "e"
  Klick 4: anderes Zeichen
-->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { useSlideContext } from '@slidev/client'
import type { Kennzahlen } from '../logik/modell'
import { ladeKennzahlen, zahl, zeigeZeichen } from '../logik/modell'

const AUSWAHL = [' ', 'a', 'e', 'n', 'r']

const { $clicks } = useSlideContext()
const daten = ref<Kennzahlen | null>(null)
ladeKennzahlen().then(d => daten.value = d)

// Gezählte Wahrscheinlichkeiten, nur für die fünf Zeichen, jede Zeile neu auf 100 % gebracht
const matrix = computed(() => {
  if (!daten.value)
    return []
  const d = daten.value
  return AUSWAHL.map((a) => {
    const zeile = AUSWAHL.map(b => d.bigramme[d.zeichen.indexOf(a)][d.zeichen.indexOf(b)])
    const summe = zeile.reduce((x, y) => x + y, 0)
    return zeile.map(v => v / summe)
  })
})

const gewaehlt = computed(() => $clicks.value >= 4 ? 3 : 2)
const onehot = computed(() => AUSWAHL.map((_, i) => (i === gewaehlt.value ? 1 : 0)))
</script>

<template>
  <div v-if="daten" class="onehot">
    <div class="block">
      <div class="beschriftung">One-Hot für „{{ zeigeZeichen(AUSWAHL[gewaehlt]) }}“</div>
      <div class="vektor" :class="{ an: $clicks >= 1 }">
        <div v-for="(v, i) in onehot" :key="i" class="zelle" :class="{ eins: v === 1 }">{{ v }}</div>
      </div>
      <div class="vektor-zeichen">
        <span v-for="z in AUSWAHL" :key="z">{{ zeigeZeichen(z) }}</span>
      </div>
    </div>

    <div class="mal">@</div>

    <div class="block">
      <div class="beschriftung">Matrix: Zeile = jetzt, Spalte = danach</div>
      <div class="matrix">
        <div class="kopfzeile">
          <span />
          <span v-for="z in AUSWAHL" :key="z">{{ zeigeZeichen(z) }}</span>
        </div>
        <div
          v-for="(zeile, i) in matrix" :key="i" class="zeile"
          :class="{ aus: $clicks >= 2 && i !== gewaehlt, gewaehlt: $clicks >= 2 && i === gewaehlt }"
        >
          <span class="faktor" :class="{ an: $clicks >= 2 }">{{ onehot[i] }} ×</span>
          <span class="zk">{{ zeigeZeichen(AUSWAHL[i]) }}</span>
          <span v-for="(p, j) in zeile" :key="j" class="wert">{{ zahl(p * 100) }}</span>
        </div>
      </div>
    </div>

    <div class="mal">=</div>

    <div class="block">
      <div class="beschriftung">Ergebnis</div>
      <div class="ergebnis" :class="{ an: $clicks >= 3 }">
        <span v-for="(p, j) in matrix[gewaehlt]" :key="`${gewaehlt}-${j}`" class="wert">{{ zahl(p * 100) }}</span>
      </div>
      <div class="erklaerung" :class="{ an: $clicks >= 3 }">genau die Zeile von „{{ zeigeZeichen(AUSWAHL[gewaehlt]) }}“</div>
    </div>
  </div>
</template>

<style scoped>
.onehot {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.6rem;
  margin-top: 2.2rem;
}

.block {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.6rem;
}

.mal {
  font-family: var(--mono);
  font-size: 2.2rem;
  color: var(--text-sehr-leise);
}

.vektor {
  display: flex;
  flex-direction: column;
  opacity: 0.2;
  transition: opacity 0.5s;
}

.vektor.an {
  opacity: 1;
}

.zelle {
  display: grid;
  place-items: center;
  width: 2.6rem;
  height: 2.6rem;
  margin-top: -2px;
  border: 2px solid var(--linie);
  background: var(--flaeche);
  font-family: var(--mono);
  font-size: 1.2rem;
  color: var(--text-sehr-leise);
}

.zelle.eins {
  border-color: var(--orange);
  background: var(--orange);
  color: #fff;
  font-weight: 700;
}

.vektor-zeichen {
  display: none;
}

.matrix {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.kopfzeile,
.zeile {
  display: grid;
  grid-template-columns: 3rem 2.4rem repeat(5, 3.6rem);
  align-items: center;
  gap: 0.3rem;
  font-family: var(--mono);
  text-align: center;
}

.kopfzeile {
  grid-template-columns: 5.7rem repeat(5, 3.6rem);
  color: var(--text-leise);
}

.zeile {
  padding: 0.25rem 0.4rem;
  border-radius: 10px;
  transition: opacity 0.5s, background 0.5s;
}

.zeile.aus {
  opacity: 0.18;
}

.zeile.gewaehlt {
  background: var(--orange-hauch);
  box-shadow: inset 0 0 0 2px var(--orange);
}

.faktor {
  color: var(--orange);
  font-weight: 700;
  opacity: 0;
  transition: opacity 0.4s;
}

.faktor.an {
  opacity: 1;
}

.wert {
  font-size: 1.15rem;
}

.ergebnis {
  display: flex;
  gap: 0.3rem;
  padding: 0.5rem;
  border-radius: 10px;
  border: 2px solid var(--orange);
  background: var(--flaeche);
  opacity: 0;
  transform: translateX(-20px);
  transition: opacity 0.6s, transform 0.6s;
}

.ergebnis .wert {
  width: 3.2rem;
  text-align: center;
  font-family: var(--mono);
}

.ergebnis.an,
.erklaerung.an {
  opacity: 1;
  transform: none;
}

.erklaerung {
  font-size: 1rem;
  color: var(--orange);
  opacity: 0;
  transition: opacity 0.6s 0.3s;
}
</style>
