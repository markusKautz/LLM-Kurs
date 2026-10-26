<!--
  Was PyTorch für die Logits herausfindet: Gradient = Vorhersage minus Wahrheit (Beispiel aus Notebook 2).
  Klick 1: Vorhersage · Klick 2: Wahrheit · Klick 3: Gradient · Klick 4: ein Lernschritt
-->
<script setup lang="ts">
import { computed } from 'vue'
import { useSlideContext } from '@slidev/client'
import { zahl } from '../logik/modell'
import { softmax } from '../logik/netz'

const ZEICHEN = ['a', 'e', 'n', 'r', '␣']
const LOGITS = [1.0, 2.0, 0.5, 0.3, 1.5]
const RICHTIG = 2
const LERNRATE = 1

const { $clicks } = useSlideContext()

const vorher = softmax(LOGITS)
const wahrheit = ZEICHEN.map((_, i) => (i === RICHTIG ? 1 : 0))
const gradient = vorher.map((p, i) => p - wahrheit[i])
const nachher = softmax(LOGITS.map((l, i) => l - LERNRATE * gradient[i]))

const vorhersage = computed(() => ($clicks.value >= 4 ? nachher : vorher))
</script>

<template>
  <div class="gradient">
    <div class="gruppe" :class="{ an: $clicks >= 1 }">
      <div class="titel">Vorhersage <span class="leise">(Softmax)</span></div>
      <div class="balken-reihe">
        <div v-for="(p, i) in vorhersage" :key="i" class="spalte">
          <div class="spur"><div class="balken blau" :class="{ richtig: i === RICHTIG }" :style="{ height: `${p * 100}%` }" /></div>
          <div class="wert">{{ zahl(p * 100) }} %</div>
          <div class="zk" :class="{ ziel: i === RICHTIG }">{{ ZEICHEN[i] }}</div>
        </div>
      </div>
    </div>

    <div class="zeichen" :class="{ an: $clicks >= 2 }">−</div>

    <div class="gruppe" :class="{ an: $clicks >= 2 }">
      <div class="titel">Wahrheit <span class="leise">(richtig ist „n“)</span></div>
      <div class="balken-reihe">
        <div v-for="(p, i) in wahrheit" :key="i" class="spalte">
          <div class="spur"><div class="balken grau" :style="{ height: `${p * 100}%` }" /></div>
          <div class="wert">{{ p ? '100 %' : '0 %' }}</div>
          <div class="zk" :class="{ ziel: i === RICHTIG }">{{ ZEICHEN[i] }}</div>
        </div>
      </div>
    </div>

    <div class="zeichen" :class="{ an: $clicks >= 3 }">=</div>

    <div class="gruppe" :class="{ an: $clicks >= 3 }">
      <div class="titel">Gradient</div>
      <div class="balken-reihe mitte">
        <div v-for="(g, i) in gradient" :key="i" class="spalte">
          <div class="spur zweiseitig">
            <div class="balken" :class="g > 0 ? 'orange oben' : 'gruen unten'" :style="{ height: `${Math.abs(g) * 50}%` }" />
          </div>
          <div class="wert">{{ g > 0 ? '+' : '' }}{{ zahl(g, 2) }}</div>
          <div class="zk" :class="{ ziel: i === RICHTIG }">{{ ZEICHEN[i] }}</div>
        </div>
      </div>
    </div>
  </div>

  <div class="erklaerung">
    <span :class="{ an: $clicks >= 3 }"><b class="orange">positiv:</b> zu viel vorhergesagt, Logit wird kleiner</span>
    <span :class="{ an: $clicks >= 3 }"><b class="gruen">negativ:</b> zu wenig, Logit wird größer</span>
    <span :class="{ an: $clicks >= 4 }"><b>nach einem Lernschritt:</b> „n“ von {{ zahl(vorher[RICHTIG] * 100) }} % auf {{ zahl(nachher[RICHTIG] * 100) }} %</span>
  </div>
</template>

<style scoped>
.gradient {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.2rem;
  margin-top: 1.8rem;
}

.gruppe {
  padding: 1rem 1.1rem;
  border-radius: 16px;
  background: var(--flaeche);
  border: 1px solid var(--linie);
  box-shadow: var(--schatten);
  opacity: 0.15;
  transition: opacity 0.6s;
}

.gruppe.an {
  opacity: 1;
}

.titel {
  font-size: 1.15rem;
  font-weight: 650;
  margin-bottom: 0.7rem;
}

.leise {
  font-weight: 400;
  font-size: 0.9rem;
  color: var(--text-leise);
}

.balken-reihe {
  display: flex;
  gap: 0.55rem;
}

.spalte {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  width: 3.2rem;
}

.spur {
  position: relative;
  width: 2.2rem;
  height: 170px;
  border-radius: 6px;
  background: var(--flaeche-hell);
}

.balken {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 6px;
  transition: height 0.9s cubic-bezier(.3, .8, .3, 1);
}

.zweiseitig::after {
  content: "";
  position: absolute;
  left: -4px;
  right: -4px;
  top: 50%;
  height: 2px;
  background: var(--text-leise);
}

.balken.oben {
  bottom: 50%;
}

.balken.unten {
  top: 50%;
  bottom: auto;
}

.blau {
  background: var(--blau);
}

.blau.richtig {
  background: var(--orange);
}

.grau {
  background: var(--text);
}

.orange {
  background: var(--orange);
  color: var(--orange);
}

.gruen {
  background: #2ea37a;
  color: #2ea37a;
}

b.orange,
b.gruen {
  background: none;
}

.wert {
  font-family: var(--mono);
  font-size: 0.85rem;
  color: var(--text-leise);
}

.zk.ziel {
  border-color: var(--orange);
  color: var(--orange);
  font-weight: 700;
}

.zeichen {
  font-family: var(--mono);
  font-size: 2.2rem;
  color: var(--text-sehr-leise);
  opacity: 0;
  transition: opacity 0.5s;
}

.zeichen.an {
  opacity: 1;
}

.erklaerung {
  display: flex;
  justify-content: center;
  gap: 2.4rem;
  margin-top: 1.4rem;
  font-size: 1.1rem;
}

.erklaerung span {
  opacity: 0;
  transition: opacity 0.6s;
}

.erklaerung span.an {
  opacity: 1;
}
</style>
