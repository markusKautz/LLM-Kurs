---
title: "Vortrag 2: Neuronale Netze"
colorSchema: light
canvasWidth: 1280
aspectRatio: 16/9
fonts:
  provider: none
  sans: Inter
  mono: JetBrains Mono
transition: fade
layout: full
---

<TitelSchreiber
  kicker="LLM-Kurs · Vortrag 2 von 3"
  titel="Wie lernt eine Maschine?"
  untertitel="Vom Zählen zum neuronalen Netz"
  :reihe="['Zeichenmodelle', 'Neuronale Netze', 'Transformer']"
  :nummer="2"
  quelle="netz"
  legende="live erzeugt von einem neuronalen Netz: 3 Zeichen Kontext, trainiert auf Grimms Märchen"
/>

<!--
**Zeit:** ca. 2 Min. (läuft, während alle ankommen)

**Kernaussage:** Heute ersetzen wir das Zählen durch Lernen.

**Schlagworte:** Vortrag 2 · neuronales Netz · Lernen

- Rechts schreibt wieder ein Programm Märchen. Diesmal ist es kein Zählmodell, sondern ein **neuronales Netz**, das nur 3 Zeichen zurückschaut.
- Der Unterschied zum letzten Mal: Das Netz kommt auch mit Kontexten klar, die es nie gesehen hat. Warum, erfahrt ihr heute.
- Ankündigen: Heute ist es länger, mit einer Pause in der Mitte.
-->

---
clicks: 4
---

<div class="kicker">Rückblick auf Vortrag 1</div>

# Wo wir stehen

<div class="grid grid-cols-3 gap-6 mt-10">
  <div v-click="1" class="karte p-6">
    <div class="beschriftung">Was wir können</div>
    <p class="merksatz mt-3">Zählen, welches Zeichen worauf folgt, und daraus Text ziehen.</p>
  </div>
  <div v-click="2" class="karte p-6">
    <div class="beschriftung">Problem 1</div>
    <p class="merksatz mt-3">Neue Kontexte kennt ein Zählmodell nicht. Verlust: <span class="akzent">unendlich</span>.</p>
  </div>
  <div v-click="3" class="karte p-6">
    <div class="beschriftung">Problem 2</div>
    <p class="merksatz mt-3">Zählen kennt keine Ähnlichkeit: „a“ und „e“ sind für das Modell völlig fremd.</p>
  </div>
</div>

<div v-click="4" class="mt-12 text-3xl text-center">
  Heute: Statt zu zählen, <b class="akzent-blau">lernt</b> das Modell.
</div>

<!--
**Zeit:** ca. 3 Min.

**Kernaussage:** Zählen ist ein guter Anfang, aber es verallgemeinert nicht.

**Schlagworte:** Zählen · unbekannter Kontext · Ähnlichkeit · Lernen

**Frage ans Publikum (vor dem ersten Klick):** "Wer weiß noch, was die Schleife eines Sprachmodells ist?" (vorhersagen, ziehen, anhängen)

[click] Was wir können: Zählen und Ziehen. Das funktioniert und schreibt schon märchenhaften Unsinn.

[click] Problem 1: Im Test tauchen Kontexte auf, die es im Training nie gab. Das Zählmodell sagt dann "unmöglich", der Verlust ist unendlich.

[click] Problem 2: Es gibt keine Ähnlichkeit. Was das Modell über "a" weiß, hilft ihm bei "e" überhaupt nicht.

[click] Die Lösung heute: ein Modell, das **lernt**. Wir fangen ganz einfach an, mit etwas, das gar nichts mit Text zu tun hat.
-->

---
clicks: 7
---

<div class="kicker">Der Plan für heute</div>

# Vom Zählen zum Lernen

<Fahrplan :vortrag="2" />

<!--
**Zeit:** ca. 2 Min.

**Kernaussage:** Sieben Schritte. Die ersten vier vor der Pause, die letzten drei danach.

**Schlagworte:** Fahrplan · Pause nach Schritt 4

[click] **Eine Gerade lernen:** was "Lernen" überhaupt heißt, an einem Beispiel ohne Text.

[click] **Bergab gehen:** wie eine Maschine ihren Fehler Schritt für Schritt kleiner macht.

[click] **Rechnen mit Tabellen:** das wichtigste Werkzeug, die Matrixmultiplikation.

[click] **Lernen statt Zählen:** unser erstes neuronales Netz für Text. Danach ist Pause.

[click] **Zeichen auf einer Karte:** wie ein Netz Ähnlichkeit lernt.

[click] **Neuronen und Schichten:** was ein "Neuron" eigentlich ist.

[click] **Training im Großen:** wie man das schnell macht, und wo die Falle liegt.

- Hinweis: Das ist der Stoff von Notebook 2 (Schritte 1 bis 4) und Notebook 3 (Schritte 5 bis 7).
-->

---
class: abschnitt
---

<div class="kicker">Schritt 1 von 7</div>

# Eine Gerade lernen

<Fahrplan :vortrag="2" :aktuell="1" />

<!--
**Zeit:** ca. 30 Sek.

"Bevor es um Text geht: Was heißt eigentlich lernen? Wir nehmen das einfachste Beispiel, das es gibt."
-->

---
clicks: 3
---

<div class="kicker">Schritt 1: Eine Gerade lernen</div>

# Wie lange dauert die Fahrt zur Berufsschule?

<Gerade modus="raten" />

<!--
**Zeit:** ca. 4 Min.

