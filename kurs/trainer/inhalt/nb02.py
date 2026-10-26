"""Inhalt von Notebook 2: Lernen mit PyTorch."""

from .bausteine import aufgabe, code, md, tipps

ZELLEN = [

# =============================================================
# WILLKOMMEN
# =============================================================

md(r"""
# Notebook 2: Ein Netz, das lernt

## Vom Zählen zum Lernen mit PyTorch

In Notebook 1 hast du ein Sprachmodell gebaut, das nur **zählt**. Am Ende haben wir zwei Schwächen gefunden:

1. Es kann **nicht verallgemeinern**. Einen unbekannten Kontext versteht es überhaupt nicht.
2. Es ist **zu selbstsicher**. Was es nie gesehen hat, hält es für unmöglich. Der Testverlust war deshalb unendlich.

In diesem Notebook baust du dein erstes **neuronales Netz**. Es zählt nicht, sondern **lernt**.
Damit löst du das zweite Problem. Das erste lösen wir in Notebook 3 mit einem größeren Netz.

Du arbeitest dabei mit **PyTorch**. Das ist die Bibliothek, mit der weltweit die meisten neuronalen Netze gebaut werden,
auch viele große Sprachmodelle. Wir lernen sie Schritt für Schritt kennen.

### Der Plan für dieses Notebook

| Teil | Was passiert |
|---|---|
| 1 | Tensoren: Rechnen mit ganzen Tabellen auf einmal |
| 2 und 3 | Das Bigramm-Modell aus Notebook 1, diesmal als Tabelle (Matrix) |
| 4 und 5 | Softmax und Verlust: Aus beliebigen Zahlen werden Wahrscheinlichkeiten |
| 6 | Lernen heißt bergab gehen |
| 7 | PyTorch findet den Weg bergab für dich |
| 8 | Das Netz lernt selbst, was du in Notebook 1 gezählt hast |
| 9 | Das Netz schreibt Text |

In diesem Notebook steckt mehr Mathematik als im ersten. Du musst aber nichts herleiten oder beweisen.
Jede Formel wird in Worten erklärt, und zu jeder gibt es eine Grafik oder ein Experiment zum Ausprobieren.
""")
,
md(r"""
## Vorbereitung

Die nächste Zelle lädt PyTorch, die Werkzeuge für dieses Notebook und **deinen eigenen Code aus Notebook 1**.
Falls sie einen Fehler meldet, schließe zuerst Notebook 1 ab. Dort muss die letzte Zelle `nb1.speichern(...)` erfolgreich gelaufen sein.

Die Bibliothek heißt PyTorch, wird aber mit `import torch` geladen.
""")
,
code(r"""
import math

import torch

from kurswerkzeuge import grafik, grafik2, nb2

nb2.pruefe_vorarbeit()

from meincode.notebook1 import Vocabulary, NGramModell, ziehe_zeichen, wahrscheinlichkeiten, zaehle_bigramme, durchschnittlicher_verlust

with open("daten/training.txt", encoding="utf-8") as datei:
    trainingstext = datei.read()

grenze = int(len(trainingstext) * 0.9)
training = trainingstext[:grenze]
test = trainingstext[grenze:]

vocabulary = Vocabulary(trainingstext)
V = len(vocabulary)

print("Alles bereit! Größe des Vokabulars:", V)
""")
,

# =============================================================
# TEIL 1: TENSOREN
# =============================================================

md(r"""
---
# Teil 1: Tensoren, Rechnen mit ganzen Tabellen

Neuronale Netze bestehen aus sehr vielen Zahlen, die in Tabellen angeordnet sind. Mit Python-Listen und Schleifen
wäre das Rechnen damit viel zu langsam. PyTorch rechnet stattdessen mit ganzen Tabellen auf einmal,
und zwar in schnellem C++-Code im Hintergrund.

Eine solche Tabelle heißt in PyTorch **Tensor**. Ein Tensor ist wie ein C#-Array `float[,]`: Alle Werte haben denselben Typ.
Jeder Tensor hat eine **Form** (englisch *shape*), zum Beispiel `(2, 3)` für 2 Zeilen und 3 Spalten.

| Begriff | Beispiel | Form |
|---|---|---|
| **Vektor** (eine Reihe Zahlen) | `torch.tensor([1.0, 2.0, 3.0])` | `(3,)` |
| **Matrix** (Tabelle) | `torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])` | `(2, 3)` |

Mit dem Wort **Matrix** meinen wir in diesem Kurs immer eine Tabelle von Zahlen.
Wir schreiben die Zahlen mit `.0`, damit PyTorch Kommazahlen daraus macht. Neuronale Netze rechnen fast immer mit Kommazahlen.
""")
,
code(r"""
a = torch.tensor([[1.0, 2.0, 3.0],
                  [4.0, 5.0, 6.0]])

print(a)
print("Form:", a.shape)          # (Zeilen, Spalten)
print()
print(torch.zeros((2, 4)))        # Matrix voller Nullen, Form (2, 4)
print()
print(torch.arange(5))            # wie range(5), aber als Tensor
""")
,
md(r"""
### Rechnen ohne Schleifen

Rechenzeichen wirken auf **jedes Element einzeln**. In C# bräuchtest du dafür eine Schleife:
""")
,
code(r"""
a = torch.tensor([[1.0, 2.0, 3.0],
                  [4.0, 5.0, 6.0]])

print(a * 10)          # jedes Element mal 10
print()
print(a + a)           # elementweise addieren
print()
print(a ** 2)          # jedes Element hoch 2
""")
,
md(r"""
### Zugriff auf Elemente, Zeilen und Spalten

| Python | Bedeutung | C# |
|---|---|---|
| `a[1, 2]` | Element in Zeile 1, Spalte 2 | `a[1, 2]` |
| `a[1]` | ganze Zeile 1 | (in C# umständlich) |
| `a[:, 2]` | ganze Spalte 2 (`:` heißt "alle Zeilen") | |
| `a[1, 2] += 1` | ein Element verändern | `a[1, 2] += 1` |
| `a[1, 2].item()` | ein einzelnes Element als normale Python-Zahl | |
""")
,
code(r"""
a = torch.tensor([[1.0, 2.0, 3.0],
                  [4.0, 5.0, 6.0]])

print(a[1, 2])
print(a[1, 2].item())
print(a[1])
print(a[:, 2])
""")
,
md(r"""
### Summen entlang einer Richtung

Oft wollen wir nicht alles aufsummieren, sondern **jede Zeile für sich** oder **jede Spalte für sich**.
Das steuert der Parameter `dim` (kurz für *dimension*, also Richtung):

- `dim=1` summiert **entlang der Zeilen** (nach rechts). Heraus kommt eine Summe pro Zeile.
- `dim=0` summiert **entlang der Spalten** (nach unten). Heraus kommt eine Summe pro Spalte.
""")
,
code(r"""
grafik2.summen_achsen([[1, 2, 3],
                       [4, 5, 6]])
""")
,
md(r"""
### Zeilenweise teilen

Was passiert bei `matrix / zeilensummen`? Die Matrix hat die Form `(2, 3)`, die Zeilensummen haben die Form `(2,)`.
Damit PyTorch weiß, dass **jede Zeile durch ihre eigene Summe** geteilt werden soll, lassen wir die Summen als Spalte stehen.
Das macht `keepdim=True`: Die Form ist dann `(2, 1)`.

PyTorch streckt die Spalte dann automatisch auf die Breite der Matrix. Das heißt **Broadcasting**:

$$
\begin{pmatrix} 1 & 2 & 3 \\ 4 & 5 & 6 \end{pmatrix} \Big/ \begin{pmatrix} 6 \\ 15 \end{pmatrix}
= \begin{pmatrix} 1/6 & 2/6 & 3/6 \\ 4/15 & 5/15 & 6/15 \end{pmatrix}
$$
""")
,
code(r"""
a = torch.tensor([[1.0, 2.0, 3.0],
                  [4.0, 5.0, 6.0]])

summen = a.sum(dim=1, keepdim=True)
print("Zeilensummen, Form", summen.shape)
print(summen)
print()
print(a / summen)
""")
,
md(r"""
---
## Aufgabe 2.1: Zeilen einer Matrix normieren

In Notebook 1 hast du `wahrscheinlichkeiten(haeufigkeiten)` geschrieben: Jeder Zähler wird durch die Summe aller Zähler geteilt.
Jetzt machst du das gleiche für eine ganze Matrix, und zwar für **jede Zeile einzeln**.

Schreibe die Funktion `zeilen_normieren(matrix)`:

- **Eingabe:** eine Matrix, zum Beispiel `[[1, 3], [2, 6]]`
- **Rückgabe:** eine neue Matrix, in der jede Zeile durch ihre Zeilensumme geteilt ist: `[[0.25, 0.75], [0.25, 0.75]]`

Ohne Schleife! Du brauchst nur `sum` mit den richtigen Parametern und eine Division.
""")
,
aufgabe(
vorlage=r"""
def zeilen_normieren(matrix):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 2.1: Hier fehlt noch dein Code")
""",
loesung=r"""
def zeilen_normieren(matrix):
    return matrix / matrix.sum(dim=1, keepdim=True)
""")
,
code(r"""
nb2.pruefe_aufgabe_1(zeilen_normieren)
""")
,
tipps(
    hinweis=r"""
    Du brauchst eine Summe **pro Zeile**. `matrix.sum()` ohne Parameter zählt alles zusammen.
    Mit `dim=1` läuft die Summe entlang einer Zeile, du bekommst also eine Summe pro Zeile.

    Probier in einer neuen Zelle aus, welche Form die Summe hat:
    ```python
    m = torch.tensor([[1.0, 3.0], [2.0, 6.0]])
    print(m.sum(dim=1).shape)
    print(m.sum(dim=1, keepdim=True).shape)
    ```
    """,
    fast=r"""
    ```python
    return matrix / matrix.sum(dim=1, keepdim=...)
    ```
    Ohne `keepdim=True` hat die Summe die Form `(2,)` statt `(2, 1)`. Dann teilt PyTorch spaltenweise statt zeilenweise.
    """,
    loesung=r"""
    ```python
    def zeilen_normieren(matrix):
        return matrix / matrix.sum(dim=1, keepdim=True)
    ```
    Für `[[1, 3], [2, 6]]`:

    - `matrix.sum(dim=1, keepdim=True)` ergibt die Zeilensummen als Spalte: `[[4], [8]]`, Form `(2, 1)`.
    - Beim Teilen streckt PyTorch diese Spalte über alle Spalten der Matrix (das heißt **Broadcasting**).
      Jede Zeile wird also durch ihre eigene Summe geteilt: `[[1/4, 3/4], [2/8, 6/8]]`.

    Ohne `keepdim=True` wäre die Summe `[4, 8]` mit Form `(2,)`. PyTorch würde dann die erste **Spalte** durch 4
    und die zweite durch 8 teilen. Das rechnet ohne Fehlermeldung, aber falsch.
    """,
)
,

# =============================================================
# TEIL 2: BIGRAMME ALS MATRIX
# =============================================================

md(r"""
---
# Teil 2: Das Bigramm-Modell als Matrix

In Notebook 1 hast du die Bigramme in einem Dictionary von Dictionaries gezählt: `zaehler["d"]["e"]`.
Jetzt speichern wir dieselbe Zählung in einer Matrix `N` mit $V \times V$ Feldern:

- Die **Zeile** ist die ID des aktuellen Zeichens.
- Die **Spalte** ist die ID des nächsten Zeichens.
- `N[a, b]` ist die Anzahl, wie oft `b` auf `a` folgte.

Statt mit Zeichen arbeiten wir ab jetzt mit den **IDs** aus deinem `Vocabulary`. Neuronale Netze rechnen nur mit Zahlen.

---
## Aufgabe 2.2: Bigramme in einer Matrix zählen

Schreibe die Funktion `bigramm_matrix(ids, V)`:

- `ids`: eine Liste von Zeichen-IDs, zum Beispiel `[0, 1, 0, 1]`
- `V`: die Größe des Vokabulars
- **Rückgabe:** eine $V \times V$-Matrix mit den Zählern

Für `[0, 1, 0, 1]` und `V = 3` soll herauskommen:

```
[[0, 2, 0],     nach 0 kam zweimal 1
 [1, 0, 0],     nach 1 kam einmal 0
 [0, 0, 0]]     nach 2 kam nichts
```

Leg mit `torch.zeros((V, V))` eine leere Matrix an und erhöhe in einer Schleife die richtigen Felder.
Viel einfacher als in Notebook 1, weil jedes Feld schon existiert und mit 0 beginnt.

**Neu in Python:** `zip(liste1, liste2)` läuft durch zwei Listen gleichzeitig.
`zip(ids[:-1], ids[1:])` liefert so alle Paare aus aktuellem und nächstem Element.
""")
,
aufgabe(
vorlage=r"""
def bigramm_matrix(ids, V):
    N = torch.zeros((V, V))

    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 2.2: Hier fehlt noch dein Code")

    return N
""",
loesung=r"""
def bigramm_matrix(ids, V):
    N = torch.zeros((V, V))

    for aktuell, naechstes in zip(ids[:-1], ids[1:]):
        N[aktuell, naechstes] += 1

    return N
""")
,
code(r"""
nb2.pruefe_aufgabe_2(bigramm_matrix)
""")
,
tipps(
    hinweis=r"""
    Für jedes Paar aus aktuellem und nächstem Zeichen erhöhst du ein Feld der Matrix um 1:
    Die Zeile ist das aktuelle Zeichen, die Spalte das nächste.

    Wie du an alle Paare kommst, zeigt dir dieser Versuch in einer neuen Zelle:
    ```python
    ids = [0, 1, 0, 1]
    print(list(zip(ids[:-1], ids[1:])))
    ```
    """,
    fast=r"""
    ```python
    for aktuell, naechstes in zip(ids[:-1], ids[1:]):
        N[..., ...] += 1
    ```
    """,
    loesung=r"""
    ```python
    def bigramm_matrix(ids, V):
        N = torch.zeros((V, V))

        for aktuell, naechstes in zip(ids[:-1], ids[1:]):
            N[aktuell, naechstes] += 1

        return N
    ```
    - `ids[:-1]` ist die Liste ohne das letzte Element, `ids[1:]` die Liste ohne das erste.
      `zip` legt beide nebeneinander. Für `[0, 1, 0, 1]` entstehen die Paare `(0, 1)`, `(1, 0)`, `(0, 1)`.
    - `N[aktuell, naechstes] += 1` zählt das Paar in Zeile `aktuell`, Spalte `naechstes`.

    Anders als in Notebook 1 musst du nichts vorher anlegen. Alle Felder gibt es schon, und sie beginnen bei 0.
    """,
)
,
md(r"""
Jetzt zählen wir den ganzen Trainingstext und rechnen mit deiner Funktion `zeilen_normieren` in Wahrscheinlichkeiten um.
Das Ergebnis `P_gezaehlt` ist **genau das Bigramm-Modell aus Notebook 1**, nur in einer anderen Form gespeichert.
""")
,
code(r"""
ids_training = vocabulary.encode(training)
ids_test = vocabulary.encode(test)

N = bigramm_matrix(ids_training, V)
P_gezaehlt = zeilen_normieren(N)

d, e = vocabulary.zeichen_zu_id["d"], vocabulary.zeichen_zu_id["e"]
print("Matrix:      P('e' nach 'd') =", P_gezaehlt[d, e].item())
print("Notebook 1:  P('e' nach 'd') =", wahrscheinlichkeiten(zaehle_bigramme(training)["d"])["e"])

grafik2.matrix_heatmap(P_gezaehlt, vocabulary.zeichen, "Die Wahrscheinlichkeitsmatrix P_gezaehlt")
""")
,
md(r"""
Die beiden Zahlen unterscheiden sich vielleicht ganz hinten in den Nachkommastellen. PyTorch rechnet standardmäßig
mit 7 genauen Stellen statt mit 16 wie normales Python. Für neuronale Netze reicht das völlig und spart viel Speicher.
""")
,

# =============================================================
# TEIL 3: ONE-HOT UND MATRIXMULTIPLIKATION
# =============================================================

md(r"""
---
# Teil 3: One-Hot und die Matrixmultiplikation

Ein neuronales Netz kann mit einer ID wie `8` wenig anfangen. Die Zahl 8 ist nicht "größer" als die 5,
sie ist nur ein anderes Zeichen. Wir brauchen eine Darstellung, die jedes Zeichen gleichberechtigt behandelt.

Die Lösung heißt **One-Hot-Kodierung**: Jedes Zeichen wird eine Reihe von $V$ Nullen
mit einer einzigen **1** an der Stelle seiner ID. Bei $V = 5$ wäre die ID 2:

$$
\text{one\_hot}(2) = (0,\ 0,\ 1,\ 0,\ 0)
$$

Für einen ganzen Text bekommt jedes Zeichen eine eigene Zeile. Heraus kommt eine Matrix der Form `(Länge des Texts, V)`.

---
## Aufgabe 2.3: One-Hot-Kodierung

Schreibe die Funktion `one_hot(ids, V)`:

- `ids`: eine Liste von IDs, zum Beispiel `[2, 0]`
- **Rückgabe:** eine Matrix der Form `(len(ids), V)`, zum Beispiel für `V = 3`: `[[0, 0, 1], [1, 0, 0]]`

Leg mit `torch.zeros` eine passende Matrix an und setze in einer Schleife in jeder Zeile `i` die Spalte `ids[i]` auf 1.

**Für Fortgeschrittene:** Es geht auch ohne Schleife. PyTorch erlaubt, mit zwei Listen auf einmal zuzugreifen:
`matrix[torch.arange(2), [2, 0]] = 1` setzt die Felder `[0, 2]` und `[1, 0]`.
""")
,
aufgabe(
vorlage=r"""
def one_hot(ids, V):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 2.3: Hier fehlt noch dein Code")
""",
loesung=r"""
def one_hot(ids, V):
    matrix = torch.zeros((len(ids), V))
    matrix[torch.arange(len(ids)), ids] = 1
    return matrix
""")
,
code(r"""
nb2.pruefe_aufgabe_3(one_hot)
""")
,
tipps(
    hinweis=r"""
    Erst die Matrix voller Nullen anlegen: so viele Zeilen wie IDs, $V$ Spalten.
    Achte auf die doppelten Klammern, `torch.zeros` bekommt die Form als **ein** Tupel: `torch.zeros((len(ids), V))`.

    Dann setzt du in jeder Zeile `i` genau ein Feld auf 1, nämlich in der Spalte `ids[i]`.
    `enumerate(ids)` liefert dir `i` und die ID gleichzeitig.
    """,
    fast=r"""
    ```python
    matrix = torch.zeros((len(ids), V))
    for i, id in enumerate(ids):
        matrix[..., ...] = 1
    return matrix
    ```
    """,
    loesung=r"""
    Mit einer Schleife:
    ```python
    def one_hot(ids, V):
        matrix = torch.zeros((len(ids), V))
        for i, id in enumerate(ids):
            matrix[i, id] = 1
        return matrix
    ```
    Für `ids = [2, 0]` und `V = 3` setzt die Schleife zuerst `matrix[0, 2] = 1`, dann `matrix[1, 0] = 1`.
    Heraus kommt `[[0, 0, 1], [1, 0, 0]]`.

    Ohne Schleife geht es auch. PyTorch erlaubt, mit zwei Listen auf einmal zuzugreifen:
    ```python
    def one_hot(ids, V):
        matrix = torch.zeros((len(ids), V))
        matrix[torch.arange(len(ids)), ids] = 1
        return matrix
    ```
    `torch.arange(2)` ist `[0, 1]`. Zusammen mit `ids = [2, 0]` sind das die Felder `[0, 2]` und `[1, 0]`, also genau dieselben.
    """,
)
,
code(r"""
grafik2.one_hot_bild("hallo", vocabulary, one_hot)
""")
,
md(r"""
### Die Matrixmultiplikation

Jetzt kommt die wichtigste Rechenoperation für neuronale Netze. Sie heißt **Matrixmultiplikation** und wird in Python mit `@` geschrieben.

Am einfachsten verstehst du sie an einem Beispiel. Eine Reihe $x$ mit 2 Zahlen wird mit einer Matrix $W$ mit 2 Zeilen multipliziert:

$$
\begin{pmatrix} 1 & 2 \end{pmatrix} \mathbin{@}
\begin{pmatrix} 10 & 20 & 30 \\ 1 & 2 & 3 \end{pmatrix}
= \begin{pmatrix} 1 \cdot 10 + 2 \cdot 1 & \quad 1 \cdot 20 + 2 \cdot 2 & \quad 1 \cdot 30 + 2 \cdot 3 \end{pmatrix}
= \begin{pmatrix} 12 & 24 & 36 \end{pmatrix}
$$

Für jede Spalte von $W$ wird gerechnet: erste Zahl von $x$ mal Wert aus der ersten Zeile, plus zweite Zahl von $x$ mal Wert aus der zweiten Zeile.
Das nennt man eine **gewichtete Summe**: Die Zahlen in $x$ bestimmen, wie stark jede Zeile von $W$ zählt.

In C# sähe das so aus:

```csharp
for (int j = 0; j < spalten; j++)
    for (int i = 0; i < zeilen; i++)
        ergebnis[j] += x[i] * W[i, j];
```

Hat $x$ mehrere Zeilen (eine pro Beispiel), passiert das für jede Zeile einzeln. Die Formen müssen dabei zusammenpassen:

$$
(N, V) \mathbin{@} (V, M) = (N, M)
$$

Die beiden inneren Zahlen müssen gleich sein, die äußeren bleiben übrig. Meldet PyTorch einen Fehler wie
`mat1 and mat2 shapes cannot be multiplied`, passen die Formen nicht zusammen.
""")
,
code(r"""
x = torch.tensor([[1.0, 2.0]])          # Form (1, 2)
W = torch.tensor([[10.0, 20.0, 30.0],
                  [ 1.0,  2.0,  3.0]])  # Form (2, 3)

print(x @ W)                            # Form (1, 3)
print("Form:", (x @ W).shape)
""")
,
md(r"""
### Der Aha-Moment

Was passiert, wenn $x$ ein One-Hot-Vektor ist? Dann wird jede Zeile von $W$ mit 0 malgenommen, außer der einen mit der 1.
Die Matrixmultiplikation **wählt genau eine Zeile** von $W$ aus.

Probier es aus: Wähle ein Zeichen und multipliziere seinen One-Hot-Vektor mit `P_gezaehlt`.
""")
,
code(r"""
grafik2.zeile_auswaehlen(P_gezaehlt, vocabulary.zeichen, one_hot)
""")
,
md(r"""
Das ist der Kern dieses Notebooks:

> **Das Bigramm-Modell aus Notebook 1 ist eine Matrixmultiplikation: `one_hot(ids, V) @ P`.**

Bisher haben wir die Matrix durch **Zählen** befüllt. Die Idee eines neuronalen Netzes ist,
die Matrix stattdessen durch **Lernen** zu befüllen. Wir starten mit irgendwelchen Zahlen
und verbessern sie Schritt für Schritt, bis die Vorhersagen gut sind.

Diese lernbaren Zahlen heißen **Gewichte** (englisch *weights*), deshalb nennen wir die Matrix ab jetzt $W$.
""")
,

# =============================================================
# TEIL 4: SOFTMAX
# =============================================================

md(r"""
---
# Teil 4: Softmax, aus beliebigen Zahlen werden Wahrscheinlichkeiten

Beim Lernen verändern wir die Gewichte in $W$ ein kleines bisschen nach oben oder unten.
Dabei können beliebige Zahlen entstehen, auch negative. Und eine Zeile wird sich fast nie genau zu 1 aufsummieren.
Wahrscheinlichkeiten müssen aber **positiv** sein und **zusammen 1** ergeben.

Dafür gibt es die **Softmax**. Sie macht aus einer Zeile beliebiger Zahlen eine Verteilung, in zwei Schritten:

1. **Alles positiv machen** mit der PyTorch-Funktion `torch.exp`. Wie sie genau rechnet, ist hier nicht wichtig.
   Du musst nur zwei Dinge wissen:
   - Das Ergebnis ist **immer positiv**, auch bei negativen Zahlen.
   - **Größer bleibt größer.** Die größte Zahl bekommt auch das größte Ergebnis.
2. **Durch die Summe teilen**, damit alles zusammen 1 ergibt. Das ist deine Funktion `zeilen_normieren` aus Aufgabe 2.1.

Probier es an einem Beispiel aus:
""")
,
code(r"""
beispiel = torch.tensor([[2.0, 0.0, -2.0]])

positiv = torch.exp(beispiel)
print("vorher:         ", beispiel)
print("nach torch.exp: ", positiv)
print("durch Summe:    ", zeilen_normieren(positiv))
""")
,
md(r"""
Aus `2, 0, -2` wird ungefähr `0,87, 0,12, 0,02`. Alle Werte sind positiv, die Summe ist 1,
und die größte Zahl hat die größte Wahrscheinlichkeit bekommen.

Die Zahlen vor der Softmax nennt man **Logits**. Ein großes Logit bedeutet "dieses Zeichen ist wahrscheinlich",
ein sehr negatives "eher nicht". Aber selbst ein sehr negatives Logit ergibt nie genau 0.

Spiel mit den Reglern. Was passiert, wenn alle Logits gleich sind? Was, wenn eines viel größer ist als die anderen?
Und was, wenn du **alle** Logits um denselben Wert verschiebst?
""")
,
code(r"""
def softmax_vorschau(logits):
    return zeilen_normieren(torch.exp(logits))

grafik2.softmax_regler(softmax_vorschau)
""")
,
md(r"""
Die letzte Beobachtung ist wichtig: Wenn du alle Logits um denselben Wert verschiebst, ändert sich **nichts**.
Es kommt nur darauf an, wie weit die Logits **auseinander** liegen.

### Ein Problem und sein Trick

`torch.exp` macht aus großen Zahlen sehr schnell riesige Zahlen. Irgendwann sind sie zu groß für den Computer:
""")
,
code(r"""
print(torch.exp(torch.tensor(50.0)))
print(torch.exp(torch.tensor(100.0)))                       # zu groß: unendlich (inf)
print(softmax_vorschau(torch.tensor([[100.0, 100.0]])))     # unendlich / unendlich = nan ("not a number")
""")
,
md(r"""
Der Trick nutzt die Beobachtung von den Reglern: Verschieben ändert nichts.
Also ziehen wir von jeder Zeile zuerst ihre **größte Zahl** ab. Danach ist die größte Zahl 0, alle anderen sind negativ,
und `torch.exp` kann keine riesigen Zahlen mehr erzeugen. Das Ergebnis bleibt dasselbe.
Jede professionelle Softmax macht das so.

---
## Aufgabe 2.4: Softmax

Schreibe die Funktion `softmax(logits)`:

- **Eingabe:** eine Matrix von Logits, Form `(N, V)`. Jede Zeile ist ein Beispiel.
- **Rückgabe:** eine Matrix gleicher Form. Jede Zeile ist eine Wahrscheinlichkeitsverteilung.

Schritte:
1. Von jeder Zeile ihr Maximum abziehen. Das Maximum jeder Zeile bekommst du mit `logits.max(dim=1, keepdim=True).values`.
   Das `.values` ist nötig, weil `max` in PyTorch zusätzlich auch die Position des Maximums liefert.
2. `torch.exp(...)` anwenden
3. Jede Zeile durch ihre Summe teilen. Das ist deine Funktion `zeilen_normieren`!
""")
,
aufgabe(
vorlage=r"""
def softmax(logits):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 2.4: Hier fehlt noch dein Code")
""",
loesung=r"""
def softmax(logits):
    verschoben = logits - logits.max(dim=1, keepdim=True).values
    return zeilen_normieren(torch.exp(verschoben))
""")
,
code(r"""
nb2.pruefe_aufgabe_4(softmax)
""")
,
tipps(
    hinweis=r"""
    Die drei Schritte stehen in der Aufgabe. Für Schritt 1:
    `logits.max(dim=1, keepdim=True).values` ist das Maximum jeder Zeile, als Spalte mit der Form `(N, 1)`.
    Ziehst du diese Spalte von `logits` ab, verschiebt sich jede Zeile um ihr eigenes Maximum (Broadcasting, wie bei `zeilen_normieren`).

    Für Schritt 3 hast du schon eine Funktion geschrieben.
    """,
    fast=r"""
    ```python
    verschoben = logits - logits.max(dim=1, keepdim=True).values
    return zeilen_normieren(torch.exp(...))
    ```
    """,
    loesung=r"""
    ```python
    def softmax(logits):
        verschoben = logits - logits.max(dim=1, keepdim=True).values
        return zeilen_normieren(torch.exp(verschoben))
    ```
    Am Beispiel einer Zeile `[2, 0, -2]`:

    1. Das Maximum ist 2. Nach dem Abziehen steht da `[0, -2, -4]`. Die größte Zahl ist jetzt 0, so kann `torch.exp` nicht überlaufen.
    2. `torch.exp` macht alle Zahlen positiv. Größer bleibt dabei größer.
    3. `zeilen_normieren` teilt durch die Summe. Jetzt ergibt jede Zeile zusammen 1, also eine Wahrscheinlichkeitsverteilung.

    Das Abziehen ändert am Ergebnis nichts. Es schützt nur vor riesigen Zahlen.
    """,
)
,

# =============================================================
# TEIL 5: KREUZENTROPIE
# =============================================================

md(r"""
---
# Teil 5: Wie falsch liegt das Netz?

Um zu lernen, braucht das Netz eine Zahl, die sagt, wie schlecht es gerade ist. Die kennst du schon aus Notebook 1:
den durchschnittlichen **Verlust** $-\log(p)$ für das richtige Zeichen. Sein Fachname ist **Kreuzentropie**.

Jetzt rechnen wir ihn für viele Beispiele gleichzeitig aus:

- `P` hat die Form `(N, V)`: Für jedes der $N$ Beispiele eine Verteilung über alle Zeichen.
- `ziele` hat die Form `(N,)`: Für jedes Beispiel die ID des Zeichens, das wirklich kam.

Wir brauchen aus jeder Zeile `i` von `P` genau den Wert in Spalte `ziele[i]`. Das geht mit dem Zugriff über zwei Listen,
den du bei One-Hot vielleicht schon benutzt hast:
""")
,
code(r"""
P = torch.tensor([[0.7, 0.2, 0.1],
                  [0.1, 0.1, 0.8],
                  [0.3, 0.3, 0.4]])
ziele = torch.tensor([0, 2, 1])

print(P[torch.arange(3), ziele])     # P[0, 0], P[1, 2], P[2, 1]
""")
,
md(r"""
Davon brauchen wir dann für jeden Wert $-\log(p)$ und am Ende den Durchschnitt.

---
## Aufgabe 2.5: Der Verlust für viele Beispiele

Schreibe die Funktion `kreuzentropie(P, ziele)`. Sie gibt den durchschnittlichen Verlust zurück.

**Hilfreich:** `torch.log(tensor)` berechnet den Logarithmus jedes Elements, `tensor.mean()` den Durchschnitt.
Das Ergebnis ist ein Tensor mit einer einzigen Zahl darin. Das ist so in Ordnung, PyTorch braucht ihn gleich genau so.
""")
,
aufgabe(
vorlage=r"""
def kreuzentropie(P, ziele):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 2.5: Hier fehlt noch dein Code")
""",
loesung=r"""
def kreuzentropie(P, ziele):
    p_richtig = P[torch.arange(len(ziele)), ziele]
    return -torch.log(p_richtig).mean()
""")
,
code(r"""
nb2.pruefe_aufgabe_5(kreuzentropie)
""")
,
tipps(
    hinweis=r"""
    Zwei Schritte:

    1. Aus jeder Zeile von `P` die Wahrscheinlichkeit des **richtigen** Zeichens holen. In Zeile `i` ist das die Spalte `ziele[i]`.
       Erinnere dich an die Variante ohne Schleife bei `one_hot`: `matrix[torch.arange(...), liste]` greift auf mehrere Felder gleichzeitig zu.
    2. Von diesen Wahrscheinlichkeiten den Verlust $-\log(p)$ berechnen und den Durchschnitt nehmen.
    """,
    fast=r"""
    ```python
    p_richtig = P[torch.arange(len(ziele)), ...]
    return -torch.log(...).mean()
    ```
    """,
    loesung=r"""
    ```python
    def kreuzentropie(P, ziele):
        p_richtig = P[torch.arange(len(ziele)), ziele]
        return -torch.log(p_richtig).mean()
    ```
    - `torch.arange(len(ziele))` sind die Zeilennummern `0, 1, 2, ...`. Zusammen mit `ziele` holt die erste Zeile
      aus jeder Zeile genau ein Feld: die Wahrscheinlichkeit, die das Modell dem richtigen Zeichen gegeben hat.
    - `torch.log` rechnet den Logarithmus jeder dieser Zahlen, das Minus davor macht daraus den Verlust.
    - `.mean()` nimmt den Durchschnitt. Das ist dasselbe wie dein `durchschnittlicher_verlust` aus Notebook 1, nur ohne Schleife.
    """,
)
,
md(r"""
### Zwei Experimente mit dem Verlust

Jetzt setzen wir alles zusammen. Das komplette Bigramm-Netz ist:

$$
P = \text{softmax}(\text{one\_hot}(\text{ids}) \mathbin{@} W)
$$

Für jedes Zeichen im Trainingstext (außer dem letzten) sagt es eine Verteilung für das nächste Zeichen voraus.
Die Eingaben sind also `ids_training[:-1]`, die richtigen Antworten `ids_training[1:]`.

**Experiment 1:** Was ist der Verlust, wenn $W$ nur Nullen enthält?
""")
,
code(r"""
eingaben = ids_training[:-1]
ziele_training = torch.tensor(ids_training[1:])

W = torch.zeros((V, V))
P = softmax(one_hot(eingaben, V) @ W)

print("Verlust mit W = 0:", kreuzentropie(P, ziele_training).item())
print("log(V)           :", math.log(V))
""")
,
md(r"""
Mit lauter Nullen sind alle Logits gleich, also gibt die Softmax jedem Zeichen dieselbe Wahrscheinlichkeit $1/V$.
Der Verlust ist dann $-\log(1/V) = \log(V) \approx 3{,}56$. Das ist der Verlust eines Modells, das **blind rät**.
Jedes Modell, das etwas gelernt hat, muss besser sein.

**Experiment 2:** Gibt es ein $W$, mit dem das Netz genau so gut ist wie die Zählung?
Ja: Wir nehmen als Logits den **Logarithmus** der gezählten Wahrscheinlichkeiten. `torch.exp` macht den Logarithmus
wieder rückgängig, also kommen nach der Softmax genau die gezählten Wahrscheinlichkeiten heraus. Die winzige Zahl `1e-10` sorgt dafür, dass nie `log(0)` berechnet wird.
""")
,
code(r"""
W = torch.log(P_gezaehlt + 1e-10)

P = softmax(one_hot(eingaben, V) @ W)
print("Netz mit W = log(P_gezaehlt):", kreuzentropie(P, ziele_training).item())
print("Zählmodell aus Notebook 1:   ", durchschnittlicher_verlust(NGramModell(training, 1), training))
""")
,
md(r"""
Praktisch derselbe Wert! Das Netz **kann** also genau das Bigramm-Modell aus Notebook 1 sein.
Die spannende Frage: **Kann es diese Gewichte selbst finden, ohne zu zählen?** Dafür müssen wir verstehen, wie Lernen funktioniert.
""")
,

# =============================================================
# TEIL 6: BERGAB GEHEN
# =============================================================

md(r"""
---
# Teil 6: Lernen heißt bergab gehen

Stell dir vor, du stehst im Nebel auf einem Hügel und willst ins Tal. Du siehst nichts, aber du spürst unter deinen Füßen,
in welche Richtung es bergab geht. Also machst du einen kleinen Schritt in diese Richtung. Und noch einen. Und noch einen.

Genau so lernt ein neuronales Netz:

- Der **Hügel** ist der Verlust. Seine Höhe hängt von den Gewichten ab.
- Deine **Position** sind die aktuellen Gewichte.
- Das **Tal** sind Gewichte mit kleinem Verlust, also gute Vorhersagen.

Wir fangen mit nur **einem** Gewicht $w$ an. Der Verlust sei $f(w) = (w - 3)^2 + 1$. Das ist eine Kurve mit dem Tal bei $w = 3$.

### Die Steigung

Wie "spürt" man, wo es bergab geht? Mit der **Steigung** der Kurve an der aktuellen Stelle.
Das kennst du vom Steigungsschild an der Straße: 10 % Steigung heißt 10 Meter nach oben auf 100 Meter Strecke.
Hier ist es genauso: Steigung 2 heißt, die Kurve geht 2 nach oben, wenn man 1 nach rechts geht.

- Ist die Steigung **positiv**, geht es nach rechts bergauf. Wir müssen nach **links**.
- Ist sie **negativ**, geht es nach rechts bergab. Wir müssen nach **rechts**.
- Ist sie **0**, sind wir am tiefsten Punkt.

In der Mathematik heißt die Steigung einer Kurve **Ableitung**. Schieb den Regler und beobachte die orange Linie.
Sie zeigt die Steigung an der Stelle $w$:
""")
,
code(r"""
grafik2.steigung_erkunden()
""")
,
md(r"""
### Die Steigung ausrechnen

Wie rechnet man die Steigung aus? Genau wie beim Straßenschild: **Höhenunterschied geteilt durch Strecke**.
Wir gehen ein winziges Stück $h$ nach rechts und nach links und schauen, wie stark sich die Höhe $f$ ändert:

$$
\text{Steigung bei } w \approx \frac{f(w + h) - f(w - h)}{2h} \qquad \text{zum Beispiel mit } h = 0{,}00001
$$

Oben steht der Höhenunterschied, unten die Strecke (von $w - h$ bis $w + h$ sind es $2h$).
Weil $h$ so winzig ist, kommt fast genau die Steigung an der Stelle $w$ heraus.

---
## Aufgabe 2.6: Die Steigung ausrechnen

Schreibe die Funktion `numerische_ableitung(f, x, h=1e-5)`. Sie bekommt eine **Funktion** `f` als Parameter
(in C# wäre das ein `Func<double, double>`) und gibt die Steigung von `f` an der Stelle `x` zurück.

`h=1e-5` ist ein **Standardwert**: Wer `h` nicht angibt, bekommt automatisch `1e-5`. Das ist die Kurzschreibweise für $0{,}00001$.
In C# schreibt man das genauso: `double h = 1e-5`.
""")
,
aufgabe(
vorlage=r"""
def numerische_ableitung(f, x, h=1e-5):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 2.6: Hier fehlt noch dein Code")
""",
loesung=r"""
def numerische_ableitung(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)
""")
,
code(r"""
nb2.pruefe_aufgabe_6(numerische_ableitung)
""")
,
tipps(
    hinweis=r"""
    `f` ist eine ganz normale Funktion, die du aufrufen kannst. `f(x + h)` ist die Höhe ein kleines Stück rechts von `x`,
    `f(x - h)` ein Stück links davon.

    Die Steigung ist: Höhenunterschied geteilt durch den Abstand der beiden Stellen.
    """,
    fast=r"""
    ```python
    return (f(x + h) - f(...)) / (...)
    ```
    Wie weit liegen `x - h` und `x + h` auseinander?
    """,
    loesung=r"""
    ```python
    def numerische_ableitung(f, x, h=1e-5):
        return (f(x + h) - f(x - h)) / (2 * h)
    ```
    - `f(x + h) - f(x - h)` ist der Höhenunterschied zwischen einem Punkt knapp rechts und einem knapp links von `x`.
    - Die beiden Punkte liegen `2 * h` auseinander. Durch diesen Abstand wird geteilt.

    Beispiel: Für `f(x) = x * x` an der Stelle 3 kommt etwa 6 heraus. An dieser Stelle steigt die Kurve also 6 nach oben pro 1 nach rechts.
    """,
)
,
code(r"""
f = lambda w: (w - 3) ** 2 + 1

for w in [0.5, 3.0, 5.0]:
    print(f"Steigung bei w = {w}: {numerische_ableitung(f, w):+.3f}")
""")
,
md(r"""
Vergleich die Werte mit dem Regler oben. Schieb ihn auf 0,5, 3 und 5: Die Steigung im Titel stimmt mit deiner Funktion überein.

### Bergab gehen

Jetzt gehen wir bergab. In jedem Schritt bewegen wir $w$ ein Stück **gegen** die Steigung:

$$
w_{\text{neu}} = w - \text{Lernrate} \cdot \text{Steigung}
$$

Das Minus sorgt dafür, dass wir bergab gehen. Die **Lernrate** bestimmt, wie groß die Schritte sind.
Ist es steil, ist auch der Schritt groß. Nahe am Tal wird es flach, und die Schritte werden von selbst kleiner.

Dieses Verfahren heißt **Gradientenabstieg** (englisch *Gradient Descent*). Es ist der Lern-Algorithmus hinter
praktisch allen neuronalen Netzen, auch hinter den ganz großen Sprachmodellen.

---
## Aufgabe 2.7: Bergab gehen mit einem Gewicht

Schreibe die Funktion `gradientenabstieg(steigung, start, lernrate, schritte)`:

- `steigung`: eine Funktion, die für ein $w$ die Steigung liefert
- `start`: der Startwert für $w$
- `lernrate`: die Schrittgröße
- `schritte`: wie viele Schritte gemacht werden
- **Rückgabe:** eine **Liste aller Positionen**, angefangen mit `start`. Bei 2 Schritten also 3 Werte.
""")
,
aufgabe(
vorlage=r"""
def gradientenabstieg(steigung, start, lernrate, schritte):
    w = start
    verlauf = [w]

    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 2.7: Hier fehlt noch dein Code")

    return verlauf
""",
loesung=r"""
def gradientenabstieg(steigung, start, lernrate, schritte):
    w = start
    verlauf = [w]

    for _ in range(schritte):
        w = w - lernrate * steigung(w)
        verlauf.append(w)

    return verlauf
""")
,
code(r"""
nb2.pruefe_aufgabe_7(gradientenabstieg)
""")
,
tipps(
    hinweis=r"""
    Die Schleife läuft `schritte`-mal. In jedem Schritt:

    1. Die Steigung an der aktuellen Stelle `w` ausrechnen. `steigung` ist eine Funktion, du rufst sie mit `w` auf.
    2. Ein Stück **gegen** die Steigung gehen. Die Länge des Schritts ist Lernrate mal Steigung.
    3. Die neue Position an `verlauf` anhängen.
    """,
    fast=r"""
    ```python
    for _ in range(schritte):
        w = w - ... * ...
        verlauf.append(w)
    ```
    """,
    loesung=r"""
    ```python
    def gradientenabstieg(steigung, start, lernrate, schritte):
        w = start
        verlauf = [w]

        for _ in range(schritte):
            w = w - lernrate * steigung(w)
            verlauf.append(w)

        return verlauf
    ```
    - Das **Minus** sorgt dafür, dass es bergab geht. Ist die Steigung positiv (rechts geht es hoch), wird `w` kleiner. Ist sie negativ, wird `w` größer.
    - Die Lernrate bestimmt, wie groß der Schritt ist. Zu klein: man kommt kaum voran. Zu groß: man springt über das Tal hinweg.
    - `verlauf` beginnt mit dem Startwert. Nach 2 Schritten enthält es deshalb 3 Werte.
    """,
)
,
md(r"""
Jetzt schauen wir deiner Funktion bei der Arbeit zu. Start ist $w = -0{,}5$. Drück auf **Play** und probier alle Lernraten aus.
""")
,
code(r"""
grafik2.gradientenabstieg_animation(gradientenabstieg)
""")
,
md(r"""
**Denkfragen.** Überleg dir erst selbst eine Antwort, bevor du aufklappst.

<details>
<summary><b>1. Was passiert bei der Lernrate 0,02?</b></summary>

Die Kugel kommt nur sehr langsam voran. Nach 20 Schritten ist sie noch weit vom Tal entfernt.
Eine zu kleine Lernrate verschwendet Rechenzeit.
</details>

<details>
<summary><b>2. Was passiert bei 0,9?</b></summary>

Die Kugel springt über das Tal hinweg auf die andere Seite, dann wieder zurück. Weil sie dabei jedes Mal etwas näher
ans Tal kommt, landet sie trotzdem dort. Aber es ist ein Zickzack.
</details>

<details>
<summary><b>3. Und bei 1,05?</b></summary>

Jetzt ist jeder Sprung so groß, dass die Kugel auf der anderen Seite **höher** landet als vorher. Sie schaukelt sich auf
und fliegt aus dem Bild. Das Training **divergiert**. Bei echten Netzen zeigt sich das so, dass der Verlust plötzlich riesig
oder `nan` wird. Dann ist die erste Maßnahme immer: Lernrate verkleinern.
</details>
""")
,

# =============================================================
# TEIL 7: PYTORCH RECHNET DIE STEIGUNG AUS
# =============================================================

md(r"""
---
# Teil 7: PyTorch findet den Weg bergab

Unser Bigramm-Netz hat nicht ein Gewicht, sondern $V \cdot V = 35 \cdot 35 = 1225$ Gewichte.
Die Idee bleibt dieselbe: Für **jedes** Gewicht brauchen wir die Steigung, also die Antwort auf die Frage
*"Wie ändert sich der Verlust, wenn ich nur an diesem einen Gewicht ein bisschen drehe?"*
Alle diese Steigungen zusammen heißen **Gradient**.

Mit deiner Funktion `numerische_ableitung` bräuchten wir dafür in jedem Lernschritt $2 \cdot 1225 = 2450$ Durchläufe durch das Netz.
Große Sprachmodelle haben **Milliarden** Gewichte. Das wäre hoffnungslos langsam.

### Die Lösung: PyTorch merkt sich jeden Rechenschritt

Hier kommt die wichtigste Fähigkeit von PyTorch. Wenn du bei einem Tensor `requires_grad=True` angibst,
merkt sich PyTorch jede Rechnung, in der dieser Tensor vorkommt. Am Ende rufst du `.backward()` auf,
und PyTorch rechnet für jedes Gewicht die Steigung aus. Sie steht danach in `.grad`.

Probieren wir es mit unserer Kurve von oben, an der Stelle $w = 0{,}5$:
""")
,
code(r"""
w = torch.tensor(0.5, requires_grad=True)     # PyTorch, merk dir alles, was mit w passiert!

verlust = (w - 3) ** 2 + 1                     # ganz normal rechnen
verlust.backward()                             # PyTorch, rechne die Steigung aus!

print("Steigung laut PyTorch:              ", w.grad.item())
print("Steigung mit numerische_ableitung:  ", numerische_ableitung(lambda x: (x - 3) ** 2 + 1, 0.5))
""")
,
md(r"""
Dasselbe Ergebnis. PyTorch misst aber nicht wie wir mit einem winzigen Schritt $h$. Es kennt für jede Grundrechenart
(plus, mal, hoch, `exp`, `log` und so weiter) die passende Regel und setzt das Ergebnis Schritt für Schritt **rückwärts**
durch alle Rechnungen zusammen. Deshalb heißt die Methode `backward`, und das Verfahren heißt **Backpropagation**.

Das Schöne: PyTorch macht das in **einem** Durchgang für **alle** Gewichte gleichzeitig, egal ob es eines ist oder eine Milliarde.

### Was PyTorch für unser Netz herausfindet

Schauen wir uns den Gradienten für ein einziges Beispiel an. Das Netz hat fünf Logits für die Zeichen `a`, `e`, `n`, `r` und das Leerzeichen
berechnet, richtig wäre `n`. Die Grafik nimmt deine Funktionen `softmax` und `kreuzentropie`, ruft `backward()` auf
und zeigt, was PyTorch als Gradient der Logits herausbekommt:
""")
,
code(r"""
grafik2.gradient_balken(softmax, kreuzentropie)
""")
,
md(r"""
Vergleich die drei Bilder. Der Gradient ist genau **Vorhersage minus Wahrheit**, also das linke Bild minus das mittlere.

Beim Lernen gehen wir **gegen** den Gradienten (das Minus in der Formel von oben). Das bedeutet:

- Beim **richtigen Zeichen** `n` ist der Gradient negativ. Sein Logit wird also **erhöht**.
- Bei allen **anderen Zeichen** ist er positiv. Ihre Logits werden **gesenkt**, und zwar umso stärker,
  je mehr das Netz fälschlich auf sie gesetzt hat. Das `e` mit 50 % bekommt den größten Dämpfer.

Das ist sehr einleuchtend: Das Netz schiebt seine Wahrscheinlichkeit dorthin, wo die richtige Antwort war,
und nimmt sie von dort weg, wo sie falsch war.

<details>
<summary><b>Für Neugierige: Kann man das auch ohne PyTorch ausrechnen?</b></summary>

Ja. Mit den Ableitungsregeln aus der Oberstufen-Mathematik kann man zeigen, dass für Softmax und Kreuzentropie zusammen
immer genau $P - Y$ herauskommt, wobei $Y$ der One-Hot-Vektor des richtigen Zeichens ist. Bei $N$ Beispielen wird noch durch $N$ geteilt,
weil der Verlust ein Durchschnitt ist. Für größere Netze wird diese Rechnung aber schnell sehr lang. Genau deshalb nimmt man PyTorch.
</details>

### Ein Lernschritt

Ein Lernschritt sieht damit so aus:

1. Vorwärts rechnen: Vorhersage und Verlust berechnen.
2. `verlust.backward()`: PyTorch füllt für jedes Gewicht `.grad`.
3. Jedes Gewicht ein Stück gegen seinen Gradienten bewegen: `gewicht -= lernrate * gewicht.grad`
4. Die Gradienten wieder auf 0 setzen: `gewicht.grad.zero_()`

Zu Schritt 3 und 4 gibt es zwei Besonderheiten:

- Das Verändern der Gewichte soll PyTorch **nicht** mitschreiben, sonst würde es auch diese Rechnung beim nächsten
  `backward()` berücksichtigen. Deshalb steht dieser Teil in einem Block `with torch.no_grad():` ("ohne Gradienten").
  Das ist so ähnlich wie ein `using`-Block in C#.
- PyTorch **addiert** neue Gradienten zu den alten dazu, statt sie zu ersetzen. Darum müssen wir sie nach jedem Schritt
  mit `.zero_()` auf 0 setzen. Der Unterstrich am Ende bedeutet in PyTorch: Der Tensor wird direkt verändert.

---
## Aufgabe 2.8: Ein Lernschritt für alle Gewichte

Schreibe die Funktion `gradientenschritt(gewichte, lernrate)`. Sie macht die Schritte 3 und 4 für eine **Liste** von Gewichten:

```python
with torch.no_grad():
    for gewicht in gewichte:
        # Schritt 3 und 4
```

Wichtig: Verändere jedes Gewicht direkt mit `-=`. Schreibst du `gewicht = gewicht - ...`, entsteht ein neuer Tensor,
und das eigentliche Gewicht bleibt unverändert.
""")
,
aufgabe(
vorlage=r"""
def gradientenschritt(gewichte, lernrate):
    with torch.no_grad():
        for gewicht in gewichte:
            # DEIN CODE HIER
            raise NotImplementedError("Aufgabe 2.8: Hier fehlt noch dein Code")
""",
loesung=r"""
def gradientenschritt(gewichte, lernrate):
    with torch.no_grad():
        for gewicht in gewichte:
            gewicht -= lernrate * gewicht.grad
            gewicht.grad.zero_()
""")
,
code(r"""
nb2.pruefe_aufgabe_8(gradientenschritt)
""")
,
tipps(
    hinweis=r"""
    In der Schleife passieren mit jedem Gewicht zwei Dinge:

    - **Schritt 3:** wie bei `gradientenabstieg` ein Stück bergab gehen. Die Steigung steht jetzt in `gewicht.grad`.
      Wichtig: mit `-=` direkt im Gewicht ändern.
    - **Schritt 4:** den Gradienten wieder auf 0 setzen. Methoden, die einen Tensor direkt verändern,
      enden in PyTorch mit einem Unterstrich, zum Beispiel `.zero_()`.
    """,
    fast=r"""
    ```python
    with torch.no_grad():
        for gewicht in gewichte:
            gewicht -= ... * gewicht.grad
            gewicht.grad....
    ```
    """,
    loesung=r"""
    ```python
    def gradientenschritt(gewichte, lernrate):
        with torch.no_grad():
            for gewicht in gewichte:
                gewicht -= lernrate * gewicht.grad
                gewicht.grad.zero_()
    ```
    - `with torch.no_grad():` sagt PyTorch: Diese Rechnung gehört nicht zum Lernen, merk sie dir nicht für `backward()`.
    - `gewicht -= lernrate * gewicht.grad` ist dieselbe Formel wie in `gradientenabstieg`, nur für alle Zahlen im Tensor gleichzeitig.
      Das `-=` verändert den vorhandenen Tensor. `gewicht = gewicht - ...` würde nur die Schleifenvariable auf einen neuen Tensor zeigen lassen.
    - `gewicht.grad.zero_()` ist nötig, weil `backward()` neue Gradienten zu den alten **dazuzählt**.
      Ohne Zurücksetzen würden sich die Gradienten aller Schritte aufaddieren.
    """,
)
,

# =============================================================
# TEIL 8: DAS BIGRAMM-NETZ TRAINIEREN
# =============================================================

md(r"""
---
# Teil 8: Das erste Netz lernt

Jetzt packen wir alles in eine Klasse. Diesen Aufbau wirst du in den nächsten Notebooks immer wieder sehen.

---
## Aufgabe 2.9: Die Klasse `BigrammNetz`

| Teil | Was es tut |
|---|---|
| `__init__(self, V)` | legt die Gewichte `self.W` als $V \times V$-Matrix voller **Nullen** an, mit `requires_grad=True` |
| `vorhersage(self, ids)` | gibt `softmax(one_hot(ids, V) @ self.W)` zurück |
| `trainingsschritt(self, ids, ziele, lernrate)` | berechnet den Verlust, ruft `backward()` auf, macht mit `gradientenschritt` einen Schritt und gibt den Verlust als normale Zahl zurück (`.item()`) |

Den Wert $V$ merkst du dir im Konstruktor in `self.V`.
`torch.zeros` kennt `requires_grad` als zusätzlichen Parameter: `torch.zeros((V, V), requires_grad=True)`.
""")
,
aufgabe(
vorlage=r"""
class BigrammNetz:
    def __init__(self, V):
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 2.9: Hier fehlt noch dein Code")

    def vorhersage(self, ids):
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 2.9: Hier fehlt noch dein Code")

    def trainingsschritt(self, ids, ziele, lernrate):
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 2.9: Hier fehlt noch dein Code")
""",
loesung=r"""
class BigrammNetz:
    def __init__(self, V):
        self.V = V
        self.W = torch.zeros((V, V), requires_grad=True)

    def vorhersage(self, ids):
        return softmax(one_hot(ids, self.V) @ self.W)

    def trainingsschritt(self, ids, ziele, lernrate):
        verlust = kreuzentropie(self.vorhersage(ids), ziele)
        verlust.backward()
        gradientenschritt([self.W], lernrate)
        return verlust.item()
""")
,
code(r"""
nb2.pruefe_aufgabe_9(BigrammNetz)
""")
,
tipps(
    hinweis=r"""
    - **Konstruktor:** Zwei Attribute. `self.V` merkt sich die Größe, `self.W` sind die Gewichte (Nullen, mit `requires_grad=True`).
    - **vorhersage:** Die Formel steht in der Tabelle. Statt `V` schreibst du dort `self.V`.
    - **trainingsschritt:** Dieselben Schritte wie im Abschnitt davor: Verlust berechnen, `backward()`, einen Schritt mit
      deiner Funktion `gradientenschritt`, den Verlust als Zahl zurückgeben.
    """,
    fast=r"""
    ```python
    def __init__(self, V):
        self.V = V
        self.W = torch.zeros((V, V), requires_grad=...)

    def vorhersage(self, ids):
        return softmax(one_hot(ids, self.V) @ ...)

    def trainingsschritt(self, ids, ziele, lernrate):
        verlust = kreuzentropie(self.vorhersage(ids), ...)
        verlust.backward()
        gradientenschritt(..., lernrate)
        return verlust.item()
    ```
    `gradientenschritt` erwartet eine **Liste** von Gewichten, auch wenn es nur eines ist.
    """,
    loesung=r"""
    ```python
    class BigrammNetz:
        def __init__(self, V):
            self.V = V
            self.W = torch.zeros((V, V), requires_grad=True)

        def vorhersage(self, ids):
            return softmax(one_hot(ids, self.V) @ self.W)

        def trainingsschritt(self, ids, ziele, lernrate):
            verlust = kreuzentropie(self.vorhersage(ids), ziele)
            verlust.backward()
            gradientenschritt([self.W], lernrate)
            return verlust.item()
    ```
    - `requires_grad=True` sagt PyTorch, dass es für `self.W` Gradienten ausrechnen soll. Ohne das gäbe es kein `self.W.grad`.
    - `one_hot(ids, self.V) @ self.W` sucht für jede ID die passende Zeile aus `W` heraus. Die Softmax macht daraus Wahrscheinlichkeiten.
    - Im Trainingsschritt rechnet `backward()` die Gradienten aus, `gradientenschritt([self.W], lernrate)` geht damit bergab.
      Die eckigen Klammern machen aus dem einen Gewicht eine Liste.
    - `.item()` macht aus dem Tensor mit einer Zahl eine normale Python-Zahl, die man ausgeben und in Listen sammeln kann.
    """,
)
,
md(r"""
### Das Training

Jetzt kommt der große Moment. Das Netz startet mit lauter Nullen, weiß also nichts. Dann macht es 300 Schritte bergab.
Die gestrichelte Linie ist der Verlust des Zählmodells aus Notebook 1.

Die Lernrate 50 wirkt riesig. Weil der Verlust aber ein Durchschnitt über etwa 9600 Beispiele ist, sind die Gradienten winzig.
Welche Lernrate passt, hängt immer vom Problem ab. Man findet sie durch Ausprobieren.
""")
,
code(r"""
bigramm_netz = BigrammNetz(V)

zaehl_verlust = durchschnittlicher_verlust(NGramModell(training, 1), training)
kurve = grafik2.LiveKurve(titel="Das Bigramm-Netz lernt", ziel=zaehl_verlust, ziel_text="Zählmodell")

for schritt in range(301):
    verlust = bigramm_netz.trainingsschritt(eingaben, ziele_training, lernrate=50)
    if schritt % 10 == 0:
        kurve.punkt(schritt, verlust)
""")
,
md(r"""
Der Verlust fällt schnell und nähert sich der gestrichelten Linie. Das Netz hat **selbst herausgefunden**, was du in Notebook 1 gezählt hast.
Vergleich die beiden Matrizen:
""")
,
code(r"""
P_gelernt = bigramm_netz.vorhersage(list(range(V)))     # eine Zeile für jedes Zeichen

grafik2.heatmaps_vergleich(
    P_gezaehlt, P_gelernt, vocabulary.zeichen,
    "Gezählt (Notebook 1)", "Gelernt (Bigramm-Netz)",
)
""")
,
md(r"""
Fast gleich. Und jetzt der Test, an dem das Zählmodell in Notebook 1 gescheitert ist, der **unbekannte Text**:
""")
,
code(r"""
P_test = bigramm_netz.vorhersage(ids_test[:-1])
print("Bigramm-Netz auf dem Testtext:", kreuzentropie(P_test, torch.tensor(ids_test[1:])).item())
print("Zählmodell auf dem Testtext:  ", durchschnittlicher_verlust(NGramModell(training, 1), test))
""")
,
md(r"""
Das Netz hat einen **endlichen** Testverlust. Der Grund ist die Softmax: Sie gibt nie genau 0 heraus,
also hält das Netz kein Zeichen für völlig unmöglich. **Problem 2 aus Notebook 1 ist gelöst.**
""")
,

# =============================================================
# TEIL 9: TEXT GENERIEREN
# =============================================================

md(r"""
---
# Teil 9: Das Netz schreibt

Zum Schluss soll das Netz Text erzeugen. Dafür verwenden wir deine Funktion `ziehe_zeichen` aus Notebook 1.
Sie erwartet ein Dictionary `{zeichen: wahrscheinlichkeit}`. Das Netz liefert aber einen Tensor.

---
## Aufgabe 2.10: Text generieren mit dem Netz

Du brauchst zwei Funktionen:

**`naechste_verteilung(netz, vocabulary, text)`**
1. Nimm das **letzte Zeichen** von `text` und hol dir seine ID aus `vocabulary.zeichen_zu_id`.
2. Rufe `netz.vorhersage([id])` auf. Heraus kommt eine Matrix mit einer Zeile. Davon brauchst du die Zeile `[0]`.
3. Mach daraus mit `.tolist()` eine normale Python-Liste von Zahlen.
4. Gib ein Dictionary `{zeichen: wahrscheinlichkeit}` zurück. Die Zuordnung ID zu Zeichen steht in `vocabulary.id_zu_zeichen`.

**`generiere(netz, vocabulary, start, laenge)`** funktioniert wie `generiere_bigramm` aus Notebook 1:
Sie hängt `laenge`-mal ein mit `ziehe_zeichen` gezogenes Zeichen an den Text an.
Ein "unbekanntes Zeichen" kann hier nicht mehr vorkommen. Das Netz hat immer eine Antwort.
""")
,
aufgabe(
vorlage=r"""
def naechste_verteilung(netz, vocabulary, text):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 2.10: Hier fehlt noch dein Code")


def generiere(netz, vocabulary, start, laenge):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 2.10: Hier fehlt noch dein Code")
""",
loesung=r"""
def naechste_verteilung(netz, vocabulary, text):
    id = vocabulary.zeichen_zu_id[text[-1]]
    werte = netz.vorhersage([id])[0].tolist()
    return {vocabulary.id_zu_zeichen[i]: p for i, p in enumerate(werte)}


def generiere(netz, vocabulary, start, laenge):
    text = start
    for _ in range(laenge):
        text += ziehe_zeichen(naechste_verteilung(netz, vocabulary, text))
    return text
""")
,
code(r"""
nb2.pruefe_aufgabe_10(naechste_verteilung, generiere)
""")
,
tipps(
    hinweis=r"""
    **naechste_verteilung** in vier Schritten, wie in der Aufgabe beschrieben:
    ID des letzten Zeichens holen, `netz.vorhersage([id])` aufrufen, Zeile `[0]` nehmen und mit `.tolist()` in eine Liste umwandeln.
    Danach brauchst du zu jeder Position `i` in dieser Liste das passende Zeichen. Das kennst du vom `Vocabulary`: `enumerate`.

    **generiere** ist wie `generiere_bigramm` aus Notebook 1, nur ohne `break`. Das Netz hat immer eine Verteilung.
    """,
    fast=r"""
    ```python
    def naechste_verteilung(netz, vocabulary, text):
        id = vocabulary.zeichen_zu_id[text[-1]]
        werte = netz.vorhersage([id])[0].tolist()
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
        id = vocabulary.zeichen_zu_id[text[-1]]
        werte = netz.vorhersage([id])[0].tolist()
        return {vocabulary.id_zu_zeichen[i]: p for i, p in enumerate(werte)}


    def generiere(netz, vocabulary, start, laenge):
        text = start
        for _ in range(laenge):
            text += ziehe_zeichen(naechste_verteilung(netz, vocabulary, text))
        return text
    ```
    - `netz.vorhersage([id])` bekommt eine Liste mit einer ID und liefert eine Matrix mit **einer** Zeile. `[0]` holt diese Zeile.
    - `.tolist()` macht aus dem Tensor eine normale Liste, zum Beispiel `[0.01, 0.3, ...]`. Position `i` gehört zum Zeichen mit der ID `i`.
    - Die Dictionary Comprehension baut daraus `{' ': 0.01, 'a': 0.3, ...}`. Genau dieses Format erwartet `ziehe_zeichen` aus Notebook 1.
    - `generiere` hängt in jedem Durchlauf ein gezogenes Zeichen an. Weil `naechste_verteilung` immer auf `text[-1]` schaut,
      bestimmt das neue Zeichen den nächsten Schritt.
    """,
)
,
md(r"""
Das Netz schreibt! Führ die Zelle ruhig mehrmals aus.
""")
,
code(r"""
print(generiere(bigramm_netz, vocabulary, "d", 300))
""")
,
md(r"""
Kommt dir das bekannt vor? Der Text sieht aus wie der Bigramm-Text aus Notebook 1. Das ist kein Zufall:
Das Netz hat genau das gelernt, was das Zählmodell weiß. Es sieht ja auch nur **ein** Zeichen als Kontext.

Hier noch einmal Schritt für Schritt. Das ist dieselbe Animation wie in Notebook 1, jetzt mit deinem Netz:
""")
,
code(r"""
grafik.generierung_schritt_fuer_schritt(
    start="d",
    schritte=40,
    verteilung_fuer=lambda bisher: naechste_verteilung(bigramm_netz, vocabulary, bisher),
    ziehe_zeichen=ziehe_zeichen,
)
""")
,

# =============================================================
# ABSCHLUSS
# =============================================================

md(r"""
---
# Abschluss: Deinen Code speichern

Die nächste Zelle prüft alle Aufgaben noch einmal und speichert deinen Code in `meincode/notebook2.py`.
""")
,
code(r"""
nb2.speichern(
    zeilen_normieren,
    bigramm_matrix,
    one_hot,
    softmax,
    kreuzentropie,
    numerische_ableitung,
    gradientenabstieg,
    gradientenschritt,
    BigrammNetz,
    naechste_verteilung,
    generiere,
)
""")
,
md(r"""
## Zusammenfassung

| Begriff | Bedeutung |
|---|---|
| **Tensor, Form** | Tabelle von Zahlen in PyTorch, z. B. Form `(N, V)` |
| **Matrixmultiplikation** `@` | gewichtete Summen; $(N, V) \mathbin{@} (V, M) = (N, M)$ |
| **One-Hot** | Zeichen als Reihe mit einer einzigen 1. Mal einer Matrix wählt es eine Zeile aus. |
| **Gewichte** | die Zahlen, die das Netz lernt |
| **Logits** | Ausgaben des Netzes vor der Softmax |
| **Softmax** | macht aus Logits eine Wahrscheinlichkeitsverteilung, nie genau 0 |
| **Kreuzentropie** | der durchschnittliche Verlust, wie in Notebook 1 |
| **Steigung, Ableitung** | wie stark sich der Verlust ändert, wenn man an einem Gewicht dreht |
| **Gradient** | die Steigungen für alle Gewichte zusammen |
| **Gradientenabstieg** | Gewichte in kleinen Schritten gegen den Gradienten verändern |
| **Lernrate** | die Schrittgröße. Zu klein ist langsam, zu groß geht schief. |
| `requires_grad`, `backward()`, `.grad` | PyTorch merkt sich die Rechnung und berechnet den Gradienten |
| **Backpropagation** | so heißt das Rückwärtsrechnen des Gradienten durch alle Rechenschritte |

## Ausblick auf Notebook 3

Dein Bigramm-Netz ist so gut wie das Zählmodell, aber nicht besser. Es sieht nur ein Zeichen Kontext,
und **Problem 1** aus Notebook 1 ist noch offen: Ähnliche Kontexte werden nicht ähnlich behandelt.

In Notebook 3 baust du ein **größeres Netz**, das mehrere Zeichen Kontext sieht und mit unbekannten Kontexten zurechtkommt.
Dabei lernst du die fertigen Bausteine von PyTorch kennen. Du wirst sehen, dass vieles davon genau das ist, was du hier selbst gebaut hast.
""")
,
]
