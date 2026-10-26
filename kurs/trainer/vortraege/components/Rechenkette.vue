<!--
  Wie PyTorch die Steigung findet: erst vorwärts rechnen, dann die Steigung rückwärts weiterreichen.
  Beispiel aus Notebook 2: Verlust = (w − 3)² + 1 an der Stelle w = 0,5
  Klick 1: vorwärts · Klick 2: rückwärts · Klick 3: was die Steigung bedeutet
-->
<script setup lang="ts">
import { useSlideContext } from '@slidev/client'

const { $clicks } = useSlideContext()

// Jeder Kasten ist ein Rechenschritt mit seinem Ergebnis.
// "rueck": Wie stark ändert sich der Verlust, wenn sich dieses Ergebnis ein bisschen ändert?
// "regel": womit dieser Schritt die Steigung beim Rückweg malnimmt
const SCHRITTE = [
  { name: 'w', wert: '0,5', rueck: '−5', regel: '' },
  { name: '− 3', wert: '−2,5', rueck: '−5', regel: '× 1' },
  { name: 'hoch 2', wert: '6,25', rueck: '1', regel: '× 2 × (−2,5)' },
  { name: '+ 1 = Verlust', wert: '7,25', rueck: '1', regel: '× 1' },
]
</script>

<template>
  <div class="kette">
    <div class="reihe">
      <template v-for="(s, i) in SCHRITTE" :key="i">
        <div class="kasten" :class="{ start: i === 0, ende: i === SCHRITTE.length - 1, an: $clicks >= 1 }" :style="{ transitionDelay: `${i * 350}ms` }">
          <div class="name">{{ s.name }}</div>
          <div class="wert">{{ s.wert }}</div>
          <div class="rueck" :class="{ an: $clicks >= 2 }" :style="{ transitionDelay: `${(SCHRITTE.length - i) * 450}ms` }">
            Steigung {{ s.rueck }}
          </div>
        </div>
        <div v-if="i < SCHRITTE.length - 1" class="verbindung">
          <svg viewBox="0 0 90 60" class="pfeil vor" :class="{ an: $clicks >= 1 }" :style="{ transitionDelay: `${i * 350 + 200}ms` }"><path d="M2 18h80m-8-7 8 7-8 7" /></svg>
          <svg viewBox="0 0 90 60" class="pfeil zurueck" :class="{ an: $clicks >= 2 }" :style="{ transitionDelay: `${(SCHRITTE.length - 1 - i) * 450 + 250}ms` }"><path d="M88 44H8m8-7-8 7 8 7" /></svg>
          <span class="regel" :class="{ an: $clicks >= 2 }" :style="{ transitionDelay: `${(SCHRITTE.length - 1 - i) * 450 + 250}ms` }">{{ SCHRITTE[i + 1].regel }}</span>
        </div>
      </template>
    </div>

    <div class="legende">
      <span class="vor-farbe" :class="{ an: $clicks >= 1 }">vorwärts: rechnen</span>
      <span class="rueck-farbe" :class="{ an: $clicks >= 2 }">rückwärts: Steigung weiterreichen, Schritt für Schritt malnehmen</span>
    </div>

    <div class="code karte" :class="{ an: $clicks >= 3 }">
      <div><span class="k">verlust</span>.backward()</div>
      <div><span class="k">w</span>.grad  <span class="leise"># −5</span></div>
      <div class="satz">Steigung −5: Nach rechts geht es bergab. Also <b>w größer machen</b>.</div>
    </div>
  </div>
</template>

<style scoped>
.kette {
  margin-top: 2rem;
}

.reihe {
  display: flex;
  align-items: center;
  justify-content: center;
}

.kasten {
  width: 10rem;
  padding: 0.9rem 0.6rem;
  border-radius: 14px;
  background: var(--flaeche);
  border: 2px solid var(--linie);
  box-shadow: var(--schatten);
  text-align: center;
  opacity: 0.25;
  transition: opacity 0.5s, border-color 0.5s;
}

.kasten.an {
  opacity: 1;
  border-color: var(--blau);
}

.kasten.start.an {
  border-color: var(--text);
}

.kasten.ende.an {
  border-color: var(--orange);
}

.name {
  font-family: var(--mono);
  font-size: 1.05rem;
  color: var(--text-leise);
}

.wert {
  margin-top: 0.2rem;
  font-family: var(--mono);
  font-size: 1.7rem;
  font-weight: 700;
}

.rueck {
  margin-top: 0.5rem;
  padding: 0.25rem 0;
  border-radius: 8px;
  background: var(--orange-hauch);
  color: var(--orange);
  font-family: var(--mono);
  font-size: 0.95rem;
  font-weight: 700;
  opacity: 0;
  transition: opacity 0.5s;
}

.rueck.an {
  opacity: 1;
}

.verbindung {
  position: relative;
  width: 6rem;
  height: 4rem;
}

.pfeil {
  position: absolute;
  inset: 0;
  fill: none;
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
  opacity: 0;
  transition: opacity 0.4s;
}

.pfeil.an {
  opacity: 1;
}

.vor {
  stroke: var(--blau);
}

.zurueck {
  stroke: var(--orange);
}

.regel {
  position: absolute;
  left: 0;
  right: 0;
  bottom: -1.2rem;
  text-align: center;
  font-family: var(--mono);
  font-size: 0.8rem;
  color: var(--orange);
  opacity: 0;
  transition: opacity 0.4s;
}

.regel.an {
  opacity: 1;
}

.legende {
  display: flex;
  justify-content: center;
  gap: 2.5rem;
  margin-top: 2.2rem;
  font-size: 1.05rem;
}

.legende span {
  opacity: 0;
  transition: opacity 0.5s;
}

.legende span.an {
  opacity: 1;
}

.vor-farbe {
  color: var(--blau);
}

.rueck-farbe {
  color: var(--orange);
}

.code {
  width: 40rem;
  margin: 1.8rem auto 0;
  padding: 1rem 1.4rem;
  font-family: var(--mono);
  font-size: 1.2rem;
  line-height: 1.6;
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.6s, transform 0.6s;
}

.code.an {
  opacity: 1;
  transform: none;
}

.k {
  color: var(--blau);
}

.leise {
  color: var(--text-sehr-leise);
}

.satz {
  margin-top: 0.5rem;
  font-family: var(--sans);
  font-size: 1.1rem;
  color: var(--text-leise);
}

.satz b {
  color: var(--text);
}
</style>
