<!--
  Der Fahrplan des Vortrags. Jeder Klick zeigt einen weiteren Schritt.
  Mit "aktuell" wird ein Schritt hervorgehoben und alle sind sofort sichtbar.
-->
<script setup lang="ts">
import { computed } from 'vue'
import { useSlideContext } from '@slidev/client'
import { PLAENE } from '../logik/plan'

const props = withDefaults(defineProps<{
  vortrag?: number
  aktuell?: number
}>(), { vortrag: 1, aktuell: 0 })

const plan = computed(() => ({ schritte: PLAENE[props.vortrag], aktuell: props.aktuell }))

const { $clicks } = useSlideContext()
const sichtbar = computed(() => plan.value.aktuell ? plan.value.schritte.length : $clicks.value)
const fortschritt = computed(() => Math.max((plan.value.aktuell || sichtbar.value) - 1, 0) / (plan.value.schritte.length - 1))
</script>

<template>
  <div class="fahrplan">
    <div class="linie"><div class="fortschritt" :style="{ width: `${fortschritt * 100}%` }" /></div>
    <div
      v-for="(schritt, i) in plan.schritte" :key="i"
      class="schritt" :class="{ an: i < sichtbar, aktuell: plan.aktuell === i + 1, vorbei: plan.aktuell && i + 1 < plan.aktuell }"
    >
      <div class="nr">{{ i + 1 }}</div>
      <div class="titel">{{ schritt.titel }}</div>
      <div class="text">{{ schritt.text }}</div>
    </div>
  </div>
</template>

<style scoped>
.fahrplan {
  position: relative;
  display: grid;
  grid-template-columns: repeat(v-bind('plan.schritte.length'), 1fr);
  gap: 1.2rem;
  margin-top: 4.5rem;
}

.linie {
  position: absolute;
  top: 1.6rem;
  left: 10%;
  right: 10%;
  height: 3px;
  border-radius: 2px;
  background: var(--linie);
}

.fortschritt {
  height: 100%;
  border-radius: 2px;
  background: var(--orange);
  transition: width 0.7s ease;
}

.schritt {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  opacity: 0;
  transform: translateY(14px);
  transition: opacity 0.6s, transform 0.6s;
}

.schritt.an {
  opacity: 1;
  transform: none;
}

.nr {
  display: grid;
  place-items: center;
  width: 3.2rem;
  height: 3.2rem;
  border-radius: 50%;
  background: var(--flaeche);
  border: 2px solid var(--orange);
  color: var(--orange);
  font-family: var(--mono);
  font-size: 1.25rem;
  font-weight: 700;
  box-shadow: var(--schatten);
}

.titel {
  margin-top: 1.1rem;
  font-size: 1.35rem;
  font-weight: 650;
}

.text {
  margin-top: 0.5rem;
  font-size: 1rem;
  line-height: 1.45;
  color: var(--text-leise);
  max-width: 13rem;
}

/* Zwischenfolie: ein Schritt hervorgehoben */
.schritt.aktuell .nr {
  background: var(--orange);
  color: #fff;
  box-shadow: var(--leuchten-orange);
  transform: scale(1.15);
}

.schritt.vorbei .nr {
  border-color: var(--text-sehr-leise);
  color: var(--text-sehr-leise);
}

.fahrplan:has(.aktuell) .schritt:not(.aktuell) {
  opacity: 0.45;
}
</style>
