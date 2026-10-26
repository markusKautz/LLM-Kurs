// Das trainierte Zeichen-Netz aus daten/erzeuge_netze.py, im Browser nachgerechnet.
// Genau wie in Notebook 3: Koordinaten nachschlagen, nebeneinanderlegen, Schicht mit ReLU, Ausgabe.

import type { Eintrag } from './modell'
import { ziehe } from './modell'

export type NetzDaten = {
  zeichen: string[]
  kontext: number
  einbettung: number[][]
  W1: number[][]
  b1: number[]
  W2: number[][]
  b2: number[]
}

export type Durchlauf = {
  eingabe: number[]
  neuronen: number[]
  logits: number[]
  wahrscheinlichkeiten: number[]
}

const geladen = new Map<string, Promise<any>>()

export function ladeJson<T>(name: string): Promise<T> {
  if (!geladen.has(name))
    geladen.set(name, fetch(`${import.meta.env.BASE_URL}modelle/${name}`).then(antwort => antwort.json()))
  return geladen.get(name)!
}

export const ladeNetz = () => ladeJson<NetzDaten>('netz_text.json')

// Zeile mal Matrix: gewichtete Summe für jede Spalte
function mal(x: number[], W: number[][], b: number[]) {
  const ergebnis = [...b]
  for (let i = 0; i < x.length; i++) {
    const zeile = W[i]
    for (let j = 0; j < ergebnis.length; j++)
      ergebnis[j] += x[i] * zeile[j]
  }
  return ergebnis
}

export function softmax(logits: number[]) {
  const groesste = Math.max(...logits)
  const e = logits.map(l => Math.exp(l - groesste))
  const summe = e.reduce((a, b) => a + b, 0)
  return e.map(v => v / summe)
}

export function durchlauf(netz: NetzDaten, text: string): Durchlauf {
  const ids = [...text.slice(-netz.kontext)].map(z => Math.max(netz.zeichen.indexOf(z), 0))
  const eingabe = ids.flatMap(id => netz.einbettung[id])
  const neuronen = mal(eingabe, netz.W1, netz.b1).map(v => Math.max(v, 0))
  const logits = mal(neuronen, netz.W2, netz.b2)
  return { eingabe, neuronen, logits, wahrscheinlichkeiten: softmax(logits) }
}

export function netzVerteilung(netz: NetzDaten, text: string): Eintrag[] {
  return durchlauf(netz, text).wahrscheinlichkeiten
    .map((p, i) => ({ zeichen: netz.zeichen[i], p }))
    .sort((a, b) => b.p - a.p)
}

export function netzErzeuge(netz: NetzDaten, start: string, laenge: number) {
  let text = start
  for (let i = 0; i < laenge; i++) {
    const eintraege = netzVerteilung(netz, text)
    text += eintraege[ziehe(eintraege)].zeichen
  }
  return text
}
