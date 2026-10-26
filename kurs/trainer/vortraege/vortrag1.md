---
title: "Vortrag 1: Zeichenmodelle"
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
  kicker="LLM-Kurs · Vortrag 1 von 3"
  titel="Wie schreibt eine Maschine?"
  untertitel="Zeichen, Zählen und Zufall"
  :reihe="['Zeichenmodelle', 'Neuronale Netze', 'Transformer']"
  :nummer="1"
/>

<!--
**Zeit:** ca. 2 Min. (läuft, während alle ankommen)

**Kernaussage:** Heute verstehen wir, wie eine Maschine Text schreiben kann. Ohne Mathe-Vorwissen.

**Schlagworte:** Vortragsreihe · drei Teile · heute: Zeichenmodelle

- Die Folie läuft schon: Rechts schreibt ein Programm live Märchen, Zeichen für Zeichen.
- Noch **nichts erklären**, nur neugierig machen: "Am Ende von heute könnt ihr genau erklären, was da rechts passiert. Und ihr baut es danach selbst."
- Die kleine Karte über dem Cursor: das sind die Kandidaten für das nächste Zeichen. Das Orange ist das gezogene.
- Reihe kurz vorstellen: heute Zeichenmodelle, dann neuronale Netze, dann Transformer (das "T" in ChatGPT).
-->

---
clicks: 2
---

<div class="kicker">Einstieg</div>

# Was passiert, wenn ChatGPT antwortet?

<ChatTippen />

<!--
**Zeit:** ca. 2 Min.

**Kernaussage:** Die Antwort entsteht Stück für Stück, nicht auf einmal.

**Schlagworte:** Stück für Stück · Token · Wortstücke

**Frage ans Publikum (vor dem ersten Klick):** "Was glaubt ihr, was ChatGPT macht, wenn es antwortet? Sucht es im Internet? Hat es die Antwort irgendwo gespeichert?" Antworten sammeln, **nicht auflösen**.

[click] Die Antwort erscheint Stück für Stück. Darauf achten lassen: Die Stücke sind keine ganzen Wörter, manchmal nur halbe.

[click] Jetzt sieht man die Stücke. Sie heißen **Tokens**. "Comp" + "iler", "Prozess" + "or".
- Ehrlich sagen: Die Zerlegung hier ist ungefähr so, wie ein echtes Modell es macht.
- Wir machen es uns heute einfacher: Unsere Stücke sind **einzelne Zeichen**. Das Prinzip ist dasselbe.

**Überleitung:** "Wie entscheidet das Modell, welches Stück als Nächstes kommt?"
-->

---
clicks: 3
---

<div class="kicker">Die Grundidee</div>

# Ein Sprachmodell kann genau eine Sache

<NaechstesZeichen start="es war einmal ein" />

<!--
**Zeit:** ca. 4 Min. Langsam, das ist die wichtigste Folie des Tages.

**Kernaussage:** Ein Sprachmodell schätzt nur, was als Nächstes kommt. Dann zieht es, hängt an und beginnt von vorn.

**Schlagworte:** Kontext · Vorhersage · Wahrscheinlichkeit · Ziehen · Schleife

[click] **Vorhersagen.** Das Modell schaut auf die letzten 4 Zeichen, den **Kontext** (orange). Mehr weiß es nicht.
- Daraus schätzt es für jedes mögliche Zeichen, wie wahrscheinlich es als Nächstes kommt.
- Nach "␣ein" kommt oft ein e (eine, einem, einen) oder ein Leerzeichen (das Wort ist zu Ende).
- "Wahrscheinlichkeit" in einfachen Worten: 48 % heißt, in etwa der Hälfte der Fälle.

[click] **Ziehen.** Wichtig: Es nimmt **nicht** einfach das wahrscheinlichste Zeichen. Es zieht, wie bei einem Glücksrad. Dazu gleich mehr.
- Das gezogene Zeichen wird angehängt.

[click] **Und wieder von vorn.** Jetzt läuft die Schleife allein. Der Kontext wandert mit.
- "Mehr passiert nicht. Auch ChatGPT macht genau das, nur mit Wortstücken und einem viel besseren Modell."
- Ruhig 20 bis 30 Sekunden zuschauen lassen.

**Überleitung:** "Das bauen wir heute nach. Woher kommen die Prozentzahlen?"
-->

---
clicks: 5
---

<div class="kicker">Der Plan für heute</div>

# Wir bauen so ein Modell selbst. Nur mit Zählen.

<Fahrplan />

<!--
**Zeit:** ca. 2 Min.

**Kernaussage:** Fünf Schritte, und jeder ist einfach.

**Schlagworte:** Fahrplan · fünf Schritte · keine Mathe nötig