**Kernaussage:** Aus Beispielen eine Regel finden, mit der man Neues vorhersagen kann. Das ist Lernen.

**Schlagworte:** Beispiele · Regel · Gerade · Vorhersage · Steigung · Verschiebung

[click] Zwölf Lehrlinge: wie weit sie fahren (km) und wie lange sie brauchen (Minuten). Jeder Punkt ist ein Lehrling.
- Man sieht: Je weiter, desto länger. Aber nicht ganz genau, es gibt Ampeln, Stau, Busse.

[click] Eine Gerade nach Augenmaß. Sie hat zwei **Regler**:
- **Steigung** (blau): Minuten pro Kilometer. Wie steil die Gerade ist.
- **Verschiebung** (orange): Minuten, die immer dazukommen, egal wie weit (Parkplatz suchen, zum Bus laufen).
- Diese zwei Zahlen sind die **Gewichte** des Modells. Ein Sprachmodell hat Milliarden davon, das Prinzip ist dasselbe.

[click] Jetzt kommt ein neuer Lehrling, 20 km entfernt. Die Gerade sagt voraus: so viele Minuten.
- **Das ist der Sinn von Lernen:** Vorhersagen für Fälle, die man noch nie gesehen hat.

**Frage ans Publikum:** "Ist diese Gerade gut? Wie könnte man das messen?"
-->

---
clicks: 4
---

<div class="kicker">Schritt 1: Eine Gerade lernen</div>

# Wie gut passt die Gerade?

<Gerade modus="fehler" />

<!--
**Zeit:** ca. 4 Min.

**Kernaussage:** Der Verlust misst, wie weit die Gerade insgesamt danebenliegt. Gute Gerade = kleiner Verlust.

**Schlagworte:** Fehler · Quadrat · Durchschnitt · Verlust

[click] Für jeden Punkt der **Fehler**: der Abstand zwischen Punkt und Gerade (orange Striche).

[click] Wir nehmen jeden Fehler **mal sich selbst**, das heißt quadrieren. Man sieht es als echte Quadrate.
- Warum? Erstens zählen Fehler nach oben und unten gleich (minus mal minus ist plus).
- Zweitens zählen große Fehler viel stärker: doppelter Fehler, vierfache Fläche.

[click] Der **Verlust** ist der Durchschnitt aller Quadrate. Eine einzige Zahl für "wie schlecht ist die Gerade".
- Das kennt ihr aus Vortrag 1: Auch dort war der Verlust eine Zahl, und kleiner ist besser. Nur die Rechnung ist hier eine andere.

[click] Eine bessere Gerade: Die Quadrate schrumpfen, der Verlust sinkt.

**Überleitung:** "Wie findet man die beste Gerade, ohne zu raten?"
-->

---
clicks: 2
---

<div class="kicker">Schritt 1: Eine Gerade lernen</div>

# An einem Regler drehen

<Gerade modus="regler" />

<!--
**Zeit:** ca. 3 Min.

**Kernaussage:** Für jede Einstellung der Regler gibt es einen Verlust. Lernen heißt: die Einstellung mit dem kleinsten Verlust finden.

**Schlagworte:** Regler · Verlustkurve · Tal

- Rechts: Für jede mögliche Steigung zeigt die Kurve den Verlust. Die Verschiebung lassen wir hier fest.

[click] Die Steigung wird verstellt: zu flach, zu steil, und zurück. Die orange Kugel zeigt den Verlust dazu.
- Zu flach: großer Verlust. Zu steil: auch großer Verlust. Dazwischen ein Tal.

[click] Ganz unten im **Tal** ist die beste Steigung.
- Die Regler unten kann man auch selbst bewegen, falls jemand ausprobieren will.

**Überleitung:** "Bei 2 Reglern könnte man noch alles durchprobieren. Ein Sprachmodell hat Milliarden Regler. Wir brauchen einen schlaueren Weg ins Tal."
-->

---
class: abschnitt
---

<div class="kicker">Schritt 2 von 7</div>

# Bergab gehen

<Fahrplan :vortrag="2" :aktuell="2" />

<!--
**Zeit:** ca. 30 Sek.

"Wie findet man das Tal, ohne alles auszuprobieren?"
-->

---
layout: full
---

<SlidevVideo autoplay autoreset="slide" class="video-folie">
  <source src="/videos/Bergab.mp4" type="video/mp4" />
</SlidevVideo>

<!--
**Zeit:** ca. 4 Min. (Video 22 Sek., startet von selbst)

**Kernaussage:** Man schaut, in welche Richtung es bergab geht (Steigung), und macht einen kleinen Schritt dorthin. Immer wieder.

**Schlagworte:** Steigung · Ableitung · Gradientenabstieg · Lernrate

- Bild: Ihr steht im Nebel auf einem Hügel. Ihr seht nichts, aber ihr spürt unter den Füßen, wo es bergab geht. Also ein kleiner Schritt in diese Richtung. Und noch einer.
- Die Kurve ist der Verlust für ein einziges Gewicht w (dieselbe Kurve wie in Notebook 2).
- Die orange Linie an der Kugel zeigt die **Steigung**. Wie ein Straßenschild: Steigung −5 heißt, nach rechts geht es steil bergab.
- **Die Regel:** neues w = altes w − Lernrate × Steigung.
  - Steigung negativ, also wird w größer: die Kugel geht nach rechts.
  - Je steiler, desto größer der Schritt. Am Tal wird es flach, die Schritte werden von allein klein.
