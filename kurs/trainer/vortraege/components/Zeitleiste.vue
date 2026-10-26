<!--
  Eine Zeitleiste. Jeder Klick zeigt ein weiteres Ereignis.
-->
<script setup lang="ts">
import { useSlideContext } from '@slidev/client'

const props = defineProps<{
  ereignisse: { jahr: string, titel: string, text: string, hervor?: boolean }[]
}>()

const { $clicks } = useSlideContext()
</script>

<template>
  <div class="zeitleiste">
    <div class="achse">
      <div class="fortschritt" :style="{ width: `${(Math.min($clicks, props.ereignisse.length) / props.ereignisse.length) * 100}%` }" />
    </div>
    <div
      v-for="(e, i) in props.ereignisse" :key="i"
      class="ereignis" :class="{ an: i < $clicks, hervor: e.hervor, oben: i % 2 === 0 }"
      :style="{ left: `${((i + 0.5) / props.ereignisse.length) * 100}%` }"
    >
      <div class="karte inhalt">
        <div class="jahr">{{ e.jahr }}</div>
        <div class="titel">{{ e.titel }}</div>
        <div class="text">{{ e.text }}</div>
      </div>
      <div class="stiel" />
      <div class="punkt" />
    </div>
  </div>
</template>

<style scoped>
.zeitleiste {
  position: relative;
  height: 440px;
  margin-top: 0.5rem;
}

.achse {
  position: absolute;
  left: 0;
  right: 0;
  top: 50%;
  height: 4px;
  border-radius: 2px;
  background: var(--linie);
}

.fortschritt {
  height: 100%;
  border-radius: 2px;
  background: linear-gradient(90deg, var(--blau), var(--orange));
  transition: width 0.9s ease;
}

.ereignis {
  position: absolute;
  top: 50%;
  width: 0;
  opacity: 0;
  transition: opacity 0.6s;
}

.ereignis.an {
  opacity: 1;
}

.punkt {
  position: absolute;
  left: -9px;
  top: -7px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--flaeche);
  border: 4px solid var(--blau);
}

.ereignis.hervor .punkt {
  border-color: var(--orange);
  box-shadow: var(--leuchten-orange);
}

.stiel {
  position: absolute;
  left: -1px;
  width: 2px;
  height: 46px;
  background: var(--linie);
}

.oben .stiel {
  bottom: 0;
}

.ereignis:not(.oben) .stiel {
  top: 0;
}

.inhalt {
  position: absolute;
  left: -125px;
  width: 250px;
  padding: 0.9rem 1rem;
  transition: transform 0.6s;
}

.oben .inhalt {
  bottom: 46px;
  transform: translateY(-12px);
}

.ereignis:not(.oben) .inhalt {
  top: 46px;
  transform: translateY(12px);
}

.ereignis.an .inhalt {
  transform: none;
}

.jahr {
  font-family: var(--mono);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--blau);
}

.hervor .jahr {
  color: var(--orange);
}

.titel {
  margin-top: 0.2rem;
  font-size: 1.1rem;
  font-weight: 650;
}

.text {
  margin-top: 0.35rem;
  font-size: 0.92rem;
  line-height: 1.45;
  color: var(--text-leise);
}
</style>
