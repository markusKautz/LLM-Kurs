<!--
  Drei Zeichen als Eingabe: One-Hot wäre riesig, Koordinaten sind klein.
  Klick 1: One-Hot für drei Zeichen · Klick 2: Koordinaten-Tabelle · Klick 3: nachschlagen · Klick 4: nebeneinanderlegen
-->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { useSlideContext } from '@slidev/client'
import { zahl, zeigeZeichen } from '../logik/modell'
import { ladeJson } from '../logik/netz'

const props = withDefaults(defineProps<{ kontext?: string }>(), { kontext: 'der' })

const { $clicks } = useSlideContext()
const karte = ref<{ zeichen: string[], staende: number[][][] } | null>(null)
ladeJson<{ zeichen: string[], staende: number[][][] }>('netz_karte.json').then(d => karte.value = d)

const ZEILEN = ['a', 'd', 'e', 'i', 'n', 'r', 's']
const tabelle = computed(() => {
  if (!karte.value)
    return []
  const ende = karte.value.staende[karte.value.staende.length - 1]
  return ZEILEN.map(z => ({ z, k: ende[karte.value!.zeichen.indexOf(z)] }))
})
const nachgeschlagen = computed(() => [...props.kontext].map(z => tabelle.value.find(t => t.z === z)?.k ?? [0, 0]))
</script>

<template>
  <div v-if="karte" class="einbettung">
    <div class="links">
      <div class="kontext">
        <span v-for="(z, i) in props.kontext" :key="i" class="zk gross" :class="{ leuchtet: $clicks >= 3 }">{{ zeigeZeichen(z) }}</span>
      </div>

      <div class="weg onehot" :class="{ an: $clicks >= 1, durch: $clicks >= 2 }">
        <div class="beschriftung">als One-Hot</div>
        <div class="streifen">
          <div v-for="i in 3" :key="i" class="streifen-zeile">
            <span v-for="k in 40" :key="k" class="punkt" :class="{ eins: k === 9 + i * 7 }" />
          </div>
        </div>
        <div class="zahl-text">3 × 40 = <b>120 Zahlen</b>, fast alle 0</div>
      </div>

      <div class="weg koordinaten" :class="{ an: $clicks >= 4 }">
        <div class="beschriftung">als Koordinaten, nebeneinander</div>
        <div class="vektor">
          <template v-for="(k, i) in nachgeschlagen" :key="i">
            <span class="paar"><span>{{ zahl(k[0], 2) }}</span><span>{{ zahl(k[1], 2) }}</span></span>
          </template>
        </div>
        <div class="zahl-text">3 × 2 = <b>6 Zahlen</b></div>
      </div>
    </div>

    <div class="tabelle karte" :class="{ an: $clicks >= 2 }">
      <div class="beschriftung">Koordinaten-Tabelle (wird gelernt)</div>
      <div class="kopf"><span>Zeichen</span><span>x</span><span>y</span></div>
      <div v-for="t in tabelle" :key="t.z" class="zeile" :class="{ treffer: $clicks >= 3 && props.kontext.includes(t.z) }">
        <span class="zk">{{ zeigeZeichen(t.z) }}</span>
        <span>{{ zahl(t.k[0], 2) }}</span>
        <span>{{ zahl(t.k[1], 2) }}</span>
      </div>
      <div class="punkte">… eine Zeile für jedes der 40 Zeichen</div>
    </div>
  </div>
</template>

<style scoped>
.einbettung {
  display: grid;
  grid-template-columns: 1fr 22rem;
  gap: 2.5rem;
  margin-top: 1.4rem;
}

.links {
  display: flex;
  flex-direction: column;
  gap: 1.4rem;
}

.kontext {
  display: flex;
  gap: 0.6rem;
}

.zk.gross {
  min-width: 3.4rem;
  height: 3.4rem;
  font-size: 1.8rem;
  transition: border-color 0.4s, box-shadow 0.4s;
}

.zk.gross.leuchtet {
  border-color: var(--orange);
  box-shadow: var(--leuchten-orange);
}

.weg {
  padding: 1rem 1.2rem;
  border-radius: 14px;
  border: 1px solid var(--linie);
  background: var(--flaeche);
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.6s, transform 0.6s;
}

.weg.an {
  opacity: 1;
  transform: none;
}

.weg.durch {
  opacity: 0.4;
}

.streifen {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin: 0.7rem 0;
}

.streifen-zeile {
  display: flex;
  gap: 3px;
}

.punkt {
  width: 11px;
  height: 11px;
  border-radius: 2px;
  background: var(--flaeche-hell);
}

.punkt.eins {
  background: var(--orange);
}

.zahl-text {
  font-size: 1.05rem;
  color: var(--text-leise);
}

.zahl-text b {
  color: var(--text);
}

.vektor {
  display: flex;
  gap: 0.6rem;
  margin: 0.7rem 0;
}

.paar {
  display: flex;
  border: 2px solid var(--orange);
  border-radius: 8px;
  overflow: hidden;
}

.paar span {
  padding: 0.35rem 0.55rem;
  font-family: var(--mono);
  font-size: 1.1rem;
  background: var(--flaeche);
}

.paar span + span {
  border-left: 1px solid var(--linie);
}

.tabelle {
  padding: 1rem 1.2rem;
  opacity: 0;
  transform: translateX(14px);
  transition: opacity 0.6s, transform 0.6s;
}

.tabelle.an {
  opacity: 1;
  transform: none;
}

.kopf,
.zeile {
  display: grid;
  grid-template-columns: 4.5rem 1fr 1fr;
  align-items: center;
  gap: 0.5rem;
  font-family: var(--mono);
  text-align: right;
}

.kopf {
  margin-top: 0.6rem;
  padding-bottom: 0.3rem;
  border-bottom: 1px solid var(--linie);
  font-size: 0.85rem;
  color: var(--text-leise);
}

.kopf span:first-child,
.zeile .zk {
  justify-self: start;
}

.zeile {
  padding: 0.25rem 0.4rem;
  margin: 0.15rem -0.4rem;
  border-radius: 8px;
  font-size: 1.05rem;
  transition: background 0.4s;
}

.zeile.treffer {
  background: var(--orange-hauch);
  color: var(--orange);
  font-weight: 700;
}

.punkte {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: var(--text-sehr-leise);
}
</style>
