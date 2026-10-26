// Zählmodelle wie in Notebook 1: Für jeden Kontext aus n Zeichen steht da,
// wie oft welches Zeichen danach kam. Gezählt mit daten/erzeuge_modelle.py.

export type Zaehler = Record<string, Record<string, number>>
export type Eintrag = { zeichen: string, p: number }

export type Kennzahlen = {
  markow: { buchstaben: number, VV: number, VK: number, KV: number, KK: number }
  zeichen: string[]
  laenge: number
  haeufigkeit: number[]
  bigramme: number[][]
  explosion: { n: number, moeglich: number, gesehen: number, unbekannt: number }[]
  verluste: { n: number, training: number, test: number | null, nullen: number }[]
  woerter: number
  auszug: string
  datenhunger: {
    stufen: { zeichen: number, unbekannt: Record<string, number> }[]
    kontexte: number
    einmal: number
  }
}

export const KONTEXT = 4

const geladen = new Map<string, Promise<any>>()

function lade(name: string) {
  if (!geladen.has(name))
    geladen.set(name, fetch(`${import.meta.env.BASE_URL}modelle/${name}`).then(antwort => antwort.json()))
  return geladen.get(name)!
}

export function ladeModell(n = KONTEXT): Promise<Zaehler> {
  return lade(`maerchen${n}.json`)
}

export function ladeKennzahlen(): Promise<Kennzahlen> {
  return lade('kennzahlen.json')
}

// Wie wahrscheinlich ist jedes Zeichen nach diesem Text? Sortiert, wahrscheinlichstes zuerst.
export function verteilung(modell: Zaehler, text: string, n = KONTEXT): Eintrag[] {
  const zaehler = modell[n === 0 ? '' : text.slice(-n)]
  if (!zaehler)
    return []
  const gesamt = Object.values(zaehler).reduce((a, b) => a + b, 0)
  return Object.entries(zaehler)
    .map(([zeichen, anzahl]) => ({ zeichen, p: anzahl / gesamt }))
    .sort((a, b) => b.p - a.p)
}

// Zieht ein Zeichen, wie random.choices in Notebook 1. Gibt die Position in der Verteilung zurück.
export function ziehe(eintraege: Eintrag[]): number {
  let rest = Math.random()
  for (let i = 0; i < eintraege.length; i++) {
    rest -= eintraege[i].p
    if (rest <= 0)
      return i
  }
  return eintraege.length - 1
}

// Erzeugt Text mit einem n-Gramm-Modell. gierig: immer das wahrscheinlichste Zeichen statt zu ziehen.
export function erzeuge(modell: Zaehler, start: string, laenge: number, n: number, gierig = false): string {
  let text = start
  for (let i = 0; i < laenge; i++) {
    const eintraege = verteilung(modell, text, n)
    if (!eintraege.length)
      break
    text += eintraege[gierig ? 0 : ziehe(eintraege)].zeichen
  }
  return text
}

// So sieht ein Zeichen auf der Folie aus: Leerzeichen und Zeilenumbruch sichtbar machen
export function zeigeZeichen(zeichen: string): string {
  if (zeichen === ' ')
    return '␣'
  if (zeichen === '\n')
    return '↵'
  return zeichen
}

// Zahlen mit Tausenderpunkten, wie man sie in Deutschland schreibt
export function zahl(wert: number, stellen = 0): string {
  return wert.toLocaleString('de-DE', { minimumFractionDigits: stellen, maximumFractionDigits: stellen })
}

export const pause = (ms: number) => new Promise(fertig => setTimeout(fertig, ms))
