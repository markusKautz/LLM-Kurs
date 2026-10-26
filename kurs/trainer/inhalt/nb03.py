"""Inhalt von Notebook 3: Ein größeres Netz."""

from .bausteine import aufgabe, code, md, tipps

ZELLEN = [

# =============================================================
# WILLKOMMEN
# =============================================================

md(r"""
# Notebook 3: Ein größeres Netz

## Mehr Kontext und Zeichen mit Bedeutung

Dein Bigramm-Netz aus Notebook 2 kann schon einiges. Es lernt selbst und hält nichts für unmöglich.
Aber es sieht nur **ein einziges Zeichen** als Kontext. Und **Problem 1** aus Notebook 1 ist noch offen:

> Ein Modell soll ähnliche Kontexte ähnlich behandeln, auch wenn es einen Kontext noch nie gesehen hat.

In diesem Notebook baust du ein Netz, das **drei Zeichen** auf einmal sieht und dieses Problem löst.
Die Idee dazu stammt aus einer berühmten Arbeit von Yoshua Bengio aus dem Jahr 2003. Sie ist einer der Grundsteine moderner Sprachmodelle.

### Der Plan für dieses Notebook

| Teil | Was passiert |
|---|---|
| 1 | Warum Zählen bei mehr Kontext nicht funktioniert |
| 2 | Trainingsbeispiele mit drei Zeichen Kontext |
| 3 | Jedes Zeichen bekommt einen Platz auf einer Karte |
| 4 | Die verborgene Schicht: Neuronen, die an- und ausgehen |
| 5 | Das Netz von Hand bauen und trainieren |
| 6 | Dasselbe Netz mit den fertigen Bausteinen von PyTorch |
| 7 | Schneller lernen mit Minibatches |
| 8 | Was hat das Netz gelernt? Die Karte der Zeichen |
| 9 | Größer ist nicht immer besser |
| 10 | Das Netz schreibt |
| 11 | Was du jetzt über Sprachmodelle weißt |

Die meisten Bausteine kennst du schon aus Notebook 2. Neu sind die Karte der Zeichen und die verborgene Schicht.
""")
,
md(r"""
## Vorbereitung

Die nächste Zelle lädt PyTorch, die Werkzeuge und deinen Code aus Notebook 1 und 2.
Falls sie einen Fehler meldet, schließe zuerst die früheren Notebooks ab.

Neu sind zwei Zeilen: `from torch import nn` lädt die fertigen Bausteine für neuronale Netze (*neural networks*),
`import torch.nn.functional as F` ein paar fertige Funktionen. Beides lernst du in Teil 6 kennen.
""")
,
code(r"""
import time

import torch
from torch import nn
import torch.nn.functional as F

from kurswerkzeuge import grafik, grafik2, grafik3, nb3

nb3.pruefe_vorarbeit()

from meincode.notebook1 import Vocabulary, NGramModell, ziehe_zeichen
from meincode.notebook2 import softmax, kreuzentropie, gradientenschritt

with open("daten/training.txt", encoding="utf-8") as datei:
    trainingstext = datei.read()

grenze = int(len(trainingstext) * 0.9)
training = trainingstext[:grenze]
test = trainingstext[grenze:]

vocabulary = Vocabulary(trainingstext)
V = len(vocabulary)
ids_training = vocabulary.encode(training)
ids_test = vocabulary.encode(test)

print("Alles bereit! Größe des Vokabulars:", V)
""")
,

# =============================================================
# TEIL 1: WARUM NICHT EINFACH MEHR ZÄHLEN?
# =============================================================

md(r"""
---
# Teil 1: Warum nicht einfach mehr zählen?

In Notebook 1 hast du gesehen: Je mehr Zeichen ein Zählmodell als Kontext nimmt, desto besser klingt der Text.
Aber desto häufiger trifft es im Testtext auf einen Kontext, den es **noch nie gesehen** hat. Dann weiß es gar nichts.

Wie oft passiert das bei drei Zeichen Kontext? Zählen wir nach:
""")
,
code(r"""
kontexte_training = {training[i:i + 3] for i in range(len(training) - 3)}
kontexte_test = [test[i:i + 3] for i in range(len(test) - 3)]
unbekannt = [k for k in kontexte_test if k not in kontexte_training]

print(f"Mögliche Kontexte aus 3 Zeichen: {V ** 3}")
print(f"Davon im Training gesehen:       {len(kontexte_training)}")
print(f"Im Testtext unbekannt:           {len(unbekannt)} von {len(kontexte_test)} ({len(unbekannt) / len(kontexte_test):.0%})")
print("Beispiele:", unbekannt[:8])
""")
,
md(r"""
Bei jedem unbekannten Kontext ist das Zählmodell völlig ratlos. Dabei sind viele davon gar nicht so fremd.
Wer weiß, was nach `"die"` kommt, könnte auch bei `"dia"` oder `"sie"` eine gute Vermutung haben.

Das Zählmodell kann das nicht, weil für es jedes Zeichen nur ein Name ist. Es weiß nicht, dass sich `a` und `e`
ähnlicher sind als `a` und `!`. Genau das soll unser neues Netz lernen.

Die Idee in einem Satz:

> **Jedes Zeichen bekommt einen Platz auf einer Karte. Ähnliche Zeichen sollen nah beieinander liegen.**

Dann kann das Netz von bekannten Kontexten auf ähnliche, unbekannte Kontexte schließen.
Und das Beste: Wo welches Zeichen liegt, muss niemand festlegen. Das Netz lernt es selbst.
""")
,

# =============================================================
# TEIL 2: TRAININGSBEISPIELE
# =============================================================

md(r"""
---
# Teil 2: Trainingsbeispiele mit drei Zeichen Kontext

Im Bigramm-Netz war ein Beispiel ein einzelnes Zeichen und das Zeichen danach.
Jetzt ist ein Beispiel ein Stück aus **drei Zeichen** und das Zeichen danach.
Wir schieben dazu ein Fenster über den Text:

| Text | Kontext X | Ziel Y |
|---|---|---|
| **der** morgen | `der` | `␣` |
| d**er␣**morgen | `er␣` | `m` |
| de**r␣m**orgen | `r␣m` | `o` |

---
## Aufgabe 3.1: Trainingsbeispiele bauen

Schreibe die Funktion `baue_beispiele(ids, kontext)`:

- **Eingabe:** eine Liste von IDs und die Länge des Kontexts
- **Rückgabe:** zwei Tensoren `X` und `Y`
  - `X` hat eine Zeile pro Beispiel mit `kontext` IDs, Form `(N, kontext)`
  - `Y` enthält für jedes Beispiel die ID, die danach kommt, Form `(N,)`

Beispiel: `baue_beispiele([5, 6, 7, 8, 9], 3)` liefert `X = [[5, 6, 7], [6, 7, 8]]` und `Y = [8, 9]`.

So gehst du vor:
1. Zwei leere Listen anlegen
2. Für jede Position `i` von `0` bis `len(ids) - kontext`: das Stück `ids[i:i + kontext]` an die eine Liste hängen, die ID `ids[i + kontext]` an die andere
3. Beide Listen mit `torch.tensor(...)` in Tensoren umwandeln

Zwei Werte gibst du in Python mit `return a, b` zurück. Abholen kannst du sie mit `X, Y = baue_beispiele(...)`.
""")
,
aufgabe(
vorlage=r"""
def baue_beispiele(ids, kontext):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 3.1: Hier fehlt noch dein Code")
""",
loesung=r"""
def baue_beispiele(ids, kontext):
    eingaben = []
    ziele = []
    for i in range(len(ids) - kontext):
        eingaben.append(ids[i:i + kontext])
        ziele.append(ids[i + kontext])
    return torch.tensor(eingaben), torch.tensor(ziele)
""")
,
code(r"""
nb3.pruefe_aufgabe_1(baue_beispiele)
""")
,
tipps(
    hinweis=r"""
    Das Muster kennst du von `zaehle_bigramme`: Eine Schleife über alle Positionen, an denen nach dem Kontext noch ein Zeichen kommt.
    An Position `i` ist das Stück `ids[i:i + kontext]` die Eingabe und `ids[i + kontext]` das Ziel.

    Wie weit läuft die Schleife? Bei `[5, 6, 7, 8, 9]` und `kontext = 3` gibt es nur zwei Beispiele, an den Positionen 0 und 1.
    """,
    fast=r"""
    ```python
    eingaben = []
    ziele = []
    for i in range(len(ids) - kontext):
        eingaben.append(...)
        ziele.append(...)
    return torch.tensor(eingaben), torch.tensor(ziele)
    ```
    """,
    loesung=r"""
    ```python
    def baue_beispiele(ids, kontext):
        eingaben = []
        ziele = []
        for i in range(len(ids) - kontext):
            eingaben.append(ids[i:i + kontext])
            ziele.append(ids[i + kontext])
        return torch.tensor(eingaben), torch.tensor(ziele)
    ```
    Für `[5, 6, 7, 8, 9]` und `kontext = 3`:

    - `len(ids) - kontext` ist 2, die Schleife läuft also für `i = 0` und `i = 1`.
    - Bei `i = 0` kommt `[5, 6, 7]` in die Eingaben und `8` in die Ziele. Bei `i = 1` sind es `[6, 7, 8]` und `9`.
    - `torch.tensor(eingaben)` macht aus der Liste von Listen eine Tabelle mit Form `(2, 3)`, `torch.tensor(ziele)` eine Liste mit Form `(2,)`.
    """,
)
,
md(r"""
Damit bauen wir die Beispiele für Training und Test. So sehen die ersten aus:
""")
,
code(r"""
X_training, Y_training = baue_beispiele(ids_training, 3)
X_test, Y_test = baue_beispiele(ids_test, 3)

print("X_training:", X_training.shape, "  Y_training:", Y_training.shape)
grafik3.kontext_tabelle(X_training, Y_training, vocabulary)
""")
,

# =============================================================
# TEIL 3: EINBETTUNGEN
# =============================================================

md(r"""
---
# Teil 3: Jedes Zeichen bekommt einen Platz auf einer Karte

Auf einer Landkarte hat jede Stadt zwei Koordinaten. Städte, die nah beieinander liegen, haben ähnliche Koordinaten.
Genau so geben wir jedem Zeichen **Koordinaten**. Für den Anfang zwei Stück, damit wir die Karte später zeichnen können.

Alle Koordinaten stehen in einer Tabelle `C` mit einer Zeile pro Zeichen. Am Anfang sind es Zufallszahlen.
Beim Training verschiebt das Netz die Zeichen auf der Karte, bis die Vorhersagen gut sind.
""")
,
code(r"""
torch.manual_seed(1)
C = torch.randn((V, 2))       # V Zeilen, 2 Spalten, Zufallszahlen um 0 herum

print("Form von C:", C.shape)
print("Koordinaten von 'a':", C[vocabulary.zeichen_zu_id["a"]])

grafik3.zeichen_karte(C, vocabulary.zeichen, "Die Karte am Anfang: Zufall")
""")
,
md(r"""
Vokale sind orange, Konsonanten blau. Im Moment liegen sie wild durcheinander. Merk dir das Bild für später.

Fachleute nennen diese Koordinaten **Einbettung** (englisch *embedding*): Jedes Zeichen wird in eine Karte "eingebettet".

### Koordinaten nachschlagen

Mit `C[ids]` schlägst du die Koordinaten vieler Zeichen auf einmal nach. Das ist übrigens genau das,
was `one_hot(ids) @ C` aus Notebook 2 macht, nur schneller.

Für unsere Beispiele brauchen wir noch einen Trick. `X[:, 0]` ist die **Spalte 0** von `X`,
also das erste Zeichen jedes Beispiels. Der Doppelpunkt heißt "alle Zeilen".
""")
,
code(r"""
X_klein = X_training[:4]
print("Vier Beispiele:\n", X_klein)
print("Spalte 0, das erste Zeichen jedes Beispiels:", X_klein[:, 0])
print("Koordinaten dieser Zeichen:\n", C[X_klein[:, 0]])
""")
,
md(r"""
Das Netz soll aber alle drei Zeichen sehen. Wir hängen ihre Koordinaten deshalb **nebeneinander**:
Aus 3 Zeichen mit je 2 Koordinaten werden 6 Zahlen pro Beispiel.

Zum Nebeneinanderhängen gibt es `torch.cat` (von *concatenate*, aneinanderhängen):
""")
,
code(r"""
a = torch.tensor([[1, 2], [3, 4]])
b = torch.tensor([[9, 9], [8, 8]])
print(torch.cat([a, b], dim=1))     # dim=1: nach rechts anhängen
""")
,
md(r"""
---
## Aufgabe 3.2: Zeichen in Koordinaten übersetzen

Schreibe die Funktion `einbetten(C, X)`:

- **Eingabe:** die Koordinaten-Tabelle `C` (Form `(V, koordinaten)`) und die Beispiele `X` (Form `(N, kontext)`)
- **Rückgabe:** eine Tabelle mit allen Koordinaten jedes Beispiels nebeneinander, Form `(N, kontext * koordinaten)`

So gehst du vor:
1. Für jede Spalte `i` von `X` die Koordinaten `C[X[:, i]]` nachschlagen und in einer Liste sammeln.
   Die Anzahl der Spalten ist `X.shape[1]`.
2. Die Liste mit `torch.cat(liste, dim=1)` nebeneinanderhängen
""")
,
aufgabe(
vorlage=r"""
def einbetten(C, X):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 3.2: Hier fehlt noch dein Code")
""",
loesung=r"""
def einbetten(C, X):
    teile = []
    for i in range(X.shape[1]):
        teile.append(C[X[:, i]])
    return torch.cat(teile, dim=1)
""")
,
code(r"""
nb3.pruefe_aufgabe_2(einbetten)
""")
,
tipps(
    hinweis=r"""
    `X[:, i]` ist die Spalte `i` von `X`, also das i-te Zeichen jedes Beispiels.
    `C[X[:, i]]` schlägt für alle diese Zeichen gleichzeitig die Koordinaten nach. Heraus kommt eine Tabelle mit Form `(N, koordinaten)`.

    Das machst du für jede Spalte und hängst die Teile am Ende **nebeneinander**: `torch.cat(liste, dim=1)`.
    Die Anzahl der Spalten ist `X.shape[1]`.
    """,
    fast=r"""
    ```python
    teile = []
    for i in range(X.shape[1]):
        teile.append(C[...])
    return torch.cat(teile, dim=...)
    ```
    """,
    loesung=r"""
    ```python
    def einbetten(C, X):
        teile = []
        for i in range(X.shape[1]):
            teile.append(C[X[:, i]])
        return torch.cat(teile, dim=1)
    ```
    Mit 3 Zeichen Kontext und 2 Koordinaten pro Zeichen:

    - Die Schleife läuft dreimal. Jedes Mal kommt eine Tabelle mit Form `(N, 2)` in die Liste: die Koordinaten des ersten, zweiten und dritten Zeichens.
    - `torch.cat(teile, dim=1)` hängt die drei Tabellen nebeneinander. Heraus kommt Form `(N, 6)`.
      Jede Zeile enthält jetzt alle Koordinaten eines Beispiels hintereinander.

    Mit `dim=0` würden die Tabellen untereinander gehängt. Das ergäbe Form `(3 * N, 2)` und wäre falsch.
    """,
)
,
code(r"""
print("Aus", X_klein.shape, "wird", einbetten(C, X_klein).shape)
""")
,

# =============================================================
# TEIL 4: DIE VERBORGENE SCHICHT
# =============================================================

md(r"""
---
# Teil 4: Die verborgene Schicht

Aus den 6 Zahlen pro Beispiel soll das Netz 35 Logits machen, eins für jedes Zeichen.
Das Bigramm-Netz hat dafür eine einzige Matrix verwendet. Jetzt bauen wir einen **Zwischenschritt** ein:

""")
,
code(r"""
grafik3.netz_bild(kontext=3, koordinaten=2, neuronen=100, V=V)
""")
,
md(r"""
Der Zwischenschritt heißt **verborgene Schicht** (englisch *hidden layer*), weil man ihn von außen nicht sieht.
Er besteht aus **Neuronen**. Jedes Neuron rechnet etwas ganz Einfaches:

1. Es nimmt die 6 Eingabezahlen, multipliziert jede mit einem eigenen Gewicht und zählt alles zusammen.
2. Es zählt noch eine eigene Zahl $b$ dazu, die **Verschiebung** (englisch *bias*).

Für 100 Neuronen auf einmal ist das genau eine Matrixmultiplikation plus $b$: `x @ W1 + b1`.
`W1` hat die Form `(6, 100)`, eine Spalte pro Neuron. `b1` hat 100 Zahlen.

### Warum noch ein Schritt dazwischen?

Hinter die Neuronen kommt eine zweite Matrix: `h @ W2 + b2` macht aus den 100 Neuronen die 35 Logits.
Aber Achtung: Zwei Matrixmultiplikationen hintereinander sind wieder nur **eine** Matrixmultiplikation.
Das Netz würde damit nichts dazugewinnen. Probier es aus:
""")
,
code(r"""
x = torch.randn((1, 6))
A = torch.randn((6, 100))
B = torch.randn((100, 35))

zwei_schritte = (x @ A) @ B
ein_schritt = x @ (A @ B)          # A @ B ist wieder nur eine Matrix

print("Gleiches Ergebnis:", torch.allclose(zwei_schritte, ein_schritt, atol=1e-4))
""")
,
md(r"""
Deshalb kommt zwischen die beiden Schritte eine **Knickstelle**. Die einfachste heißt **ReLU** und macht nur eins:

> **Negative Zahlen werden 0. Alles andere bleibt, wie es ist.**

Man kann sich das wie einen Schalter vorstellen: Ein Neuron mit negativem Wert ist **aus**, eines mit positivem Wert ist **an**.
Für jedes Beispiel ist eine andere Gruppe von Neuronen an. Ein Neuron könnte zum Beispiel lernen,
nur bei Kontexten anzugehen, die mit einem Vokal enden. Durch dieses An und Aus kann das Netz viel mehr als eine einzelne Matrix.

---
## Aufgabe 3.3: ReLU

Schreibe die Funktion `relu(x)`, die in einem Tensor alle negativen Zahlen durch 0 ersetzt.

PyTorch hat dafür eine passende Funktion: `torch.clamp(x, min=0)` begrenzt alle Werte nach unten auf 0.
("clamp" heißt "festklemmen".)
""")
,
aufgabe(
vorlage=r"""
def relu(x):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 3.3: Hier fehlt noch dein Code")
""",
loesung=r"""
def relu(x):
    return torch.clamp(x, min=0)
""")
,
code(r"""
nb3.pruefe_aufgabe_3(relu)
grafik3.relu_kurve(relu)
""")
,
tipps(
    hinweis=r"""
    Du musst nichts selbst durchlaufen. `torch.clamp` arbeitet auf dem ganzen Tensor auf einmal und begrenzt alle Werte.
    Überleg dir, welche Grenze du brauchst: nach unten oder nach oben, und bei welcher Zahl?
    """,
    fast=r"""
    ```python
    return torch.clamp(x, min=...)
    ```
    """,
    loesung=r"""
    ```python
    def relu(x):
        return torch.clamp(x, min=0)
    ```
    `torch.clamp(x, min=0)` lässt jede Zahl ab 0 unverändert und setzt alles darunter auf genau 0.
    Aus `[-2, 0.5, 3]` wird `[0, 0.5, 3]`.

    Das ist alles, was ReLU tut. Erst durch diesen Knick kann das Netz mehr als nur gerade Linien lernen.
    """,
)
,

# =============================================================
# TEIL 5: DAS NETZ VON HAND
# =============================================================

md(r"""
---
# Teil 5: Das Netz von Hand

Jetzt setzen wir alles zusammen, so wie beim `BigrammNetz` in Notebook 2. Das Netz hat fünf Gewichts-Tabellen:

| Gewicht | Form | Aufgabe |
|---|---|---|
| `C` | `(V, koordinaten)` | die Karte der Zeichen |
| `W1`, `b1` | `(kontext * koordinaten, neuronen)` und `(neuronen,)` | die verborgene Schicht |
| `W2`, `b2` | `(neuronen, V)` und `(V,)` | von den Neuronen zu den Logits |

Der Konstruktor ist schon fertig. Er füllt die Gewichte mit kleinen Zufallszahlen.
Warum nicht mit Nullen wie in Notebook 2? Wenn alle Neuronen gleich anfangen, lernen sie alle dasselbe.
Der Zufall sorgt dafür, dass jedes Neuron etwas anderes lernt.

---
## Aufgabe 3.4: Die Klasse `HandNetz`

Schreibe die drei Methoden:

| Methode | Was sie tut |
|---|---|
| `logits(self, X)` | 1. `x = einbetten(self.C, X)` <br> 2. `h = relu(x @ self.W1 + self.b1)` <br> 3. gibt `h @ self.W2 + self.b2` zurück |
| `gewichte(self)` | gibt die Liste `[self.C, self.W1, self.b1, self.W2, self.b2]` zurück |
| `trainingsschritt(self, X, Y, lernrate)` | wie beim `BigrammNetz`: Verlust mit `kreuzentropie(softmax(...), Y)` berechnen, `backward()`, `gradientenschritt(self.gewichte(), lernrate)`, Verlust mit `.item()` zurückgeben |
""")
,
aufgabe(
vorlage=r"""
class HandNetz:
    def __init__(self, V, kontext, koordinaten, neuronen):
        self.kontext = kontext
        self.C = torch.randn((V, koordinaten), requires_grad=True)
        self.W1 = torch.randn((kontext * koordinaten, neuronen)) * 0.3
        self.W1.requires_grad = True
        self.b1 = torch.zeros(neuronen, requires_grad=True)
        self.W2 = torch.randn((neuronen, V)) * 0.1
        self.W2.requires_grad = True
        self.b2 = torch.zeros(V, requires_grad=True)

    def logits(self, X):
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 3.4: Hier fehlt noch dein Code")

    def gewichte(self):
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 3.4: Hier fehlt noch dein Code")

    def trainingsschritt(self, X, Y, lernrate):
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 3.4: Hier fehlt noch dein Code")
""",
loesung=r"""
class HandNetz:
    def __init__(self, V, kontext, koordinaten, neuronen):
        self.kontext = kontext
        self.C = torch.randn((V, koordinaten), requires_grad=True)
        self.W1 = torch.randn((kontext * koordinaten, neuronen)) * 0.3
        self.W1.requires_grad = True
        self.b1 = torch.zeros(neuronen, requires_grad=True)
        self.W2 = torch.randn((neuronen, V)) * 0.1
        self.W2.requires_grad = True
        self.b2 = torch.zeros(V, requires_grad=True)

    def logits(self, X):
        x = einbetten(self.C, X)
        h = relu(x @ self.W1 + self.b1)
        return h @ self.W2 + self.b2

    def gewichte(self):
        return [self.C, self.W1, self.b1, self.W2, self.b2]

    def trainingsschritt(self, X, Y, lernrate):
        verlust = kreuzentropie(softmax(self.logits(X)), Y)
        verlust.backward()
        gradientenschritt(self.gewichte(), lernrate)
        return verlust.item()
""")
,
code(r"""
nb3.pruefe_aufgabe_4(HandNetz)
""")
,
tipps(
    hinweis=r"""
    Alles Nötige steht in der Tabelle der Aufgabe:

    - **logits:** drei Zeilen. Erst die Koordinaten holen, dann die erste Schicht mit ReLU, dann die zweite Schicht.
    - **gewichte:** eine Liste mit allen fünf Gewichts-Tensoren aus dem Konstruktor.
    - **trainingsschritt:** wie beim `BigrammNetz` in Notebook 2. Der Unterschied: Statt `self.vorhersage(ids)` rechnest du
      `softmax(self.logits(X))`, und an `gradientenschritt` gibst du alle Gewichte.
    """,
    fast=r"""
    ```python
    def logits(self, X):
        x = einbetten(self.C, X)
        h = relu(x @ self.W1 + ...)
        return h @ ... + self.b2

    def gewichte(self):
        return [self.C, ...]

    def trainingsschritt(self, X, Y, lernrate):
        verlust = kreuzentropie(softmax(...), Y)
        verlust.backward()
        gradientenschritt(..., lernrate)
        return verlust.item()
    ```
    """,
    loesung=r"""
    ```python
    def logits(self, X):
        x = einbetten(self.C, X)
        h = relu(x @ self.W1 + self.b1)
        return h @ self.W2 + self.b2

    def gewichte(self):
        return [self.C, self.W1, self.b1, self.W2, self.b2]

    def trainingsschritt(self, X, Y, lernrate):
        verlust = kreuzentropie(softmax(self.logits(X)), Y)
        verlust.backward()
        gradientenschritt(self.gewichte(), lernrate)
        return verlust.item()
    ```
    - **logits:** `x` sind die Koordinaten aller Kontext-Zeichen nebeneinander. `x @ self.W1 + self.b1` ist die erste Schicht,
      `relu` setzt die negativen Werte auf 0. Die zweite Schicht macht aus den Neuronen eine Zahl pro Zeichen im Vokabular.
    - **gewichte:** Auch die Koordinaten-Tabelle `self.C` gehört dazu. Sie wird genauso gelernt wie die anderen Gewichte.
    - **trainingsschritt:** Softmax, Verlust, `backward()`, Schritt bergab. `self.gewichte()` mit Klammern ruft die Methode auf und liefert die Liste.
    """,
)
,
md(r"""
### Das Training

Wie in Notebook 2 trainieren wir mit **allen** Trainingsbeispielen auf einmal. Die gestrichelte Linie ist das Bigramm-Netz
aus Notebook 2 auf dem Testtext. Das Netz sieht jetzt drei Zeichen, es sollte also besser werden.

Die orange Linie ist der Verlust auf dem **Testtext**, den das Netz beim Lernen nie sieht.
""")
,
code(r"""
torch.manual_seed(1)
hand_netz = HandNetz(V, kontext=3, koordinaten=2, neuronen=100)

kurve = grafik2.LiveKurve(titel="Das HandNetz lernt", ziel=2.28, ziel_text="Bigramm-Netz")
start = time.time()

for schritt in range(501):
    verlust = hand_netz.trainingsschritt(X_training, Y_training, lernrate=1.0)
    if schritt % 25 == 0:
        with torch.no_grad():
            verlust_test = kreuzentropie(softmax(hand_netz.logits(X_test)), Y_test).item()
        kurve.punkt(schritt, verlust, verlust_test)

print(f"Dauer: {time.time() - start:.1f} Sekunden")
""")
,
md(r"""
Das Netz ist schon nach wenigen hundert Schritten besser als das Bigramm-Netz. Drei Zeichen Kontext helfen.

`with torch.no_grad():` kennst du aus Notebook 2. Beim Testen soll PyTorch nicht mitrechnen,
denn aus dem Testtext wird nicht gelernt.
""")
,

# =============================================================
# TEIL 6: PYTORCH-BAUSTEINE
# =============================================================

md(r"""
---
# Teil 6: Dasselbe mit den Bausteinen von PyTorch

Du hast jetzt ein komplettes Netz selbst gebaut. Bei größeren Netzen wird das schnell unübersichtlich.
Deshalb bringt PyTorch fertige Bausteine mit. Das Gute: Du kennst sie alle schon, denn du hast sie gerade selbst gebaut.

### `nn.Linear`: eine Schicht

`nn.Linear(6, 100)` ist ein Paket aus Gewichten und Verschiebung. Aufgerufen rechnet es `x @ W + b`:
""")
,
code(r"""
schicht = nn.Linear(6, 100)

x = torch.randn((4, 6))
print("Aus", x.shape, "wird", schicht(x).shape)
print("Die Verschiebung b hat", schicht.bias.shape[0], "Zahlen")
""")
,
md(r"""
### `nn.Embedding`: die Karte der Zeichen

`nn.Embedding(V, 2)` ist eine Tabelle mit `V` Zeilen und 2 Spalten, gefüllt mit Zufallszahlen.
Die Tabelle selbst steckt in `.weight`. Das ist dein `C`.
""")
,
code(r"""
karte = nn.Embedding(V, 2)
print("Form der Tabelle:", karte.weight.shape)
print("Mit einbetten:", einbetten(karte.weight, X_klein).shape)
""")
,
md(r"""
### `nn.Module`: ein ganzes Netz

Ein Netz in PyTorch ist eine Klasse, die von `nn.Module` erbt. Das kennst du aus C#: `class ZeichenNetz : Module`.
Die Klasse hat zwei Teile:

- `__init__` legt die Bausteine an. Ganz am Anfang steht immer `super().__init__()`, das ruft den Konstruktor der Basisklasse auf (wie `: base()` in C#).
- `forward(self, X)` beschreibt die Rechnung von der Eingabe bis zu den Logits.

Danach rufst du das Netz einfach wie eine Funktion auf: `netz(X)`. PyTorch ruft dann `forward` für dich auf.
Und `netz.parameters()` findet automatisch alle Gewichte in allen Bausteinen. Die Liste in `gewichte()` brauchst du nicht mehr.

### `F.cross_entropy`: Softmax und Verlust in einem

`F.cross_entropy(logits, Y)` macht genau dasselbe wie `kreuzentropie(softmax(logits), Y)`. Überzeug dich selbst:
""")
,
code(r"""
logits = hand_netz.logits(X_klein)
ziele = Y_training[:4]

print("Deine Funktionen:", kreuzentropie(softmax(logits), ziele).item())
print("F.cross_entropy: ", F.cross_entropy(logits, ziele).item())
""")
,
md(r"""
### `torch.optim.SGD`: dein `gradientenschritt`

Der **Optimierer** übernimmt den Lernschritt. Man gibt ihm die Gewichte und die Lernrate:

```python
optimierer = torch.optim.SGD(netz.parameters(), lr=0.1)
```

| Mit dem Optimierer | Was du in Notebook 2 selbst geschrieben hast |
|---|---|
| `optimierer.zero_grad()` | `gewicht.grad.zero_()` für alle Gewichte |
| `optimierer.step()` | `gewicht -= lernrate * gewicht.grad` für alle Gewichte |

SGD steht für *Stochastic Gradient Descent*, also Gradientenabstieg. Was "stochastic" (zufällig) bedeutet, siehst du in Teil 7.

---
## Aufgabe 3.5: Die Klasse `ZeichenNetz`

Baue das Netz noch einmal, diesmal mit den PyTorch-Bausteinen:

**`__init__`** legt drei Bausteine an:

| Attribut | Baustein |
|---|---|
| `self.einbettung` | `nn.Embedding(V, koordinaten)` |
| `self.schicht1` | `nn.Linear(kontext * koordinaten, neuronen)` |
| `self.schicht2` | `nn.Linear(neuronen, V)` |

**`forward(self, X)`** rechnet:
1. `x = einbetten(self.einbettung.weight, X)`
2. `h = relu(self.schicht1(x))`
3. gibt `self.schicht2(h)` zurück
""")
,
aufgabe(
vorlage=r"""
class ZeichenNetz(nn.Module):
    def __init__(self, V, kontext, koordinaten, neuronen):
        super().__init__()
        self.kontext = kontext
        # DEIN CODE HIER: self.einbettung, self.schicht1, self.schicht2
        raise NotImplementedError("Aufgabe 3.5: Hier fehlt noch dein Code")

    def forward(self, X):
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 3.5: Hier fehlt noch dein Code")
""",
loesung=r"""
class ZeichenNetz(nn.Module):
    def __init__(self, V, kontext, koordinaten, neuronen):
        super().__init__()
        self.kontext = kontext
        self.einbettung = nn.Embedding(V, koordinaten)
        self.schicht1 = nn.Linear(kontext * koordinaten, neuronen)
        self.schicht2 = nn.Linear(neuronen, V)

    def forward(self, X):
        x = einbetten(self.einbettung.weight, X)
        h = relu(self.schicht1(x))
        return self.schicht2(h)
""")
,
code(r"""
nb3.pruefe_aufgabe_5(ZeichenNetz)
""")
,
tipps(
    hinweis=r"""
    - **__init__:** drei Zeilen, eine pro Zeile der Tabelle. Jeder Baustein bekommt die Größen, die in der Tabelle stehen.
      Die Bausteine legen ihre Gewichte selbst an, du musst dich um `requires_grad` nicht kümmern.
    - **forward:** Das ist dieselbe Rechnung wie `HandNetz.logits`. Die Koordinaten-Tabelle steckt jetzt in `self.einbettung.weight`.
      Statt `x @ self.W1 + self.b1` schreibst du einfach `self.schicht1(x)`.
    """,
    fast=r"""
    ```python
    def __init__(self, V, kontext, koordinaten, neuronen):
        super().__init__()
        self.kontext = kontext
        self.einbettung = nn.Embedding(V, ...)
        self.schicht1 = nn.Linear(..., neuronen)
        self.schicht2 = nn.Linear(neuronen, ...)

    def forward(self, X):
        x = einbetten(self.einbettung.weight, X)
        h = relu(...)
        return ...
    ```
    """,
    loesung=r"""
    ```python
    class ZeichenNetz(nn.Module):
        def __init__(self, V, kontext, koordinaten, neuronen):
            super().__init__()
            self.kontext = kontext
            self.einbettung = nn.Embedding(V, koordinaten)
            self.schicht1 = nn.Linear(kontext * koordinaten, neuronen)
            self.schicht2 = nn.Linear(neuronen, V)

        def forward(self, X):
            x = einbetten(self.einbettung.weight, X)
            h = relu(self.schicht1(x))
            return self.schicht2(h)
    ```
    - `nn.Embedding(V, koordinaten)` ist die Koordinaten-Tabelle `C` aus dem `HandNetz`: eine Zeile pro Zeichen.
    - `nn.Linear(kontext * koordinaten, neuronen)` ersetzt `W1` und `b1`. Die Eingabe hat `kontext * koordinaten` Zahlen,
      weil `einbetten` die Koordinaten aller Kontext-Zeichen nebeneinanderhängt.
    - `nn.Linear(neuronen, V)` ersetzt `W2` und `b2` und liefert eine Zahl pro Zeichen im Vokabular.
    - `forward` rechnet genau wie `HandNetz.logits`. Weil alle Bausteine Attribute von `self` sind, findet `netz.parameters()` ihre Gewichte automatisch.
    """,
)
,
md(r"""
Wie viele Gewichte hat das Netz? `netz.parameters()` liefert alle Gewichts-Tabellen, `.numel()` zählt die Zahlen in einer Tabelle:
""")
,
code(r"""
netz = ZeichenNetz(V, kontext=3, koordinaten=2, neuronen=100)
print("Anzahl Gewichte:", sum(p.numel() for p in netz.parameters()))
""")
,

# =============================================================
# TEIL 7: MINIBATCHES
# =============================================================

md(r"""
---
# Teil 7: Schneller lernen mit Minibatches

Bisher hat das Netz für **jeden** Lernschritt alle 9.600 Trainingsbeispiele durchgerechnet.
Bei unserem kleinen Text geht das noch. In Notebook 7 trainierst du mit fast 500.000 Zeichen, und echte Sprachmodelle lernen aus Milliarden.

Die Lösung kennst du von Umfragen: Um zu wissen, was ein ganzes Land denkt, fragt man nicht alle, sondern **eine zufällige Stichprobe**.
Das Ergebnis ist nicht ganz genau, aber gut genug, um die Richtung zu kennen.

Beim Training heißt die Stichprobe **Minibatch**. Für jeden Lernschritt ziehen wir 32 zufällige Beispiele.
Jeder Schritt ist dadurch etwas ungenauer, aber viel schneller. In derselben Zeit schafft das Netz deshalb viel mehr Schritte.
Daher kommt das "stochastic" in SGD.

---
## Aufgabe 3.6: Einen Minibatch ziehen

Schreibe die Funktion `ziehe_minibatch(X, Y, groesse)`:

1. Ziehe `groesse` zufällige Positionen: `auswahl = torch.randint(0, len(X), (groesse,))`
2. Gib `X[auswahl]` und `Y[auswahl]` zurück

Wichtig ist, dass du für `X` und `Y` **dieselbe** Auswahl nimmst. Sonst passen Eingaben und Ziele nicht mehr zusammen.
""")
,
aufgabe(
vorlage=r"""
def ziehe_minibatch(X, Y, groesse):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 3.6: Hier fehlt noch dein Code")
""",
loesung=r"""
def ziehe_minibatch(X, Y, groesse):
    auswahl = torch.randint(0, len(X), (groesse,))
    return X[auswahl], Y[auswahl]
""")
,
code(r"""
nb3.pruefe_aufgabe_6(ziehe_minibatch)
""")
,
tipps(
    hinweis=r"""
    `torch.randint(von, bis, form)` zieht zufällige ganze Zahlen von `von` bis ausschließlich `bis`.
    Die Form ist ein Tupel. Für eine Liste mit `groesse` Zahlen schreibst du `(groesse,)`. Das Komma macht daraus ein Tupel.

    Mit einer Liste von Positionen kannst du mehrere Zeilen auf einmal holen: `X[auswahl]`.
    Nimm für `X` und `Y` dieselbe Auswahl.
    """,
    fast=r"""
    ```python
    auswahl = torch.randint(0, ..., (groesse,))
    return X[...], Y[...]
    ```
    """,
    loesung=r"""
    ```python
    def ziehe_minibatch(X, Y, groesse):
        auswahl = torch.randint(0, len(X), (groesse,))
        return X[auswahl], Y[auswahl]
    ```
    - `torch.randint(0, len(X), (groesse,))` zieht `groesse` zufällige Zeilennummern zwischen 0 und `len(X) - 1`.
    - `X[auswahl]` holt genau diese Zeilen aus `X`, `Y[auswahl]` die passenden Ziele.
      Weil beide dieselbe `auswahl` verwenden, gehört das Ziel in Zeile 0 des Minibatches zur Eingabe in Zeile 0.
    """,
)
,
md(r"""
---
## Aufgabe 3.7: Die Trainingsschleife

Schreibe die Funktion `trainiere(netz, X, Y, schritte, lernrate, groesse=32)`.
Sie trainiert ein `nn.Module` und gibt eine Liste mit dem Verlust jedes Schritts zurück.

1. Einen Optimierer anlegen: `optimierer = torch.optim.SGD(netz.parameters(), lr=lernrate)`
2. Eine leere Liste `verluste` anlegen
3. `schritte`-mal:
   - einen Minibatch `Xb, Yb` ziehen
   - `verlust = F.cross_entropy(netz(Xb), Yb)`
   - `optimierer.zero_grad()`, dann `verlust.backward()`, dann `optimierer.step()`
   - `verlust.item()` an die Liste hängen
4. Die Liste zurückgeben

`groesse=32` ist ein **Standardwert**: Wer `trainiere` ohne `groesse` aufruft, bekommt 32. Das gibt es in C# genauso.
""")
,
aufgabe(
vorlage=r"""
def trainiere(netz, X, Y, schritte, lernrate, groesse=32):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 3.7: Hier fehlt noch dein Code")
""",
loesung=r"""
def trainiere(netz, X, Y, schritte, lernrate, groesse=32):
    optimierer = torch.optim.SGD(netz.parameters(), lr=lernrate)
    verluste = []
    for _ in range(schritte):
        Xb, Yb = ziehe_minibatch(X, Y, groesse)
        verlust = F.cross_entropy(netz(Xb), Yb)
        optimierer.zero_grad()
        verlust.backward()
        optimierer.step()
        verluste.append(verlust.item())
    return verluste
""")
,
code(r"""
nb3.pruefe_aufgabe_7(trainiere)
""")
,
tipps(
    hinweis=r"""
    Die Schritte stehen in der Aufgabe. Achte vor allem auf die Reihenfolge in jedem Schritt:

    1. Minibatch ziehen
    2. Verlust berechnen
    3. alte Gradienten löschen, neue berechnen, einen Schritt machen
    4. den Verlust als Zahl in der Liste merken

    Der Optimierer übernimmt das, was bisher dein `gradientenschritt` gemacht hat.
    """,
    fast=r"""
    ```python
    optimierer = torch.optim.SGD(netz.parameters(), lr=lernrate)
    verluste = []
    for _ in range(schritte):
        Xb, Yb = ziehe_minibatch(X, Y, groesse)
        verlust = F.cross_entropy(netz(...), ...)
        optimierer.zero_grad()
        verlust.backward()
        optimierer.step()
        verluste.append(...)
    return verluste
    ```
    """,
    loesung=r"""
    ```python
    def trainiere(netz, X, Y, schritte, lernrate, groesse=32):
        optimierer = torch.optim.SGD(netz.parameters(), lr=lernrate)
        verluste = []
        for _ in range(schritte):
            Xb, Yb = ziehe_minibatch(X, Y, groesse)
            verlust = F.cross_entropy(netz(Xb), Yb)
            optimierer.zero_grad()
            verlust.backward()
            optimierer.step()
            verluste.append(verlust.item())
        return verluste
    ```
    - Der Optimierer bekommt einmal alle Gewichte des Netzes (`netz.parameters()`) und die Lernrate.
    - `netz(Xb)` ruft `forward` auf und liefert die Logits. `F.cross_entropy` macht daraus in einem Schritt Softmax und Verlust.
    - `optimierer.zero_grad()` löscht die alten Gradienten, `verlust.backward()` berechnet die neuen, `optimierer.step()` geht bergab.
      Das sind genau die Schritte, die dein `gradientenschritt` von Hand gemacht hat.
    - `verlust.item()` speichert den Verlust als normale Zahl. So kannst du später die Lernkurve zeichnen.
    """,
)
,
md(r"""
### Das Training

Wir rufen `trainiere` 20-mal mit je 500 Schritten auf und zeichnen nach jeder Runde den Verlust auf allen Trainings- und Testbeispielen.
Die kleine Hilfsfunktion `verlust_auf` rechnet ihn aus, ohne dass PyTorch mitrechnet.

Die gestrichelte Linie ist jetzt das HandNetz aus Teil 5.
""")
,
code(r"""
def verlust_auf(netz, X, Y):
    with torch.no_grad():
        return F.cross_entropy(netz(X), Y).item()


hand_netz_test = kreuzentropie(softmax(hand_netz.logits(X_test)), Y_test).item()

torch.manual_seed(1)
netz = ZeichenNetz(V, kontext=3, koordinaten=2, neuronen=100)
kurve = grafik2.LiveKurve(titel="ZeichenNetz mit Minibatches", ziel=hand_netz_test, ziel_text="HandNetz")
start = time.time()

for runde in range(21):
    if runde > 0:
        trainiere(netz, X_training, Y_training, schritte=500, lernrate=0.1)
    kurve.punkt(runde * 500, verlust_auf(netz, X_training, Y_training), verlust_auf(netz, X_test, Y_test))

print(f"Dauer: {time.time() - start:.1f} Sekunden")
""")
,
md(r"""
Das Netz macht 10.000 Schritte statt 500 und braucht dafür ungefähr gleich lang. Am Ende ist es etwas besser als das HandNetz.

Die Kurve wackelt dabei ein wenig. Das ist der Zufall der Minibatches: Jeder Schritt zeigt nur ungefähr in die richtige Richtung.
""")
,

# =============================================================
# TEIL 8: DIE KARTE DER ZEICHEN
# =============================================================

md(r"""
---
# Teil 8: Was hat das Netz gelernt?

Jetzt der spannendste Moment. Erinnerst du dich an die zufällige Karte aus Teil 3? So sieht sie nach dem Training aus:
""")
,
code(r"""
grafik3.zeichen_karte(netz.einbettung.weight, vocabulary.zeichen, "Die Karte nach dem Training")
""")
,
md(r"""
Schau genau hin:
- Wo liegen die Vokale (orange)? Liegen sie näher beieinander als vorher?
- Wo liegen Leerzeichen, Punkt und Zeilenumbruch?
- Gibt es Konsonanten, die nah beieinander liegen? Haben sie etwas gemeinsam?

Niemand hat dem Netz gesagt, was ein Vokal ist. Es hat nur gelernt, das nächste Zeichen vorherzusagen.
Dabei hat es von selbst herausgefunden, dass sich manche Zeichen **ähnlich verhalten**, und sie zusammengeschoben.
Jeder Lauf sieht etwas anders aus, weil das Netz mit anderen Zufallszahlen startet.

### Ein unbekannter Kontext

In Teil 1 haben wir Kontexte gesammelt, die im Training nie vorkommen. Was sagt das Zählmodell aus Notebook 1 dazu, was das Netz?
""")
,
code(r"""
kontext = unbekannt[0]
print(f"Kontext: {kontext!r}")

zaehl_modell = NGramModell(training, 3)
print("Das Zählmodell kennt danach:", zaehl_modell.zaehler.get(kontext, "nichts"))

with torch.no_grad():
    P = softmax(netz(torch.tensor([vocabulary.encode(kontext)])))
verteilung = {vocabulary.id_zu_zeichen[i]: p for i, p in enumerate(P[0].tolist())}
grafik3.top_vorhersagen(verteilung, f"Was das Netz nach {kontext!r} erwartet")
""")
,
md(r"""
Das Zählmodell ist ratlos, das Netz hat eine Vermutung. Ist sie sinnvoll? Probier auch `unbekannt[1]`, `unbekannt[2]` und so weiter.
**Problem 1 aus Notebook 1 ist gelöst**: Das Netz behandelt ähnliche Kontexte ähnlich.

### Mehr Koordinaten

Zwei Koordinaten sind praktisch zum Zeichnen, aber eng. Mit 10 Koordinaten hat das Netz viel mehr Platz,
um verschiedene Eigenschaften der Zeichen abzulegen. Zeichnen können wir eine 10-dimensionale Karte allerdings nicht mehr.
""")
,
code(r"""
torch.manual_seed(1)
netz10 = ZeichenNetz(V, kontext=3, koordinaten=10, neuronen=100)
kurve = grafik2.LiveKurve(titel="ZeichenNetz mit 10 Koordinaten", ziel=verlust_auf(netz, X_test, Y_test), ziel_text="2 Koordinaten")

for runde in range(21):
    if runde > 0:
        trainiere(netz10, X_training, Y_training, schritte=500, lernrate=0.1)
    kurve.punkt(runde * 500, verlust_auf(netz10, X_training, Y_training), verlust_auf(netz10, X_test, Y_test))
""")
,
md(r"""
Noch einmal ein deutlicher Sprung nach unten.

Aber schau dir die beiden Linien an: Die blaue (Training) liegt jetzt klar **unter** der orangen (Test).
Das Netz ist auf Texten, die es kennt, besser als auf neuen. Was passiert, wenn wir das Netz noch viel größer machen?
""")
,

# =============================================================
# TEIL 9: OVERFITTING
# =============================================================

md(r"""
---
# Teil 9: Größer ist nicht immer besser

Wir bauen ein riesiges Netz: 8 Zeichen Kontext, 20 Koordinaten und 1000 Neuronen.
""")
,
code(r"""
X8_training, Y8_training = baue_beispiele(ids_training, 8)
X8_test, Y8_test = baue_beispiele(ids_test, 8)

torch.manual_seed(1)
riesen_netz = ZeichenNetz(V, kontext=8, koordinaten=20, neuronen=1000)
print("Anzahl Gewichte:", sum(p.numel() for p in riesen_netz.parameters()))

kurve = grafik2.LiveKurve(titel="Ein riesiges Netz", ziel=verlust_auf(netz10, X_test, Y_test), ziel_text="netz10 auf dem Test")
for runde in range(21):
    if runde > 0:
        trainiere(riesen_netz, X8_training, Y8_training, schritte=500, lernrate=0.2)
    kurve.punkt(runde * 500, verlust_auf(riesen_netz, X8_training, Y8_training), verlust_auf(riesen_netz, X8_test, Y8_test))
""")
,
md(r"""
Der Trainingsverlust stürzt ab, bis auf etwa 0,2. Aber der Testverlust wird nach kurzer Zeit **wieder schlechter**
und landet am Ende sogar über dem viel kleineren `netz10`.

Das Netz hat fast 200.000 Gewichte, aber nur knapp 10.000 Trainingsbeispiele. Es hat genug Platz, um sich den
Trainingstext einfach **auswendig zu merken**. Das kennst du vielleicht aus der Schule: Wer die Antworten der Probeprüfung
auswendig lernt, ist bei der Probeprüfung perfekt und bei der echten Prüfung schlecht.

Das heißt **Overfitting** (Überanpassung). Du kennst das Wort schon aus Notebook 1, dort beim Zählmodell mit großem n.

Was hilft dagegen?
- **Mehr Daten.** Je mehr Text, desto schwerer ist es, alles auswendig zu lernen. Das machen wir in Notebook 7.
- **Ein passend großes Netz.** Größer ist nur besser, wenn genug Daten da sind.
- **Rechtzeitig aufhören**, wenn der Testverlust nicht mehr sinkt.
- Ein Trick namens **Dropout**, den du in Notebook 6 kennenlernst.

**Denkfrage:** Woran erkennst du Overfitting in der Kurve, ohne den Text anzuschauen?
""")
,

# =============================================================
# TEIL 10: TEXT GENERIEREN
# =============================================================

md(r"""
---
# Teil 10: Das Netz schreibt

Zum Schluss soll das Netz Text erzeugen. Das funktioniert wie in Notebook 2, mit zwei Unterschieden:
- Das Netz bekommt die **letzten `netz.kontext` Zeichen** statt nur des letzten.
- Das Netz liefert **Logits**. Daraus macht deine `softmax` Wahrscheinlichkeiten.

---
## Aufgabe 3.8: Text generieren mit mehr Kontext

**`naechste_verteilung(netz, vocabulary, text)`**
1. Die letzten Zeichen holen: `text[-netz.kontext:]`, und mit `vocabulary.encode` in IDs umwandeln
2. Daraus eine Tabelle mit **einem** Beispiel machen: `torch.tensor([ids])`. Die eckigen Klammern sind wichtig, das Netz erwartet eine Tabelle.
3. Das Netz aufrufen und `softmax` anwenden. Am besten in `with torch.no_grad():`, denn hier wird nicht gelernt.
4. Wie in Notebook 2: Zeile `[0]` nehmen, `.tolist()`, und ein Dictionary `{zeichen: wahrscheinlichkeit}` zurückgeben

**`generiere(netz, vocabulary, start, laenge)`** funktioniert genau wie in Notebook 2.
Der Starttext muss mindestens `netz.kontext` Zeichen lang sein.
""")
,
aufgabe(
vorlage=r"""
def naechste_verteilung(netz, vocabulary, text):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 3.8: Hier fehlt noch dein Code")


def generiere(netz, vocabulary, start, laenge):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 3.8: Hier fehlt noch dein Code")
""",
loesung=r"""
def naechste_verteilung(netz, vocabulary, text):
    ids = vocabulary.encode(text[-netz.kontext:])
    with torch.no_grad():
        P = softmax(netz(torch.tensor([ids])))
    werte = P[0].tolist()
    return {vocabulary.id_zu_zeichen[i]: p for i, p in enumerate(werte)}


def generiere(netz, vocabulary, start, laenge):
    text = start
    for _ in range(laenge):
        text += ziehe_zeichen(naechste_verteilung(netz, vocabulary, text))
    return text
""")
,
code(r"""
nb3.pruefe_aufgabe_8(naechste_verteilung, generiere)
""")
,
tipps(
    hinweis=r"""
    **naechste_verteilung:** Der Unterschied zu Notebook 2: Das Netz sieht jetzt mehrere Zeichen.
    Du nimmst also die letzten `netz.kontext` Zeichen statt nur des letzten. Das Netz erwartet eine Tabelle,
    deshalb packst du die IDs in eine zusätzliche Liste: `torch.tensor([ids])` hat die Form `(1, kontext)`.
    Danach geht es weiter wie in Notebook 2: Softmax, Zeile `[0]`, `.tolist()`, Dictionary.

    **generiere** kannst du aus Notebook 2 übernehmen.
    """,
    fast=r"""
    ```python
    def naechste_verteilung(netz, vocabulary, text):
        ids = vocabulary.encode(text[-netz.kontext:])
        with torch.no_grad():
            P = softmax(netz(torch.tensor([...])))
        werte = P[0].tolist()
        return {vocabulary.id_zu_zeichen[i]: p for i, p in enumerate(...)}


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
            P = softmax(netz(torch.tensor([ids])))
        werte = P[0].tolist()
        return {vocabulary.id_zu_zeichen[i]: p for i, p in enumerate(werte)}


    def generiere(netz, vocabulary, start, laenge):
        text = start
        for _ in range(laenge):
            text += ziehe_zeichen(naechste_verteilung(netz, vocabulary, text))
        return text
    ```
    - `text[-netz.kontext:]` sind die letzten Zeichen, zum Beispiel `"hal"` bei Kontext 3. `encode` macht daraus IDs.
    - `torch.tensor([ids])` ist eine Tabelle mit **einem** Beispiel. Ohne die eckigen Klammern wäre es eine einfache Liste,
      und das Netz könnte sie nicht verarbeiten.
    - `with torch.no_grad():` spart Arbeit. Beim Erzeugen wird nicht gelernt, also braucht PyTorch sich nichts für `backward()` zu merken.
    - Der Rest ist wie in Notebook 2. Auch `generiere` ist unverändert. Es ruft nur deine neue `naechste_verteilung` auf.
    """,
)
,
code(r"""
print(generiere(netz10, vocabulary, "der", 400))
""")
,
md(r"""
Vergleich das mit dem Text des Bigramm-Netzes aus Notebook 2. Es gibt mehr echte Wörter und weniger Buchstabensalat.
Ganz ohne Fehler ist es noch nicht, denn drei Zeichen sind immer noch ein kurzes Gedächtnis.

Hier noch einmal Schritt für Schritt. Der blaue Kasten zeigt jetzt drei Zeichen Kontext:
""")
,
code(r"""
grafik.generierung_schritt_fuer_schritt(
    start="die",
    schritte=40,
    verteilung_fuer=lambda bisher: naechste_verteilung(netz10, vocabulary, bisher),
    ziehe_zeichen=ziehe_zeichen,
    kontext_laenge=netz10.kontext,
)
""")
,

# =============================================================
# TEIL 11: WAS DU JETZT ÜBER SPRACHMODELLE WEISST
# =============================================================

md(r"""
---
# Teil 11: Was du jetzt über Sprachmodelle weißt

Du hast in drei Notebooks ein kleines Sprachmodell selbst gebaut. ChatGPT und Co. sind viel größer und in vielen Details anders gebaut.
Die Grundidee ist aber dieselbe. Deshalb kannst du jetzt einiges erklären, was viele Leute an KI überrascht.

## Die Grundidee

Ein Sprachmodell kann genau eine Sache: Es schätzt für jedes mögliche nächste Stück Text, wie wahrscheinlich es ist.
Dann wird eines davon gezogen und angehängt, und alles beginnt von vorn. Das ist die Schleife in deinem `generiere`.

Große Modelle arbeiten mit Wortstücken statt mit einzelnen Zeichen und sehen viel mehr Text davor. An der Schleife ändert das nichts.
Auch eine lange Antwort von ChatGPT entsteht Stück für Stück, immer mit der Frage: Was kommt wahrscheinlich als Nächstes?

Probier es noch einmal aus. Dreimal derselbe Anfang:
""")
,
code(r"""
for versuch in range(3):
    print(f"Versuch {versuch + 1}:", generiere(netz10, vocabulary, "der hund ", 60).replace("\n", " "))
""")
,
md(r"""
## Fünf Grenzen, die du selbst gesehen hast

**1. Plausibel ist nicht dasselbe wie wahr.**
Dein Netz schreibt Wörter, die nach Deutsch aussehen, aber oft keinen Sinn ergeben. Das liegt nicht an einem Fehler.
Beim Training wurde nur belohnt, dass das tatsächlich folgende Zeichen eine hohe Wahrscheinlichkeit bekommt.
Ob ein Satz **stimmt**, hat das Netz nie geprüft. Es kann das auch gar nicht.

Große Modelle haben dasselbe Problem auf höherem Niveau. Ihre Antworten klingen fast immer überzeugend,
auch wenn eine Zahl, ein Name oder eine Quelle erfunden ist. Das nennt man **Halluzinieren**.

**2. Es weiß nur, was in den Trainingsdaten stand.**
In Notebook 1 bekam ein unbekannter Kontext die Wahrscheinlichkeit 0 und den Verlust unendlich.
Dein Netz verallgemeinert schon besser, aber ein Fragezeichen oder eine Ziffer kann es nie schreiben.
Sie kommen im Trainingstext nicht vor, deshalb fehlen sie im Vokabular.

Große Modelle kennen nichts, was nach dem Ende ihrer Trainingsdaten passiert ist, außer sie dürfen nebenbei im Internet suchen. Und sie kennen nichts, was nie öffentlich war,
zum Beispiel die Abläufe in deinem Betrieb. Was das Modell wissen soll, musst du ihm in der Frage mitgeben.

**3. Zufall gehört dazu.**
Dein `ziehe_zeichen` zieht zufällig. Deshalb kam oben dreimal ein anderer Text heraus.
Dieselbe Frage an ChatGPT kann deshalb verschiedene Antworten bringen. Eine Antwort ist keine feste "Meinung" des Modells, sondern eine Ziehung.

**4. Das Gedächtnis ist begrenzt.**
Dein Netz sieht drei Zeichen. Was davor stand, existiert für es nicht.
Große Modelle sehen sehr viel mehr Text, aber auch bei ihnen ist irgendwann Schluss. Das nennt man das **Kontextfenster**.
In sehr langen Gesprächen oder bei riesigen Dokumenten geht deshalb etwas verloren.

**5. Auswendiglernen ist nicht Verstehen.**
In Teil 9 hat das riesige Netz den Trainingstext fast auswendig gelernt. Auf neuem Text war es trotzdem schlecht.
Auch große Modelle können Texte, die oft in ihren Trainingsdaten vorkamen, fast wörtlich wiedergeben.
Dass ein Modell eine bekannte Aufgabe gut löst, sagt deshalb wenig darüber, wie gut es eine wirklich neue Aufgabe löst.

## Wo steckt das Wissen?

Dein Netz hat keine Datenbank, keine Regeln und keine Wörterliste. Alles, was es kann, steckt in seinen Gewichten, also in Zahlen:
""")
,
code(r"""
gewichte = sum(p.numel() for p in netz10.parameters())
print(f"Dein Netz:        {gewichte:>15,} Gewichte".replace(",", "."))
print(f"GPT-3 (2020):     {175_000_000_000:>15,} Gewichte".replace(",", "."))
""")
,
md(r"""
Bei großen Modellen ist es genauso, nur mit Milliarden Zahlen. Niemand hat ihnen Regeln einprogrammiert.
Was sie können, haben sie beim Training aus riesigen Textmengen gelernt, mit demselben Gradientenabstieg wie dein Netz.
Deshalb kann man auch nicht einfach nachschauen, **warum** ein Modell eine bestimmte Antwort gibt.

## Was das für die Arbeit mit KI bedeutet

- **Prüfe Fakten**, vor allem Zahlen, Namen und Quellen. Das Modell klingt auch dann sicher, wenn es falsch liegt.
- **Teste Code**, den eine KI schreibt. Er sieht oft richtig aus, weil er wahrscheinlichem Code ähnelt. Ob er läuft, zeigt erst der Test.
- **Gib das nötige Wissen mit.** Was nicht in den Trainingsdaten stand, muss in deiner Frage stehen.
- **Frag bei Wichtigem nach** oder stell die Frage anders. Weichen die Antworten stark voneinander ab, ist Vorsicht angebracht.
""")
,

# =============================================================
# ABSCHLUSS
# =============================================================

md(r"""
---
# Abschluss: Deinen Code speichern

Die nächste Zelle prüft alle Aufgaben noch einmal und speichert deinen Code in `meincode/notebook3.py`.
""")
,
code(r"""
nb3.speichern(
    baue_beispiele,
    einbetten,
    relu,
    HandNetz,
    ZeichenNetz,
    ziehe_minibatch,
    trainiere,
    naechste_verteilung,
    generiere,
)
""")
,
md(r"""
## Zusammenfassung

| Begriff | Bedeutung |
|---|---|
| **Kontext** | die letzten Zeichen, die das Netz sieht. Hier drei statt einem. |
| **Einbettung (Embedding)** | Koordinaten für jedes Zeichen. Ähnliche Zeichen landen nah beieinander. |
| **Neuron** | gewichtete Summe der Eingaben plus Verschiebung $b$ |
| **Verborgene Schicht** | viele Neuronen zwischen Eingabe und Ausgabe: `x @ W1 + b1` |
| **ReLU** | negative Zahlen werden 0. Ohne diese Knickstelle wären zwei Schichten nur eine. |
| `nn.Module`, `nn.Linear`, `nn.Embedding` | die fertigen Bausteine von PyTorch für Netze, Schichten und Einbettungen |
| `F.cross_entropy` | Softmax und Kreuzentropie in einem |
| **Optimierer** (`torch.optim.SGD`) | übernimmt den Lernschritt: `zero_grad()` und `step()` |
| **Minibatch** | eine zufällige Stichprobe von Beispielen für einen Lernschritt |
| **Overfitting** | das Netz lernt auswendig: Trainingsverlust sinkt, Testverlust steigt |

## Ausblick auf Notebook 4

Die Grenzen aus Teil 11 gelten für jedes Sprachmodell. Eine davon lässt sich aber stark verbessern: das kurze Gedächtnis.
Dein Netz sieht jetzt drei Zeichen. Aber was ist mit dem Wort, das vor 20 Zeichen stand?
Das Fenster einfach größer zu machen hat in Teil 9 nicht gut funktioniert: Das Netz wird riesig und lernt auswendig.

In Notebook 4 lernst du eine ganz andere Idee kennen: Jedes Zeichen darf **auf alle Zeichen davor zurückschauen**.
Das ist die Vorbereitung für den wichtigsten Baustein moderner Sprachmodelle, die **Aufmerksamkeit**.
""")
,
]