[click] **Text wird zu Zahlen:** Computer rechnen nur mit Zahlen.

[click] **Zählen:** Woher die Prozentzahlen kommen.

[click] **Ziehen:** Warum Zufall dazugehört.

[click] **Mehr Kontext:** Warum weiter zurückschauen hilft, und wo es hakt.

[click] **Bewerten:** Wie man misst, ob ein Modell gut ist.

- Hinweis: Nach dem Vortrag baut ihr genau das in Notebook 1 selbst, in Python.
-->

---
clicks: 4
---

<div class="kicker">Ein Blick zurück</div>

# Die Idee ist über 100 Jahre alt

<Zeitleiste :ereignisse="[
  { jahr: '1913', titel: 'Andrei Markow', text: 'zählt von Hand 20.000 Buchstaben aus Puschkins Versroman Eugen Onegin.' },
  { jahr: '1948', titel: 'Claude Shannon', text: 'erzeugt künstlichen englischen Text, nur durch Zählen und Ziehen.' },
  { jahr: '2017', titel: 'Der Transformer', text: 'Forscher bei Google stellen den Bauplan vor, auf dem heutige Sprachmodelle beruhen.' },
  { jahr: '2022', titel: 'ChatGPT', text: 'erscheint und macht Sprachmodelle in kurzer Zeit weltbekannt.', hervor: true },
]" />

<!--
**Zeit:** ca. 2 Min. Kann bei Zeitnot entfallen.

**Kernaussage:** Die Grundidee (zählen, was worauf folgt) ist alt. Neu sind die Rechenleistung und bessere Modelle.

**Schlagworte:** Markow · Shannon · Transformer · ChatGPT

[click] **1913, Andrei Markow**, russischer Mathematiker. Hat ohne Computer gezählt, wie oft auf einen Vokal ein Vokal oder ein Konsonant folgt. Das machen wir gleich nach.
- Nach ihm heißen heute die "Markow-Ketten": Das Nächste hängt nur vom Letzten ab.

[click] **1948, Claude Shannon**, Begründer der Informationstheorie. Er hat mit Zählen und Ziehen künstlichen englischen Text erzeugt, genau wie unser Modell heute. Mit mehr Kontext wurde sein Text immer englischer. Das zeigen wir später live.

[click] **2017, Transformer.** Ein neuer Bauplan für Sprachmodelle. Das ist Thema von Vortrag 3.

[click] **2022, ChatGPT.** Auf einmal kennt es jeder.

**Überleitung:** "Bevor wir zählen wie Markow: Was zählen wir überhaupt?"
-->

---
clicks: 4
---

<div class="kicker">Unser Lernmaterial</div>

# Woraus unser Modell lernt

<MaerchenText />

<!--
**Zeit:** ca. 2 Min.

**Kernaussage:** Alles, was unsere Modelle heute können, lernen sie aus einem einzigen Text: Märchen der Brüder Grimm.

**Schlagworte:** Grimms Märchen · Lernmaterial · fast eine halbe Million Zeichen · nur dieser Text

- Links läuft der Anfang von "Hänsel und Gretel" durch, so wie das Modell ihn bekommt. Kurz mitlesen lassen.

[click] **Woher:** fast 60 Märchen der Brüder Grimm aus einer Ausgabe von 1921. Der Text ist gemeinfrei, also frei von Urheberrechten (Projekt Gutenberg).
- Frage ans Publikum: "Welche Märchen kennt ihr?" Die meisten sind dabei.

[click] **Wie viel:** 476.207 Zeichen, gut 82.000 Wörter. Ausgedruckt etwa 240 Buchseiten, also ein dickes Buch.
- Zum Vergleich: Große Sprachmodelle lesen beim Training Milliarden von Buchseiten. Unser Text ist winzig, reicht aber, um das Prinzip zu sehen.

[click] **Wie er aussieht:**
- Alles kleingeschrieben, auch Namen. So braucht das Modell nur 40 verschiedene Zeichen statt fast 70.
- Alte Rechtschreibung wie "daß" und "hieß". Das Modell übernimmt sie, denn es kennt nur diesen Text.
- Keine Überschriften: Die Märchen hängen einfach aneinander.

[click] **Merksatz:** Das Modell weiß nichts über die Welt, keine Grammatik, kein Wörterbuch. Nur diesen Text.

**Überleitung:** "Fangen wir dort an, wo Markow angefangen hat: beim Zählen."
-->

---
clicks: 3
---

<div class="kicker">Markows Experiment, mit unseren Märchen</div>

# Was folgt auf einen Vokal?

<MarkowZaehler />

<!--
**Zeit:** ca. 3 Min.