- Das heißt **Gradientenabstieg**. Gradient = alle Steigungen zusammen, wenn es viele Gewichte gibt.
- Fachwort für die Steigung: **Ableitung**. Muss man nicht ausrechnen können, das macht gleich PyTorch.
-->

---
clicks: 2
---

<div class="kicker">Schritt 2: Bergab gehen</div>

# Wie groß soll ein Schritt sein?

<Lernrate />

<!--
**Zeit:** ca. 3 Min.

**Kernaussage:** Die Lernrate bestimmt die Schrittgröße. Zu klein ist langsam, zu groß geht schief.

**Schlagworte:** Lernrate · zu klein · zu groß · über das Ziel hinaus

[click] Alle drei starten an derselben Stelle.
- **Zu klein:** Kommt an, braucht aber ewig.
- **Gut:** In wenigen Schritten im Tal.
- **Zu groß:** Springt über das Tal auf die andere Seite, dort ist es noch steiler, der nächste Sprung noch größer. Es wird immer schlimmer.

[click] Die Formel noch einmal. Die Lernrate ist eine Zahl, die **wir** festlegen. Die richtige findet man durch Ausprobieren.
- Im Notebook seht ihr genau das: Mit einer zu großen Lernrate springt der Verlust wild herum.
-->

---
clicks: 1
---

<div class="kicker">Schritt 2: Bergab gehen</div>

# Die Maschine findet die Gerade selbst

<Gerade modus="lernen" />

<!--
**Zeit:** ca. 4 Min.

**Kernaussage:** Mit Gradientenabstieg drehen sich beide Regler gleichzeitig in die richtige Richtung. Niemand muss raten.

**Schlagworte:** zwei Gewichte · Verlustlandschaft · Weg ins Tal

- Links startet eine ziemlich schlechte Gerade: fast flach und viel zu hoch.
- Rechts die **Verlustlandschaft**: jeder Punkt ist eine Einstellung der beiden Regler (Steigung nach rechts, Verschiebung nach oben). Je dunkler blau, desto kleiner der Verlust. Der gestrichelte Kreis ist das Ziel.

[click] Das Lernen läuft. Bei jedem Schritt:
1. Verlust berechnen
2. Steigung für **beide** Regler bestimmen
3. Beide ein kleines Stück bergab drehen
- Rechts sieht man den Weg der Kugel durch die Landschaft, links dreht sich die Gerade passend.
- Der Weg ist nicht gerade, weil die Landschaft ein langes, schräges Tal ist.

**Merksatz:** Das ist Lernen, wie es jedes neuronale Netz macht. Nur mit Milliarden Reglern statt zwei.
-->

---
clicks: 3
---

<div class="kicker">Schritt 2: Bergab gehen</div>

# Woher kennt der Computer die Steigung?

<Rechenkette />

<!--
**Zeit:** ca. 4 Min.

**Kernaussage:** PyTorch merkt sich jeden Rechenschritt und rechnet die Steigung rückwärts aus. Das heißt Backpropagation.

**Schlagworte:** vorwärts rechnen · rückwärts · Backpropagation · backward() · .grad

- Das Problem: Bei Milliarden Gewichten kann man nicht für jedes einzelne ausprobieren, wie sich der Verlust ändert. Das würde ewig dauern.

[click] **Vorwärts:** Die Rechnung aus dem Video, in kleinen Schritten. w = 0,5, minus 3, hoch 2, plus 1 ergibt den Verlust 7,25.

[click] **Rückwärts:** Von hinten nach vorn reicht PyTorch die Steigung weiter. Jeder Schritt kennt seine eigene kleine Regel und nimmt die Steigung damit mal.
- "+1" ändert nichts (mal 1). "hoch 2" macht mal 2 mal den Wert (mal 2 mal −2,5 = −5). "−3" ändert nichts.
- Am Ende steht bei w die Steigung −5. Genau das, was das Video gezeigt hat.
- **Nicht die Regeln auswendig lernen lassen.** Nur das Prinzip: rückwärts durch alle Schritte.

[click] In PyTorch ist das eine Zeile: verlust.backward(). Danach steht die Steigung in w.grad.
- Das Besondere: Das geht für **alle** Gewichte gleichzeitig in einem Durchgang, egal ob eins oder eine Milliarde.
-->

---
class: abschnitt
---

<div class="kicker">Schritt 3 von 7</div>

# Rechnen mit Tabellen

<Fahrplan :vortrag="2" :aktuell="3" />

<!--
**Zeit:** ca. 30 Sek.

"Neuronale Netze rechnen nicht mit einzelnen Zahlen, sondern mit ganzen Tabellen auf einmal."
-->

---
clicks: 5
---

<div class="kicker">Schritt 3: Rechnen mit Tabellen</div>

# Tensoren: Zahlen in jeder Form

<TensorFormen />

<!--
**Zeit:** ca. 2 Min. Kann bei Zeitnot kürzer werden.

**Kernaussage:** Ein Tensor ist eine Zahl, eine Liste, eine Tabelle oder ein Stapel von Tabellen. Die Form sagt, wie viele Zahlen in welcher Richtung.

**Schlagworte:** Tensor · Form (shape) · ohne Schleife

[click] Eine einzelne Zahl, zum Beispiel der Verlust.

[click] Eine Liste, zum Beispiel die Koordinaten eines Zeichens. Form (3,): 3 Zahlen.

[click] Eine Tabelle, zum Beispiel mehrere Beispiele untereinander. Form (2, 3): 2 Zeilen, 3 Spalten.

