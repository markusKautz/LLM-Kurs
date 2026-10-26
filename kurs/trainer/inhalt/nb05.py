"""Inhalt von Notebook 5: Aufmerksamkeit."""

from .bausteine import aufgabe, code, md, tipps

ZELLEN = [

# =============================================================
# WILLKOMMEN
# =============================================================

md(r"""
# Notebook 5: Aufmerksamkeit

## Das Netz entscheidet selbst, worauf es schaut

In Notebook 4 hast du gesehen, wie ein Zeichen auf alle Zeichen davor zurückschauen kann:
Es vergibt **Punkte**, die Zukunft wird maskiert, die Softmax macht daraus Gewichte, und dann wird gemischt.
Die Punkte hast du aber von Hand festgelegt.

In diesem Notebook lernt das Netz, die Punkte **selbst zu berechnen**. Das heißt **Aufmerksamkeit** (englisch *attention*).
Sie wurde 2017 in der Arbeit "Attention Is All You Need" vorgestellt und steckt heute in jedem großen Sprachmodell.
Am Ende trainierst du ein Netz, das auf 32 Zeichen zurückschauen kann, und schaust ihm beim Denken zu.

### Der Plan für dieses Notebook

| Teil | Was passiert |
|---|---|
| 1 | Die Idee: Frage, Schlagwort und Inhalt |
| 2 | Wie gut passen zwei Zeichen zusammen? |
| 3 | Alle Punkte auf einmal |
| 4 | Aufmerksamkeit in einer Zeile |
| 5 | Ein Aufmerksamkeits-Kopf |
| 6 | Die Reihenfolge der Zeichen |
| 7 | Trainingsdaten aus ganzen Blöcken |
| 8 | Das Aufmerksamkeits-Netz trainieren |
| 9 | Worauf schaut das Netz? |
| 10 | Das Netz schreibt |
""")
,
md(r"""
## Vorbereitung
""")
,
code(r"""
import math

import torch
from torch import nn
import torch.nn.functional as F

from kurswerkzeuge import grafik, grafik2, grafik4, nb5

nb5.pruefe_vorarbeit()

from meincode.notebook1 import Vocabulary, ziehe_zeichen
from meincode.notebook3 import ZeichenNetz, baue_beispiele, trainiere, relu
from meincode.notebook4 import maskieren, gewichteter_durchschnitt

with open("daten/training.txt", encoding="utf-8") as datei:
    trainingstext = datei.read()

grenze = int(len(trainingstext) * 0.9)
vocabulary = Vocabulary(trainingstext)
V = len(vocabulary)
ids_training = torch.tensor(vocabulary.encode(trainingstext[:grenze]))
ids_test = torch.tensor(vocabulary.encode(trainingstext[grenze:]))

print("Alles bereit!")
""")
,

# =============================================================
# TEIL 1: DIE IDEE
# =============================================================

md(r"""
---
# Teil 1: Die Idee: Frage, Schlagwort und Inhalt

Stell dir eine Bibliothek vor. Du suchst ein Buch über Hunde.
- Du hast eine **Frage** im Kopf: "Ich suche etwas über Hunde."
- Jedes Buch hat ein **Schlagwort** auf dem Rücken: "Tiere", "Kochen", "Autos".
- Und jedes Buch hat einen **Inhalt**.

Du vergleichst deine Frage mit allen Schlagwörtern. Bücher mit passendem Schlagwort schaust du dir genau an, die anderen kaum.
Was du am Ende mitnimmst, ist eine Mischung aus den Inhalten der passenden Bücher.

Genau so funktioniert Aufmerksamkeit. Jedes Zeichen im Text erzeugt aus seinen Koordinaten drei Dinge:

| Name | Englisch | Bedeutung |
|---|---|---|
| **Frage** | Query, `q` | Wonach suche ich gerade? |
| **Schlagwort** | Key, `k` | Was habe ich zu bieten? |
| **Inhalt** | Value, `v` | Was gebe ich weiter, wenn jemand auf mich schaut? |

Die Punkte aus Notebook 4 entstehen, indem man die Frage eines Zeichens mit den Schlagwörtern aller Zeichen davor vergleicht.
Gemischt werden dann die **Inhalte**.

Ein Beispiel, wie das bei Text aussehen könnte: Das Zeichen nach einem Leerzeichen fragt "Wie hat der Satz angefangen?".
Zeichen am Satzanfang haben ein passendes Schlagwort und bekommen viele Punkte. Was die Zeichen genau fragen und anbieten,
legt aber niemand fest. Das lernt das Netz selbst.
""")
,

# =============================================================
# TEIL 2: PASSUNG
# =============================================================

md(r"""
---
# Teil 2: Wie gut passen zwei Zeichen zusammen?

Frage und Schlagwort sind Listen von Zahlen, zum Beispiel je drei Zahlen. Wie misst man, ob sie zusammenpassen?

> **Malnehmen und zusammenzählen.**

| | Zahl 1 | Zahl 2 | Zahl 3 | Summe |
|---|---|---|---|---|
| Frage `q` | 1 | 0 | 2 | |
| Schlagwort `k` | 1 | 0 | 1 | |
| `q * k` | 1 | 0 | 2 | **3** |

Das Ergebnis ist groß, wenn bei Frage und Schlagwort **an denselben Stellen große Zahlen** stehen.
Steht bei einem eine positive und beim anderen eine negative Zahl, wird die Summe kleiner.

Diese Rechnung heißt **Skalarprodukt**. Du kennst sie schon: Genau das macht `@` für jede Zeile und Spalte.

---
## Aufgabe 5.1: Wie gut passen zwei Zeichen zusammen?

Schreibe die Funktion `passung(q, k)` für zwei Listen von Zahlen (Tensoren mit einer Richtung):
Malnehmen mit `q * k`, zusammenzählen mit `.sum()`.
""")
,
aufgabe(
vorlage=r"""
def passung(q, k):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 5.1: Hier fehlt noch dein Code")
""",
loesung=r"""
def passung(q, k):
    return (q * k).sum()
""")
,
code(r"""
nb5.pruefe_aufgabe_1(passung)
""")
,
tipps(
    hinweis=r"""
    Schau dir die Tabelle oben noch einmal an: erst Zahl für Zahl malnehmen, dann alles zusammenzählen.

    In PyTorch nimmt `q * k` zwei Listen **Stelle für Stelle** mal. Probier es in einer neuen Zelle aus:
    ```python
    q = torch.tensor([1.0, 0.0, 2.0])
    k = torch.tensor([1.0, 0.0, 1.0])
    print(q * k)
    ```
    """,
    fast=r"""
    ```python
    return (q * k)....
    ```
    Welche Methode zählt alle Zahlen eines Tensors zusammen?
    """,
    loesung=r"""
    ```python
    def passung(q, k):
        return (q * k).sum()
    ```
    - `q * k` nimmt die Zahlen an derselben Stelle mal: `[1, 0, 2] * [1, 0, 1]` ergibt `[1, 0, 2]`.
    - `.sum()` zählt sie zusammen: `1 + 0 + 2 = 3`.

    Die Klammern sind wichtig. Ohne sie würde Python zuerst `k.sum()` rechnen und dann `q` damit malnehmen.
    """,
)
,
code(r"""
frage = torch.tensor([1.0, 0.0, 2.0])
print("passt gut:     ", passung(frage, torch.tensor([1.0, 0.0, 1.0])).item())
print("passt nicht:   ", passung(frage, torch.tensor([-1.0, 1.0, 0.0])).item())
print("passt sehr gut:", passung(frage, torch.tensor([2.0, 0.0, 3.0])).item())
""")
,

# =============================================================
# TEIL 3: ALLE PUNKTE AUF EINMAL
# =============================================================

md(r"""
---
# Teil 3: Alle Punkte auf einmal

Für einen Text mit `T` Zeichen gibt es `T` Fragen und `T` Schlagwörter. Wir brauchen die Passung **jeder** Frage mit **jedem** Schlagwort,
also eine Tabelle mit `T` mal `T` Punkten. Mit einer Schleife wäre das langsam. Mit `@` geht es auf einmal:

```python
q @ k.mT
```

`.mT` **kippt** die Tabelle `k`: Aus Zeilen werden Spalten (das *T* steht für *transponieren*).
Das ist nötig, weil `@` immer eine Zeile von links mit einer **Spalte** von rechts verrechnet.
Nach dem Kippen steht jedes Schlagwort in einer Spalte.
""")
,
code(r"""
k = torch.tensor([[1, 2, 3],
                  [4, 5, 6]])
print("k:\n", k)
print("k.mT (gekippt):\n", k.mT)
""")
,
md(r"""
Prüfen wir, ob `q @ k.mT` wirklich alle Passungen liefert:
""")
,
code(r"""
q = torch.randn(4, 3)
k = torch.randn(4, 3)
alle = q @ k.mT

print("Form:", alle.shape)
print("Frage 2 mit Schlagwort 1, mit @:      ", alle[2, 1].item())
print("Frage 2 mit Schlagwort 1, mit passung:", passung(q[2], k[1]).item())
""")
,
md(r"""
### Ein kleiner Trick: durch die Wurzel teilen

Je mehr Zahlen Frage und Schlagwort haben, desto größer werden die Punkte. Sehr große Punkte machen die Softmax "spitz":
Ein Zeichen bekommt fast alles, alle anderen fast nichts. Dann lernt das Netz schlecht.

Deshalb teilen wir die Punkte durch die Wurzel aus der Anzahl der Zahlen. Das hält sie in einem vernünftigen Bereich.
Es ist ein ähnlicher Trick wie das Abziehen des Maximums bei der Softmax: Er ändert die Idee nicht, macht die Rechnung aber stabil.
""")
,
code(r"""
punkte_klein = torch.tensor([[1.0, 2.0, 3.0]])
print("Softmax normal:      ", torch.softmax(punkte_klein, dim=-1))
print("Softmax 10-mal so groß:", torch.softmax(punkte_klein * 10, dim=-1))
""")
,
md(r"""
---
## Aufgabe 5.2: Alle Punkte auf einmal

Schreibe die Funktion `punkte(q, k)`. Sie gibt `q @ k.mT` geteilt durch `math.sqrt(k.shape[-1])` zurück.

`k.shape[-1]` ist die Anzahl der Zahlen in einem Schlagwort. Wie in Notebook 4 nehmen wir `-1` und `.mT`,
damit die Funktion auch mit einem Stapel aus vielen Texten funktioniert.
""")
,
aufgabe(
vorlage=r"""
def punkte(q, k):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 5.2: Hier fehlt noch dein Code")
""",
loesung=r"""
def punkte(q, k):
    return q @ k.mT / math.sqrt(k.shape[-1])
""")
,
code(r"""
nb5.pruefe_aufgabe_2(punkte)
""")
,
tipps(
    hinweis=r"""
    Die Rechnung hat zwei Teile:

    1. Alle Passungen auf einmal: `q @ k.mT`. Das steht im Text über der Aufgabe.
    2. Das Ergebnis durch die Wurzel aus der Anzahl der Zahlen pro Schlagwort teilen.
       Die Anzahl ist `k.shape[-1]`, die Wurzel rechnet `math.sqrt(...)`.
    """,
    fast=r"""
    ```python
    return q @ ... / math.sqrt(...)
    ```
    """,
    loesung=r"""
    ```python
    def punkte(q, k):
        return q @ k.mT / math.sqrt(k.shape[-1])
    ```
    - `k.mT` kippt `k`, sodass jedes Schlagwort in einer Spalte steht. `q @ k.mT` rechnet dann jede Frage (Zeile) mit jedem Schlagwort (Spalte).
      Das Feld in Zeile `i` und Spalte `j` ist `passung(q[i], k[j])`.
    - Hat jedes Schlagwort zum Beispiel 16 Zahlen, ist `k.shape[-1]` gleich 16, und es wird durch 4 geteilt.
      Das hält die Punkte klein genug, damit die Softmax nicht zu spitz wird.
    - Die Reihenfolge ist wichtig: `q @ k.mT` ist nicht dasselbe wie `k @ q.mT`. Zeilen sind die Fragen, Spalten die Schlagwörter.
    """,
)
,

# =============================================================
# TEIL 4: AUFMERKSAMKEIT
# =============================================================

md(r"""
---
# Teil 4: Aufmerksamkeit in einer Zeile

Jetzt hast du alle Teile. Aufmerksamkeit ist:

1. Punkte aus Fragen und Schlagwörtern berechnen: `punkte(q, k)`
2. Damit die Inhalte `v` gewichtet mischen. Das ist dein `gewichteter_durchschnitt` aus Notebook 4.
   Er maskiert die Zukunft und wendet die Softmax an.

---
## Aufgabe 5.3: Aufmerksamkeit

Schreibe die Funktion `aufmerksamkeit(q, k, v)`. Es ist wirklich nur eine Zeile.
""")
,
aufgabe(
vorlage=r"""
def aufmerksamkeit(q, k, v):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 5.3: Hier fehlt noch dein Code")
""",
loesung=r"""
def aufmerksamkeit(q, k, v):
    return gewichteter_durchschnitt(punkte(q, k), v)
""")
,
code(r"""
nb5.pruefe_aufgabe_3(aufmerksamkeit)
""")
,
tipps(
    hinweis=r"""
    Du hast beide Teile schon:

    - `punkte(q, k)` aus Aufgabe 5.2 liefert die Punkte.
    - `gewichteter_durchschnitt(punkte, x)` aus Notebook 4 maskiert die Punkte, macht mit der Softmax Gewichte daraus und mischt damit `x`.

    Was soll hier gemischt werden: die Fragen, die Schlagwörter oder die Inhalte?
    """,
    fast=r"""
    ```python
    return gewichteter_durchschnitt(punkte(..., ...), ...)
    ```
    """,
    loesung=r"""
    ```python
    def aufmerksamkeit(q, k, v):
        return gewichteter_durchschnitt(punkte(q, k), v)
    ```
    - `punkte(q, k)` vergleicht jede Frage mit jedem Schlagwort.
    - `gewichteter_durchschnitt` macht daraus Gewichte (ohne Blick in die Zukunft) und mischt die **Inhalte** `v`.

    Wie in der Bibliothek: Frage und Schlagwort entscheiden, welche Bücher du anschaust. Mitnehmen tust du aber den Inhalt.
    """,
)
,
md(r"""
Das ist die Formel aus der berühmten Arbeit von 2017. Dort steht sie so:

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^T}{\sqrt{d}}\right) V
$$

Du hast jedes Stück davon selbst gebaut: $Q K^T$ ist `q @ k.mT`, $\sqrt{d}$ ist die Wurzel, die Softmax kennst du,
und $\cdot V$ ist `@ v`. Das Maskieren steht in der Formel nicht, gehört bei Sprachmodellen aber immer dazu.
""")
,

# =============================================================
# TEIL 5: EIN AUFMERKSAMKEITS-KOPF
# =============================================================

md(r"""
---
# Teil 5: Ein Aufmerksamkeits-Kopf

Woher kommen Frage, Schlagwort und Inhalt? Jedes Zeichen hat seine Koordinaten `x` aus der Einbettung.
Daraus machen drei Schichten `nn.Linear` die drei Dinge. Man kann sie sich als drei **Übersetzer** vorstellen:
Der erste übersetzt die Koordinaten eines Zeichens in seine Frage, der zweite in sein Schlagwort, der dritte in seinen Inhalt.

Diese drei Schichten haben keine Verschiebung `b`, deshalb steht dort `bias=False`.
Was sie übersetzen, lernt das Netz beim Training.

Den ganzen Baustein nennt man einen **Aufmerksamkeits-Kopf** (englisch *attention head*).

---
## Aufgabe 5.4: Ein Aufmerksamkeits-Kopf

Schreibe die Klasse `AufmerksamkeitsKopf(nn.Module)`:

**`__init__(self, C, H)`**: `C` ist die Anzahl der Koordinaten pro Zeichen, `H` die Anzahl der Zahlen in Frage, Schlagwort und Inhalt.

| Attribut | Baustein |
|---|---|
| `self.query` | `nn.Linear(C, H, bias=False)` |
| `self.key` | `nn.Linear(C, H, bias=False)` |
| `self.value` | `nn.Linear(C, H, bias=False)` |

**`forward(self, x)`** gibt `aufmerksamkeit(self.query(x), self.key(x), self.value(x))` zurück.
""")
,
aufgabe(
vorlage=r"""
class AufmerksamkeitsKopf(nn.Module):
    def __init__(self, C, H):
        super().__init__()
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 5.4: Hier fehlt noch dein Code")

    def forward(self, x):
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 5.4: Hier fehlt noch dein Code")
""",
loesung=r"""
class AufmerksamkeitsKopf(nn.Module):
    def __init__(self, C, H):
        super().__init__()
        self.query = nn.Linear(C, H, bias=False)
        self.key = nn.Linear(C, H, bias=False)
        self.value = nn.Linear(C, H, bias=False)

    def forward(self, x):
        return aufmerksamkeit(self.query(x), self.key(x), self.value(x))
""")
,
code(r"""
nb5.pruefe_aufgabe_4(AufmerksamkeitsKopf)
""")
,
tipps(
    hinweis=r"""
    - **__init__:** drei Übersetzer, je ein `nn.Linear` von `C` Zahlen auf `H` Zahlen, ohne Verschiebung (`bias=False`).
      Vergiss `super().__init__()` nicht, das steht schon in der Vorlage.
    - **forward:** Jeder Übersetzer macht aus `x` etwas anderes: die Fragen, die Schlagwörter, die Inhalte.
      Diese drei gibst du an deine Funktion `aufmerksamkeit`.
    """,
    fast=r"""
    ```python
    def __init__(self, C, H):
        super().__init__()
        self.query = nn.Linear(C, H, bias=False)
        self.key = ...
        self.value = ...

    def forward(self, x):
        return aufmerksamkeit(self.query(x), ..., ...)
    ```
    """,
    loesung=r"""
    ```python
    class AufmerksamkeitsKopf(nn.Module):
        def __init__(self, C, H):
            super().__init__()
            self.query = nn.Linear(C, H, bias=False)
            self.key = nn.Linear(C, H, bias=False)
            self.value = nn.Linear(C, H, bias=False)

        def forward(self, x):
            return aufmerksamkeit(self.query(x), self.key(x), self.value(x))
    ```
    - Die drei `nn.Linear` sind gleich aufgebaut, lernen aber verschiedene Gewichte. Deshalb macht jeder aus denselben Koordinaten etwas anderes.
    - `self.query(x)` liefert für jedes Zeichen seine Frage, `self.key(x)` sein Schlagwort, `self.value(x)` seinen Inhalt.
    - `aufmerksamkeit` erledigt den Rest. Ein Aufmerksamkeits-Kopf ist also nur: drei Übersetzer plus deine Funktion aus Aufgabe 5.3.
    """,
)
,

# =============================================================
# TEIL 6: POSITIONEN
# =============================================================

md(r"""
---
# Teil 6: Die Reihenfolge der Zeichen

Am Ende von Notebook 4 haben wir gesehen: Beim Mischen geht die Reihenfolge verloren.
Gilt das auch für die Aufmerksamkeit? Wir vergleichen "abc" mit "bac". Das letzte Zeichen ist in beiden Fällen `c`,
nur die beiden Zeichen davor sind vertauscht.
""")
,
code(r"""
torch.manual_seed(0)
karte = nn.Embedding(V, 8)
kopf = AufmerksamkeitsKopf(8, 8)

def letzte_zeile(text):
    x = karte(torch.tensor(vocabulary.encode(text)))
    return kopf(x)[-1]

print("'abc':", letzte_zeile("abc"))
print("'bac':", letzte_zeile("bac"))
""")
,
md(r"""
Genau gleich. Für das `c` ist es egal, in welcher Reihenfolge die Zeichen davor standen. Für Sprache ist das schlecht:
"die Katze jagt den Hund" und "den Hund jagt die Katze" bedeuten etwas anderes.

Die Lösung ist überraschend einfach: Jede **Position** bekommt auch eigene Koordinaten, genau wie jedes Zeichen.
Die Koordinaten der Position werden zu den Koordinaten des Zeichens **dazugezählt**.
Ein `a` an Position 0 hat dann andere Koordinaten als ein `a` an Position 1.
""")
,
code(r"""
positionen = nn.Embedding(3, 8)      # Koordinaten für die Positionen 0, 1 und 2

def letzte_zeile_mit_position(text):
    x = karte(torch.tensor(vocabulary.encode(text))) + positionen(torch.arange(len(text)))
    return kopf(x)[-1]

print("'abc':", letzte_zeile_mit_position("abc"))
print("'bac':", letzte_zeile_mit_position("bac"))
""")
,
md(r"""
Jetzt unterscheiden sich die beiden. `torch.arange(3)` ist `[0, 1, 2]`, also die Positionen der Zeichen.
Wie die Positionen auf der Karte liegen, lernt das Netz ebenfalls selbst.
""")
,

# =============================================================
# TEIL 7: BLÖCKE
# =============================================================

md(r"""
---
# Teil 7: Trainingsdaten aus ganzen Blöcken

In Notebook 3 war ein Trainingsbeispiel ein Stück aus drei Zeichen und **ein** Ziel.
Mit Aufmerksamkeit geht das viel effizienter: Wir nehmen einen ganzen **Block** aus 32 Zeichen,
und **jedes** Zeichen im Block sagt das nächste voraus. Aus einem Block werden so 32 Beispiele auf einmal.

Das Ziel `Y` ist dabei einfach derselbe Block, **um ein Zeichen nach rechts verschoben**:

| | | | | | | | | |
|---|---|---|---|---|---|---|---|---|
| **X** | `d` | `e` | `r` | `␣` | `m` | `o` | `r` | `g` |
| **Y** | `e` | `r` | `␣` | `m` | `o` | `r` | `g` | `e` |

Das `d` soll `e` vorhersagen. Das `e` sieht `d` und `e` und soll `r` vorhersagen. Und so weiter.
Dank der Maske kann dabei kein Zeichen spicken.

### Werkzeug: `torch.stack`

`torch.stack(liste)` stapelt eine Liste gleich langer Zeilen zu einer Tabelle:
""")
,
code(r"""
print(torch.stack([torch.tensor([1, 2, 3]), torch.tensor([4, 5, 6])]))
""")
,
md(r"""
---
## Aufgabe 5.5: Trainingsblöcke ziehen

Schreibe die Funktion `ziehe_bloecke(ids, kontext, anzahl)`. `ids` ist ein Tensor mit allen IDs des Texts.

1. Zufällige Startpositionen ziehen: `starts = torch.randint(0, len(ids) - kontext, (anzahl,))`
2. `X` ist der Stapel aus allen Blöcken `ids[s:s + kontext]`
3. `Y` ist der Stapel aus allen Blöcken `ids[s + 1:s + kontext + 1]`
4. `X, Y` zurückgeben

Für die Stapel kannst du eine List Comprehension verwenden: `torch.stack([ids[s:s + kontext] for s in starts])`
""")
,
aufgabe(
vorlage=r"""
def ziehe_bloecke(ids, kontext, anzahl):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 5.5: Hier fehlt noch dein Code")
""",
loesung=r"""
def ziehe_bloecke(ids, kontext, anzahl):
    starts = torch.randint(0, len(ids) - kontext, (anzahl,))
    X = torch.stack([ids[s:s + kontext] for s in starts])
    Y = torch.stack([ids[s + 1:s + kontext + 1] for s in starts])
    return X, Y
""")
,
code(r"""
nb5.pruefe_aufgabe_5(ziehe_bloecke)
""")
,
tipps(
    hinweis=r"""
    Ein Block für `Y` ist derselbe Textausschnitt wie für `X`, nur **um ein Zeichen nach rechts verschoben**.
    So steht in `Y` an jeder Stelle das Zeichen, das im Text als Nächstes kommt.

    `torch.stack(liste)` stapelt eine Liste von gleich langen Tensoren zu einer Tabelle, jeder Tensor wird eine Zeile.
    """,
    fast=r"""
    ```python
    starts = torch.randint(0, len(ids) - kontext, (anzahl,))
    X = torch.stack([ids[s:s + kontext] for s in starts])
    Y = torch.stack([ids[...:...] for s in starts])
    return X, Y
    ```
    """,
    loesung=r"""
    ```python
    def ziehe_bloecke(ids, kontext, anzahl):
        starts = torch.randint(0, len(ids) - kontext, (anzahl,))
        X = torch.stack([ids[s:s + kontext] for s in starts])
        Y = torch.stack([ids[s + 1:s + kontext + 1] for s in starts])
        return X, Y
    ```
    Mit `kontext = 4` und dem Text `"hallo welt"`, Startposition 0:

    - `X` bekommt `"hall"`, `Y` bekommt `"allo"`. Unter jedem Zeichen in `X` steht in `Y` das nächste Zeichen.
    - Die Startpositionen gehen nur bis `len(ids) - kontext`, damit auch der verschobene Block für `Y` noch in den Text passt.
    - `torch.stack` macht aus der Liste von `anzahl` Blöcken eine Tabelle mit Form `(anzahl, kontext)`.
    """,
)
,
code(r"""
X, Y = ziehe_bloecke(ids_training, 32, 2)
print("X:", X.shape)
print("X[0]:", repr(vocabulary.decode(X[0].tolist())))
print("Y[0]:", repr(vocabulary.decode(Y[0].tolist())))
""")
,

# =============================================================
# TEIL 8: DAS AUFMERKSAMKEITS-NETZ
# =============================================================

md(r"""
---
# Teil 8: Das Aufmerksamkeits-Netz

Jetzt bauen wir das ganze Netz. Es bekommt einen Stapel aus Blöcken `X` und liefert für **jede Position** in jedem Block Logits:

1. Koordinaten der Zeichen plus Koordinaten der Positionen
2. Ein Aufmerksamkeits-Kopf: Jedes Zeichen sammelt Informationen von den Zeichen davor.
3. Eine verborgene Schicht mit ReLU wie in Notebook 3: Das Netz "denkt" über das Gesammelte nach.
4. Eine letzte Schicht macht daraus die Logits.

Du musst dir dabei keine Gedanken über Stapel machen. `nn.Embedding`, `nn.Linear` und deine Funktionen rechnen automatisch
für alle Blöcke gleichzeitig.

---
## Aufgabe 5.6: Das Aufmerksamkeits-Netz

**`__init__(self, V, kontext, C)`**:

| Attribut | Baustein |
|---|---|
| `self.kontext` | `kontext` |
| `self.zeichen` | `nn.Embedding(V, C)` |
| `self.position` | `nn.Embedding(kontext, C)` |
| `self.kopf` | `AufmerksamkeitsKopf(C, C)` |
| `self.schicht` | `nn.Linear(C, 4 * C)` |
| `self.ausgabe` | `nn.Linear(4 * C, V)` |

**`forward(self, X)`**:
1. `T = X.shape[-1]` ist die Länge der Blöcke
2. `x = self.zeichen(X) + self.position(torch.arange(T))`
3. `h = relu(self.schicht(self.kopf(x)))`
4. `self.ausgabe(h)` zurückgeben
""")
,
aufgabe(
vorlage=r"""
class AufmerksamkeitsNetz(nn.Module):
    def __init__(self, V, kontext, C):
        super().__init__()
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 5.6: Hier fehlt noch dein Code")

    def forward(self, X):
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 5.6: Hier fehlt noch dein Code")
""",
loesung=r"""
class AufmerksamkeitsNetz(nn.Module):
    def __init__(self, V, kontext, C):
        super().__init__()
        self.kontext = kontext
        self.zeichen = nn.Embedding(V, C)
        self.position = nn.Embedding(kontext, C)
        self.kopf = AufmerksamkeitsKopf(C, C)
        self.schicht = nn.Linear(C, 4 * C)
        self.ausgabe = nn.Linear(4 * C, V)

    def forward(self, X):
        T = X.shape[-1]
        x = self.zeichen(X) + self.position(torch.arange(T))
        h = relu(self.schicht(self.kopf(x)))
        return self.ausgabe(h)
""")
,
code(r"""
nb5.pruefe_aufgabe_6(AufmerksamkeitsNetz)
""")
,
tipps(
    hinweis=r"""
    - **__init__:** sechs Zeilen, eine pro Zeile der Tabelle. Das erste Attribut ist eine normale Zahl, die anderen sind Bausteine.
    - **forward:** vier Schritte. Neu ist die Position: `torch.arange(T)` sind die Positionen `0, 1, ..., T - 1`.
      `self.position` schlägt für jede Position Koordinaten nach, genau wie `self.zeichen` für jedes Zeichen.
      Beides wird zusammengezählt.
    """,
    fast=r"""
    ```python
    def __init__(self, V, kontext, C):
        super().__init__()
        self.kontext = kontext
        self.zeichen = nn.Embedding(V, C)
        self.position = nn.Embedding(..., C)
        self.kopf = AufmerksamkeitsKopf(C, C)
        self.schicht = nn.Linear(C, ...)
        self.ausgabe = nn.Linear(..., V)

    def forward(self, X):
        T = X.shape[-1]
        x = self.zeichen(X) + self.position(...)
        h = relu(self.schicht(...))
        return self.ausgabe(h)
    ```
    """,
    loesung=r"""
    ```python
    class AufmerksamkeitsNetz(nn.Module):
        def __init__(self, V, kontext, C):
            super().__init__()
            self.kontext = kontext
            self.zeichen = nn.Embedding(V, C)
            self.position = nn.Embedding(kontext, C)
            self.kopf = AufmerksamkeitsKopf(C, C)
            self.schicht = nn.Linear(C, 4 * C)
            self.ausgabe = nn.Linear(4 * C, V)

        def forward(self, X):
            T = X.shape[-1]
            x = self.zeichen(X) + self.position(torch.arange(T))
            h = relu(self.schicht(self.kopf(x)))
            return self.ausgabe(h)
    ```
    Der Weg durch das Netz:

    1. `self.zeichen(X) + self.position(torch.arange(T))`: Jedes Zeichen bekommt Koordinaten dafür, **was** es ist, plus Koordinaten dafür, **wo** es steht.
       So ist ein `a` am Anfang etwas anderes als ein `a` am Ende.
    2. `self.kopf(x)`: Jedes Zeichen sammelt Informationen von den Zeichen davor.
    3. `relu(self.schicht(...))`: Eine Schicht mit 4 * C Neuronen verarbeitet das Gesammelte, wie die erste Schicht im `ZeichenNetz`.
    4. `self.ausgabe(h)`: eine Zahl pro Zeichen im Vokabular, an **jeder** Position. Die Form ist `(Anzahl, T, V)`.
    """,
)
,
md(r"""
### Vorbereitung für das Training

Das Netz liefert jetzt Logits mit drei Richtungen: Blöcke, Positionen und Zeichen.
`F.cross_entropy` erwartet aber eine Tabelle mit einer Zeile pro Beispiel.
Deshalb legen wir alle Blöcke **untereinander**: `.view(-1, V)` macht aus 32 Blöcken mit je 32 Positionen eine Tabelle mit 1024 Zeilen.
Die `-1` heißt dabei "rechne selbst aus, wie viele Zeilen das sind".
""")
,
code(r"""
def verlust_bloecke(netz, X, Y):
    logits = netz(X)
    return F.cross_entropy(logits.view(-1, V), Y.view(-1))


def schaetze_verlust(netz, ids):
    with torch.no_grad():
        X, Y = ziehe_bloecke(ids, netz.kontext, 200)
        return verlust_bloecke(netz, X, Y).item()
""")
,
md(r"""
`schaetze_verlust` nimmt 200 zufällige Blöcke statt des ganzen Texts. Das geht schneller und ist genau genug.

### Der Vergleich: dein ZeichenNetz aus Notebook 3

Damit wir wissen, wo wir stehen, trainieren wir zuerst noch einmal das beste Netz aus Notebook 3.
""")
,
code(r"""
X3_training, Y3_training = baue_beispiele(ids_training.tolist(), 3)
X3_test, Y3_test = baue_beispiele(ids_test.tolist(), 3)

torch.manual_seed(1)
zeichen_netz = ZeichenNetz(V, kontext=3, koordinaten=10, neuronen=100)
trainiere(zeichen_netz, X3_training, Y3_training, schritte=10000, lernrate=0.1)

with torch.no_grad():
    zeichen_netz_test = F.cross_entropy(zeichen_netz(X3_test), Y3_test).item()
print("ZeichenNetz auf dem Test:", round(zeichen_netz_test, 3))
""")
,
md(r"""
### Ein schlauerer Optimierer

Für Netze mit Aufmerksamkeit verwenden wir einen anderen Optimierer: **AdamW**.
Er funktioniert wie SGD, passt aber die Schrittgröße für jedes Gewicht selbst an.
Gewichte, die lange in dieselbe Richtung wollen, bekommen größere Schritte. So lernt das Netz schneller.
Die Bedienung ist genau gleich: `zero_grad()`, `backward()`, `step()`.

### Das Training

Das Netz sieht 32 Zeichen auf einmal und hat 32 Koordinaten pro Zeichen. Das Training dauert etwa eine halbe Minute.
""")
,
code(r"""
torch.manual_seed(1)
netz = AufmerksamkeitsNetz(V, kontext=32, C=32)
optimierer = torch.optim.AdamW(netz.parameters(), lr=3e-3)
print("Anzahl Gewichte:", sum(p.numel() for p in netz.parameters()))

kurve = grafik2.LiveKurve(titel="Das Aufmerksamkeits-Netz lernt", ziel=zeichen_netz_test, ziel_text="ZeichenNetz")
for schritt in range(3001):
    X, Y = ziehe_bloecke(ids_training, 32, 32)
    verlust = verlust_bloecke(netz, X, Y)
    optimierer.zero_grad()
    verlust.backward()
    optimierer.step()

    if schritt % 200 == 0:
        kurve.punkt(schritt, schaetze_verlust(netz, ids_training), schaetze_verlust(netz, ids_test))
""")
,
md(r"""
Ehrlich gesagt: Ein einzelner Aufmerksamkeits-Kopf ist noch nicht besser als dein `ZeichenNetz`, eher etwas schlechter.
Das ist normal. Ein Kopf kann Informationen einsammeln, aber das Netz hat danach nur eine kleine Schicht, um darüber nachzudenken.

Dafür hat es etwas, das dem `ZeichenNetz` fehlt: Es sieht **32 Zeichen** statt 3 und ist dabei nicht größer geworden.
Das `ZeichenNetz` mit 16 Zeichen aus Notebook 4 hatte fast 20.000 Gewichte und war auf dem Test katastrophal.

In Notebook 6 baust du aus diesem Baustein den echten **Transformer**: viele Köpfe, mehr Nachdenken und mehrere Schichten übereinander.
Dann zieht er am `ZeichenNetz` vorbei.
""")
,

# =============================================================
# TEIL 9: HINEINSCHAUEN
# =============================================================

md(r"""
---
# Teil 9: Worauf schaut das Netz?

Das Schöne an der Aufmerksamkeit: Man kann zuschauen. Wir berechnen für einen Satz die Gewichte des Kopfs,
also wie stark jedes Zeichen auf jedes frühere Zeichen schaut. Das sind genau deine Funktionen:
""")
,
code(r"""
satz = "der hund läuft über den gehweg."

with torch.no_grad():
    ids = torch.tensor(vocabulary.encode(satz))
    x = netz.zeichen(ids) + netz.position(torch.arange(len(satz)))
    q, k = netz.kopf.query(x), netz.kopf.key(x)
    gewichte = torch.softmax(maskieren(punkte(q, k)), dim=-1)

grafik4.aufmerksamkeit_erkunden(gewichte, satz)
""")
,
md(r"""
Schieb den Regler durch den Satz. Fällt dir etwas auf?
- Schauen viele Zeichen vor allem auf sich selbst oder auf das Zeichen direkt davor?
- Was passiert nach einem Leerzeichen?
- Schaut irgendein Zeichen weit zurück?

Ein einzelner Kopf muss sich auf eine Art des Zurückschauens festlegen. Mehrere Köpfe könnten verschiedene Dinge gleichzeitig beachten.
Genau das bauen wir in Notebook 6.

Hier dasselbe als Tabelle für die ersten 14 Zeichen:
""")
,
code(r"""
grafik4.gewichte_bild(gewichte[:14, :14], satz[:14], "Aufmerksamkeit nach dem Training")
""")
,

# =============================================================
# TEIL 10: TEXT GENERIEREN
# =============================================================

md(r"""
---
# Teil 10: Das Netz schreibt

Fast wie in Notebook 3. Es gibt zwei kleine Unterschiede:
- Der Text darf kürzer sein als `netz.kontext`. Du nimmst einfach die letzten **höchstens** `netz.kontext` Zeichen: `text[-netz.kontext:]`
- Das Netz liefert Logits für **jede** Position. Für das nächste Zeichen brauchst du nur die **letzte**: `logits[0, -1]`

---
## Aufgabe 5.7: Text generieren mit Aufmerksamkeit

**`naechste_verteilung(netz, vocabulary, text)`**
1. `ids = vocabulary.encode(text[-netz.kontext:])`
2. Mit `torch.no_grad()`: `logits = netz(torch.tensor([ids]))`
3. `P = torch.softmax(logits[0, -1], dim=-1)`
4. Daraus wie bisher ein Dictionary `{zeichen: wahrscheinlichkeit}` machen

**`generiere(netz, vocabulary, start, laenge)`** übernimmst du aus Notebook 3.
""")
,
aufgabe(
vorlage=r"""
def naechste_verteilung(netz, vocabulary, text):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 5.7: Hier fehlt noch dein Code")


def generiere(netz, vocabulary, start, laenge):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 5.7: Hier fehlt noch dein Code")
""",
loesung=r"""
def naechste_verteilung(netz, vocabulary, text):
    ids = vocabulary.encode(text[-netz.kontext:])
    with torch.no_grad():
        logits = netz(torch.tensor([ids]))
    P = torch.softmax(logits[0, -1], dim=-1)
    return {vocabulary.id_zu_zeichen[i]: p for i, p in enumerate(P.tolist())}


def generiere(netz, vocabulary, start, laenge):
    text = start
    for _ in range(laenge):
        text += ziehe_zeichen(naechste_verteilung(netz, vocabulary, text))
    return text
""")
,
code(r"""
nb5.pruefe_aufgabe_7(naechste_verteilung, generiere)
""")
,
tipps(
    hinweis=r"""
    Fast wie in Notebook 3. Der wichtige Unterschied: Das Netz liefert jetzt an **jeder** Position eine Vorhersage.
    Die Logits haben die Form `(1, T, V)`: ein Text, `T` Positionen, `V` Zahlen pro Position.

    Für das nächste Zeichen brauchst du nur die Vorhersage an der **letzten** Position des einen Texts.
    Weil das nur eine einfache Liste ist, nimmst du `torch.softmax(..., dim=-1)` statt deiner eigenen `softmax` für Tabellen.

    `generiere` übernimmst du unverändert aus Notebook 3.
    """,
    fast=r"""
    ```python
    def naechste_verteilung(netz, vocabulary, text):
        ids = vocabulary.encode(text[-netz.kontext:])
        with torch.no_grad():
            logits = netz(torch.tensor([ids]))
        P = torch.softmax(logits[..., ...], dim=-1)
        return {vocabulary.id_zu_zeichen[i]: p for i, p in enumerate(P.tolist())}


    def generiere(netz, vocabulary, start, laenge):
        text = start
        for _ in range(laenge):
            text += ziehe_zeichen(...)
        return text
    ```
    """,
    loesung=r"""
    ```python
    def naechste_verteilung(netz, vocabulary, text):
        ids = vocabulary.encode(text[-netz.kontext:])
        with torch.no_grad():
            logits = netz(torch.tensor([ids]))
        P = torch.softmax(logits[0, -1], dim=-1)
        return {vocabulary.id_zu_zeichen[i]: p for i, p in enumerate(P.tolist())}


    def generiere(netz, vocabulary, start, laenge):
        text = start
        for _ in range(laenge):
            text += ziehe_zeichen(naechste_verteilung(netz, vocabulary, text))
        return text
    ```
    - `text[-netz.kontext:]` schneidet höchstens so viele Zeichen ab, wie das Netz Positionen kennt. Ist der Text kürzer, nimmt es einfach alle.
    - `logits[0, -1]` heißt: erster (und einziger) Text, letzte Position. Das ist die Vorhersage für das Zeichen **nach** dem Text.
      Die Vorhersagen an den anderen Positionen braucht man nur beim Training.
    - `torch.softmax(..., dim=-1)` macht daraus Wahrscheinlichkeiten, der Rest ist wie in Notebook 3.
    """,
)
,
code(r"""
print(generiere(netz, vocabulary, "d", 400))
""")
,
md(r"""
Das Netz kann jetzt mit einem einzigen Zeichen starten. Es braucht keinen Starttext mit fester Länge mehr.

---
# Abschluss: Deinen Code speichern
""")
,
code(r"""
nb5.speichern(
    passung,
    punkte,
    aufmerksamkeit,
    AufmerksamkeitsKopf,
    ziehe_bloecke,
    AufmerksamkeitsNetz,
    naechste_verteilung,
    generiere,
)
""")
,
md(r"""
## Zusammenfassung

| Begriff | Bedeutung |
|---|---|
| **Query, Key, Value** | Frage, Schlagwort und Inhalt jedes Zeichens. Jedes entsteht mit einem eigenen `nn.Linear`. |
| **Skalarprodukt** | malnehmen und zusammenzählen. Groß, wenn Frage und Schlagwort zusammenpassen. |
| `q @ k.mT` | alle Passungen auf einmal. `.mT` kippt die Tabelle. |
| **Aufmerksamkeit** | Punkte aus Fragen und Schlagwörtern, maskieren, Softmax, Inhalte mischen |
| **Aufmerksamkeits-Kopf** | ein Baustein, der für jedes Zeichen Informationen von früheren Zeichen einsammelt |
| **Positions-Einbettung** | eigene Koordinaten für jede Position, damit die Reihenfolge nicht verloren geht |
| **Block** | ein Stück Text, in dem jedes Zeichen das nächste vorhersagt. Das Ziel ist der Block um eins verschoben. |
| **AdamW** | ein Optimierer, der die Schrittgröße für jedes Gewicht selbst anpasst |

## Ausblick auf Notebook 6

Ein Kopf allein ist noch kein Transformer. In Notebook 6 kommen die restlichen Bausteine dazu:
mehrere Köpfe, die gleichzeitig auf verschiedene Dinge achten, mehr Platz zum Nachdenken, Abkürzungen
und mehrere Schichten übereinander. Damit hast du dann alle Teile, aus denen auch GPT gebaut ist.
""")
,
]