**Kernaussage:** Schon simples Zählen zeigt Muster in der Sprache.

**Schlagworte:** Vokal · Konsonant · zählen · Muster · Anteil

**Frage ans Publikum (vor dem ersten Klick):** "Was glaubt ihr: Kommt nach einem Vokal eher ein Vokal oder ein Konsonant?"

[click] Wir zählen wie Markow, Buchstabe für Buchstabe. Leerzeichen und Satzzeichen lassen wir weg.
- Rechts die Tabelle: Zeile = was gerade kam, Spalte = was danach kam.
- Bei jedem Buchstaben leuchtet das Feld auf, das gezählt wird. "e" nach "s" heißt: Konsonant, dann Vokal.

[click] Jetzt im Zeitraffer der ganze Märchentext: über 370.000 Buchstaben. Markow hat 20.000 von Hand gezählt.

[click] Aus den Zählern werden Anteile:
- **Nach einem Vokal kommt in 83 % der Fälle ein Konsonant.** Zwei Vokale hintereinander sind selten.
- Nach einem Konsonanten ist es ungefähr halbe-halbe.
- Markow fand 1913 im Russischen dasselbe Muster.

**Merksatz:** Was als Nächstes kommt, hängt davon ab, was gerade kam. Genau das nutzt ein Sprachmodell.
-->

---
class: abschnitt
---

<div class="kicker">Schritt 1 von 5</div>

# Text wird zu Zahlen

<Fahrplan :aktuell="1" />

<!--
**Zeit:** ca. 30 Sek.

Kurz einordnen: "Erster Schritt. Der Computer muss mit Text rechnen können."
-->

---
layout: full
---

<SlidevVideo autoplay autoreset="slide" class="video-folie">
  <source src="/videos/Vokabular.mp4" type="video/mp4" />
</SlidevVideo>

<!--
**Zeit:** ca. 3 Min. (Video 30 Sek., startet von selbst)

**Kernaussage:** Jedes Zeichen bekommt eine feste Nummer. So wird Text zu einer Liste von Zahlen.

**Schlagworte:** Vokabular · ID · encode · decode

- Erst zuschauen lassen, dann erklären. Mit Pfeil links und rechts kann man das Video neu starten.
- **1. Jedes Zeichen nur einmal:** "hallo welt" hat 10 Zeichen, aber nur 8 verschiedene. Das zweite und dritte l fallen weg.
- **2. Sortieren:** damit die Reihenfolge immer gleich ist, egal in welcher Reihenfolge die Zeichen im Text vorkommen. Das Leerzeichen kommt nach vorn, weil es im Zeichensatz die kleinste Nummer hat.
- **3. Durchnummerieren:** Die Nummer heißt **ID**. Die Liste aller Zeichen mit ihrer ID heißt **Vokabular**.
- **4. Übersetzen:** Aus "hallo" wird [3, 1, 4, 4, 5]. Das heißt **encode**. Der Rückweg von Zahlen zu Text heißt **decode**.
- Für C#-Leute: Das ist ein Dictionary<char, int> und eines in die andere Richtung.
-->

---
clicks: 3
---

<div class="kicker">Schritt 1: Text wird zu Zahlen</div>

# Das Alphabet der Märchen

<Alphabet />

<!--
**Zeit:** ca. 2 Min.

**Kernaussage:** Unser Märchentext braucht nur 40 verschiedene Zeichen. Schon die Häufigkeit allein ist ein (schlechtes) Modell.

**Schlagworte:** 40 Zeichen · Häufigkeit · Modell ohne Kontext

- Erinnerung: Weil alles kleingeschrieben ist, reichen 40 Zeichen.
- Fun Fact: Im ganzen Text kommt **kein einziges y** vor.

[click] Jedes Zeichen bekommt seine ID, von 0 (Zeilenumbruch) bis 39 (ü).

[click] Wie oft kommt jedes Zeichen vor? Je höher die blaue Füllung, desto häufiger.
- Das Leerzeichen ist das häufigste "Zeichen" (fast jedes sechste), dann e und n.

[click] Ein erstes Modell: Zeichen nur nach Häufigkeit ziehen, ohne auf den Kontext zu schauen.
- Ergebnis: Buchstabensalat, aber mit den richtigen Zutaten. Viele e, viele Leerzeichen.
- "Das Modell weiß, **welche** Zeichen häufig sind, aber nicht, **wann**."

**Überleitung:** "Wir brauchen also: Was kommt **nach** einem bestimmten Zeichen?"
-->

---
class: abschnitt
---

<div class="kicker">Schritt 2 von 5</div>

# Zählen

<Fahrplan :aktuell="2" />

<!--
**Zeit:** ca. 30 Sek.