[click] Ein Stapel von Tabellen. Beim Training rechnet man viele Tabellen gleichzeitig.

[click] Alles heißt in PyTorch **Tensor**. Für C#-Leute: wie ein mehrdimensionales Array, aber man rechnet damit wie mit einer einzelnen Zahl. tabelle * 2 verdoppelt alle Zahlen, ohne Schleife.
-->

---
layout: full
---

<SlidevVideo autoplay autoreset="slide" class="video-folie">
  <source src="/videos/MatrixMal.mp4" type="video/mp4" />
</SlidevVideo>

<!--
**Zeit:** ca. 3 Min. (Video 19 Sek., startet von selbst)

**Kernaussage:** Die Matrixmultiplikation (@) rechnet für jede Spalte eine gewichtete Summe. Sie ist die wichtigste Rechnung in jedem neuronalen Netz.

**Schlagworte:** Matrixmultiplikation · @ · Zeile mal Spalte · gewichtete Summe · Formen müssen passen

- Für jede Spalte von W: erste Zahl von x mal erste Zahl der Spalte, plus zweite mal zweite.
- Erste Spalte: 1·10 + 2·1 = 12. Zweite: 24. Dritte: 36.
- **Gewichtete Summe:** x bestimmt, wie stark jede Zeile von W zählt. Hier zählt die zweite Zeile doppelt so viel wie die erste.
- **Formen:** (1, 2) @ (2, 3) ergibt (1, 3). Die inneren Zahlen müssen gleich sein, die äußeren bleiben übrig.
  - Wenn im Notebook der Fehler "shapes cannot be multiplied" kommt: Die Formen passen nicht.
- Für C#-Leute: zwei verschachtelte for-Schleifen, PyTorch macht es in einem Rutsch und sehr schnell.
-->

---
class: abschnitt
---

<div class="kicker">Schritt 4 von 7</div>

# Lernen statt Zählen

<Fahrplan :vortrag="2" :aktuell="4" />

<!--
**Zeit:** ca. 30 Sek.

"Jetzt verbinden wir alles: das Zählmodell aus Vortrag 1 und das Lernen von heute."
-->

---
clicks: 4
---

<div class="kicker">Schritt 4: Lernen statt Zählen</div>

# Das Zählmodell ist eine Matrix

<OneHotAuswahl />

<!--
**Zeit:** ca. 4 Min. Der Aha-Moment, langsam.

**Kernaussage:** Ein One-Hot-Vektor mal eine Matrix wählt genau eine Zeile aus. Das Zählmodell aus Vortrag 1 ist also eine Matrixmultiplikation.

**Schlagworte:** One-Hot · Zeile auswählen · Gewichte statt Zähler

- Rechts die Bigramm-Tabelle aus Vortrag 1 (nur für 5 Zeichen, in Prozent). Zeile = jetzt, Spalte = danach.

[click] **One-Hot:** Ein Zeichen wird zu einer Liste mit lauter Nullen und einer einzigen 1, an der Stelle des Zeichens. Hier für "e".

[click] Matrixmultiplikation: Jede Zeile der Tabelle wird mit 0 oder 1 malgenommen. Alles mal 0 verschwindet.

[click] Übrig bleibt genau die Zeile von "e": die Wahrscheinlichkeiten für das Zeichen nach "e".

[click] Mit "n" kommt die Zeile von "n" heraus.

**Merksatz:** Das Zählmodell ist eine Matrixmultiplikation. Die Idee eines neuronalen Netzes: Die Matrix wird nicht gezählt, sondern **gelernt**. Die Zahlen darin heißen **Gewichte**, die Matrix W.
-->

---
clicks: 2
---

<div class="kicker">Schritt 4: Lernen statt Zählen</div>

# Softmax: aus beliebigen Zahlen werden Wahrscheinlichkeiten

<SoftmaxStufen />

<!--
**Zeit:** ca. 3 Min.

**Kernaussage:** Ein Netz gibt beliebige Zahlen aus (Logits). Softmax macht daraus Wahrscheinlichkeiten.

**Schlagworte:** Logits · torch.exp · durch die Summe teilen · Softmax

- Problem: Beim Lernen werden die Gewichte verändert. Dabei können negative Zahlen herauskommen, und die Zeilen ergeben nicht mehr 100 %.
- Die Zahlen, die das Netz ausgibt, heißen **Logits**. Großer Logit = das Netz hält das Zeichen für wahrscheinlich.

[click] **torch.exp** macht jede Zahl positiv, und größer bleibt größer. Aus negativen Zahlen werden kleine positive.
- Wie torch.exp genau rechnet, ist egal. Nur diese zwei Eigenschaften zählen.

[click] **Durch die Summe teilen**, genau wie beim Zählmodell. Ergebnis: Wahrscheinlichkeiten, zusammen 100 %.
- Diese zwei Schritte zusammen heißen **Softmax**. Ihr schreibt die Funktion im Notebook selbst.
-->

---
clicks: 4
---

<div class="kicker">Schritt 4: Lernen statt Zählen</div>

# Was der Gradient dem Netz sagt

<GradientBalken />

<!--
**Zeit:** ca. 4 Min.

**Kernaussage:** Für jedes Zeichen sagt der Gradient: zu viel oder zu wenig vorhergesagt. Er ist einfach Vorhersage minus Wahrheit.

**Schlagworte:** Vorhersage · Wahrheit · Gradient · zu viel · zu wenig

