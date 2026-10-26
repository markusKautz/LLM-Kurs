<!--
  Eine Gerade durch Punkte: Fahrstrecke zur Berufsschule (km) und Fahrzeit (Minuten).

  modus="raten"   Klick 1: Punkte · Klick 2: eine geratene Gerade · Klick 3: Vorhersage für 20 km
  modus="fehler"  Klick 1: Fehler · Klick 2: Fehler als Quadrate · Klick 3: Verlust · Klick 4: bessere Gerade
  modus="regler"  Klick 1: an der Steigung drehen, rechts die Verlustkurve · Klick 2: das Tal markieren
  modus="lernen"  Klick 1: Gradientenabstieg mit Weg durch die Verlustlandschaft · Klick 2: Ergebnis
-->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useIsSlideActive, useSlideContext } from '@slidev/client'
import { pause, zahl } from '../logik/modell'

const props = withDefaults(defineProps<{ modus?: 'raten' | 'fehler' | 'regler' | 'lernen' }>(), { modus: 'raten' })

const PUNKTE = [[2, 9], [3, 13], [5, 14], [6, 18], [8, 20], [9, 25], [11, 25], [12, 29], [14, 31], [15, 36], [17, 37], [19, 42]]
const GERATEN = { w: 1.2, b: 12 }
const START_LERNEN = { w: 0.2, b: 30 }

// Diagramm
const B = 600
const H = 420
const R = { links: 52, rechts: 16, oben: 16, unten: 48 }
const X_MAX = 22
const Y_MAX = 50
const px = (x: number) => R.links + (x / X_MAX) * (B - R.links - R.rechts)
const py = (y: number) => H - R.unten - (y / Y_MAX) * (H - R.oben - R.unten)
const proEinheitY = (H - R.oben - R.unten) / Y_MAX

// Die beste Gerade (kleinste Quadrate), zum Vergleich
const n = PUNKTE.length
const mx = PUNKTE.reduce((a, [x]) => a + x, 0) / n
const my = PUNKTE.reduce((a, [, y]) => a + y, 0) / n
const BESTE_W = PUNKTE.reduce((a, [x, y]) => a + (x - mx) * (y - my), 0) / PUNKTE.reduce((a, [x]) => a + (x - mx) ** 2, 0)
const BESTE = { w: BESTE_W, b: my - BESTE_W * mx }

function verlust(w: number, b: number) {
  return PUNKTE.reduce((a, [x, y]) => a + (w * x + b - y) ** 2, 0) / n
}

const { $clicks } = useSlideContext()
const aktiv = useIsSlideActive()
const w = ref(GERATEN.w)
const b = ref(GERATEN.b)
const weg = ref<{ w: number, b: number }[]>([])
const schritte = ref(0)
let lauf = 0

const fehler = computed(() => PUNKTE.map(([x, y]) => ({ x, y, vorhersage: w.value * x + b.value })))
const aktuellerVerlust = computed(() => verlust(w.value, b.value))

// Animiert w und b weich zu einem Ziel
async function gleite(ziel: { w: number, b: number }, dauer: number, meinLauf: number) {
  const start = { w: w.value, b: b.value }
  const anfang = performance.now()
  while (meinLauf === lauf) {
    const t = Math.min((performance.now() - anfang) / dauer, 1)
    const f = t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2
    w.value = start.w + (ziel.w - start.w) * f
    b.value = start.b + (ziel.b - start.b) * f
    if (t === 1)
      return
    await pause(16)
  }
}

// Gradientenabstieg. Intern in 10-km-Schritten, damit beide Regler ähnlich schnell lernen.
async function lerne(meinLauf: number) {
  let w10 = START_LERNEN.w * 10
  let bb = START_LERNEN.b
  weg.value = [{ ...START_LERNEN }]
  for (let schritt = 1; schritt <= 120 && meinLauf === lauf; schritt++) {
    let gw = 0
    let gb = 0
    for (const [x, y] of PUNKTE) {
      const e = w10 * (x / 10) + bb - y
      gw += (2 * e * (x / 10)) / n
      gb += (2 * e) / n
    }
    w10 -= 0.4 * gw
    bb -= 0.4 * gb
    w.value = w10 / 10
    b.value = bb
    schritte.value = schritt
    weg.value.push({ w: w.value, b: b.value })
    await pause(schritt < 20 ? 140 : 45)
  }
}

