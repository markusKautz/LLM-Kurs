<!--
  Tensoren: eine Zahl, eine Liste, eine Tabelle, ein Stapel von Tabellen. Jeder Klick zeigt eine Form mehr.
-->
<script setup lang="ts">
import { useSlideContext } from '@slidev/client'

const { $clicks } = useSlideContext()

const TABELLE = [[1, 5, 2], [0, 3, 7]]
const FORMEN = [
  { name: 'Zahl', form: '()', beispiel: 'der Verlust' },
  { name: 'Liste', form: '(3,)', beispiel: 'Koordinaten eines Zeichens' },
  { name: 'Tabelle', form: '(2, 3)', beispiel: 'mehrere Beispiele' },
  { name: 'Stapel', form: '(4, 2, 3)', beispiel: 'viele Tabellen auf einmal' },
]
</script>

<template>
  <div class="formen">
    <div v-for="(f, i) in FORMEN" :key="i" class="form" :class="{ an: $clicks > i }">
      <div class="bild">
        <div v-if="i === 0" class="zelle gross">7</div>
        <div v-if="i === 1" class="liste"><div v-for="z in [4, 1, 6]" :key="z" class="zelle">{{ z }}</div></div>
        <div v-if="i === 2" class="tabelle">
          <div v-for="(zeile, r) in TABELLE" :key="r" class="liste"><div v-for="(z, c) in zeile" :key="c" class="zelle">{{ z }}</div></div>
        </div>
        <div v-if="i === 3" class="stapel">
          <div v-for="s in 4" :key="s" class="tabelle ebene" :style="{ transform: `translate(${(s - 1) * 14}px, ${-(s - 1) * 14}px)`, zIndex: 5 - s }">
            <div v-for="(zeile, r) in TABELLE" :key="r" class="liste"><div v-for="(z, c) in zeile" :key="c" class="zelle">{{ (z + s) % 10 }}</div></div>
          </div>
        </div>
      </div>
      <div class="name">{{ f.name }}</div>
      <div class="formtext">Form <code>{{ f.form }}</code></div>
      <div class="beispiel">{{ f.beispiel }}</div>
    </div>
  </div>
  <div class="unten" :class="{ an: $clicks >= 5 }">
    Alles heißt in PyTorch <b>Tensor</b>. Gerechnet wird mit dem ganzen Tensor auf einmal, ohne Schleife.
  </div>
</template>

<style scoped>
.formen {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
  margin-top: 2.2rem;
}

.form {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  opacity: 0.15;
  transform: translateY(12px);
  transition: opacity 0.6s, transform 0.6s;
}

.form.an {
  opacity: 1;
  transform: none;
}

.bild {
  height: 13rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.liste {
  display: flex;
}

.tabelle {
  display: flex;
  flex-direction: column;
}

.zelle {
  display: grid;
  place-items: center;
  width: 2.8rem;
  height: 2.8rem;
  margin: -1px 0 0 -1px;
  border: 2px solid var(--blau);
  background: #eaf2fc;
  font-family: var(--mono);
  font-size: 1.25rem;
  font-weight: 600;
}

.zelle.gross {
  width: 3.6rem;
  height: 3.6rem;
  font-size: 1.6rem;
  border-radius: 6px;
}

.stapel {
  position: relative;
  width: 11rem;
  height: 9rem;
}

.ebene {
  position: absolute;
  left: 0.6rem;
  bottom: 0.6rem;
  background: var(--flaeche);
}

.name {
  font-size: 1.5rem;
  font-weight: 700;
}

.formtext {
  margin-top: 0.3rem;
  color: var(--text-leise);
}

.formtext code {
  font-family: var(--mono);
  color: var(--orange);
  font-weight: 700;
}

.beispiel {
  margin-top: 0.4rem;
  font-size: 0.95rem;
  color: var(--text-leise);
}

.unten {
  margin-top: 2.4rem;
  text-align: center;
  font-size: 1.4rem;
  opacity: 0;
  transition: opacity 0.6s;
}

.unten.an {
  opacity: 1;
}

.unten b {
  color: var(--blau);
}
</style>