- Verlust wie in Vortrag 1: wie überrascht ist das Netz vom richtigen Zeichen. Fachwort: **Kreuzentropie**.
- Beispiel: Das Netz soll das Zeichen nach etwas vorhersagen, richtig ist "n".

[click] Die Vorhersage nach der Softmax. Das Netz gibt "n" nur wenig.

[click] Die Wahrheit: "n" 100 %, alles andere 0 %.

[click] Der Gradient ist **Vorhersage minus Wahrheit**. Das rechnet PyTorch mit backward() aus.
- **Positiv** (orange, nach oben): zu viel vorhergesagt. Der Lernschritt macht diese Logits kleiner.
- **Negativ** (grün, nach unten): zu wenig. Nur beim richtigen Zeichen. Der Lernschritt macht diesen Logit größer.

[click] Ein Lernschritt. Die Balken links ändern sich: "n" bekommt deutlich mehr. Mehr passiert beim Lernen nicht, nur sehr oft.
-->

---
clicks: 2
---

<div class="kicker">Schritt 4: Lernen statt Zählen</div>

# Das erste Netz lernt

<BigrammNetzLernt />

<!--
**Zeit:** ca. 4 Min.

**Kernaussage:** Das Netz startet mit lauter Nullen und lernt durch Gradientenabstieg genau das, was wir in Vortrag 1 gezählt haben.

**Schlagworte:** Bigramm-Netz · Start bei 0 · Lernschritte · gleiches Ergebnis wie Zählen

- Links die Gewichte W des Netzes, nach der Softmax. Anfangs alles gleich hell: Jedes Zeichen ist gleich wahrscheinlich (1 von 40). Verlust 3,69.

[click] Das Training läuft live, hier im Browser. 200 Lernschritte auf dem ganzen Märchentext.
- Man sieht, wie das Muster entsteht: erst die häufigsten Paare, dann immer feiner.
- Die Verlustkurve in der Mitte fällt schnell und wird dann flach.

[click] Rechts die gezählte Tabelle aus Vortrag 1. Fast gleich!
- Das Netz hat ganz von allein herausgefunden, was wir gezählt haben. Der Verlust landet fast genau bei dem des Zählmodells.
- **Frage:** "Wozu der Aufwand, wenn Zählen dasselbe ergibt?" Antwort: Lernen funktioniert auch, wo Zählen nicht mehr geht. Das sehen wir nach der Pause.

**Ende von Notebook 2.** Hier passt die Pause.
-->

---
class: abschnitt
---

<div class="kicker">Pause</div>

# 10 Minuten Pause

<PauseUhr :minuten="10" />

<!--
**Zeit:** 10 Min.

Die Uhr läuft automatisch, sobald die Folie erscheint.

Bis hier: Stoff von Notebook 2. Nach der Pause: Notebook 3.
-->

---
class: abschnitt
---

<div class="kicker">Schritt 5 von 7</div>

# Zeichen auf einer Karte

<Fahrplan :vortrag="2" :aktuell="5" />

<!--
**Zeit:** ca. 1 Min. inklusive kurzer Wiederholung

Kurz wiederholen, was vor der Pause war: Lernen heißt bergab gehen. Das Bigramm-Netz lernt dasselbe wie das Zählen.

"Jetzt geben wir dem Netz mehr Kontext. Und dabei lernt es etwas, was Zählen nie konnte: Ähnlichkeit."
-->

---
clicks: 4
---

<div class="kicker">Schritt 5: Zeichen auf einer Karte</div>

# Drei Zeichen als Eingabe

<EinbettungNachschlagen kontext="der" />

<!--
**Zeit:** ca. 4 Min.

**Kernaussage:** Jedes Zeichen bekommt einen Platz auf einer Karte (Koordinaten). Diese Koordinaten werden mitgelernt. Das heißt Einbettung.

**Schlagworte:** Kontext · Koordinaten · Einbettung · Embedding · nachschlagen

- Das Netz soll jetzt 3 Zeichen sehen, hier "der".

[click] Mit One-Hot wären das 3 mal 40 = 120 Zahlen, fast alle 0. Und jedes Zeichen wäre für das Netz gleich weit von jedem anderen entfernt: keine Ähnlichkeit.

[click] Die neue Idee: eine Tabelle mit **Koordinaten** für jedes Zeichen. Wie Orte auf einer Landkarte, hier mit 2 Zahlen: x und y.
- Ganz wichtig: Die Tabelle ist am Anfang zufällig und wird **mitgelernt**, genau wie alle anderen Gewichte.

[click] Für jedes der 3 Zeichen wird die Zeile nachgeschlagen.

[click] Die Koordinaten werden nebeneinandergelegt: nur 6 Zahlen.
- Fachwort: **Einbettung** (englisch Embedding).
- Die Hoffnung: Zeichen, die sich ähnlich verhalten, landen beim Lernen nah beieinander. Ob das klappt, sehen wir gleich.
-->

---
class: abschnitt
---

<div class="kicker">Schritt 6 von 7</div>

# Neuronen und Schichten

<Fahrplan :vortrag="2" :aktuell="6" />

<!--
**Zeit:** ca. 30 Sek.

"Was passiert mit den 6 Zahlen? Jetzt kommen die Neuronen."
-->

---
clicks: 5
---

<div class="kicker">Schritt 6: Neuronen und Schichten</div>

# Ein Neuron

<Neuron />

<!--
**Zeit:** ca. 4 Min.

**Kernaussage:** Ein Neuron nimmt Zahlen, gewichtet sie, zählt zusammen, addiert eine Verschiebung und schickt das Ergebnis durch ReLU.