watch([$clicks, aktiv], async ([klicks, jetzt]) => {
  const meinLauf = ++lauf
  if (!jetzt)
    return
  if (props.modus === 'fehler') {
    if (klicks < 4) {
      w.value = GERATEN.w
      b.value = GERATEN.b
    }
    else {
      await gleite(BESTE, 2200, meinLauf)
    }
  }
  if (props.modus === 'regler') {
    if (klicks === 0) {
      w.value = GERATEN.w
      b.value = BESTE.b
    }
    if (klicks === 1) {
      b.value = BESTE.b
      await gleite({ w: 0.6, b: BESTE.b }, 1600, meinLauf)
      await gleite({ w: 3.2, b: BESTE.b }, 3000, meinLauf)
      await gleite({ w: BESTE.w, b: BESTE.b }, 2000, meinLauf)
    }
    if (klicks >= 2) {
      w.value = BESTE.w
      b.value = BESTE.b
    }
  }
  if (props.modus === 'lernen') {
    if (klicks === 0) {
      w.value = START_LERNEN.w
      b.value = START_LERNEN.b
      weg.value = [{ ...START_LERNEN }]
      schritte.value = 0
    }
    if (klicks === 1)
      await lerne(meinLauf)
  }
  if (props.modus === 'raten') {
    w.value = GERATEN.w
    b.value = GERATEN.b
  }
}, { immediate: true })

// Rechte Seite im Modus "regler": Verlust abhängig von der Steigung
const KURVE = { B: 420, H: 300, wMin: 0.4, wMax: 3.4, vMax: 260 }
const kx = (wert: number) => 40 + ((wert - KURVE.wMin) / (KURVE.wMax - KURVE.wMin)) * (KURVE.B - 56)
const ky = (v: number) => KURVE.H - 36 - (Math.min(v, KURVE.vMax) / KURVE.vMax) * (KURVE.H - 56)
const kurve = computed(() => {
  const teile: string[] = []
  for (let i = 0; i <= 120; i++) {
    const wert = KURVE.wMin + (i / 120) * (KURVE.wMax - KURVE.wMin)
    teile.push(`${kx(wert).toFixed(1)},${ky(verlust(wert, BESTE.b)).toFixed(1)}`)
  }
  return `M${teile.join(' L')}`
})

// Rechte Seite im Modus "lernen": die Verlustlandschaft über Steigung und Verschiebung
const LAND = { B: 420, H: 360, wMin: 0, wMax: 3, bMin: -5, bMax: 35, spalten: 60, zeilen: 50 }
const lx = (wert: number) => 44 + ((wert - LAND.wMin) / (LAND.wMax - LAND.wMin)) * (LAND.B - 56)
const ly = (wert: number) => LAND.H - 40 - ((wert - LAND.bMin) / (LAND.bMax - LAND.bMin)) * (LAND.H - 56)
const landschaft = (() => {
  const felder: { x: number, y: number, b: number, h: number, farbe: string }[] = []
  const zb = (LAND.B - 56) / LAND.spalten
  const zh = (LAND.H - 56) / LAND.zeilen
  for (let i = 0; i < LAND.spalten; i++) {
    for (let j = 0; j < LAND.zeilen; j++) {
      const wert = LAND.wMin + ((i + 0.5) / LAND.spalten) * (LAND.wMax - LAND.wMin)
      const bb = LAND.bMin + ((j + 0.5) / LAND.zeilen) * (LAND.bMax - LAND.bMin)
      const t = Math.min(Math.log10(verlust(wert, bb) + 1) / 3, 1)
      // tief = blau, hoch = hell
      const farbe = `rgba(42, 120, 214, ${(0.85 * (1 - t) ** 2).toFixed(3)})`
      felder.push({ x: 44 + i * zb, y: LAND.H - 40 - (j + 1) * zh, b: zb + 0.5, h: zh + 0.5, farbe })
    }
  }
  return felder
})()
const wegPfad = computed(() => weg.value.map(p => `${lx(p.w).toFixed(1)},${ly(p.b).toFixed(1)}`).join(' '))
</script>