"Jetzt zählen wir wie Markow, aber mit allen Zeichen statt nur Vokal und Konsonant."
-->

---
layout: full
---

<SlidevVideo autoplay autoreset="slide" class="video-folie">
  <source src="/videos/BigrammeZaehlen.mp4" type="video/mp4" />
</SlidevVideo>

<!--
**Zeit:** ca. 3 Min. (Video 27 Sek., startet von selbst)

**Kernaussage:** Wir zählen, welches Zeichen auf welches folgt. Aus den Zählern werden Wahrscheinlichkeiten.

**Schlagworte:** Paar · Bigramm · Zähler · Dictionary

- Ein Paar aus zwei aufeinanderfolgenden Zeichen heißt **Bigramm** ("bi" = zwei).
- Das orange Fenster rutscht über den Text, immer zwei Zeichen.
- Rechts der **Zähler**: Für jedes Zeichen merkt er sich, was danach kam und wie oft.
- Links der Python-Code dazu, die blaue Markierung zeigt die Zeile, die gerade arbeitet. **Nicht den Code erklären**, nur zeigen: "So sieht das in Python aus, das schreibt ihr im Notebook selbst."
- Am Ende: Nach "n" kam zweimal "n", zweimal "a", einmal "d". Das sind 5 Fälle. 2 von 5 sind 40 %.

**Frage ans Publikum:** "Was kommt nach 'a'? Und was nach dem Leerzeichen?"
-->

---
clicks: 4
---

<div class="kicker">Schritt 2: Zählen</div>

# Alle Paare der Märchen auf einmal

<BigrammKarte :zeilen="['q', ' ', 'e']" />

<!--
**Zeit:** ca. 3 Min.

**Kernaussage:** Die ganze Zählung passt in eine Tabelle mit 40 mal 40 Feldern. Jede Zeile ist eine eigene Verteilung.

**Schlagworte:** Tabelle · Zeile = jetzt · Spalte = danach · dunkel = häufig

[click] Die Karte baut sich auf. Erklären: Zeile = das Zeichen jetzt, Spalte = das Zeichen danach. Je dunkler, desto häufiger.
- Viele Felder sind fast weiß: Diese Paare kommen im Deutschen kaum vor.

[click] **Zeile "q":** Nach q kam im ganzen Text **immer** u. 26 von 26 Mal. Das Modell ist sich hier ganz sicher.

[click] **Zeile Leerzeichen:** Das ist der Anfang eines neuen Worts. Hier ist das Modell unsicher: d (der, die, das), s, e, w, ...
- "Am Wortanfang ist die Auswahl am größten. Darum ist das schwer vorherzusagen."

[click] **Zeile "e":** nach e oft r oder n (der, den, einen). Das kennt jeder vom Deutschen.

**Merksatz:** Das Modell hat nichts "verstanden". Es hat nur gezählt. Trotzdem steckt viel Wissen über Deutsch in dieser Tabelle.
-->

---
clicks: 3
---

<div class="kicker">Schritt 2: Zählen</div>

# Aus Zählern werden Wahrscheinlichkeiten

<Normieren zeichen="h" />

<!--
**Zeit:** ca. 2 Min.

**Kernaussage:** Wahrscheinlichkeit = wie oft geteilt durch wie oft insgesamt. Mehr ist es nicht.

**Schlagworte:** Anteil · teilen durch die Summe · zusammen 100 %

[click] Was kam im Märchentext nach "h"? Zum Beispiel 4.185 Mal ein Leerzeichen (Wortende: "noch", "ich").

[click] Zusammen kam nach h über 20.000 Mal irgendein Zeichen.

[click] Jeden Zähler durch die Summe teilen. Ergebnis: der Anteil, also die Wahrscheinlichkeit.
- Beispiel aus dem Alltag: 3 von 4 Leuten trinken Kaffee, das sind 75 %.
- Alle Anteile zusammen ergeben immer 100 %.

**Überleitung:** "Jetzt haben wir die Prozentzahlen. Welches Zeichen nehmen wir denn nun?"
-->

---
class: abschnitt
---

<div class="kicker">Schritt 3 von 5</div>

# Ziehen

<Fahrplan :aktuell="3" />

<!--
**Zeit:** ca. 30 Sek.

"Wir haben Wahrscheinlichkeiten. Wie wird daraus ein Zeichen?"
-->

---
clicks: 3
---

<div class="kicker">Schritt 3: Ziehen</div>

# Warum nicht immer das Wahrscheinlichste?

<GierigOderZiehen start="es war einmal " :n="4" />

<!--
**Zeit:** ca. 2 Min.

**Kernaussage:** Wer immer das Wahrscheinlichste nimmt, dreht sich im Kreis. Zufall macht den Text lebendig.

