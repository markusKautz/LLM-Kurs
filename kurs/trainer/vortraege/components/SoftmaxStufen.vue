<!--
  Softmax in drei Stufen: beliebige Zahlen → alle positiv → zusammen 100 %.
  Klick 1: torch.exp · Klick 2: durch die Summe teilen
-->
<script setup lang="ts">
import { computed } from 'vue'
import { useSlideContext } from '@slidev/client'
import { zahl } from '../logik/modell'

const props = withDefaults(defineProps<{ logits?: number[], zeichen?: string[] }>(), {
  logits: () => [2, 1, 0.2, -1, -2],
  zeichen: () => ['e', 'n', 'r', 'a', 'x'],
})

const { $clicks } = useSlideContext()
const exp = computed(() => props.logits.map(l => Math.exp(l)))
const summe = computed(() => exp.value.reduce((a, b) => a + b, 0))
const stufe = computed(() => Math.min($clicks.value, 2))

const werte = computed(() => stufe.value === 0 ? props.logits : stufe.value === 1 ? exp.value : exp.value.map(v => v / summe.value))
const MASSSTAB = [2.2, 7.5, 1]
const TITEL = ['Logits: beliebige Zahlen', 'torch.exp: alle positiv, größer bleibt größer', 'geteilt durch die Summe: Wahrscheinlichkeiten']
const format = (v: number) => stufe.value === 2 ? `${zahl(v * 100)} %` : zahl(v, 2)
</script>

<template>
  <div class="softmax">
    <div class="stufen">
      <span v-for="(t, i) in TITEL" :key="i" class="stufe" :class="{ aktiv: stufe === i, vorbei: stufe > i }">
        <b>{{ i + 1 }}</b> {{ t }}
      </span>
    </div>

    <div class="diagramm">
      <div class="nulllinie" :style="{ bottom: stufe === 0 ? '45%' : '0%' }" />
      <div v-for="(v, i) in werte" :key="i" class="spalte">
        <div
          class="balken" :class="{ negativ: v < 0, wahrscheinlich: stufe === 2 }"
          :style="{
            height: `${Math.abs(v) / MASSSTAB[stufe] * (stufe === 0 ? 45 : 92)}%`,
            bottom: stufe === 0 ? (v < 0 ? `${45 - Math.abs(v) / MASSSTAB[0] * 45}%` : '45%') : '0%',
          }"
        >
          <span class="wert" :class="{ unten: v < 0 }">{{ format(v) }}</span>
        </div>
      </div>
    </div>
    <div class="zeichenreihe">
      <span v-for="z in props.zeichen" :key="z" class="zk">{{ z }}</span>
    </div>

    <div class="fuss">
      <template v-if="stufe === 1">Summe: <b>{{ zahl(summe, 2) }}</b></template>
      <template v-if="stufe === 2">zusammen: <b class="orange">100 %</b></template>
    </div>
  </div>
</template>

<style scoped>
.softmax {
  margin-top: 1rem;
}

.stufen {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.2rem;
}

.stufe {
  padding: 0.45rem 0.9rem;
  border-radius: 999px;
  border: 1px solid var(--linie);
  font-size: 1rem;
  color: var(--text-sehr-leise);
  transition: all 0.4s;
}

.stufe b {
  font-family: var(--mono);
  margin-right: 0.3rem;
}

.stufe.aktiv {
  color: var(--text);
  border-color: var(--orange);
  box-shadow: var(--leuchten-orange);
}

.stufe.vorbei {
  color: var(--text-leise);
}

.diagramm {
  position: relative;
  display: flex;
  justify-content: center;
  gap: 2.2rem;
  height: 300px;
  padding: 0 2rem;
  border-bottom: 1px solid transparent;
}

.nulllinie {
  position: absolute;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--text-leise);
  transition: bottom 0.8s ease;
}

.spalte {
  position: relative;
  width: 6rem;
}

.balken {
  position: absolute;
  left: 0;
  right: 0;
  border-radius: 8px;
  background: linear-gradient(to top, var(--blau-tief), var(--blau));
  transition: height 0.9s cubic-bezier(.3, .8, .3, 1), bottom 0.9s cubic-bezier(.3, .8, .3, 1), background 0.6s;
}

.balken.negativ {
  background: linear-gradient(to bottom, #9a9fab, #c4c7cf);
}

.balken.wahrscheinlich {
  background: linear-gradient(to top, var(--orange-tief), var(--orange));
}

.wert {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  margin-bottom: 0.3rem;
  text-align: center;
  font-family: var(--mono);
  font-size: 1.1rem;
  font-weight: 600;
}

.wert.unten {
  bottom: auto;
  top: 100%;
  margin-top: 0.3rem;
}

.zeichenreihe {
  display: flex;
  justify-content: center;
  gap: 2.2rem;
  padding: 0 2rem;
  margin-top: 0.8rem;
}

.zeichenreihe .zk {
  width: 6rem;
}

.fuss {
  margin-top: 1rem;
  min-height: 2rem;
  text-align: center;
  font-family: var(--mono);
  font-size: 1.25rem;
}

.orange {
  color: var(--orange);
}
</style>