<template>
  <div class="gerade" :class="props.modus">
    <svg :width="B" :height="H" class="diagramm">
      <!-- Raster und Achsen -->
      <g class="raster">
        <line v-for="y in [10, 20, 30, 40, 50]" :key="`y${y}`" :x1="px(0)" :x2="px(X_MAX)" :y1="py(y)" :y2="py(y)" />
      </g>
      <line :x1="px(0)" :x2="px(X_MAX)" :y1="py(0)" :y2="py(0)" class="achse" />
      <line :x1="px(0)" :x2="px(0)" :y1="py(0)" :y2="py(Y_MAX)" class="achse" />
      <text v-for="x in [0, 5, 10, 15, 20]" :key="`tx${x}`" :x="px(x)" :y="py(0) + 20" class="zahl mitte">{{ x }}</text>
      <text v-for="y in [0, 10, 20, 30, 40, 50]" :key="`ty${y}`" :x="px(0) - 10" :y="py(y) + 4" class="zahl rechts">{{ y }}</text>
      <text :x="(px(0) + px(X_MAX)) / 2" :y="H - 6" class="achsentitel mitte">Fahrstrecke in km</text>
      <text x="14" :y="H / 2" class="achsentitel mitte" :transform="`rotate(-90 14 ${H / 2})`">Fahrzeit in Minuten</text>

      <!-- Fehler als Quadrate -->
      <g v-if="props.modus === 'fehler'">
        <rect
          v-for="(f, i) in fehler" :key="`q${i}`" class="quadrat" :class="{ an: $clicks >= 2 }"
          :x="px(f.x)" :y="py(Math.max(f.y, f.vorhersage))"
          :width="Math.abs(f.y - f.vorhersage) * proEinheitY" :height="Math.abs(f.y - f.vorhersage) * proEinheitY"
        />
        <line
          v-for="(f, i) in fehler" :key="`f${i}`" class="fehlerlinie" :class="{ an: $clicks >= 1 }"
          :x1="px(f.x)" :x2="px(f.x)" :y1="py(f.y)" :y2="py(f.vorhersage)"
        />
      </g>

      <!-- Die Gerade -->
      <line
        class="linie" :class="{ an: props.modus !== 'raten' || $clicks >= 2 }"
        :x1="px(0)" :y1="py(b)" :x2="px(X_MAX)" :y2="py(w * X_MAX + b)"
      />

      <!-- Die Punkte -->
      <circle
        v-for="([x, y], i) in PUNKTE" :key="i" :cx="px(x)" :cy="py(y)" r="7" class="punkt"
        :class="{ an: props.modus !== 'raten' || $clicks >= 1 }" :style="{ transitionDelay: `${i * 70}ms` }"
      />

      <!-- Vorhersage für 20 km -->
      <g v-if="props.modus === 'raten'" class="vorhersage" :class="{ an: $clicks >= 3 }">
        <line :x1="px(20)" :x2="px(20)" :y1="py(0)" :y2="py(20 * w + b)" class="hilfslinie" />
        <line :x1="px(0)" :x2="px(20)" :y1="py(20 * w + b)" :y2="py(20 * w + b)" class="hilfslinie" />
        <circle :cx="px(20)" :cy="py(20 * w + b)" r="9" class="neu" />
        <text :x="px(20) - 14" :y="py(20 * w + b) - 16" class="beschriftung-neu rechts">20 km → {{ zahl(20 * w + b) }} Min.</text>
      </g>
    </svg>

    <!-- Rechte Seite -->
    <div class="seite">
      <template v-if="props.modus === 'raten'">
        <div class="karte kasten" :class="{ an: $clicks >= 2 }">
          <div class="beschriftung">Eine Gerade, nach Augenmaß</div>
          <div class="formel">Fahrzeit = <b class="blau">{{ zahl(w, 1) }}</b> × km + <b class="orange">{{ zahl(b) }}</b></div>
          <div class="klein"><b class="blau">Steigung:</b> Minuten pro Kilometer</div>
          <div class="klein"><b class="orange">Verschiebung:</b> Minuten, die immer dazukommen</div>
        </div>
      </template>

      <template v-if="props.modus === 'fehler'">
        <div class="karte kasten" :class="{ an: $clicks >= 3 }">
          <div class="beschriftung">Verlust</div>
          <div class="verlust">{{ zahl(aktuellerVerlust, 1) }}</div>
          <div class="klein">Durchschnitt aller Quadrate. Kleiner ist besser.</div>
          <div class="formel klein">Fahrzeit = {{ zahl(w, 2) }} × km + {{ zahl(b, 1) }}</div>
        </div>
      </template>

      <template v-if="props.modus === 'regler'">
        <svg :width="KURVE.B" :height="KURVE.H" class="kurve">
          <line :x1="kx(KURVE.wMin)" :x2="kx(KURVE.wMax)" :y1="ky(0)" :y2="ky(0)" class="achse" />
          <line :x1="kx(KURVE.wMin)" :x2="kx(KURVE.wMin)" :y1="ky(0)" :y2="ky(KURVE.vMax)" class="achse" />
          <text v-for="t in [1, 2, 3]" :key="t" :x="kx(t)" :y="ky(0) + 20" class="zahl mitte">{{ t }}</text>
          <text :x="KURVE.B / 2 + 10" :y="KURVE.H - 4" class="achsentitel mitte">Steigung (Minuten pro km)</text>
          <text x="14" :y="KURVE.H / 2 - 10" class="achsentitel mitte" :transform="`rotate(-90 14 ${KURVE.H / 2 - 10})`">Verlust</text>
          <path :d="kurve" class="verlustkurve" />
          <g v-if="$clicks >= 2" class="tal">
            <line :x1="kx(BESTE.w)" :x2="kx(BESTE.w)" :y1="ky(0)" :y2="ky(verlust(BESTE.w, BESTE.b)) - 10" class="hilfslinie" />
            <text :x="kx(BESTE.w)" :y="ky(0) - 60" class="tal-text mitte">das Tal</text>
          </g>
          <circle :cx="kx(w)" :cy="ky(aktuellerVerlust)" r="9" class="ball" />
        </svg>
        <div class="schieber">
          <label>Steigung <input v-model.number="w" type="range" min="0.4" max="3.4" step="0.01"><b>{{ zahl(w, 2) }}</b></label>
          <label>Verschiebung <input v-model.number="b" type="range" min="-5" max="25" step="0.1"><b>{{ zahl(b, 1) }}</b></label>
          <div class="klein">Verlust: <b>{{ zahl(aktuellerVerlust, 1) }}</b></div>
        </div>
      </template>

      <template v-if="props.modus === 'lernen'">
        <svg :width="LAND.B" :height="LAND.H" class="landschaft">
          <rect v-for="(f, i) in landschaft" :key="i" :x="f.x" :y="f.y" :width="f.b" :height="f.h" :fill="f.farbe" />
          <text v-for="t in [0, 1, 2, 3]" :key="`w${t}`" :x="lx(t)" :y="LAND.H - 22" class="zahl mitte">{{ t }}</text>
          <text v-for="t in [0, 10, 20, 30]" :key="`b${t}`" :x="38" :y="ly(t) + 4" class="zahl rechts">{{ t }}</text>
          <text :x="LAND.B / 2 + 16" :y="LAND.H - 2" class="achsentitel mitte">Steigung</text>
          <text x="12" :y="LAND.H / 2 - 20" class="achsentitel mitte" :transform="`rotate(-90 12 ${LAND.H / 2 - 20})`">Verschiebung</text>
          <polyline :points="wegPfad" class="weg" />
          <circle :cx="lx(BESTE.w)" :cy="ly(BESTE.b)" r="7" class="ziel" />
          <circle :cx="lx(w)" :cy="ly(b)" r="9" class="ball" />
        </svg>
        <div class="lernstand">
          <span>Schritt <b>{{ schritte }}</b></span>
          <span>Verlust <b>{{ zahl(aktuellerVerlust, 1) }}</b></span>
        </div>
        <div class="lernstand leise">
          Fahrzeit = {{ zahl(w, 2) }} × km + {{ zahl(b, 1) }}
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.gerade {
  display: grid;
  grid-template-columns: 600px 1fr;
  gap: 2rem;
  align-items: center;
  margin-top: 0.6rem;
}

