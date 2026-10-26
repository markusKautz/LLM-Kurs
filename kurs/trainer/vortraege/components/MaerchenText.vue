<!--
  Der Text, aus dem alle Modelle lernen. Links läuft ein Stück echter Text langsam durch.
  Klick 1: woher der Text kommt · Klick 2: wie viel es ist · Klick 3: wie er aussieht · Klick 4: Merksatz
-->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { useIsSlideActive, useSlideContext } from '@slidev/client'
import type { Kennzahlen } from '../logik/modell'
import { ladeKennzahlen, zahl } from '../logik/modell'

// Eine Buchseite hat ungefähr 2.000 Zeichen
const ZEICHEN_PRO_SEITE = 2000

const { $clicks } = useSlideContext()
const aktiv = useIsSlideActive()
const daten = ref<Kennzahlen | null>(null)
ladeKennzahlen().then(d => daten.value = d)

// Ungerade Teile sind die Namen, die bei Klick 3 hervorgehoben werden
const teile = computed(() => daten.value?.auszug.split(/(hänsel|gretel)/) ?? [])
const seiten = computed(() => daten.value ? Math.round(daten.value.laenge / ZEICHEN_PRO_SEITE / 10) * 10 : 0)
</script>

<template>
  <div v-if="daten" class="maerchen">
    <div class="seite karte">
      <div class="fenster">
        <div class="lauftext" :class="{ laeuft: aktiv }">
          <template v-for="(t, i) in teile" :key="i">
            <span v-if="i % 2 === 1" class="name" :class="{ an: $clicks >= 3 }">{{ t }}</span>
            <template v-else>{{ t }}</template>
          </template>
        </div>
      </div>
    </div>

    <div class="fakten">
      <div class="fakt" :class="{ an: $clicks >= 1 }">
        <div class="beschriftung">woher</div>
        <div class="gross">Fast 60 Märchen der Brüder Grimm</div>
        <div class="klein">Hänsel und Gretel, Rotkäppchen, Die Bremer Stadtmusikanten … aus einer Ausgabe von 1921</div>
      </div>
      <div class="fakt" :class="{ an: $clicks >= 2 }">
        <div class="beschriftung">wie viel</div>
        <div class="zahlen">
          <div><b>{{ zahl(daten.laenge) }}</b><span>Zeichen</span></div>
          <div><b>{{ zahl(daten.woerter) }}</b><span>Wörter</span></div>
          <div><b>≈ {{ seiten }}</b><span>Buchseiten</span></div>
        </div>
      </div>
      <div class="fakt" :class="{ an: $clicks >= 3 }">
        <div class="beschriftung">wie er aussieht</div>
        <ul>
          <li>alles kleingeschrieben, auch <span class="name an">hänsel</span> und <span class="name an">gretel</span></li>
          <li>alte Rechtschreibung: „hieß“, „ist's“, „daß“</li>
          <li>keine Überschriften, ein Märchen nach dem anderen</li>
        </ul>
      </div>
    </div>
  </div>
  <div class="merksatz text-center mt-4 schluss" :class="{ an: $clicks >= 4 }">
    Dieser Text ist <span class="akzent">alles</span>, was unser Modell je zu lesen bekommt.
  </div>
</template>

<style scoped>
.maerchen {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 1.8rem;
  margin-top: 1.1rem;
}

.seite {
  padding: 1rem 1.4rem;
}

.fenster {
  height: 20.5rem;
  overflow: hidden;
  mask-image: linear-gradient(transparent, #000 12%, #000 82%, transparent);
}

.lauftext {
  font-family: var(--mono);
  font-size: 1.02rem;
  line-height: 1.7;
  white-space: pre-wrap;
  padding-top: 2rem;
  animation: lauf 110s linear infinite;
  animation-play-state: paused;
}

.lauftext.laeuft {
  animation-play-state: running;
}

@keyframes lauf {
  to { transform: translateY(-85%); }
}

.name {
  border-radius: 4px;
  transition: background 0.5s, color 0.5s, box-shadow 0.5s;
}

.name.an {
  background: rgba(42, 120, 214, 0.1);
  box-shadow: inset 0 0 0 1.5px var(--blau);
  color: var(--blau-tief);
}

.fakten {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.fakt {
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.5s, transform 0.5s;
}

.fakt.an {
  opacity: 1;
  transform: none;
}

.gross {
  font-size: 1.45rem;
  font-weight: 700;
  margin-top: 0.15rem;
}

.klein {
  font-size: 0.95rem;
  color: var(--text-leise);
  margin-top: 0.2rem;
}

.zahlen {
  display: flex;
  gap: 1.8rem;
  margin-top: 0.3rem;
}

.zahlen div {
  display: flex;
  flex-direction: column;
}

.zahlen b {
  font-family: var(--mono);
  font-size: 1.6rem;
  color: var(--blau);
}

.zahlen span {
  font-size: 0.95rem;
  color: var(--text-leise);
}

ul {
  margin: 0.3rem 0 0;
  padding-left: 1.2rem;
  font-size: 1.05rem;
  line-height: 1.6;
}

.schluss {
  opacity: 0;
  transition: opacity 0.6s;
}

.schluss.an {
  opacity: 1;
}
</style>