**Schlagworte:** Eingaben · Gewichte · Summe · Verschiebung · ReLU

[click] Drei Eingaben, jede mit einem Gewicht. Dicke Linie = großes Gewicht. Orange = negatives Gewicht.

[click] Jede Eingabe wird mit ihrem Gewicht malgenommen.

[click] Alles zusammenzählen, dazu die Verschiebung. Das kennt ihr: Es ist genau die Gerade von vorhin, nur mit mehr Eingaben. Und es ist eine Spalte der Matrixmultiplikation.

[click] **ReLU:** Ist das Ergebnis negativ, wird es 0. Sonst bleibt es. Mehr ist ReLU nicht.
- Das Neuron "feuert" also nur, wenn genug zusammenkommt.

[click] Anderes Beispiel: Hier kommt etwas Negatives heraus, ReLU macht 0 daraus. Das Neuron bleibt stumm.

- Der Name kommt von Nervenzellen im Gehirn. Aber Vorsicht: Mit echten Nervenzellen hat das nur sehr entfernt zu tun.
-->

---
clicks: 4
---

<div class="kicker">Schritt 6: Neuronen und Schichten</div>

# Warum der Knick so wichtig ist

<ReluBaukasten />

<!--
**Zeit:** ca. 3 Min.

**Kernaussage:** Jedes Neuron bringt einen Knick. Aus genug Knicken lässt sich jede Kurve zusammensetzen.

**Schlagworte:** Knick · viele Neuronen · jede Form

- Gestrichelt: irgendeine krumme Kurve, die das Netz lernen soll.
- Ohne ReLU wäre alles nur eine Gerade, auch mit vielen Schichten. Eine Gerade nach einer Gerade bleibt eine Gerade.

[click] 1 Neuron: ein Knick. Grob.

[click] 3 Neuronen: Die Form ist schon zu erahnen.

[click] 6 Neuronen: schon ziemlich nah.

[click] 24 Neuronen: kaum noch ein Unterschied.

**Merksatz:** Mehr Neuronen, mehr Knicke, mehr Formen. Damit kann ein Netz beliebig komplizierte Zusammenhänge lernen.
-->

---
clicks: 4
---

<div class="kicker">Schritt 6: Neuronen und Schichten</div>

# Das ganze Netz, live gerechnet

<NetzFluss :kontexte="['kön', 'er ', 'sch', 'und']" />

<!--
**Zeit:** ca. 4 Min.

**Kernaussage:** 3 Zeichen → Koordinaten → 200 Neuronen mit ReLU → für jedes Zeichen ein Logit → Softmax. Das ist das ganze Netz aus Notebook 3.

**Schlagworte:** Einbettung · verborgene Schicht · Ausgabe · Softmax · live

- Das Netz ist echt: trainiert auf den Märchen, die Rechnung läuft hier live im Browser.
- Diesmal 10 Koordinaten pro Zeichen statt 2, und 200 Neuronen.

[click] "kön": Das Netz ist sich ziemlich sicher, es kommt "i" (könig), sonst "n" (können).
- In der Mitte: Nur ein Teil der Neuronen ist aktiv (blau), der Rest ist durch ReLU auf 0 (grau).

[click] "er␣": Ein Wort ist zu Ende, das nächste beginnt. Jetzt ist das Netz unsicher, viele Möglichkeiten.

[click] "sch": oft "l" (schloss, schlafen), "e" oder "w". Mehrere gute Möglichkeiten.

[click] "und": meist ein Leerzeichen.
- Jeder Kontext weckt andere Neuronen auf. Was ein einzelnes Neuron "bedeutet", weiß niemand genau.
-->

---
class: abschnitt
---

<div class="kicker">Schritt 7 von 7</div>

# Training im Großen

<Fahrplan :vortrag="2" :aktuell="7" />

<!--
**Zeit:** ca. 30 Sek.

"Wie trainiert man so ein Netz auf fast einer halben Million Zeichen? Und was lernt es dabei?"
-->

---
clicks: 2
---

<div class="kicker">Schritt 7: Training im Großen</div>

# Minibatches: schneller lernen mit Stichproben

<Minibatch />

<!--
**Zeit:** ca. 3 Min.

**Kernaussage:** Für jeden Lernschritt reicht eine kleine Zufallsauswahl der Beispiele. Das ist viel schneller.

**Schlagworte:** Minibatch · Stichprobe · wackelige Kurve

- Wir haben über 400.000 Trainingsbeispiele. Für jeden einzelnen Lernschritt alle durchzurechnen, wäre sehr langsam.

[click] Stattdessen: Für jeden Schritt nur 32 zufällige Beispiele. Das heißt **Minibatch**.
- Wie bei einer Umfrage: Man fragt nicht alle Menschen, sondern eine Stichprobe. Das Ergebnis ist nicht perfekt, aber gut genug.

[click] Die echte Lernkurve aus dem Training: Sie wackelt stark, weil jeder Minibatch andere Beispiele hat. Aber im Mittel geht es klar bergab.
- 30.000 Schritte mit je 32 Beispielen statt 30.000 Schritte mit je 400.000.
-->

---
clicks: 3
---

<div class="kicker">Schritt 7: Training im Großen</div>

# Was hat das Netz gelernt?

<KarteEntsteht />

<!--
**Zeit:** ca. 4 Min. Der zweite Aha-Moment.

**Kernaussage:** Ohne dass es jemand gesagt hat, sortiert das Netz die Zeichen: Vokale zu Vokalen, Satzzeichen zu Satzzeichen.