.raster line {
  stroke: var(--linie);
  stroke-dasharray: 3 5;
}

.achse {
  stroke: var(--text-leise);
  stroke-width: 1.5;
}

.zahl {
  font-family: var(--mono);
  font-size: 13px;
  fill: var(--text-leise);
}

.achsentitel {
  font-size: 14px;
  fill: var(--text-leise);
}

.mitte {
  text-anchor: middle;
}

.rechts {
  text-anchor: end;
}

.punkt {
  fill: var(--text);
  stroke: #fff;
  stroke-width: 2;
  opacity: 0;
  transform-box: fill-box;
  transform-origin: center;
  transform: scale(0.3);
  transition: opacity 0.4s, transform 0.4s;
}

.punkt.an {
  opacity: 1;
  transform: none;
}

.linie {
  stroke: var(--blau);
  stroke-width: 4;
  stroke-linecap: round;
  opacity: 0;
  transition: opacity 0.6s;
}

.linie.an {
  opacity: 1;
}

.fehlerlinie {
  stroke: var(--orange);
  stroke-width: 3;
  opacity: 0;
  transition: opacity 0.5s;
}

.fehlerlinie.an {
  opacity: 1;
}

.quadrat {
  fill: rgba(235, 104, 52, 0.16);
  stroke: rgba(235, 104, 52, 0.55);
  stroke-width: 1;
  opacity: 0;
  transition: opacity 0.6s;
}