**Schlagworte:** gierig · Schleife · Ziehen · Abwechslung

**Frage ans Publikum (vor dem ersten Klick):** "Wäre es nicht am besten, immer das Zeichen mit der höchsten Wahrscheinlichkeit zu nehmen?" Die meisten sagen ja.

[click] Links: immer das Wahrscheinlichste, mit 4 Zeichen Kontext. Nach kurzer Zeit wiederholt sich der Text endlos. Die Wiederholung ist orange markiert.
- Warum? Der Kontext kommt irgendwann wieder an dieselbe Stelle, und dann passiert jedes Mal genau dasselbe.

[click] Rechts: Ziehen nach Wahrscheinlichkeit. Der Text ist abwechslungsreich. Jedes Mal, wenn man die Folie neu zeigt, ist er anders.

[click] Fazit vorlesen.
- Bezug zu ChatGPT: Deshalb gibt ChatGPT auf dieselbe Frage nicht immer dieselbe Antwort.
-->

---
clicks: 3
---

<div class="kicker">Schritt 3: Ziehen</div>

# Ziehen wie mit einem Glücksrad

<Gluecksrad kontext=" ein" />

<!--
**Zeit:** ca. 3 Min.

**Kernaussage:** Jedes Zeichen bekommt ein Stück vom Rad, so groß wie seine Wahrscheinlichkeit. Zufall, aber fair.

**Schlagworte:** Glücksrad · Stückgröße = Wahrscheinlichkeit · Zufall · auf Dauer stimmt es

- Das Rad zeigt die Verteilung nach "␣ein", wie auf Folie 3: e fast die Hälfte, Leerzeichen ein gutes Drittel.

[click] Einmal drehen. Der Zeiger oben zeigt das gezogene Zeichen.
- "Auch ein seltenes Zeichen kann mal drankommen. Nur eben selten."

[click] Zehnmal drehen. Die Strichliste rechts zählt mit. Bei 10 Mal kann es noch ziemlich daneben liegen.

[click] Tausendmal drehen. Jetzt passen die Balken sehr genau zu den schwarzen Strichen (der Wahrscheinlichkeit laut Modell).
- **Merksatz:** Einzeln ist es Zufall, auf Dauer stimmen die Anteile.
- Im Notebook macht das die Python-Funktion random.choices.
-->

---
class: abschnitt
---

<div class="kicker">Schritt 4 von 5</div>

# Mehr Kontext

<Fahrplan :aktuell="4" />

<!--
**Zeit:** ca. 30 Sek.

"Bisher haben wir nur ein Zeichen zurückgeschaut. Was passiert, wenn wir weiter zurückschauen?"
-->

---
clicks: 6
---

<div class="kicker">Schritt 4: Mehr Kontext · Shannons Experiment von 1948</div>

# Je weiter zurück, desto besser der Text

<NGrammTreppe :bis="5" />

<!--
**Zeit:** ca. 3 Min.

**Kernaussage:** Mit mehr Kontext wird der Text immer deutscher. Genau das hat Shannon 1948 fürs Englische gezeigt.

**Schlagworte:** n = Anzahl Zeichen zurück · n-Gramm · Shannon

- **n** ist die Zahl der Zeichen, auf die das Modell zurückschaut. Das Modell heißt dann **n-Gramm-Modell**.
- Jede Zeile wird live erzeugt. Alles beginnt mit "es war einmal ".

[click] **n = 0:** nur Häufigkeit. Buchstabensalat (wie vorhin beim Alphabet).

[click] **n = 1:** ein Zeichen zurück (unsere Bigramme). Silben werden aussprechbar.

[click] **n = 2:** erste kurze echte Wörter: der, die, und.

[click] **n = 3:** viele echte Wörter.

[click] **n = 4:** klingt schon nach Märchen, ergibt aber keinen Sinn.

[click] **n = 5:** fast nur echte Wörter, manchmal ganze Satzstücke aus den Märchen.

**Frage ans Publikum:** "Wenn mehr immer besser ist, warum nicht 50 Zeichen zurück?" Antworten sammeln, dann nächste Folie.
-->

---
clicks: 7
---

<div class="kicker">Schritt 4: Mehr Kontext</div>

# Der Haken: Die Möglichkeiten explodieren

<KontextExplosion />

<!--
**Zeit:** ca. 3 Min.

**Kernaussage:** Mit jedem Zeichen mehr gibt es 40-mal so viele mögliche Kontexte. Kein Text der Welt ist groß genug, um sie alle zu sehen.

**Schlagworte:** Kombinationen · 40 hoch n · unbekannter Kontext · Datenhunger

