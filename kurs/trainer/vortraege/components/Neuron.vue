<!--
  Ein einzelnes Neuron: Eingaben mal Gewichte, zusammenzählen, Verschiebung dazu, ReLU.
  Klick 1: Eingaben und Gewichte · Klick 2: malnehmen · Klick 3: zusammenzählen + Verschiebung · Klick 4: ReLU
  Klick 5: anderes Beispiel, bei dem ReLU die Zahl auf 0 setzt
-->
<script setup lang="ts">
import { computed } from 'vue'
import { useSlideContext } from '@slidev/client'
import { zahl } from '../logik/modell'

const BEISPIELE = [
  { x: [0.8, -0.5, 1.2], w: [1.5, -1.0, 0.5], b: -0.4 },
  { x: [-0.6, 0.9, 0.3], w: [1.5, -1.0, 0.5], b: -0.4 },
]

const { $clicks } = useSlideContext()
const bsp = computed(() => BEISPIELE[$clicks.value >= 5 ? 1 : 0])
const produkte = computed(() => bsp.value.x.map((x, i) => x * bsp.value.w[i]))
const summe = computed(() => produkte.value.reduce((a, b) => a + b, 0) + bsp.value.b)
const ausgabe = computed(() => Math.max(summe.value, 0))

const Y = [70, 170, 270]

// Negative Zahlen in der Rechnung in Klammern, damit "· −1" nicht wie ein Tippfehler aussieht
const klammer = (wert: number) => wert < 0 ? `(${zahl(wert, 1)})` : zahl(wert, 1)
</script>

<template>
  <div class="neuron">
    <svg width="760" height="340" class="bild">
      <!-- Verbindungen -->
      <g v-for="(x, i) in bsp.x" :key="`l${i}`">
        <line
          :x1="120" :y1="Y[i]" x2="430" y2="170" class="kante"
          :class="{ an: $clicks >= 1, negativ: bsp.w[i] < 0 }"
          :style="{ strokeWidth: 2 + Math.abs(bsp.w[i]) * 4 }"
        />
        <text :x="250" :y="(Y[i] + 170) / 2 - 12 + i * 4" class="gewicht" :class="{ an: $clicks >= 1, negativ: bsp.w[i] < 0 }">× {{ zahl(bsp.w[i], 1) }}</text>
        <text :x="330" :y="(Y[i] * 0.35 + 170 * 0.65) + (i - 1) * 10 - 6" class="produkt" :class="{ an: $clicks >= 2 }">= {{ zahl(produkte[i], 2) }}</text>
      </g>

      <!-- Eingaben -->
      <g v-for="(x, i) in bsp.x" :key="`e${i}`" class="eingabe" :class="{ an: $clicks >= 1 }">
        <circle cx="90" :cy="Y[i]" r="30" />
        <text x="90" :y="Y[i] + 6" class="wert">{{ zahl(x, 1) }}</text>
      </g>

      <!-- Das Neuron -->
      <circle cx="470" cy="170" r="48" class="koerper" :class="{ an: $clicks >= 3 }" />
      <text x="470" y="160" class="sigma">Σ</text>
      <text x="470" y="190" class="summe" :class="{ an: $clicks >= 3 }">{{ zahl(summe, 2) }}</text>
      <text x="470" y="250" class="verschiebung" :class="{ an: $clicks >= 3 }">+ Verschiebung {{ zahl(bsp.b, 1) }}</text>

      <!-- ReLU -->
      <line x1="520" y1="170" x2="580" y2="170" class="kante an" />
      <g class="relu" :class="{ an: $clicks >= 4 }">
        <rect x="580" y="135" width="74" height="70" rx="12" />
        <polyline points="592,190 617,190 642,148" class="relu-kurve" />
        <text x="617" y="228" class="relu-text">ReLU</text>
      </g>
      <line x1="654" y1="170" x2="690" y2="170" class="kante" :class="{ an: $clicks >= 4 }" />
      <g class="aus" :class="{ an: $clicks >= 4, null: ausgabe === 0 }">
        <circle cx="722" cy="170" r="30" />
        <text x="722" y="176" class="wert">{{ zahl(ausgabe, 2) }}</text>
      </g>
    </svg>

    <div class="rechnung" :class="{ an: $clicks >= 3 }">
      <span v-for="(p, i) in produkte" :key="i">{{ i ? ' + ' : '' }}{{ klammer(bsp.x[i]) }} · {{ klammer(bsp.w[i]) }}</span>
      <span> + ({{ zahl(bsp.b, 1) }}) = <b>{{ zahl(summe, 2) }}</b></span>
      <span v-if="$clicks >= 4" class="relu-satz">
        → ReLU: {{ summe < 0 ? 'negativ, also' : 'positiv, bleibt' }} <b class="orange">{{ zahl(ausgabe, 2) }}</b>
      </span>
    </div>
  </div>
