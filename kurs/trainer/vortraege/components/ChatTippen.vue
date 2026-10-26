<!--
  Ein Chatfenster, in dem die Antwort Stück für Stück erscheint.
  Klick 1: die Antwort entsteht
  Klick 2: die Stücke (Tokens) werden sichtbar
-->
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useIsSlideActive, useSlideContext } from '@slidev/client'
import { pause } from '../logik/modell'

const FRAGE = 'Erklär mir in einem Satz, was ein Compiler macht.'
// Ungefähr so zerlegt ein Sprachmodell den Text in Stücke
const STUECKE = ['Ein', ' Comp', 'iler', ' über', 'setzt', ' den', ' Quell', 'text', ',', ' den', ' du', ' schreib', 'st', ',', ' in',
  ' Maschinen', 'code', ',', ' den', ' der', ' Prozess', 'or', ' direkt', ' aus', 'führen', ' kann', '.']

const { $clicks } = useSlideContext()
const aktiv = useIsSlideActive()
const sichtbar = ref(0)
const neu = ref(-1)
let lauf = 0

async function tippen(meinLauf: number) {
  sichtbar.value = 0
  await pause(500)
  for (let i = 1; i <= STUECKE.length; i++) {
    if (meinLauf !== lauf)
      return
    sichtbar.value = i
    neu.value = i - 1
    await pause(170 + Math.random() * 120)
  }
  neu.value = -1
}

watch([$clicks, aktiv], ([klicks, jetzt]) => {
  const meinLauf = ++lauf
  if (!jetzt)
    return
  if (klicks === 0)
    sichtbar.value = 0
  else if (klicks === 1)
    tippen(meinLauf)
  else
    sichtbar.value = STUECKE.length
}, { immediate: true })
</script>

<template>
  <div class="chat karte" :class="{ an: $clicks >= 1 }">
    <div class="kopf">
      <span class="punkt" /><span class="punkt" /><span class="punkt" />
      <span class="name">Chat</span>
    </div>
    <div class="verlauf">
      <div class="blase frage">{{ FRAGE }}</div>
      <div class="blase antwort" :class="{ stuecke: $clicks >= 2 }">
        <span
          v-for="(stueck, i) in STUECKE.slice(0, sichtbar)" :key="i"
          class="stueck" :class="{ neu: i === neu, ungerade: i % 2 === 1 }"
        >{{ stueck }}</span><span v-if="sichtbar < STUECKE.length && $clicks >= 1" class="cursor" />
      </div>
    </div>
    <div class="fuss" :class="{ an: $clicks >= 2 }">
      {{ STUECKE.length }} Stücke, eines nach dem anderen. Diese Stücke heißen <b>Tokens</b>.
    </div>
  </div>
</template>

<style scoped>
.chat {
  width: 820px;
  margin: 1.6rem auto 0;
  overflow: hidden;
  opacity: 0;
  transform: translateY(16px) scale(0.98);
  transition: opacity 0.6s, transform 0.6s;
}

.chat.an {
  opacity: 1;
  transform: none;
}

.kopf {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.75rem 1.1rem;
  border-bottom: 1px solid var(--linie);
  background: var(--flaeche-hell);
}

.punkt {
  width: 0.7rem;
  height: 0.7rem;
  border-radius: 50%;
  background: var(--linie);
}

.name {
  margin-left: 0.6rem;
  font-size: 0.85rem;
  color: var(--text-leise);
}

.verlauf {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.4rem 1.5rem;
  min-height: 15rem;
}

.blase {
  max-width: 82%;
  padding: 0.8rem 1.1rem;
  border-radius: 14px;
  font-size: 1.3rem;
  line-height: 1.6;
}

.frage {
  align-self: flex-end;
  background: var(--blau);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.antwort {
  align-self: flex-start;
  background: var(--flaeche-hell);
  border-bottom-left-radius: 4px;
  white-space: pre-wrap;
}

.stueck {
  border-radius: 4px;
  transition: background 0.4s, box-shadow 0.4s;
}

.stueck.neu {
  background: rgba(235, 104, 52, 0.25);
}

/* Klick 2: die Grenzen der Stücke werden sichtbar */
.antwort.stuecke .stueck {
  background: rgba(42, 120, 214, 0.14);
  box-shadow: inset 0 -2px 0 rgba(42, 120, 214, 0.5);
}

.antwort.stuecke .stueck.ungerade {
  background: rgba(235, 104, 52, 0.14);
  box-shadow: inset 0 -2px 0 rgba(235, 104, 52, 0.55);
}

.cursor {
  display: inline-block;
  width: 0.5em;
  height: 1em;
  margin-left: 2px;
  vertical-align: -0.12em;
  border-radius: 2px;
  background: var(--text);
  animation: blinken 0.9s steps(1) infinite;
}

@keyframes blinken {
  50% { opacity: 0; }
}

.fuss {
  padding: 0.9rem 1.5rem;
  border-top: 1px solid var(--linie);
  font-size: 1.1rem;
  color: var(--text-leise);
  opacity: 0;
  transition: opacity 0.5s;
}

.fuss.an {
  opacity: 1;
}
</style>