[click] **1 Zeichen:** 40 mögliche Kontexte, alle kommen vor.

[click] **2 Zeichen:** 40 mal 40 = 1.600. Nur die Hälfte kommt im Text vor (viele Paare gibt es im Deutschen nicht, z. B. "qx").

[click] **3 Zeichen:** 64.000 möglich, etwa 6.000 kommen vor.

[click] **4 Zeichen:** 2,5 Millionen möglich.

[click] **5 Zeichen:** über 100 Millionen.

[click] **6 Zeichen:** 4 Milliarden möglich, gesehen keine 100.000.
- Vergleich: Mit jeder Stelle mehr wird es 40-mal so viel, wie bei einem Zahlenschloss mit immer mehr Rädern.

[click] **Die rechte Spalte ist das Problem.** Im Testtext (den das Modell nie gesehen hat) ist bei 6 Zeichen jeder sechste Kontext völlig neu.
- Bei einem neuen Kontext weiß ein Zählmodell **gar nichts**. Es hat keine Ahnung, dass "katze" so ähnlich ist wie "kater".

**Überleitung:** "Hilft es, einfach mehr Text zu nehmen?"
-->

---
clicks: 5
---

<div class="kicker">Schritt 4: Mehr Kontext</div>

# Großer Kontext braucht viel Text

<Datenhunger />

<!--
**Zeit:** ca. 3 Min.

**Kernaussage:** Je länger der Kontext, desto mehr Text braucht ein Zählmodell. Mehr Text hilft, aber immer weniger.

**Schlagworte:** Datenhunger · mehr Text · unbekannte Kontexte · nur einmal gesehen

- Wir bleiben bei 6 Zeichen Kontext und fragen: Was passiert, wenn wir mehr Text zum Zählen haben?
- Gemessen auf echtem Text: Wir zählen nur einen Teil des Trainingstexts und prüfen jedes Mal denselben Testtext.

[click] Mit 43.000 Zeichen (ein Zehntel) ist fast jeder zweite Kontext im Test unbekannt: 45 %.

[click] Mehr Text: 107.000 Zeichen, 32 %. 214.000 Zeichen, 23 %. Der ganze Trainingstext mit 429.000 Zeichen: 16 %.
- Blau wird immer länger, Orange immer kürzer. Mehr Text hilft also.

[click] Aber: Die letzte Verdopplung bringt nur noch 23 % auf 16 %. Jede weitere Verdopplung bringt noch weniger.
- Um fast alle 6er-Kontexte zu kennen, bräuchten wir ein Vielfaches des Textes. Bei 10 Zeichen Kontext wäre kein Text der Welt groß genug.

[click] Selbst die Kontexte, die das Modell gesehen hat, sind wackelig: **Mehr als die Hälfte kam nur ein einziges Mal vor.**
- Dort kennt das Modell genau ein Beispiel. Es sagt dann mit 100 % das Zeichen voraus, das damals kam. Das ist Auswendiglernen, kein Wissen.

[click] **Merksatz:** Wer nur zählt, braucht für langen Kontext riesige Textmengen.
- Ausblick (nicht vertiefen): Neuronale Netze lernen Ähnlichkeiten. Sie müssen nicht jeden Kontext einzeln gesehen haben. Das ist Thema von Vortrag 2.
- Auch große Sprachmodelle brauchen aber riesige Textmengen. Mit 40 hoch n Möglichkeiten käme trotzdem niemand hinterher.

**Überleitung:** "Wie misst man eigentlich, ob ein Modell gut oder schlecht ist?"
-->

---
class: abschnitt
---

<div class="kicker">Schritt 5 von 5</div>

# Bewerten

<Fahrplan :aktuell="5" />

<!--
**Zeit:** ca. 30 Sek.

"Bisher haben wir nach Gefühl gesagt: Der Text klingt besser. Jetzt messen wir das mit einer Zahl."
-->

---
clicks: 6
---

<div class="kicker">Schritt 5: Bewerten</div>

# Wie überrascht ist das Modell?

<VerlustKurve />

<!--
**Zeit:** ca. 3 Min. Langsam.

**Kernaussage:** Wir schauen, welche Wahrscheinlichkeit das Modell dem **richtigen** Zeichen gegeben hat. Wenig Wahrscheinlichkeit = große Überraschung = großer Verlust.

**Schlagworte:** richtiges Zeichen · Überraschung · Verlust · kleiner ist besser

- Idee: Wir kennen das richtige nächste Zeichen (es steht im Text). Wir fragen das Modell: Wie wahrscheinlich fandest du es?

[click] Die Kurve zeigt den **Verlust** für jede Wahrscheinlichkeit. Links hoch, rechts null.
- Die Formel dahinter heißt "minus Logarithmus". Muss man nicht ausrechnen können, nur die Form verstehen.