**Schlagworte:** Karte der Zeichen · Ähnlichkeit gelernt · niemand hat es ihm gesagt

- Das ist die echte Koordinaten-Tabelle eines Netzes mit 2 Koordinaten, während des Trainings aufgezeichnet.
- Am Anfang liegen alle Zeichen zufällig durcheinander.

[click] Das Training läuft im Zeitraffer, 30.000 Lernschritte. Die Zeichen wandern.

[click] Die **Vokale** markieren: Sie landen in derselben Ecke.
- Niemand hat dem Netz gesagt, was ein Vokal ist! Es hat nur gemerkt: Nach diesen Zeichen passieren ähnliche Dinge.

[click] Die **Satzzeichen**: auch sie liegen zusammen. Nach Punkt, Komma, Fragezeichen kommt ähnliches (Leerzeichen, Zeilenumbruch).

**Merksatz:** Genau das konnte das Zählmodell nicht: Ähnlichkeit. Was das Netz über "a" lernt, hilft ihm jetzt auch bei "e".
-->

---
clicks: 3
---

<div class="kicker">Schritt 7: Training im Großen</div>

# Ein Kontext, den es nie gesehen hat

<UnbekannterKontext kontext="hnc" />

<!--
**Zeit:** ca. 3 Min.

**Kernaussage:** Das Netz verallgemeinert: Es gibt auch für unbekannte Kontexte sinnvolle Antworten.

**Schlagworte:** unbekannter Kontext · verallgemeinern · Zählmodell scheitert

[click] Im Testtext steht "hühnchen" bzw. "hähnchen". Die Zeichenfolge "hnc" kam im ganzen Training kein einziges Mal vor.

[click] Das Zählmodell mit 3 Zeichen Kontext hat diesen Kontext nie gezählt. Es weiß gar nichts.

[click] Das Netz gibt "h" über 90 %. Richtig!
- Wie? Genau weiß man das bei einem Netz nie. Vermutlich hat es aus ähnlichen Kontexten gelernt, dass nach "nc" fast immer "h" kommt. Die Ähnlichkeit steckt in den Koordinaten und Neuronen.
- Das heißt **verallgemeinern**, das wichtigste Ziel von maschinellem Lernen.
-->

---
clicks: 3
---

<div class="kicker">Schritt 7: Training im Großen</div>

# Größer ist nicht immer besser

<Overfitting />

<!--
**Zeit:** ca. 4 Min.

**Kernaussage:** Ein zu großes Netz lernt die Trainingsdaten auswendig. Auf neuen Daten wird es schlechter. Das heißt Overfitting.

**Schlagworte:** Overfitting · auswendig lernen · Training gegen Test · Lücke

- Hier mit einem kurzen Text (dem aus den Notebooks, rund 11.000 Zeichen), damit man den Effekt gut sieht.
- Blau: Verlust auf dem Training. Orange: Verlust auf dem Test.

[click] **Kleines Netz** (7.000 Gewichte): Beide Kurven fallen, Test bleibt etwas über Training. Gesund.

[click] **Riesiges Netz** (fast 200.000 Gewichte, 8 Zeichen Kontext): Training fällt fast auf 0. Aber der Test steigt wieder an!

[click] Die Lücke zwischen den Kurven: Das Netz hat den Trainingstext **auswendig gelernt**.
- Wie in Vortrag 1 beim Zählen mit viel Kontext. Und wie in der Schule: Auswendiglernen hilft nur bei den Übungsaufgaben.
- Gegenmittel: mehr Daten oder ein kleineres Netz. Große Sprachmodelle trainiert man deshalb mit riesigen Textmengen.
-->

---
clicks: 2
---

<div class="kicker">Schritt 7: Training im Großen</div>

# Das Netz schreibt

<NetzSchreibt />

<!--
**Zeit:** ca. 3 Min.

**Kernaussage:** Mit nur 3 Zeichen Kontext schreibt das Netz besser als jedes Zählmodell, und es hat einen ehrlichen, endlichen Testverlust.

**Schlagworte:** Text erzeugen · Testverlust · Vergleich

[click] Das Netz schreibt live, dieselbe Schleife wie immer: vorhersagen, ziehen, anhängen.
- Viele echte Wörter, manche Fantasiewörter. Sinn ergibt es noch nicht.

[click] Der Vergleich auf dem Testtext:
- **Zählen:** unendlich (unbekannte Paare).
- **Bigramm-Netz:** 2,27. Es weiß dasselbe wie das Zählen, gibt aber nie ganz 0.
- **Zeichen-Netz mit 3 Zeichen:** 1,60. Deutlich besser.
-->

---
clicks: 3
---

<div class="kicker">Die Grenze</div>

# Drei Zeichen sind ein kurzes Gedächtnis

<div class="grid grid-cols-2 gap-8 mt-10">
  <div v-click="1" class="karte p-6">
    <div class="beschriftung">Das Problem</div>
    <p class="merksatz mt-3">Am Satzende weiß das Netz nicht mehr, wie der Satz angefangen hat. Es sieht immer nur die letzten 3 Zeichen.</p>
  </div>
  <div v-click="2" class="karte p-6">
    <div class="beschriftung">Einfach mehr Zeichen?</div>
    <p class="merksatz mt-3">Ein festes Fenster mit 16 Zeichen macht das Netz riesig. Und riesig heißt: <span class="akzent">auswendig lernen</span>.</p>
  </div>
</div>