.quadrat.an {
  opacity: 1;
}

.vorhersage {
  opacity: 0;
  transition: opacity 0.6s;
}

.vorhersage.an {
  opacity: 1;
}

.hilfslinie {
  stroke: var(--text-sehr-leise);
  stroke-dasharray: 5 5;
}

.neu {
  fill: var(--orange);
  stroke: #fff;
  stroke-width: 3;
}

.beschriftung-neu {
  font-size: 17px;
  font-weight: 650;
  fill: var(--orange);
}

.seite {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.kasten {
  padding: 1.3rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.6s, transform 0.6s;
}

.kasten.an {
  opacity: 1;
  transform: none;
}

.formel {
  font-family: var(--mono);
  font-size: 1.35rem;
}

.klein {
  font-size: 1rem;
  color: var(--text-leise);
}

.formel.klein {
  font-size: 0.95rem;
}

.blau {
  color: var(--blau);
}

.orange {
  color: var(--orange);
}

.verlust {
  font-family: var(--mono);
  font-size: 3.2rem;
  font-weight: 700;
  color: var(--orange);
}

.verlustkurve {
  fill: none;
  stroke: var(--text);
  stroke-width: 3;
}

.ball {
  fill: var(--orange);
  stroke: #fff;
  stroke-width: 3;
  filter: drop-shadow(0 2px 4px rgba(235, 104, 52, 0.5));
}

.tal-text {
  font-size: 16px;
  font-weight: 650;
  fill: var(--blau);
}

.schieber {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.95rem;
  color: var(--text-leise);
}

.schieber label {
  display: grid;
  grid-template-columns: 7rem 1fr 3.5rem;
  align-items: center;
  gap: 0.6rem;
}

.schieber input {
  accent-color: var(--blau);
}

.schieber b {
  font-family: var(--mono);
  color: var(--text);
  text-align: right;
}

.weg {
  fill: none;
  stroke: var(--orange);
  stroke-width: 2.5;
  stroke-linejoin: round;
}

.ziel {
  fill: none;
  stroke: var(--text);
  stroke-width: 2.5;
  stroke-dasharray: 3 3;
}

.lernstand {
  display: flex;
  gap: 1.4rem;
  font-family: var(--mono);
  font-size: 1rem;
}

.leise {
  color: var(--text-leise);
}
</style>