[click] **90 %:** Das Modell war sich fast sicher und lag richtig. Verlust fast 0.

[click] **50 %:** halb sicher, Verlust 0,69.

[click] **10 %:** hat es kaum erwartet. Verlust steigt deutlich.

[click] **1 %:** sehr überrascht. Verlust 4,6.

[click] **0 %:** Das Modell hielt das richtige Zeichen für **unmöglich**. Der Verlust ist **unendlich**. Die schlimmste mögliche Strafe.
- **Merksatz:** Verlust ist eine Zahl für "wie überrascht". Kleiner ist besser. 0 wäre perfekt.
-->

---
clicks: 2
---

<div class="kicker">Schritt 5: Bewerten</div>

# Der Verlust für einen ganzen Satz

<VerlustBeispiel satz="der könig sprach" :n="2" />

<!--
**Zeit:** ca. 2 Min. Kann bei Zeitnot entfallen.

**Kernaussage:** Für einen ganzen Text nimmt man den Durchschnitt aller Verluste. Eine Zahl für das ganze Modell.

**Schlagworte:** jedes Zeichen einzeln · Durchschnitt · Wortanfänge sind schwer

- Modell hier: 2 Zeichen zurück. Die ersten zwei Zeichen sind der Start, für sie gibt es keine Vorhersage.

[click] Für jedes Zeichen: Wie wahrscheinlich fand das Modell es? Darüber der Verlust.
- **Hohe orange Balken an Wortanfängen:** "k" nach "r␣" (3,0), "s" nach "g␣". Wer weiß schon, welches Wort als Nächstes kommt?
- **Niedrige Balken mitten im Wort:** "n" nach "kö" (94 %), "h" nach "ac" (92 %). Wenn ein Wort angefangen hat, ist der Rest leicht.

[click] Der Durchschnitt aller Balken: **eine Zahl für den ganzen Satz.** Dieselbe Rechnung macht man für einen ganzen Text.
-->

---
clicks: 3
---

<div class="kicker">Schritt 5: Bewerten</div>

# Training und Test

<TrainingTest />

<!--
**Zeit:** ca. 4 Min. Wichtigste Erkenntnis des zweiten Teils.

**Kernaussage:** Ein Modell muss mit **neuem** Text klarkommen. Mehr Kontext hilft beim Auswendiglernen, aber nicht bei neuem Text.

**Schlagworte:** Training · Test · auswendig lernen · verallgemeinern · unendlich

[click] Wir teilen den Text: 90 % zum Zählen (**Training**), 10 % hält das Modell nie in der Hand (**Test**).
- Wie in der Berufsschule: Wer nur die Übungsaufgaben auswendig kann, besteht die Prüfung mit neuen Aufgaben nicht.

[click] Verlust auf dem Training: Je mehr Kontext, desto kleiner. Das Modell wird scheinbar immer besser.

[click] Verlust auf dem Test: Schon ab n = 1 ist er **unendlich**!
- Warum? Irgendwo im Test kommt ein Paar, das im Training nie vorkam. Das Modell sagt: unmöglich, also unendlich.
- Mit mehr Kontext werden diese "unmöglichen" Stellen immer mehr: bei 6 Zeichen über ein Viertel.
- **Merksatz:** Ein Zählmodell lernt auswendig. Es kann nicht **verallgemeinern**.
-->

---
clicks: 3
---

<div class="kicker">Die Grenze des Zählens</div>

# Zählen kennt keine Ähnlichkeit

<div class="grid grid-cols-2 gap-8 mt-10">
  <div v-click="1" class="karte p-6">
    <div class="beschriftung">Was ein Mensch weiß</div>
    <p class="merksatz mt-3">„hund“ und „katze“ sind beides Tiere. Was nach dem einen passt, passt oft auch nach dem anderen.</p>
  </div>
  <div v-click="2" class="karte p-6">
    <div class="beschriftung">Was ein Zählmodell weiß</div>
    <p class="merksatz mt-3">„hund“ und „katze“ sind völlig verschiedene Zeichenfolgen. Was es nie gezählt hat, kennt es nicht.</p>
  </div>
</div>

<div v-click="3" class="mt-10 text-2xl text-center">
  Wir brauchen ein Modell, das <b class="akzent">Ähnlichkeit</b> lernen kann. Das ist ein <b class="akzent-blau">neuronales Netz</b>.
</div>

<!--
**Zeit:** ca. 2 Min.

**Kernaussage:** Zählmodelle kennen nur exakte Treffer. Für echte Sprachmodelle braucht man Modelle, die Ähnlichkeiten erkennen.