</template>

<style scoped>
.neuron {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 0.8rem;
}

.kante {
  stroke: var(--blau);
  opacity: 0.15;
  transition: opacity 0.5s;
}

.kante.negativ {
  stroke: var(--orange);
}

.kante.an {
  opacity: 0.85;
}

.gewicht,
.produkt {
  font-family: var(--mono);
  font-size: 17px;
  font-weight: 700;
  text-anchor: middle;
  opacity: 0;
  transition: opacity 0.5s;
  paint-order: stroke;
  stroke: var(--hintergrund);
  stroke-width: 6px;
}

.gewicht {
  fill: var(--blau);
}

.gewicht.negativ {
  fill: var(--orange);
}

.produkt {
  fill: var(--text);
  font-size: 15px;
}

.gewicht.an,
.produkt.an {
  opacity: 1;
}

.eingabe circle,
.aus circle {
  fill: var(--flaeche);
  stroke: var(--text);
  stroke-width: 2.5;
}

.eingabe {
  opacity: 0.2;
  transition: opacity 0.5s;
}

.eingabe.an {
  opacity: 1;
}

.wert {
  font-family: var(--mono);
  font-size: 18px;
  font-weight: 700;
  text-anchor: middle;
}

.koerper {
  fill: var(--flaeche);
  stroke: var(--linie);
  stroke-width: 3;
  transition: stroke 0.5s, fill 0.5s;
}

.koerper.an {
  stroke: var(--blau);
  fill: #eaf2fc;
}

.sigma {
  font-size: 26px;
  text-anchor: middle;
  fill: var(--text-leise);
}

.summe,
.verschiebung {
  font-family: var(--mono);
  text-anchor: middle;
  opacity: 0;
  transition: opacity 0.5s;
}

.summe {
  font-size: 18px;
  font-weight: 700;
}

.verschiebung {
  font-size: 14px;
  fill: var(--text-leise);
}

.summe.an,
.verschiebung.an {
  opacity: 1;
}

.relu {
  opacity: 0.2;
  transition: opacity 0.5s;
}

.relu.an {
  opacity: 1;
}

.relu rect {
  fill: var(--flaeche);
  stroke: var(--orange);
  stroke-width: 2.5;
}

.relu-kurve {
  fill: none;
  stroke: var(--orange);
  stroke-width: 3.5;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.relu-text {
  font-family: var(--mono);
  font-size: 13px;
  text-anchor: middle;
  fill: var(--orange);
}

.aus {
  opacity: 0;
  transition: opacity 0.5s;
}

.aus.an {
  opacity: 1;
}

.aus.an circle {
  stroke: var(--orange);
  fill: var(--orange-hauch);
}

.aus.null circle {
  stroke: var(--text-sehr-leise);
  fill: var(--flaeche-hell);
}

.rechnung {
  font-family: var(--mono);
  font-size: 1.25rem;
  opacity: 0;
  transition: opacity 0.6s;
}

.rechnung.an {
  opacity: 1;
}

.relu-satz {
  margin-left: 1rem;
}

.orange {
  color: var(--orange);
}
</style>
