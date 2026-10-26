"""Inhalt von Notebook 7: Das große Training."""

from .bausteine import aufgabe, code, md, tipps

ZELLEN = [

# =============================================================
# WILLKOMMEN
# =============================================================

md(r"""
# Notebook 7: Das große Training

## Dein Transformer schreibt Märchen

Du hast alle Teile eines Transformers selbst gebaut. In Notebook 6 hat er aber gezeigt, dass er mit 11.000 Zeichen
zu wenig zu lesen hat: Er hat angefangen, den Text auswendig zu lernen.

In diesem letzten Notebook bekommt dein Transformer einen über 40-mal so großen Text: die Märchen der Brüder Grimm.
Du trainierst ihn ein paar Minuten lang, vergleichst ihn mit allen Modellen aus diesem Kurs und lässt ihn eigene Märchen schreiben.

### Der Plan für dieses Notebook

| Teil | Was passiert |
|---|---|
| 1 | Der neue Text |
| 2 | Die Modelle aus Notebook 1 bis 3 als Vergleich |
| 3 | Wie groß ist dein Transformer? |
| 4 | Das große Training |
| 5 | Die Temperatur: vorsichtig oder mutig schreiben |
| 6 | Worauf schauen die Köpfe? |
| 7 | Rückblick: Dein Weg zum Transformer |
| 8 | Wie geht es weiter? |
""")
,
md(r"""
## Vorbereitung

Diesmal brauchst du Code aus allen bisherigen Notebooks.
""")
,
code(r"""
import math
from pathlib import Path

import torch
import torch.nn.functional as F

from kurswerkzeuge import grafik2, grafik4, grafik6, nb7

nb7.pruefe_vorarbeit()

from meincode.notebook1 import Vocabulary, NGramModell, durchschnittlicher_verlust, ziehe_zeichen
from meincode.notebook2 import BigrammNetz, kreuzentropie
from meincode.notebook3 import ZeichenNetz, baue_beispiele, trainiere
from meincode.notebook4 import maskieren
from meincode.notebook5 import punkte, ziehe_bloecke
from meincode.notebook6 import Transformer

print("Alles bereit!")
""")
,

# =============================================================
# TEIL 1: DER NEUE TEXT
# =============================================================

md(r"""
---
# Teil 1: Der neue Text

Die Datei `daten/maerchen.txt` enthält fast 60 Märchen der Brüder Grimm, zum Beispiel "Hänsel und Gretel",
"Rotkäppchen" und "Die Bremer Stadtmusikanten". Sie stammen aus einer Ausgabe von 1921.
Der Text ist gemeinfrei (frei von Urheberrechten) und kommt von [Projekt Gutenberg](https://www.gutenberg.org/ebooks/77905).

Wie bei unserem bisherigen Text sind alle Buchstaben klein. Die Rechtschreibung ist alt, zum Beispiel "daß" statt "dass".
Dein Modell wird das übernehmen, denn es lernt nur aus dem, was es liest.
""")
,
code(r"""
with open("daten/maerchen.txt", encoding="utf-8") as datei:
    maerchentext = datei.read()

grenze = int(len(maerchentext) * 0.9)
training = maerchentext[:grenze]
test = maerchentext[grenze:]

vocabulary = Vocabulary(maerchentext)
V = len(vocabulary)
ids_training = torch.tensor(vocabulary.encode(training))
ids_test = torch.tensor(vocabulary.encode(test))

print(f"Anzahl Zeichen: {len(maerchentext)}")
print(f"Größe des Vokabulars: {V}")
print("Zeichen:", "".join(vocabulary.zeichen))
print()
print(maerchentext[:600])
""")
,
md(r"""
Das Vokabular ist etwas größer als bisher, weil die Märchen Anführungszeichen, Fragezeichen und Ausrufezeichen enthalten.
Deine Klasse `Vocabulary` aus Notebook 1 kommt damit ohne Änderung zurecht.
""")
,

# =============================================================
# TEIL 2: DIE VERGLEICHSMODELLE
# =============================================================

md(r"""
---
# Teil 2: Die Modelle aus Notebook 1 bis 3 als Vergleich

Bevor der Transformer trainiert, schauen wir, wie gut die bisherigen Modelle auf den Märchen sind.

**Blind raten:** Jedes Zeichen gleich wahrscheinlich. Der Verlust ist $\log(V)$.

**Das Zählmodell aus Notebook 1:**
""")
,
code(r"""
blind = math.log(V)
print("Blind raten:", round(blind, 3))

zaehl_modell = NGramModell(training, 1)
print("Zählmodell (Bigramm) auf dem Test:", durchschnittlicher_verlust(zaehl_modell, test))
""")
,
md(r"""
Unendlich, wie in Notebook 1. Auch in 430.000 Zeichen kommt nicht jedes Zeichenpaar vor, das im Testtext steht.

**Das Bigramm-Netz aus Notebook 2.** Mit allen 430.000 Beispielen auf einmal wäre jeder Lernschritt langsam.
Wir nehmen deshalb in jedem Schritt 5.000 zufällige Beispiele, also einen großen Minibatch wie in Notebook 3.
""")
,
code(r"""
torch.manual_seed(1)
bigramm_netz = BigrammNetz(V)
for schritt in range(300):
    auswahl = torch.randint(0, len(ids_training) - 1, (5000,))
    bigramm_netz.trainingsschritt(ids_training[auswahl], ids_training[auswahl + 1], lernrate=50)

with torch.no_grad():
    bigramm_test = kreuzentropie(bigramm_netz.vorhersage(ids_test[:-1]), ids_test[1:]).item()
print("Bigramm-Netz auf dem Test:", round(bigramm_test, 3))
""")
,
md(r"""
**Das ZeichenNetz aus Notebook 3** mit drei Zeichen Kontext:
""")
,
code(r"""
X3_training, Y3_training = baue_beispiele(ids_training.tolist(), 3)
X3_test, Y3_test = baue_beispiele(ids_test.tolist(), 3)

torch.manual_seed(1)
zeichen_netz = ZeichenNetz(V, kontext=3, koordinaten=10, neuronen=200)
trainiere(zeichen_netz, X3_training, Y3_training, schritte=20000, lernrate=0.1)

with torch.no_grad():
    zeichen_netz_test = F.cross_entropy(zeichen_netz(X3_test), Y3_test).item()
print("ZeichenNetz auf dem Test:", round(zeichen_netz_test, 3))
""")
,

# =============================================================
# TEIL 3: WIE GROSS IST DEIN TRANSFORMER?
# =============================================================

md(r"""
---
# Teil 3: Wie groß ist dein Transformer?

Wenn von Sprachmodellen die Rede ist, hört man oft Zahlen wie "7 Milliarden Parameter". Parameter sind die Gewichte,
also alle Zahlen, die das Netz beim Training lernt. Du hast sie bisher mit einer langen Zeile gezählt. Jetzt wird eine Funktion daraus.

---
## Aufgabe 7.1: Gewichte zählen

Schreibe die Funktion `zaehle_gewichte(netz)`. Sie zählt alle Zahlen in allen Gewichts-Tensoren von `netz.parameters()`.
`p.numel()` liefert die Anzahl der Zahlen in einem Tensor `p`.
""")
,
aufgabe(
vorlage=r"""
def zaehle_gewichte(netz):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 7.1: Hier fehlt noch dein Code")
""",
loesung=r"""
def zaehle_gewichte(netz):
    return sum(p.numel() for p in netz.parameters())
""")
,
code(r"""
nb7.pruefe_aufgabe_1(zaehle_gewichte)
""")
,
tipps(
    hinweis=r"""
    `netz.parameters()` liefert alle Gewichts-Tensoren des Netzes, einen nach dem anderen. Du kannst mit einer Schleife darüberlaufen.

    Für jeden Tensor `p` sagt `p.numel()`, wie viele Zahlen darin stehen. Du musst diese Anzahlen nur noch zusammenzählen.
    """,
    fast=r"""
    ```python
    anzahl = 0
    for p in netz.parameters():
        anzahl += ...
    return anzahl
    ```
    """,
    loesung=r"""
    ```python
    def zaehle_gewichte(netz):
        return sum(p.numel() for p in netz.parameters())
    ```
    Am Beispiel `nn.Linear(3, 4)`:

    - `netz.parameters()` liefert zwei Tensoren: die Gewichte mit Form `(4, 3)` und die Verschiebungen mit Form `(4,)`.
    - `p.numel()` ergibt 12 und 4. `sum(...)` zählt sie zusammen: 16.

    Die Schreibweise `sum(... for p in ...)` ist die Kurzform der Schleife aus Tipp 2. Die lange Form ist genauso richtig:
    ```python
    anzahl = 0
    for p in netz.parameters():
        anzahl += p.numel()
    return anzahl
    ```
    """,
)
,
md(r"""
Unser Transformer für die Märchen bekommt 64 Koordinaten pro Zeichen, 4 Köpfe, 3 Blöcke und sieht 64 Zeichen auf einmal.
Dropout ist 0.1, denn mit dem großen Text ist die Gefahr des Auswendiglernens kleiner.
""")
,
code(r"""
torch.manual_seed(1)
transformer = Transformer(V, kontext=64, C=64, koepfe=4, bloecke=3, dropout=0.1)

def mit_punkten(zahl):
    return f"{zahl:,}".replace(",", ".")


meine = zaehle_gewichte(transformer)
print(f"Dein Transformer: {mit_punkten(meine):>15} Gewichte")
print(f"GPT-2 (2019):     {mit_punkten(124_000_000):>15} Gewichte, etwa {mit_punkten(124_000_000 // meine)}-mal so viele")
print(f"GPT-3 (2020):     {mit_punkten(175_000_000_000):>15} Gewichte, etwa {mit_punkten(175_000_000_000 // meine)}-mal so viele")
""")
,
md(r"""
Dein Transformer ist winzig. Aber er ist nach **demselben Bauplan** gebaut wie GPT-2 und GPT-3.
Die großen Modelle haben mehr Blöcke, mehr Köpfe, mehr Koordinaten und lernen aus viel mehr Text.
""")
,

# =============================================================
# TEIL 4: DAS GROSSE TRAINING
# =============================================================

md(r"""
---
# Teil 4: Das große Training

Jetzt kommt das große Training: 4.000 Schritte mit je 32 Blöcken aus 64 Zeichen. Das sind über 8 Millionen Zeichen,
die der Transformer liest. Jedes Zeichen der Märchen sieht er dabei im Schnitt fast 20-mal.

Je nach Computer dauert das **3 bis 10 Minuten**. Während du wartest, kannst du über diese Fragen nachdenken:
- Warum liegen die blaue und die orange Linie diesmal viel näher beieinander als in Notebook 6?
- Was würde passieren, wenn wir noch viel länger trainieren?

Das fertige Netz wird in `meincode/maerchen_transformer.pt` gespeichert. Wenn du das Notebook später noch einmal öffnest,
setze `neu_trainieren = False`. Dann wird das gespeicherte Netz geladen, und du musst nicht noch einmal warten.
""")
,
code(r"""
neu_trainieren = True
datei = Path("meincode/maerchen_transformer.pt")


def verlust_bloecke(netz, X, Y):
    logits = netz(X)
    return F.cross_entropy(logits.view(-1, logits.shape[-1]), Y.view(-1))


def schaetze_verlust(netz, ids):
    netz.eval()
    with torch.no_grad():
        X, Y = ziehe_bloecke(ids, netz.kontext, 200)
        verlust = verlust_bloecke(netz, X, Y).item()
    netz.train()
    return verlust


if datei.exists() and not neu_trainieren:
    transformer.load_state_dict(torch.load(datei, weights_only=True))
    print("Gespeichertes Netz geladen.")
else:
    optimierer = torch.optim.AdamW(transformer.parameters(), lr=3e-3)
    kurve = grafik2.LiveKurve(titel="Dein Transformer liest Märchen", ziel=zeichen_netz_test, ziel_text="ZeichenNetz")
    for schritt in range(4001):
        X, Y = ziehe_bloecke(ids_training, transformer.kontext, 32)
        verlust = verlust_bloecke(transformer, X, Y)
        optimierer.zero_grad()
        verlust.backward()
        optimierer.step()
        if schritt % 250 == 0:
            kurve.punkt(schritt, schaetze_verlust(transformer, ids_training), schaetze_verlust(transformer, ids_test))
    torch.save(transformer.state_dict(), datei)
    print("Training fertig, Netz gespeichert in", datei)

transformer_test = schaetze_verlust(transformer, ids_test)
transformer.eval()
print("Transformer auf dem Test:", round(transformer_test, 3))
""")
,
md(r"""
Der Transformer ist deutlich besser als alle anderen Modelle. Und diesmal liegen Training und Test nah beieinander:
Mit genug Text lernt das Netz die **Sprache** und nicht den Text auswendig.

`transformer.eval()` schaltet Dropout aus. Ab jetzt wird nicht mehr trainiert, nur noch geschrieben.
""")
,

# =============================================================
# TEIL 5: TEMPERATUR
# =============================================================

md(r"""
---
# Teil 5: Die Temperatur: vorsichtig oder mutig schreiben

Bei ChatGPT und anderen Sprachmodellen gibt es eine Einstellung namens **Temperatur**. Jetzt baust du sie selbst.

Die Idee: Bevor die Softmax aus den Logits Wahrscheinlichkeiten macht, teilen wir alle Logits durch die Temperatur.

| Temperatur | Wirkung auf die Logits | Wirkung auf den Text |
|---|---|---|
| **kleiner als 1**, z. B. 0.5 | Abstände werden größer | Das wahrscheinlichste Zeichen gewinnt fast immer. Vorsichtig, aber oft eintönig und mit Wiederholungen. |
| **genau 1** | unverändert | so, wie das Netz es gelernt hat |
| **größer als 1**, z. B. 2 | Abstände werden kleiner | Auch unwahrscheinliche Zeichen kommen dran. Mutig, aber oft wirr. |

Erinnerst du dich an die Softmax-Regler in Notebook 2? Wenn die Logits weit auseinanderliegen, bekommt eines fast alles.
Genau das steuert die Temperatur.

---
## Aufgabe 7.2: Die Temperatur

Erweitere deine beiden Funktionen aus Notebook 5 um einen Parameter `temperatur` mit dem Standardwert `1.0`:

**`naechste_verteilung(netz, vocabulary, text, temperatur=1.0)`**: wie in Notebook 5, aber die Logits der letzten Position
werden vor der Softmax durch `temperatur` geteilt: `torch.softmax(logits[0, -1] / temperatur, dim=-1)`

**`generiere(netz, vocabulary, start, laenge, temperatur=1.0)`**: wie in Notebook 5, gibt die Temperatur an `naechste_verteilung` weiter.
""")
,
aufgabe(
vorlage=r"""
def naechste_verteilung(netz, vocabulary, text, temperatur=1.0):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 7.2: Hier fehlt noch dein Code")


def generiere(netz, vocabulary, start, laenge, temperatur=1.0):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 7.2: Hier fehlt noch dein Code")
""",
loesung=r"""
def naechste_verteilung(netz, vocabulary, text, temperatur=1.0):
    ids = vocabulary.encode(text[-netz.kontext:])
    with torch.no_grad():
        logits = netz(torch.tensor([ids]))
    P = torch.softmax(logits[0, -1] / temperatur, dim=-1)
    return {vocabulary.id_zu_zeichen[i]: p for i, p in enumerate(P.tolist())}


def generiere(netz, vocabulary, start, laenge, temperatur=1.0):
    text = start
    for _ in range(laenge):
        text += ziehe_zeichen(naechste_verteilung(netz, vocabulary, text, temperatur))
    return text
""")
,
code(r"""
nb7.pruefe_aufgabe_2(naechste_verteilung, generiere)
""")
,
tipps(
    hinweis=r"""
    Du kannst beide Funktionen aus Notebook 5 kopieren. Sie stehen in `meincode/notebook5.py`. Dann änderst du drei Stellen:

    1. Beide Funktionen bekommen einen zusätzlichen Parameter `temperatur=1.0`. Der Standardwert sorgt dafür, dass alte Aufrufe weiter funktionieren.
    2. In `naechste_verteilung` werden die Logits vor der Softmax **durch** die Temperatur geteilt.
    3. `generiere` gibt die Temperatur an `naechste_verteilung` weiter. Sonst kommt sie dort nie an.
    """,
    fast=r"""
    ```python
    def naechste_verteilung(netz, vocabulary, text, temperatur=1.0):
        ids = vocabulary.encode(text[-netz.kontext:])
        with torch.no_grad():
            logits = netz(torch.tensor([ids]))
        P = torch.softmax(logits[0, -1] / ..., dim=-1)
        return {vocabulary.id_zu_zeichen[i]: p for i, p in enumerate(P.tolist())}


    def generiere(netz, vocabulary, start, laenge, temperatur=1.0):
        text = start
        for _ in range(laenge):
            text += ziehe_zeichen(naechste_verteilung(netz, vocabulary, text, ...))
        return text
    ```
    """,
    loesung=r"""
    ```python
    def naechste_verteilung(netz, vocabulary, text, temperatur=1.0):
        ids = vocabulary.encode(text[-netz.kontext:])
        with torch.no_grad():
            logits = netz(torch.tensor([ids]))
        P = torch.softmax(logits[0, -1] / temperatur, dim=-1)
        return {vocabulary.id_zu_zeichen[i]: p for i, p in enumerate(P.tolist())}


    def generiere(netz, vocabulary, start, laenge, temperatur=1.0):
        text = start
        for _ in range(laenge):
            text += ziehe_zeichen(naechste_verteilung(netz, vocabulary, text, temperatur))
        return text
    ```
    Was das Teilen bewirkt, am Beispiel der Logits `[0, 2, 1]`:

    - **Temperatur 1:** Die Logits bleiben gleich. Alles ist wie in Notebook 5.
    - **Temperatur 0.5:** Geteilt durch 0.5 ergibt `[0, 4, 2]`. Die Abstände werden größer, das beste Zeichen gewinnt fast immer. Der Text wird vorsichtiger.
    - **Temperatur 2:** Geteilt durch 2 ergibt `[0, 1, 0.5]`. Die Abstände werden kleiner, auch seltene Zeichen kommen öfter dran. Der Text wird wilder.

    In `generiere` ist nur der letzte Parameter beim Aufruf neu. Ohne ihn würde `naechste_verteilung` immer mit 1.0 rechnen.
    """,
)
,
md(r"""
Probier die Temperatur aus. Der Text startet immer mit "es war einmal ". Wie verändert sich das Märchen, wenn du die Temperatur
nach unten oder nach oben schiebst? Mit dem Knopf erzeugst du bei gleicher Temperatur einen neuen Text.
""")
,
code(r"""
grafik6.temperatur_regler(naechste_verteilung, generiere, transformer, vocabulary)
""")
,
md(r"""
Und hier ein längeres Märchen. Du kannst den Anfang ändern, zum Beispiel in `"der könig sprach"` oder `"hänsel und gretel"`.
""")
,
code(r"""
print(generiere(transformer, vocabulary, "es war einmal ein armer müller, ", 1000, temperatur=0.8))
""")
,
md(r"""
Lies genau hin. Was kann dein Transformer schon, was noch nicht?
- Die meisten **Wörter** sind echte deutsche Wörter, oft sogar typische Märchenwörter wie "könig", "sprach" oder "daß".
- **Satzzeichen** sitzen meist richtig: Nach "sprach" kommt ein Doppelpunkt, wörtliche Rede steht in Anführungszeichen.
- **Sinn** ergeben die Sätze aber selten. Dafür ist das Modell zu klein, der Text zu kurz und das Gedächtnis von 64 Zeichen zu knapp.

Das ist ein riesiger Schritt vom Buchstabensalat des Bigramm-Modells aus Notebook 1. Und alles, was fehlt,
ist eine Frage von Größe, Datenmenge und Rechenzeit, nicht von einem anderen Bauplan.
""")
,

# =============================================================
# TEIL 6: DIE KÖPFE
# =============================================================

md(r"""
---
# Teil 6: Worauf schauen die Köpfe?

Wie in Notebook 6 schauen wir den Köpfen zu, diesmal im ersten und im letzten Block.
""")
,
code(r"""
satz = "da sprach der wolf: \"ich will dich fressen.\""
ids_satz = vocabulary.encode(satz)

grafik6.koepfe_bild(grafik6.koepfe_gewichte(transformer, ids_satz, punkte, maskieren, block_nummer=0), satz, "Block 1")
grafik6.koepfe_bild(grafik6.koepfe_gewichte(transformer, ids_satz, punkte, maskieren, block_nummer=2), satz, "Block 3")
""")
,
md(r"""
Die Köpfe im ersten Block schauen meist auf die Zeichen direkt davor. Sie erkennen Buchstabenfolgen.
In späteren Blöcken schauen manche Köpfe weiter zurück, zum Beispiel auf den Anfang eines Worts oder auf das Anführungszeichen.

Schau dir einzelne Köpfe genauer an. Findest du einen Kopf, der beim schließenden Anführungszeichen auf das öffnende zurückschaut?
""")
,
code(r"""
gewichte = grafik6.koepfe_gewichte(transformer, ids_satz, punkte, maskieren, block_nummer=2)
grafik4.aufmerksamkeit_erkunden(gewichte[0], satz, "Block 3, Kopf 1")
""")
,

# =============================================================
# TEIL 7: RÜCKBLICK
# =============================================================

md(r"""
---
# Teil 7: Rückblick: Dein Weg zum Transformer

Alle Modelle aus diesem Kurs, gemessen auf demselben Märchen-Testtext. Das Zählmodell aus Notebook 1 fehlt,
denn sein Verlust ist unendlich.
""")
,
code(r"""
grafik6.verlust_treppe([
    ("Blind raten", blind),
    ("Bigramm-Netz (Notebook 2)", bigramm_test),
    ("ZeichenNetz (Notebook 3)", zeichen_netz_test),
    ("Transformer (Notebook 6 und 7)", transformer_test),
])
""")
,
md(r"""
| Notebook | Was du gebaut hast | Was es konnte |
|---|---|---|
| 1 | Zählmodell, Verlust | Text vorhersagen durch Zählen. Aber hilflos bei Unbekanntem. |
| 2 | Tensoren, Softmax, Gradientenabstieg, Bigramm-Netz | Ein Netz, das selbst lernt und nichts für unmöglich hält |
| 3 | Einbettungen, verborgene Schicht, Minibatches | Ähnliche Zeichen werden ähnlich behandelt. Drei Zeichen Kontext. |
| 4 | Durchschnitt, Dreiecksmatrix, Maske | Auf alle früheren Zeichen zurückschauen, ohne zu spicken |
| 5 | Query, Key, Value, Positionen | Das Netz entscheidet selbst, worauf es schaut |
| 6 | Mehrere Köpfe, FeedForward, Abkürzungen, Transformer | Der Bauplan von GPT |
| 7 | Großes Training, Temperatur | Dein Transformer schreibt Märchen |

### Was deinem Modell zu ChatGPT noch fehlt

Der Bauplan ist derselbe. Die Unterschiede liegen woanders:

| | Dein Transformer | Große Sprachmodelle |
|---|---|---|
| **Größe** | etwa 160.000 Gewichte | Milliarden bis Billionen Gewichte |
| **Einheiten** | einzelne Zeichen | **Tokens**: häufige Wortstücke wie "Haus", "ung" oder "spiel" |
| **Text** | 430.000 Zeichen Märchen | Billionen Tokens aus Büchern, Webseiten und Code |
| **Kontext** | 64 Zeichen | Hunderttausende Tokens |
| **Training** | ein paar Minuten auf deinem Computer | Monate auf Tausenden Grafikkarten |
| **Feinschliff** | keiner | Nach dem Training lernen die Modelle zusätzlich, hilfreich zu antworten und Gespräche zu führen. Dabei bewerten Menschen viele Antworten. |

Dein Modell kann nur eines: Text fortsetzen, der so klingt wie das, was es gelesen hat.
Genau das ist auch der Kern der großen Modelle. Alles andere baut darauf auf.
""")
,

# =============================================================
# TEIL 8: WIE GEHT ES WEITER?
# =============================================================

md(r"""
---
# Teil 8: Wie geht es weiter?

Du hast jetzt alles, um selbst zu experimentieren. Ein paar Ideen:

1. **Ein eigener Text.** Lege eine eigene Textdatei in den Ordner `daten`, zum Beispiel Songtexte, Rezepte oder Code.
   Je mehr Text, desto besser. Unter 100.000 Zeichen lernt der Transformer meist nur auswendig.
   Wandle den Text am besten mit `.lower()` in Kleinbuchstaben um, dann wird das Vokabular kleiner.
2. **Größer bauen.** Was passiert mit mehr Blöcken (`bloecke=6`) oder mehr Koordinaten (`C=128`)? Das Training dauert dann länger.
3. **Länger trainieren.** Was passiert nach 10.000 Schritten? Wann fängt das Overfitting an?
4. **Mehr Kontext.** Probier `kontext=128`. Kann sich das Netz dann besser an den Anfang eines Satzes erinnern?

Und falls du noch tiefer einsteigen willst: Der Kurs folgt in großen Teilen der Videoreihe "Neural Networks: Zero to Hero"
von Andrej Karpathy (auf Englisch, auf YouTube). Dort baut er dasselbe Modell und geht danach noch weiter bis zu GPT-2.
""")
,
code(r"""
# Platz für deine Experimente
""")
,
md(r"""
---
# Abschluss: Deinen Code speichern
""")
,
code(r"""
nb7.speichern(
    zaehle_gewichte,
    naechste_verteilung,
    generiere,
)
""")
,
md(r"""
## Geschafft!

Du hast in sieben Notebooks ein Sprachmodell von Grund auf gebaut: vom Zählen von Buchstabenpaaren
bis zu einem Transformer mit mehreren Köpfen und Blöcken, der eigene Märchen schreibt.

Jeder Baustein darin stammt von dir. Wenn das nächste Mal jemand sagt, Sprachmodelle seien Magie,
weißt du es besser: Es sind Einbettungen, Aufmerksamkeit, ein paar Schichten mit ReLU und sehr viel Gradientenabstieg.
""")
,
]