**Schlagworte:** Ähnlichkeit · verallgemeinern · neuronales Netz

[click] Ein Mensch verallgemeinert ganz selbstverständlich: Hat man "der hund schläft" gelesen, ist "die katze schläft" auch kein Problem.

[click] Das Zählmodell hat dafür keine Möglichkeit. Jede Zeichenfolge steht für sich allein.

[click] Die Lösung kommt im nächsten Vortrag: ein neuronales Netz. Es lernt zum Beispiel, dass Vokale sich ähnlich verhalten, ohne dass man es ihm sagt.
-->

---
---

<div class="kicker">Zusammenfassung</div>

# Was ihr heute gelernt habt

<div class="raster-karten grid-cols-5">
  <div v-click class="karte"><div class="nr">1</div><h3>Text wird zu Zahlen</h3><p>Jedes Zeichen bekommt eine ID. Das Vokabular übersetzt hin und zurück.</p></div>
  <div v-click class="karte"><div class="nr">2</div><h3>Zählen</h3><p>Wie oft folgt welches Zeichen auf welches? Geteilt durch die Summe ergibt das Wahrscheinlichkeiten.</p></div>
  <div v-click class="karte"><div class="nr">3</div><h3>Ziehen</h3><p>Zufällig nach Wahrscheinlichkeit, wie ein Glücksrad. Sonst dreht sich der Text im Kreis.</p></div>
  <div v-click class="karte"><div class="nr">4</div><h3>Mehr Kontext</h3><p>Besserer Text, aber die Möglichkeiten explodieren. Neue Kontexte kennt das Modell nicht.</p></div>
  <div v-click class="karte"><div class="nr">5</div><h3>Bewerten</h3><p>Verlust misst die Überraschung. Ehrlich ist nur der Test mit neuem Text.</p></div>
</div>

<div v-click class="mt-12 merksatz text-center">
  Ein Sprachmodell sagt das nächste Stück voraus, zieht, hängt an. Immer wieder.
</div>

<!--
**Zeit:** ca. 2 Min.

**Kernaussage:** Fünf Schritte, eine Schleife.

Jeden Schritt mit einem Satz wiederholen, am besten von den Teilnehmern sagen lassen: "Was war nochmal Schritt 2?"

[click] Text wird zu Zahlen.

[click] Zählen.

[click] Ziehen.

[click] Mehr Kontext.

[click] Bewerten.

[click] Der Merksatz vom Anfang. Jetzt verstehen ihn alle.
-->

---
---

<div class="kicker">Wie es weitergeht</div>

# Jetzt seid ihr dran

<div class="grid grid-cols-2 gap-8 mt-10">
  <div v-click class="karte p-7">
    <div class="beschriftung">Notebook 1</div>
    <h3 class="text-2xl font-semibold mt-2 mb-4">Ihr baut das Zählmodell selbst</h3>
    <ul class="text-lg leading-relaxed">
      <li>das Vokabular mit encode und decode</li>
      <li>Bigramme zählen</li>
      <li>Wahrscheinlichkeiten und Ziehen</li>
      <li>Text erzeugen mit n Zeichen Kontext</li>
      <li>den Verlust auf Training und Test</li>
    </ul>
  </div>
  <div v-click class="karte p-7">
    <div class="beschriftung">Vortrag 2</div>
    <h3 class="text-2xl font-semibold mt-2 mb-4">Neuronale Netze</h3>
    <ul class="text-lg leading-relaxed">
      <li>Wie eine Maschine aus Fehlern lernt</li>
      <li>Eine Gerade durch Punkte legen</li>
      <li>Vom Zählen zum Lernen</li>
      <li>Ein Netz, das Ähnlichkeit erkennt</li>
    </ul>
  </div>
</div>

<!--
**Zeit:** ca. 2 Min., danach Fragen

- Notebook 1 baut genau die Schritte von heute nach, in Python, mit Tipps zu jeder Aufgabe.
- Im Notebook gibt es zu jeder Aufgabe drei Tipps: Hinweis, fast die Lösung, die Lösung. Ermutigen, die Tipps zu nutzen.
- Ausblick Vortrag 2: Statt zu zählen, lernt ein Modell aus seinen Fehlern. Wir beginnen ganz einfach: mit einer Geraden durch ein paar Punkte.

**Fragen sammeln.** Typische Fragen:
- "Ist ChatGPT auch nur ein Zählmodell?" Nein, es ist ein neuronales Netz (Vortrag 2 und 3). Aber es macht dieselbe Schleife: vorhersagen, ziehen, anhängen.
- "Woher weiß ChatGPT dann Dinge?" Aus riesigen Textmengen beim Training. Genauer in Vortrag 3.
-->