<div v-click="3" class="mt-10 text-2xl text-center">
  Die Lösung in Vortrag 3: Jedes Zeichen darf auf <b class="akzent">alle</b> Zeichen davor schauen. Das heißt <b class="akzent-blau">Aufmerksamkeit</b>.
</div>

<!--
**Zeit:** ca. 2 Min.

**Kernaussage:** Unser Netz hat ein festes, kurzes Fenster. Größere Fenster machen es nur größer, nicht schlauer.

**Schlagworte:** festes Fenster · Gedächtnis · Aufmerksamkeit

[click] Beispiel: "Der König, der drei Töchter hatte, ..." Wenn das Netz beim Verb ankommt, ist "König" längst aus dem Fenster gerutscht.

[click] Fenster vergrößern klingt einfach. Aber: Mehr Eingaben heißt mehr Gewichte, und wir haben gerade gesehen, was dann passiert.

[click] Die Lösung ist eine ganz andere Idee: Aufmerksamkeit. Das ist das Herzstück von ChatGPT und Thema von Vortrag 3.
-->

---
---

<div class="kicker">Zusammenfassung</div>

# Was ihr heute gelernt habt

<div class="raster-karten grid-cols-4">
  <div v-click class="karte"><div class="nr">1</div><h3>Lernen</h3><p>Gewichte so einstellen, dass der Verlust klein wird. Wie eine Gerade durch Punkte.</p></div>
  <div v-click class="karte"><div class="nr">2</div><h3>Bergab gehen</h3><p>Steigung bestimmen, ein Stück bergab, immer wieder. Die Steigung liefert PyTorch mit backward().</p></div>
  <div v-click class="karte"><div class="nr">3</div><h3>Tabellen</h3><p>Tensoren und Matrixmultiplikation: viele gewichtete Summen auf einmal.</p></div>
  <div v-click class="karte"><div class="nr">4</div><h3>Lernen statt Zählen</h3><p>Softmax macht Wahrscheinlichkeiten. Das Bigramm-Netz lernt, was wir gezählt haben.</p></div>
  <div v-click class="karte"><div class="nr">5</div><h3>Karte der Zeichen</h3><p>Koordinaten für jedes Zeichen, mitgelernt. Ähnliche Zeichen landen nah beieinander.</p></div>
  <div v-click class="karte"><div class="nr">6</div><h3>Neuronen</h3><p>Gewichtete Summe plus ReLU. Viele Knicke ergeben jede Form.</p></div>
  <div v-click class="karte"><div class="nr">7</div><h3>Training</h3><p>Minibatches machen es schnell. Zu große Netze lernen auswendig.</p></div>
  <div v-click class="karte merksatz-karte"><h3>Das Wichtigste</h3><p>Ein Netz verallgemeinert: Es kommt auch mit Kontexten klar, die es nie gesehen hat.</p></div>
</div>

<!--
**Zeit:** ca. 2 Min.

Wie in Vortrag 1: Jeden Schritt kurz von den Teilnehmern wiederholen lassen. "Was macht ReLU?" "Was ist eine Lernrate?"

[click] Lernen.

[click] Bergab gehen.

[click] Tabellen.

[click] Lernen statt Zählen.

[click] Karte der Zeichen.

[click] Neuronen.

[click] Training.

[click] Das Wichtigste: Verallgemeinern.
-->

---
---

<div class="kicker">Wie es weitergeht</div>

# Jetzt seid ihr dran

<div class="grid grid-cols-3 gap-6 mt-10">
  <div v-click class="karte p-6">
    <div class="beschriftung">Notebook 2</div>
    <h3 class="text-xl font-semibold mt-2 mb-3">Lernen mit PyTorch</h3>
    <ul class="leading-relaxed">
      <li>Tensoren und Matrizen</li>
      <li>One-Hot und Softmax</li>
      <li>Steigung und bergab gehen</li>
      <li>das Bigramm-Netz trainieren</li>
    </ul>
  </div>
  <div v-click class="karte p-6">
    <div class="beschriftung">Notebook 3</div>
    <h3 class="text-xl font-semibold mt-2 mb-3">Ein größeres Netz</h3>
    <ul class="leading-relaxed">
      <li>Koordinaten für Zeichen</li>
      <li>ReLU und Neuronen</li>
      <li>Minibatches und Training</li>
      <li>die Karte der Zeichen</li>
    </ul>
  </div>
  <div v-click class="karte p-6">
    <div class="beschriftung">Vortrag 3</div>
    <h3 class="text-xl font-semibold mt-2 mb-3">Der Transformer</h3>
    <ul class="leading-relaxed">
      <li>Zurückschauen auf alles</li>
      <li>Aufmerksamkeit</li>
      <li>der Bauplan von ChatGPT</li>
      <li>was große Modelle anders machen</li>
    </ul>
  </div>
</div>

<!--
**Zeit:** ca. 2 Min., danach Fragen

- Notebook 2 deckt Schritt 1 bis 4 ab (ohne die Gerade, die war nur zum Verstehen).
- Notebook 3 deckt Schritt 5 bis 7 ab.
- Notebook 3 endet mit einem Teil über die Grenzen von Sprachmodellen.

**Typische Fragen:**
- "Lernt ChatGPT gerade, während ich mit ihm rede?" Nein. Das Training ist vorher abgeschlossen, beim Antworten werden die Gewichte nicht verändert.
- "Wie lange dauert das Training von großen Modellen?" Wochen bis Monate auf Tausenden Grafikkarten. Unser Netz braucht etwa eine Minute.
-->
