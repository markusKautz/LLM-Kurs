<!--
  Großer Kontext braucht viel Text: unbekannte Kontexte im Test bei immer mehr Trainingstext (echte Messung).
  Klick 1: wenig Text · Klick 2: immer mehr Text · Klick 3: doppelt so viel hilft wenig
  Klick 4: auch gesehene Kontexte kamen oft nur einmal vor · Klick 5: Merksatz
-->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { useSlideContext } from '@slidev/client'
import type { Kennzahlen } from '../logik/modell'
import { ladeKennzahlen, zahl } from '../logik/modell'

const props = withDefaults(defineProps<{ n?: number }>(), { n: 6 })

const { $clicks } = useSlideContext()
const daten = ref<Kennzahlen | null>(null)
ladeKennzahlen().then(d => daten.value = d)

const stufen = computed(() => daten.value?.datenhunger.stufen ?? [])
const meisteZeichen = computed(() => Math.max(...stufen.value.map(s => s.zeichen), 1))
const unbekannt = (s: { unbekannt: Record<string, number> }) => s.unbekannt[props.n]
// Die Balken für "unbekannt" reichen bis 50 %
const breite = (anteil: number) => `${Math.min(anteil / 0.5, 1) * 100}%`
const sichtbar = (i: number) => i === 0 ? $clicks.value >= 1 : $clicks.value >= 2
const einmalAnteil = computed(() => daten.value ? daten.value.datenhunger.einmal / daten.value.datenhunger.kontexte : 0)
</script>

<template>
  <div v-if="daten" class="hunger">
    <div class="tabelle karte">
      <div class="kopf">
        <span>Trainingstext</span>
        <span />
        <span class="orange">im Test nie gesehene Kontexte ({{ n }} Zeichen)</span>
      </div>
      <div v-for="(s, i) in stufen" :key="i" class="zeile" :class="{ an: sichtbar(i) }" :style="{ transitionDelay: i > 0 ? `${(i - 1) * 350}ms` : '0ms' }">
        <span class="menge">{{ zahl(s.zeichen) }} Zeichen</span>
        <span class="spur"><span class="blau" :style="{ width: sichtbar(i) ? `${(s.zeichen / meisteZeichen) * 100}%` : '0%', transitionDelay: i > 0 ? `${(i - 1) * 350}ms` : '0ms' }" /></span>
        <span class="ergebnis">
          <span class="spur"><span class="orange-balken" :style="{ width: sichtbar(i) ? breite(unbekannt(s)) : '0%', transitionDelay: i > 0 ? `${(i - 1) * 350 + 200}ms` : '200ms' }" /></span>
          <b>{{ zahl(unbekannt(s) * 100, 0) }} %</b>
        </span>
      </div>
      <div class="hinweis" :class="{ an: $clicks >= 3 }">
        Doppelt so viel Text: von {{ zahl(unbekannt(stufen[2]) * 100, 0) }} % nur auf {{ zahl(unbekannt(stufen[3]) * 100, 0) }} %.
        Mehr Text hilft, aber immer langsamer.
      </div>
    </div>

    <div class="einmal karte" :class="{ an: $clicks >= 4 }">
      <div class="beschriftung">und die Kontexte, die das Modell gesehen hat?</div>
      <div class="einmal-zeile">
        <div>
          <div class="geteilt">
            <span class="teil-einmal" :style="{ width: `${einmalAnteil * 100}%` }" />
            <span class="teil-oefter" />
          </div>
          <div class="legende"><span class="orange">{{ zahl(einmalAnteil * 100, 0) }} % nur einmal</span><span>öfter</span></div>
        </div>
        <div class="einmal-text">
          <b>{{ zahl(daten.datenhunger.einmal) }}</b> von {{ zahl(daten.datenhunger.kontexte) }} Kontexten mit {{ n }} Zeichen
          kamen im Training <b>nur ein einziges Mal</b> vor. Die „Wahrscheinlichkeit“ beruht dort auf einem einzigen Beispiel.
        </div>
      </div>
    </div>
  </div>
  <div class="merksatz text-center mt-4 schluss" :class="{ an: $clicks >= 5 }">
    Wer nur zählt, braucht für langen Kontext <span class="akzent">riesige</span> Textmengen.
  </div>
</template>

<style scoped>
.hunger {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
  margin-top: 1.1rem;
}

.tabelle {
  padding: 1rem 1.4rem 0.9rem;
}

.kopf,
.zeile {
  display: grid;
  grid-template-columns: 11rem 1fr 1.3fr;
  align-items: center;
  gap: 1.4rem;
}

.kopf {
  font-size: 0.95rem;
  color: var(--text-leise);
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--linie);
}

.orange {
  color: var(--orange);
  font-weight: 650;
}

.zeile {
  padding: 0.55rem 0;
  border-bottom: 1px solid var(--linie);
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.5s, transform 0.5s;
}

.zeile.an {
  opacity: 1;
  transform: none;
}

.menge {
  font-family: var(--mono);
  font-size: 1.15rem;
}

.spur {
  display: block;
  height: 0.8rem;
  border-radius: 5px;
  background: var(--flaeche-hell);
  overflow: hidden;
}

.spur span {
  display: block;
  height: 100%;
  border-radius: 5px;
  transition: width 0.9s cubic-bezier(.2, .8, .2, 1);
}

.blau {
  background: var(--blau);
}

.orange-balken {
  background: var(--orange);
}

.ergebnis {
  display: grid;
  grid-template-columns: 1fr 4rem;
  align-items: center;
  gap: 0.8rem;
}

.ergebnis b {
  font-family: var(--mono);
  font-size: 1.3rem;
  color: var(--orange);
  text-align: right;
}

.hinweis {
  margin-top: 0.7rem;
  font-size: 1.05rem;
  font-weight: 600;
  opacity: 0;
  transition: opacity 0.6s;
}

.hinweis.an {
  opacity: 1;
}

.einmal {
  padding: 0.9rem 1.4rem;
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.6s, transform 0.6s;
}

.einmal.an {
  opacity: 1;
  transform: none;
}

.einmal-zeile {
  display: grid;
  grid-template-columns: 14rem 1fr;
  align-items: center;
  gap: 1.4rem;
  margin-top: 0.4rem;
}

.geteilt {
  display: flex;
  gap: 2px;
  height: 1.4rem;
}

.teil-einmal {
  border-radius: 5px;
  background: var(--orange);
}

.teil-oefter {
  flex: 1;
  border-radius: 5px;
  background: var(--flaeche-hell);
}

.legende {
  display: flex;
  justify-content: space-between;
  margin-top: 0.3rem;
  font-size: 0.85rem;
  color: var(--text-leise);
}

.einmal-text {
  font-size: 1.02rem;
  line-height: 1.45;
}

.schluss {
  opacity: 0;
  transition: opacity 0.6s;
}

.schluss.an {
  opacity: 1;
}
</style>
