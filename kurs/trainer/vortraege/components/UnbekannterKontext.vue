<!--
  Ein Kontext, der im Training nie vorkam. Das Zählmodell weiß nichts, das Netz verallgemeinert.
  Klick 1: wo der Kontext im Test steht · Klick 2: Zählmodell · Klick 3: das Netz
-->
<script setup lang="ts">
import { computed, ref, shallowRef } from 'vue'
import { useSlideContext } from '@slidev/client'
import { zahl, zeigeZeichen } from '../logik/modell'
import type { NetzDaten } from '../logik/netz'
import { durchlauf, ladeJson, ladeNetz } from '../logik/netz'

type Fall = { kontext: string, richtig: string, p: number, umfeld: string }

const props = withDefaults(defineProps<{ kontext?: string }>(), { kontext: 'hnc' })

const { $clicks } = useSlideContext()
const netz = shallowRef<NetzDaten | null>(null)
const fall = ref<Fall | null>(null)
ladeNetz().then(n => netz.value = n)
ladeJson<{ unbekannt: Fall[] }>('vergleich.json').then((d) => {
  fall.value = d.unbekannt.find(f => f.kontext === props.kontext) ?? d.unbekannt[0]
})

const oben = computed(() => {
  if (!netz.value || !fall.value)
    return []
  return durchlauf(netz.value, fall.value.kontext).wahrscheinlichkeiten
    .map((p, i) => ({ z: netz.value!.zeichen[i], p })).sort((a, b) => b.p - a.p).slice(0, 5)
})
const umfeldTeile = computed(() => {
  if (!fall.value)
    return []
  const i = fall.value.umfeld.indexOf(fall.value.kontext)
  return [fall.value.umfeld.slice(0, i), fall.value.kontext, fall.value.umfeld.slice(i + 3, i + 4), fall.value.umfeld.slice(i + 4)]
})
</script>

<template>
  <div v-if="fall && netz" class="unbekannt">
    <div class="satz karte" :class="{ an: $clicks >= 1 }">
      <div class="beschriftung">aus dem Testtext</div>
      <div class="text">
        …{{ umfeldTeile[0] }}<span class="kontext">{{ umfeldTeile[1] }}</span><span class="richtig">{{ umfeldTeile[2] }}</span>{{ umfeldTeile[3] }}…
      </div>
      <div class="klein">„{{ fall.kontext }}“ kam im ganzen Training <b>kein einziges Mal</b> vor.</div>
    </div>

    <div class="vergleich">
      <div class="seite karte" :class="{ an: $clicks >= 2 }">
        <div class="titel">Zählmodell, 3 Zeichen</div>
        <div class="nichts">
          <div class="gross">?</div>
          <div>Diesen Kontext hat es nie gezählt.<br>Es hat <b>keine Antwort</b>.</div>
        </div>
      </div>
      <div class="seite karte" :class="{ an: $clicks >= 3 }">
        <div class="titel">Netz, 3 Zeichen</div>
        <div v-for="e in oben" :key="e.z" class="eintrag" :class="{ treffer: e.z === fall.richtig }">
          <span class="zk">{{ zeigeZeichen(e.z) }}</span>
          <span class="spur"><span :style="{ width: `${e.p * 100}%` }" /></span>
          <span class="prozent">{{ zahl(e.p * 100) }} %</span>
        </div>
        <div class="klein">Richtig wäre „{{ fall.richtig }}“. Das Netz hat ähnliche Kontexte gesehen.</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.unbekannt {
  display: flex;
  flex-direction: column;
  gap: 1.4rem;
  margin-top: 1.2rem;
}

.satz {
  padding: 1rem 1.4rem;
  opacity: 0;
  transition: opacity 0.6s;
}

.satz.an {
  opacity: 1;
}

.text {
  margin: 0.4rem 0;
  font-family: var(--mono);
  font-size: 1.6rem;
}

.kontext {
  border-radius: 6px;
  background: var(--orange-hauch);
  box-shadow: inset 0 0 0 2px var(--orange);
  color: var(--orange);
  padding: 0 0.15rem;
}

.richtig {
  text-decoration: underline;
  text-decoration-color: var(--blau);
  text-decoration-thickness: 3px;
  text-underline-offset: 6px;
}

.klein {
  font-size: 1rem;
  color: var(--text-leise);
}

.vergleich {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.6rem;
}

.seite {
  padding: 1.1rem 1.4rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.6s, transform 0.6s;
}

.seite.an {
  opacity: 1;
  transform: none;
}

.titel {
  font-size: 1.2rem;
  font-weight: 650;
}

.nichts {
  display: flex;
  align-items: center;
  gap: 1.2rem;
  font-size: 1.15rem;
  color: var(--text-leise);
  margin-top: 0.6rem;
}

.gross {
  font-family: var(--mono);
  font-size: 4rem;
  font-weight: 700;
  color: var(--text-sehr-leise);
}

.eintrag {
  display: grid;
  grid-template-columns: 2.4rem 1fr 3.6rem;
  align-items: center;
  gap: 0.6rem;
}

.spur {
  height: 0.7rem;
  border-radius: 5px;
  background: var(--flaeche-hell);
  overflow: hidden;
}

.spur span {
  display: block;
  height: 100%;
  border-radius: 5px;
  background: var(--text-sehr-leise);
}

.treffer .spur span {
  background: var(--blau);
}

.treffer .zk {
  border-color: var(--blau);
  color: var(--blau);
  font-weight: 700;
}

.prozent {
  font-family: var(--mono);
  text-align: right;
  color: var(--text-leise);
}
</style>
