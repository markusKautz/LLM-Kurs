// Der Fahrplan von Vortrag 1. Wird auf der Übersicht und auf den Zwischenfolien gezeigt.
export const VORTRAG1 = [
  { titel: 'Text wird zu Zahlen', text: 'Jedes Zeichen bekommt eine Nummer' },
  { titel: 'Zählen', text: 'Welches Zeichen folgt auf welches?' },
  { titel: 'Ziehen', text: 'Zufällig, aber nach Wahrscheinlichkeit' },
  { titel: 'Mehr Kontext', text: 'Weiter zurückschauen' },
  { titel: 'Bewerten', text: 'Wie gut ist das Modell?' },
]

// Der Fahrplan von Vortrag 2
export const VORTRAG2 = [
  { titel: 'Eine Gerade lernen', text: 'Was heißt eigentlich Lernen?' },
  { titel: 'Bergab gehen', text: 'Den Fehler Schritt für Schritt verkleinern' },
  { titel: 'Rechnen mit Tabellen', text: 'Matrizen statt Schleifen' },
  { titel: 'Lernen statt Zählen', text: 'Das erste neuronale Netz' },
  { titel: 'Zeichen auf einer Karte', text: 'Ähnliche Zeichen, ähnliche Plätze' },
  { titel: 'Neuronen und Schichten', text: 'Das Netz bekommt Knicke' },
  { titel: 'Training im Großen', text: 'Minibatches und Overfitting' },
]

export const PLAENE: Record<number, { titel: string, text: string }[]> = { 1: VORTRAG1, 2: VORTRAG2 }
