"""Inhalt von Notebook 4: Zurückschauen."""

from .bausteine import aufgabe, code, md, tipps

ZELLEN = [

# =============================================================
# WILLKOMMEN
# =============================================================

md(r"""
# Notebook 4: Zurückschauen

## Wie ein Zeichen alle Zeichen davor sehen kann

Dein `ZeichenNetz` aus Notebook 3 sieht drei Zeichen. Das ist ein sehr kurzes Gedächtnis.
Am Ende eines Satzes weiß es nicht mehr, wie der Satz angefangen hat.

In diesem Notebook lernst du eine neue Idee kennen: Statt eines festen Fensters darf jedes Zeichen
**auf alle Zeichen davor zurückschauen**. Das ist die Grundlage für die **Aufmerksamkeit** in Notebook 5,
den wichtigsten Baustein moderner Sprachmodelle.

Dieses Notebook ist kürzer als die letzten, und es wird nichts trainiert. Dafür lernst du einen Trick kennen,
der in jedem großen Sprachmodell steckt.

### Der Plan für dieses Notebook

| Teil | Was passiert |
|---|---|
| 1 | Warum ein größeres Fenster nicht hilft |
| 2 | Die einfachste Art zurückzuschauen: der Durchschnitt |
| 3 | Derselbe Durchschnitt mit einer einzigen Matrix |
| 4 | Nicht in die Zukunft schauen |
| 5 | Nicht alle Zeichen sind gleich wichtig |
""")
,
md(r"""
## Vorbereitung
""")
,
code(r"""
import time

import torch
import torch.nn.functional as F

from kurswerkzeuge import grafik4, nb4

nb4.pruefe_vorarbeit()

from meincode.notebook1 import Vocabulary
from meincode.notebook2 import softmax, zeilen_normieren
from meincode.notebook3 import ZeichenNetz, baue_beispiele, trainiere

with open("daten/training.txt", encoding="utf-8") as datei:
    trainingstext = datei.read()

grenze = int(len(trainingstext) * 0.9)
vocabulary = Vocabulary(trainingstext)
V = len(vocabulary)
ids_training = vocabulary.encode(trainingstext[:grenze])
ids_test = vocabulary.encode(trainingstext[grenze:])

print("Alles bereit!")
""")
,

# =============================================================
# TEIL 1: DAS FESTE FENSTER
# =============================================================

md(r"""
---
# Teil 1: Warum ein größeres Fenster nicht hilft

Die naheliegende Idee: Wir geben dem `ZeichenNetz` einfach mehr Kontext. Probieren wir 3, 8 und 16 Zeichen aus.
Die nächste Zelle trainiert drei Netze mit deinen Funktionen aus Notebook 3. Das dauert ungefähr eine halbe Minute.
""")
,
code(r"""
def verlust_auf(netz, X, Y):
    with torch.no_grad():
        return F.cross_entropy(netz(X), Y).item()


ergebnisse = []
for kontext in [3, 8, 16]:
    X_training, Y_training = baue_beispiele(ids_training, kontext)
    X_test, Y_test = baue_beispiele(ids_test, kontext)

    torch.manual_seed(1)
    netz = ZeichenNetz(V, kontext, koordinaten=10, neuronen=100)
    trainiere(netz, X_training, Y_training, schritte=10000, lernrate=0.1)

    gewichte = sum(p.numel() for p in netz.parameters())
    ergebnisse.append((kontext, gewichte, verlust_auf(netz, X_training, Y_training), verlust_auf(netz, X_test, Y_test)))
    print(f"Kontext {kontext:2d}: fertig")

grafik4.fenster_ergebnisse(ergebnisse)
""")
,
md(r"""
Mehr Kontext macht das Netz auf dem Training besser, auf dem Test aber **viel schlechter**. Das ist Overfitting, wie in Notebook 3.

Der Grund liegt im Aufbau. Das Netz hängt die Koordinaten aller Zeichen **nebeneinander**:
- Mit jedem Zeichen mehr wird die Eingabe länger und die Matrix `W1` größer. Mehr Gewichte heißt mehr Platz zum Auswendiglernen.
- Jede Position hat **eigene** Gewichte. Ein `e` an Position 1 und ein `e` an Position 2 werden ganz unterschiedlich verarbeitet.
  Was das Netz über ein `e` an einer Stelle lernt, nützt ihm an einer anderen Stelle nichts.

Wir brauchen also eine Art, auf viele Zeichen zurückzuschauen, **ohne** dass das Netz dabei immer größer wird.
""")
,

# =============================================================
# TEIL 2: DER DURCHSCHNITT
# =============================================================

md(r"""
---
# Teil 2: Die einfachste Art zurückzuschauen

Die neue Idee: Wir hängen die Zeichen nicht mehr nebeneinander, sondern **mischen** sie.
Jedes Zeichen bekommt eine Zusammenfassung aller Zeichen davor. Die einfachste Zusammenfassung ist der **Durchschnitt**.

Ein Durchschnitt hat immer dieselbe Größe, egal ob er aus 3 oder aus 300 Zeichen gebildet wird. Genau das wollen wir.

### Ein Text als Tabelle

Ab jetzt ist ein Text eine Tabelle `x` mit einer Zeile pro Zeichen. In jeder Zeile stehen die Koordinaten des Zeichens,
also seine Einbettung aus Notebook 3. Die Form ist `(T, C)`: `T` Zeichen mit je `C` Koordinaten.

Hier ein kleines Beispiel mit 4 Zeichen und 2 Koordinaten. Die Zahlen sind ausgedacht, damit man gut rechnen kann:
""")
,
code(r"""
x = torch.tensor([
    [2.0, 0.0],     # h
    [0.0, 4.0],     # u
    [4.0, 2.0],     # n
    [2.0, 2.0],     # d
])
grafik4.tabelle(x, ["h", "u", "n", "d"], "x: das Wort 'hund' als Tabelle")
""")
,
md(r"""
Der Durchschnitt für jedes Zeichen:

| Zeichen | schaut zurück auf | Durchschnitt |
|---|---|---|
| `h` | `h` | `[2, 0]` |
| `u` | `h`, `u` | `[1, 2]` |
| `n` | `h`, `u`, `n` | `[2, 2]` |
| `d` | `h`, `u`, `n`, `d` | `[2, 2]` |

Das `d` weiß jetzt etwas über das ganze Wort, nicht nur über sich selbst.

### Werkzeuge für die Aufgabe

- `x[:t + 1]` sind die Zeilen 0 bis einschließlich `t`, also das Zeichen `t` und alle davor.
- `.mean(dim=0)` bildet den Durchschnitt **nach unten**, also über die Zeilen. Übrig bleibt eine Zeile.
- `torch.zeros_like(x)` legt eine Tabelle voller Nullen an, die genauso groß ist wie `x`.
""")
,
code(r"""
print("Zeilen 0 bis 1:\n", x[:2])
print("Durchschnitt nach unten:", x[:2].mean(dim=0))
""")
,
md(r"""
---
## Aufgabe 4.1: Der Durchschnitt aller bisherigen Zeichen

Schreibe die Funktion `durchschnitt_bisher(x)`:

1. `ergebnis = torch.zeros_like(x)`
2. Für jede Zeile `t` von `0` bis `x.shape[0] - 1`: `ergebnis[t]` ist der Durchschnitt von `x[:t + 1]`
3. `ergebnis` zurückgeben
""")
,
aufgabe(
vorlage=r"""
def durchschnitt_bisher(x):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 4.1: Hier fehlt noch dein Code")
""",
loesung=r"""
def durchschnitt_bisher(x):
    ergebnis = torch.zeros_like(x)
    for t in range(x.shape[0]):
        ergebnis[t] = x[:t + 1].mean(dim=0)
    return ergebnis
""")
,
code(r"""
nb4.pruefe_aufgabe_1(durchschnitt_bisher)
""")
,
tipps(
    hinweis=r"""
    Zeile `t` des Ergebnisses ist der Durchschnitt der Zeilen 0 bis einschließlich `t` von `x`.

    - Die Zeilen 0 bis `t` bekommst du mit `x[:t + 1]`. Das `+ 1` ist nötig, weil die Grenze beim Ausschneiden nicht mitzählt.
    - Den Durchschnitt nach unten, also über die Zeilen hinweg, berechnet `.mean(dim=0)`.

    Leg das Ergebnis als neue Tabelle an. Verändere `x` selbst nicht.
    """,
    fast=r"""
    ```python
    ergebnis = torch.zeros_like(x)
    for t in range(x.shape[0]):
        ergebnis[t] = x[...].mean(dim=...)
    return ergebnis
    ```
    """,
    loesung=r"""
    ```python
    def durchschnitt_bisher(x):
        ergebnis = torch.zeros_like(x)
        for t in range(x.shape[0]):
            ergebnis[t] = x[:t + 1].mean(dim=0)
        return ergebnis
    ```
    Am Beispiel `x = [[1, 2], [3, 4], [5, 9]]`:

    - `torch.zeros_like(x)` legt eine Tabelle voller Nullen mit derselben Form an.
    - Bei `t = 0` ist `x[:1]` nur `[[1, 2]]`, der Durchschnitt ist `[1, 2]`.
    - Bei `t = 1` ist `x[:2]` gleich `[[1, 2], [3, 4]]`. `.mean(dim=0)` rechnet spaltenweise: `[(1+3)/2, (2+4)/2] = [2, 3]`.
    - Bei `t = 2` werden alle drei Zeilen gemittelt: `[3, 5]`.
    """,
)
,
code(r"""
grafik4.tabelle(durchschnitt_bisher(x), ["h", "u", "n", "d"], "durchschnitt_bisher(x)")
""")
,

# =============================================================
# TEIL 3: DER MATRIX-TRICK
# =============================================================

md(r"""
---
# Teil 3: Derselbe Durchschnitt mit einer einzigen Matrix

Deine Funktion ist richtig, hat aber eine Schleife. Bei langen Texten ist das langsam.
Aus Notebook 2 weißt du: Eine Matrixmultiplikation bildet **gewichtete Summen**. Und ein Durchschnitt ist eine gewichtete Summe!

Der Durchschnitt von drei Zeilen ist zum Beispiel $\frac{1}{3} \cdot \text{Zeile}_0 + \frac{1}{3} \cdot \text{Zeile}_1 + \frac{1}{3} \cdot \text{Zeile}_2$.

Wir brauchen also eine Matrix `A`, in der für jedes Zeichen die Gewichte stehen. Für 4 Zeichen:

| | h | u | n | d |
|---|---|---|---|---|
| **h** | 1 | 0 | 0 | 0 |
| **u** | 1/2 | 1/2 | 0 | 0 |
| **n** | 1/3 | 1/3 | 1/3 | 0 |
| **d** | 1/4 | 1/4 | 1/4 | 1/4 |

Dann ist `A @ x` genau der Durchschnitt aller bisherigen Zeichen, für alle Zeichen auf einmal.

### So baust du die Matrix

1. `torch.ones(T, T)` ist eine Matrix voller Einsen.
2. `torch.tril(...)` behält nur das **untere Dreieck** (*triangle lower*) und setzt alles rechts oberhalb der Diagonale auf 0.
3. Jede Zeile durch ihre Summe teilen. Das kann deine Funktion `zeilen_normieren` aus Notebook 2!
""")
,
code(r"""
print(torch.tril(torch.ones(4, 4)))
""")
,
md(r"""
---
## Aufgabe 4.2: Der Durchschnitt als Matrix

Schreibe die Funktion `mittelwert_matrix(T)`, die die Matrix `A` für `T` Zeichen zurückgibt.
""")
,
aufgabe(
vorlage=r"""
def mittelwert_matrix(T):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 4.2: Hier fehlt noch dein Code")
""",
loesung=r"""
def mittelwert_matrix(T):
    return zeilen_normieren(torch.tril(torch.ones(T, T)))
""")
,
code(r"""
nb4.pruefe_aufgabe_2(mittelwert_matrix)
""")
,
tipps(
    hinweis=r"""
    Die Matrix entsteht in zwei Schritten, die oben im Text beschrieben sind:

    1. Ein Dreieck aus Einsen: unten links und auf der Diagonale 1, rechts oben 0. Das liefert `torch.tril(...)` aus einer Matrix voller Einsen.
    2. Jede Zeile durch ihre Summe teilen. Dafür hast du in Notebook 2 eine Funktion geschrieben.
    """,
    fast=r"""
    ```python
    dreieck = torch.tril(torch.ones(T, T))
    return ...(dreieck)
    ```
    """,
    loesung=r"""
    ```python
    def mittelwert_matrix(T):
        return zeilen_normieren(torch.tril(torch.ones(T, T)))
    ```
    Für `T = 3`:

    - `torch.ones(3, 3)` ist eine Matrix voller Einsen.
    - `torch.tril(...)` behält nur das untere Dreieck mit der Diagonale: `[[1, 0, 0], [1, 1, 0], [1, 1, 1]]`.
      Zeile `t` hat also genau `t + 1` Einsen, eine für jedes Zeichen bis einschließlich `t`.
    - `zeilen_normieren` teilt jede Zeile durch ihre Summe: `[[1, 0, 0], [1/2, 1/2, 0], [1/3, 1/3, 1/3]]`.

    Mit `A @ x` bekommt jede Zeile dann genau den Durchschnitt aller Zeichen bis zu ihr. Das ist dasselbe wie in Aufgabe 4.1, nur ohne Schleife.
    """,
)
,
code(r"""
A = mittelwert_matrix(4)
grafik4.gewichte_bild(A, "hund", "Die Matrix A: Jedes Zeichen schaut gleichmäßig zurück")

print("Gleiches Ergebnis wie die Schleife:", torch.allclose(A @ x, durchschnitt_bisher(x)))
""")
,
md(r"""
Die grauen Felder rechts oben sind die **Zukunft**: Dort steht 0, ein Zeichen schaut nie auf spätere Zeichen.

Wie viel schneller ist die Matrix? Ein Vergleich mit 1000 Zeichen und je 64 Koordinaten:
""")
,
code(r"""
gross = torch.randn(1000, 64)

start = time.time()
mit_schleife = durchschnitt_bisher(gross)
zeit_schleife = time.time() - start

start = time.time()
mit_matrix = mittelwert_matrix(1000) @ gross
zeit_matrix = time.time() - start

print(f"Schleife: {zeit_schleife * 1000:.1f} Millisekunden")
print(f"Matrix:   {zeit_matrix * 1000:.1f} Millisekunden")
print("Gleiches Ergebnis:", torch.allclose(mit_schleife, mit_matrix, atol=1e-5))
""")
,

# =============================================================
# TEIL 4: NICHT IN DIE ZUKUNFT SCHAUEN
# =============================================================

md(r"""
---
# Teil 4: Nicht in die Zukunft schauen

Warum ist es so wichtig, dass ein Zeichen nicht auf spätere Zeichen schaut?

Beim Training soll **jedes** Zeichen das nächste vorhersagen. Wenn das `n` in "hund" schon das `d` sehen könnte,
wäre die Vorhersage einfach: abschreiben. Das Netz würde nur lernen zu spicken und könnte später keinen neuen Text erzeugen,
denn beim Generieren gibt es die Zukunft noch nicht.

### Punkte statt fester Gewichte

Bisher schaut jedes Zeichen **gleichmäßig** auf alle Zeichen davor. Später soll das Netz selbst entscheiden,
welche Zeichen wichtig sind. Dafür vergibt jedes Zeichen **Punkte** an die Zeichen davor: viele Punkte heißt "wichtig".

Aus Punkten macht die **Softmax** Gewichte, die zusammen 1 ergeben. Das kennst du aus Notebook 2.
Aber die Zukunft muss dabei **genau 0** bekommen. Der Trick: Wir schreiben dort **minus unendlich** hin.
`torch.exp` von minus unendlich ist genau 0, und so wird auch das Gewicht genau 0.
""")
,
code(r"""
print("exp(-unendlich) =", torch.exp(torch.tensor(float("-inf"))))

punkte = torch.tensor([[1.0, 2.0, float("-inf")]])
print("softmax von [1, 2, -inf] =", softmax(punkte))
""")
,
md(r"""
### Werkzeug: `masked_fill`

`punkte.masked_fill(bedingung, wert)` schreibt `wert` überall dorthin, wo `bedingung` wahr ist, und lässt den Rest gleich.
Die Bedingung ist eine Tabelle aus `True` und `False`. Die Zukunft finden wir so:
Im unteren Dreieck `torch.tril(torch.ones(T, T))` steht dort 0, also ist `... == 0` genau in der Zukunft wahr.
""")
,
code(r"""
print(torch.tril(torch.ones(3, 3)) == 0)
""")
,
md(r"""
---
## Aufgabe 4.3: Nicht in die Zukunft schauen

Schreibe die Funktion `maskieren(punkte)`:

1. `T = punkte.shape[-1]`. Das ist die Anzahl der Spalten. `-1` heißt "die letzte Richtung".
2. `zukunft = torch.tril(torch.ones(T, T)) == 0`
3. `punkte.masked_fill(zukunft, float("-inf"))` zurückgeben

Warum `shape[-1]` statt `shape[1]`? Beim Training rechnet das Netz viele Texte gleichzeitig.
Dann sind die Punkte ein **Stapel** aus Tabellen, Form `(Anzahl, T, T)`. Mit `-1` funktioniert deine Funktion für beides.
""")
,
aufgabe(
vorlage=r"""
def maskieren(punkte):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 4.3: Hier fehlt noch dein Code")
""",
loesung=r"""
def maskieren(punkte):
    T = punkte.shape[-1]
    zukunft = torch.tril(torch.ones(T, T)) == 0
    return punkte.masked_fill(zukunft, float("-inf"))
""")
,
code(r"""
nb4.pruefe_aufgabe_3(maskieren)
""")
,
tipps(
    hinweis=r"""
    Drei Schritte, wie in der Aufgabe:

    1. Die Größe `T` aus der **letzten** Richtung der Punkte holen.
    2. Herausfinden, wo die Zukunft ist. `torch.tril(torch.ones(T, T))` hat in der Zukunft (rechts oben) Nullen.
       Der Vergleich `== 0` macht daraus eine Tabelle aus `True` und `False`.
    3. `masked_fill` ersetzt alle Felder, an denen `True` steht, durch einen Wert. Hier ist das minus unendlich.
    """,
    fast=r"""
    ```python
    T = punkte.shape[...]
    zukunft = torch.tril(torch.ones(T, T)) == ...
    return punkte.masked_fill(zukunft, ...)
    ```
    """,
    loesung=r"""
    ```python
    def maskieren(punkte):
        T = punkte.shape[-1]
        zukunft = torch.tril(torch.ones(T, T)) == 0
        return punkte.masked_fill(zukunft, float("-inf"))
    ```
    - `punkte.shape[-1]` ist die Anzahl der Spalten. Mit `-1` klappt das auch bei einem Stapel mit Form `(Anzahl, T, T)`.
    - `zukunft` ist für `T = 3`:
      `[[False, True, True], [False, False, True], [False, False, False]]`. `True` steht genau dort, wo ein Zeichen in die Zukunft schauen würde.
    - `masked_fill` schreibt dort `float("-inf")` hinein. Die Softmax macht aus minus unendlich später genau 0.
      Mit einer 0 statt minus unendlich ginge das nicht: Die Softmax macht aus 0 eine positive Zahl, und die Zukunft würde mitzählen.
    """,
)
,
md(r"""
### Die eingebaute Softmax

Ab jetzt verwenden wir die Softmax, die in PyTorch eingebaut ist: `torch.softmax(punkte, dim=-1)`.
Sie macht dasselbe wie deine, das prüfen wir gleich. Mit `dim=-1` arbeitet sie in der letzten Richtung,
also zeilenweise. So funktioniert sie auch mit einem Stapel aus Tabellen.

Wenn alle Punkte gleich sind, zum Beispiel alle 0, kommt nach Maskieren und Softmax genau die Durchschnitts-Matrix heraus:
""")
,
code(r"""
punkte = torch.zeros(4, 4)
gewichte = torch.softmax(maskieren(punkte), dim=-1)

print("Gleich wie deine Softmax:     ", torch.allclose(gewichte, softmax(maskieren(punkte))))
print("Gleich wie mittelwert_matrix: ", torch.allclose(gewichte, mittelwert_matrix(4)))
""")
,
md(r"""
Der Durchschnitt ist also ein Sonderfall: Jedes Zeichen gibt allen Zeichen davor gleich viele Punkte.
""")
,

# =============================================================
# TEIL 5: GEWICHTETER DURCHSCHNITT
# =============================================================

md(r"""
---
# Teil 5: Nicht alle Zeichen sind gleich wichtig

Mit Punkten kann jedes Zeichen selbst bestimmen, wie stark es auf welches frühere Zeichen schaut.
Probier es aus: Das `e` in "katze" vergibt Punkte an alle Zeichen bis zu sich selbst.

- Was passiert, wenn alle Punkte gleich sind?
- Wie bekommt das `k` fast das ganze Gewicht?
- Was passiert, wenn du **alle** Punkte um denselben Wert erhöhst? (Erinnerst du dich an Notebook 2?)
""")
,
code(r"""
grafik4.punkte_regler(maskieren)
""")
,
md(r"""
---
## Aufgabe 4.4: Der gewichtete Durchschnitt

Schreibe die Funktion `gewichteter_durchschnitt(punkte, x)`. Sie setzt alles aus diesem Notebook zusammen:

1. Die Punkte maskieren
2. Mit `torch.softmax(..., dim=-1)` in Gewichte umwandeln
3. Die Gewichte mit `@` auf `x` anwenden und das Ergebnis zurückgeben
""")
,
aufgabe(
vorlage=r"""
def gewichteter_durchschnitt(punkte, x):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 4.4: Hier fehlt noch dein Code")
""",
loesung=r"""
def gewichteter_durchschnitt(punkte, x):
    gewichte = torch.softmax(maskieren(punkte), dim=-1)
    return gewichte @ x
""")
,
code(r"""
nb4.pruefe_aufgabe_4(gewichteter_durchschnitt)
""")
,
tipps(
    hinweis=r"""
    Hier setzt du nur zusammen, was es schon gibt:

    1. deine Funktion `maskieren` auf die Punkte anwenden
    2. `torch.softmax(..., dim=-1)` macht aus jeder Zeile Gewichte, die zusammen 1 ergeben
    3. die Gewichte mit `@` auf `x` anwenden, genau wie die Matrix `A` in Aufgabe 4.2
    """,
    fast=r"""
    ```python
    gewichte = torch.softmax(maskieren(...), dim=...)
    return ... @ ...
    ```
    """,
    loesung=r"""
    ```python
    def gewichteter_durchschnitt(punkte, x):
        gewichte = torch.softmax(maskieren(punkte), dim=-1)
        return gewichte @ x
    ```
    - `maskieren(punkte)` setzt die Zukunft auf minus unendlich.
    - `torch.softmax(..., dim=-1)` rechnet die Softmax für jede Zeile. Die Zukunft bekommt das Gewicht 0, die übrigen Gewichte ergeben zusammen 1.
      `dim=-1` heißt "entlang der letzten Richtung". So funktioniert es auch mit einem Stapel aus mehreren Tabellen.
    - `gewichte @ x` mischt die Zeilen von `x` mit diesen Gewichten.

    Sind alle Punkte gleich, sind auch die Gewichte gleich verteilt, und es kommt der normale Durchschnitt aus Aufgabe 4.2 heraus.
    """,
)
,
md(r"""
Ein Beispiel mit "hund": Das `d` vergibt viele Punkte an das `h`, die anderen schauen gleichmäßig zurück.
""")
,
code(r"""
punkte = torch.zeros(4, 4)
punkte[3, 0] = 3.0         # das d (Zeile 3) gibt dem h (Spalte 0) 3 Punkte

gewichte = torch.softmax(maskieren(punkte), dim=-1)
grafik4.gewichte_bild(gewichte, "hund", "Das d schaut vor allem auf das h")
grafik4.tabelle(gewichteter_durchschnitt(punkte, x), ["h", "u", "n", "d"], "gewichteter_durchschnitt(punkte, x)")
""")
,
md(r"""
Die letzte Zeile liegt jetzt nah an den Koordinaten von `h`, also `[2, 0]`.

### Was noch fehlt

Zwei Fragen sind noch offen.

**1. Woher kommen die Punkte?** Bisher haben wir sie von Hand festgelegt. In Notebook 5 lernt das Netz,
die Punkte selbst zu berechnen. Jedes Zeichen stellt dazu eine Art **Frage**, und jedes frühere Zeichen hat ein **Schlagwort**.
Je besser Frage und Schlagwort zusammenpassen, desto mehr Punkte. Das ist die **Aufmerksamkeit**.

**2. Wo bleibt die Reihenfolge?** Schau dir an, was der Durchschnitt aus "ab" und "ba" macht:
""")
,
code(r"""
a = [1.0, 0.0]
b = [0.0, 1.0]
print("Letzte Zeile bei 'ab':", durchschnitt_bisher(torch.tensor([a, b]))[-1])
print("Letzte Zeile bei 'ba':", durchschnitt_bisher(torch.tensor([b, a]))[-1])
""")
,
md(r"""
Für das letzte Zeichen sind "ab" und "ba" gleich. Beim Mischen geht die Reihenfolge verloren, so wie bei einem Smoothie,
dem man nicht mehr ansieht, welches Obst zuerst drin war. "hund" und "dnuh" wären für das Netz dasselbe Wort.
Auch dafür gibt es in Notebook 5 eine einfache Lösung.

---
# Abschluss: Deinen Code speichern
""")
,
code(r"""
nb4.speichern(
    durchschnitt_bisher,
    mittelwert_matrix,
    maskieren,
    gewichteter_durchschnitt,
)
""")
,
md(r"""
## Zusammenfassung

| Begriff | Bedeutung |
|---|---|
| **Festes Fenster** | Zeichen nebeneinanderhängen. Bei langem Kontext riesig und anfällig für Overfitting. |
| **Text als Tabelle** `(T, C)` | eine Zeile pro Zeichen mit seinen Koordinaten |
| **Durchschnitt aller bisherigen Zeichen** | die einfachste Art zurückzuschauen. Immer gleich groß, egal wie lang der Text ist. |
| `torch.tril` | unteres Dreieck einer Matrix. Damit schaut jedes Zeichen nur zurück. |
| **Maskieren** | die Zukunft auf minus unendlich setzen, damit die Softmax dort 0 ergibt |
| `dim=-1` | die letzte Richtung. Funktioniert für eine Tabelle und für einen Stapel aus Tabellen. |
| **Gewichteter Durchschnitt** | Punkte, maskieren, Softmax, `@ x`: jedes Zeichen entscheidet, worauf es schaut |

## Ausblick auf Notebook 5

Du hast jetzt fast alles für die **Aufmerksamkeit** (englisch *attention*) gebaut. Es fehlt nur noch, dass das Netz die Punkte selbst berechnet.
Genau das machst du im nächsten Notebook. Danach trainierst du dein erstes Netz, das auf 32 Zeichen zurückschauen kann.
""")
,
]
