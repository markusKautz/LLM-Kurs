"""Inhalt von Notebook 6: Der Transformer."""

from .bausteine import aufgabe, code, md, tipps

ZELLEN = [

# =============================================================
# WILLKOMMEN
# =============================================================

md(r"""
# Notebook 6: Der Transformer

## Aus einem Kopf wird ein ganzes Modell

In Notebook 5 hast du den wichtigsten Baustein gebaut: einen Aufmerksamkeits-Kopf.
Allein war er aber noch nicht besser als dein `ZeichenNetz`.

In diesem Notebook baust du daraus einen echten **Transformer**. Das ist genau der Aufbau, der auch in GPT steckt.
Dazu kommen vier Zutaten:

| Zutat | Wozu |
|---|---|
| **Mehrere Köpfe** | Mehrere Köpfe achten gleichzeitig auf verschiedene Dinge. |
| **FeedForward** | Mehr Platz, um über das Gesammelte nachzudenken |
| **Abkürzungen und LayerNorm** | Damit auch viele Schichten übereinander gut lernen |
| **Dropout** | Gegen das Auswendiglernen |

Zwei davon baust du selbst, zwei sind fertige Bausteine von PyTorch, die du nur einsetzt.
Am Ende stapelst du mehrere **Transformer-Blöcke** übereinander und trainierst das Ganze.
""")
,
md(r"""
## Vorbereitung
""")
,
code(r"""
import torch
from torch import nn
import torch.nn.functional as F

from kurswerkzeuge import grafik2, grafik4, grafik6, nb6

nb6.pruefe_vorarbeit()

from meincode.notebook1 import Vocabulary
from meincode.notebook3 import ZeichenNetz, baue_beispiele, trainiere, relu
from meincode.notebook4 import maskieren
from meincode.notebook5 import AufmerksamkeitsKopf, AufmerksamkeitsNetz, punkte, ziehe_bloecke, generiere

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
# TEIL 1: MEHRERE KÖPFE
# =============================================================

md(r"""
---
# Teil 1: Mehrere Köpfe

In Notebook 5 hat der Kopf vor allem auf das aktuelle und das vorige Zeichen geschaut.
Für eine gute Vorhersage braucht man aber oft mehrere Dinge gleichzeitig: Welche Buchstaben stehen direkt davor?
Wie hat das Wort angefangen? Steht weiter vorne ein Punkt?

Die Lösung: **mehrere Köpfe nebeneinander**. Stell dir mehrere Leute vor, die denselben Text lesen,
aber jeder mit einer anderen Frage im Kopf. Am Ende legen alle ihre Notizen zusammen.

So funktioniert es:
- Jeder Kopf ist ein `AufmerksamkeitsKopf` aus Notebook 5. Damit es nicht teurer wird, liefert jeder nur `C // anzahl` Zahlen.
  Bei `C = 32` und 4 Köpfen sind das je 8 Zahlen. (`//` ist die Division ohne Rest.)
- Die Ergebnisse aller Köpfe werden mit `torch.cat(..., dim=-1)` **nebeneinandergehängt**. Zusammen sind es wieder `C` Zahlen.
- Eine Schicht `nn.Linear(C, C)`, die **Projektion**, mischt die Notizen der Köpfe zusammen.

### Werkzeug: `nn.ModuleList`

Mehrere Köpfe speichern wir in einer Liste. Es muss aber eine `nn.ModuleList` sein, keine normale Python-Liste.
Nur dann findet `netz.parameters()` die Gewichte der Köpfe, und der Optimierer kann sie trainieren.

```python
self.koepfe = nn.ModuleList([AufmerksamkeitsKopf(C, C // anzahl) for _ in range(anzahl)])
```

---
## Aufgabe 6.1: Mehrere Köpfe

Schreibe die Klasse `MehrereKoepfe(nn.Module)`:

**`__init__(self, C, anzahl)`**:
- `self.koepfe`: eine `nn.ModuleList` mit `anzahl` Köpfen, jeder ist `AufmerksamkeitsKopf(C, C // anzahl)`
- `self.projektion`: `nn.Linear(C, C)`

**`forward(self, x)`**:
1. Jeden Kopf auf `x` anwenden und die Ergebnisse mit `torch.cat([...], dim=-1)` nebeneinanderhängen
2. Das Ergebnis durch `self.projektion` schicken und zurückgeben
""")
,
aufgabe(
vorlage=r"""
class MehrereKoepfe(nn.Module):
    def __init__(self, C, anzahl):
        super().__init__()
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 6.1: Hier fehlt noch dein Code")

    def forward(self, x):
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 6.1: Hier fehlt noch dein Code")
""",
loesung=r"""
class MehrereKoepfe(nn.Module):
    def __init__(self, C, anzahl):
        super().__init__()
        self.koepfe = nn.ModuleList([AufmerksamkeitsKopf(C, C // anzahl) for _ in range(anzahl)])
        self.projektion = nn.Linear(C, C)

    def forward(self, x):
        alle = torch.cat([kopf(x) for kopf in self.koepfe], dim=-1)
        return self.projektion(alle)
""")
,
code(r"""
nb6.pruefe_aufgabe_1(MehrereKoepfe)
""")
,
tipps(
    hinweis=r"""
    - **__init__:** Du brauchst eine Liste mit `anzahl` Köpfen. Eine normale Python-Liste geht hier nicht,
      denn dann findet `netz.parameters()` die Gewichte der Köpfe nicht. Deshalb kommt die Liste in eine `nn.ModuleList(...)`.
      Die Liste selbst baust du mit einer List Comprehension: `[... for _ in range(anzahl)]`.
    - Jeder Kopf liefert `C // anzahl` Zahlen. `//` ist die Ganzzahl-Division. Bei 4 Köpfen und C = 32 sind das 8 Zahlen pro Kopf.
    - **forward:** Jeden Kopf auf `x` anwenden, die Ergebnisse nebeneinanderhängen, durch die Projektion schicken.
    """,
    fast=r"""
    ```python
    def __init__(self, C, anzahl):
        super().__init__()
        self.koepfe = nn.ModuleList([AufmerksamkeitsKopf(C, ...) for _ in range(anzahl)])
        self.projektion = nn.Linear(C, C)

    def forward(self, x):
        alle = torch.cat([... for kopf in self.koepfe], dim=-1)
        return self.projektion(...)
    ```
    """,
    loesung=r"""
    ```python
    class MehrereKoepfe(nn.Module):
        def __init__(self, C, anzahl):
            super().__init__()
            self.koepfe = nn.ModuleList([AufmerksamkeitsKopf(C, C // anzahl) for _ in range(anzahl)])
            self.projektion = nn.Linear(C, C)

        def forward(self, x):
            alle = torch.cat([kopf(x) for kopf in self.koepfe], dim=-1)
            return self.projektion(alle)
    ```
    Mit `C = 32` und 4 Köpfen:

    - Es entstehen 4 Köpfe, jeder liefert 8 Zahlen pro Zeichen. Jeder Kopf hat eigene Gewichte und kann auf etwas anderes achten.
    - `[kopf(x) for kopf in self.koepfe]` ist eine Liste aus 4 Ergebnissen, jedes mit 8 Zahlen pro Zeichen.
    - `torch.cat(..., dim=-1)` hängt sie nebeneinander. Das ergibt wieder 4 · 8 = 32 Zahlen pro Zeichen, also dieselbe Form wie `x`.
    - `self.projektion` mischt die Ergebnisse der Köpfe miteinander, damit sie sich ergänzen können.
    """,
)
,

# =============================================================
# TEIL 2: FEEDFORWARD
# =============================================================

md(r"""
---
# Teil 2: Nachdenken: FeedForward

Die Köpfe **sammeln** Informationen von anderen Zeichen ein. Danach muss jedes Zeichen über das Gesammelte **nachdenken**.
Dafür gibt es eine verborgene Schicht, genau wie in deinem `ZeichenNetz` aus Notebook 3:

`nn.Linear` auf viermal so viele Neuronen, dann ReLU, dann `nn.Linear` zurück auf `C` Zahlen.

Diese Schicht heißt **FeedForward** (vorwärts weitergeben). Sie arbeitet für jedes Zeichen einzeln,
ohne auf andere Zeichen zu schauen. Das Zusammenspiel ist also: **erst sammeln, dann nachdenken**.

---
## Aufgabe 6.2: FeedForward

Schreibe die Klasse `FeedForward(nn.Module)`:

| | |
|---|---|
| `__init__(self, C)` | `self.schicht1 = nn.Linear(C, 4 * C)` und `self.schicht2 = nn.Linear(4 * C, C)` |
| `forward(self, x)` | gibt `self.schicht2(relu(self.schicht1(x)))` zurück |
""")
,
aufgabe(
vorlage=r"""
class FeedForward(nn.Module):
    def __init__(self, C):
        super().__init__()
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 6.2: Hier fehlt noch dein Code")

    def forward(self, x):
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 6.2: Hier fehlt noch dein Code")
""",
loesung=r"""
class FeedForward(nn.Module):
    def __init__(self, C):
        super().__init__()
        self.schicht1 = nn.Linear(C, 4 * C)
        self.schicht2 = nn.Linear(4 * C, C)

    def forward(self, x):
        return self.schicht2(relu(self.schicht1(x)))
""")
,
code(r"""
nb6.pruefe_aufgabe_2(FeedForward)
""")
,
tipps(
    hinweis=r"""
    Das ist ein kleines Netz mit zwei Schichten, wie die Mitte deines `ZeichenNetz`:
    Die erste Schicht macht aus `C` Zahlen `4 * C`, dann kommt ReLU, die zweite Schicht macht wieder `C` Zahlen daraus.

    Im `forward` liest man die Rechnung von innen nach außen: erst `schicht1`, dann `relu`, dann `schicht2`.
    """,
    fast=r"""
    ```python
    def __init__(self, C):
        super().__init__()
        self.schicht1 = nn.Linear(C, ...)
        self.schicht2 = nn.Linear(..., C)

    def forward(self, x):
        return self.schicht2(relu(...))
    ```
    """,
    loesung=r"""
    ```python
    class FeedForward(nn.Module):
        def __init__(self, C):
            super().__init__()
            self.schicht1 = nn.Linear(C, 4 * C)
            self.schicht2 = nn.Linear(4 * C, C)

        def forward(self, x):
            return self.schicht2(relu(self.schicht1(x)))
    ```
    - `schicht1` macht die Koordinaten jedes Zeichens viermal so breit. In diesem breiten Zwischenschritt hat das Netz Platz zum "Nachdenken".
    - `relu` sorgt wie immer dafür, dass das Netz mehr als gerade Linien lernen kann.
    - `schicht2` bringt alles wieder auf `C` Zahlen zurück. Ein- und Ausgabe haben dieselbe Form, damit die Abkürzung im Block funktioniert.

    Wichtig: FeedForward rechnet für jedes Zeichen **einzeln**. Die Zeichen tauschen sich nur in der Aufmerksamkeit aus.
    """,
)
,

# =============================================================
# TEIL 3: DREI FERTIGE ZUTATEN
# =============================================================

md(r"""
---
# Teil 3: Drei fertige Zutaten

Jetzt kommen drei Dinge, die du nicht selbst baust, sondern nur einsetzt. Wichtig ist, dass du weißt, **wozu** sie da sind.

### Abkürzungen

Ein Transformer hat viele Schichten übereinander. Würde jede Schicht die Koordinaten komplett neu berechnen,
ginge auf dem Weg viel verloren, und das Lernen würde sehr schwer.

Deshalb schreibt jeder Teil nur eine **Ergänzung** dazu:

```python
x = x + teil(x)
```

Stell dir ein Dokument vor, das durch mehrere Abteilungen geht. Jede Abteilung schreibt ihre Notizen an den Rand,
statt das Dokument neu zu schreiben. Das Original bleibt erhalten. Beim Lernen kommt der Gradient über diese
Abkürzungen auch direkt bei den ersten Schichten an. Englisch heißt das *residual connection*.

### LayerNorm

`nn.LayerNorm(C)` bringt die Zahlen jedes Zeichens auf eine einheitliche Größe:
Durchschnitt 0 und eine ähnliche Streuung. Das ist wie ein Lautstärkeregler, der dafür sorgt, dass kein Zeichen
"zu laut" oder "zu leise" in die nächste Schicht geht. Das macht das Training stabiler.
""")
,
code(r"""
norm = nn.LayerNorm(4)
x = torch.tensor([[1.0, 2.0, 3.0, 10.0],
                  [100.0, 200.0, 300.0, 1000.0]])

print("vorher:\n", x)
print("nach LayerNorm:\n", norm(x).detach().round(decimals=2))
""")
,
md(r"""
Beide Zeilen sehen danach gleich aus, obwohl die zweite hundertmal größer war. Es kommt nur noch auf das **Muster** an.

### Dropout

`nn.Dropout(0.2)` schaltet beim Training bei jedem Schritt **zufällig 20 % der Zahlen ab** (setzt sie auf 0).
Die übrigen werden etwas größer gemacht, damit die Summe im Schnitt gleich bleibt.

Warum sollte das helfen? Stell dir ein Team vor, in dem jeden Tag zufällig jemand fehlt. Niemand kann sich auf einen
einzelnen Kollegen verlassen, jeder muss das Wichtige selbst können. Genauso kann sich das Netz nicht auf einzelne
Neuronen verlassen und lernt deshalb weniger auswendig.

Beim Testen und beim Generieren soll Dropout **aus** sein. Dafür gibt es zwei Befehle:
- `netz.train()` schaltet in den **Trainingsmodus** (Dropout an)
- `netz.eval()` schaltet in den **Testmodus** (Dropout aus)
""")
,
code(r"""
dropout = nn.Dropout(0.5)
x = torch.ones(10)

dropout.train()
print("Training:", dropout(x))
dropout.eval()
print("Test:    ", dropout(x))
""")
,

# =============================================================
# TEIL 4: DER TRANSFORMER-BLOCK
# =============================================================

md(r"""
---
# Teil 4: Der Transformer-Block

Jetzt setzen wir alles zu einem **Transformer-Block** zusammen. Lies das Bild von unten nach oben:
""")
,
code(r"""
grafik6.transformer_bild()
""")
,
md(r"""
---
## Aufgabe 6.3: Der Transformer-Block

Schreibe die Klasse `TransformerBlock(nn.Module)`:

**`__init__(self, C, koepfe, dropout)`**:

| Attribut | Baustein |
|---|---|
| `self.norm1` | `nn.LayerNorm(C)` |
| `self.aufmerksamkeit` | `MehrereKoepfe(C, koepfe)` |
| `self.norm2` | `nn.LayerNorm(C)` |
| `self.feedforward` | `FeedForward(C)` |
| `self.dropout` | `nn.Dropout(dropout)` |

**`forward(self, x)`**: zwei Zeilen mit Abkürzung, dann `x` zurückgeben:
```python
x = x + self.dropout(self.aufmerksamkeit(self.norm1(x)))
x = x + self.dropout(self.feedforward(self.norm2(x)))
```
""")
,
aufgabe(
vorlage=r"""
class TransformerBlock(nn.Module):
    def __init__(self, C, koepfe, dropout):
        super().__init__()
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 6.3: Hier fehlt noch dein Code")

    def forward(self, x):
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 6.3: Hier fehlt noch dein Code")
""",
loesung=r"""
class TransformerBlock(nn.Module):
    def __init__(self, C, koepfe, dropout):
        super().__init__()
        self.norm1 = nn.LayerNorm(C)
        self.aufmerksamkeit = MehrereKoepfe(C, koepfe)
        self.norm2 = nn.LayerNorm(C)
        self.feedforward = FeedForward(C)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        x = x + self.dropout(self.aufmerksamkeit(self.norm1(x)))
        x = x + self.dropout(self.feedforward(self.norm2(x)))
        return x
""")
,
code(r"""
nb6.pruefe_aufgabe_3(TransformerBlock)
""")
,
tipps(
    hinweis=r"""
    - **__init__:** fünf Zeilen, eine pro Zeile der Tabelle, zum Beispiel `self.norm1 = nn.LayerNorm(C)`.
      `MehrereKoepfe` und `FeedForward` sind deine eigenen Klassen aus Aufgabe 6.1 und 6.2.
    - **forward:** Die beiden Zeilen mit Abkürzung stehen in der Aufgabe. Danach gibst du `x` zurück.

    Lies jede der beiden Zeilen von innen nach außen: normieren, rechnen, Dropout, dann zum alten `x` dazuzählen.
    """,
    fast=r"""
    ```python
    def __init__(self, C, koepfe, dropout):
        super().__init__()
        self.norm1 = nn.LayerNorm(C)
        self.aufmerksamkeit = MehrereKoepfe(C, ...)
        self.norm2 = ...
        self.feedforward = ...
        self.dropout = nn.Dropout(...)

    def forward(self, x):
        x = x + self.dropout(self.aufmerksamkeit(self.norm1(x)))
        x = x + ...
        return x
    ```
    """,
    loesung=r"""
    ```python
    class TransformerBlock(nn.Module):
        def __init__(self, C, koepfe, dropout):
            super().__init__()
            self.norm1 = nn.LayerNorm(C)
            self.aufmerksamkeit = MehrereKoepfe(C, koepfe)
            self.norm2 = nn.LayerNorm(C)
            self.feedforward = FeedForward(C)
            self.dropout = nn.Dropout(dropout)

        def forward(self, x):
            x = x + self.dropout(self.aufmerksamkeit(self.norm1(x)))
            x = x + self.dropout(self.feedforward(self.norm2(x)))
            return x
    ```
    Die erste Zeile im `forward`, von innen nach außen:

    1. `self.norm1(x)` bringt die Zahlen jedes Zeichens in einen gleichmäßigen Bereich.
    2. `self.aufmerksamkeit(...)`: Die Zeichen sammeln Informationen voneinander.
    3. `self.dropout(...)` schaltet beim Training zufällig einzelne Zahlen ab, damit das Netz nicht auswendig lernt.
    4. `x + ...` ist die **Abkürzung**: Das Ergebnis wird zum alten `x` dazugezählt, statt es zu ersetzen.
       So geht nichts verloren, und das Lernen klappt auch bei vielen Blöcken.

    Die zweite Zeile macht dasselbe mit `FeedForward` statt der Aufmerksamkeit. Für beide Teile reicht ein Dropout-Baustein,
    weil er keine Gewichte hat und nur zufällig abschaltet.
    """,
)
,

# =============================================================
# TEIL 5: DER TRANSFORMER
# =============================================================

md(r"""
---
# Teil 5: Der Transformer

Das ganze Modell ist wie dein `AufmerksamkeitsNetz` aus Notebook 5. Statt eines Kopfs und einer Schicht
kommen jetzt mehrere Transformer-Blöcke übereinander. Am Ende steht noch eine LayerNorm, dann die Ausgabe-Schicht.

Jeder Block kann auf das aufbauen, was die Blöcke darunter herausgefunden haben. Untere Blöcke erkennen eher
Buchstabenfolgen, obere eher größere Zusammenhänge.

---
## Aufgabe 6.4: Der Transformer

**`__init__(self, V, kontext, C, koepfe, bloecke, dropout=0.0)`**:

| Attribut | Baustein |
|---|---|
| `self.kontext` | `kontext` |
| `self.zeichen` | `nn.Embedding(V, C)` |
| `self.position` | `nn.Embedding(kontext, C)` |
| `self.bloecke` | `nn.ModuleList` mit `bloecke` Stück `TransformerBlock(C, koepfe, dropout)` |
| `self.norm` | `nn.LayerNorm(C)` |
| `self.ausgabe` | `nn.Linear(C, V)` |

**`forward(self, X)`**:
1. `T = X.shape[-1]` und `x = self.zeichen(X) + self.position(torch.arange(T))`, wie in Notebook 5
2. `for block in self.bloecke:` mit `x = block(x)`
3. `self.ausgabe(self.norm(x))` zurückgeben
""")
,
aufgabe(
vorlage=r"""
class Transformer(nn.Module):
    def __init__(self, V, kontext, C, koepfe, bloecke, dropout=0.0):
        super().__init__()
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 6.4: Hier fehlt noch dein Code")

    def forward(self, X):
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 6.4: Hier fehlt noch dein Code")
""",
loesung=r"""
class Transformer(nn.Module):
    def __init__(self, V, kontext, C, koepfe, bloecke, dropout=0.0):
        super().__init__()
        self.kontext = kontext
        self.zeichen = nn.Embedding(V, C)
        self.position = nn.Embedding(kontext, C)
        self.bloecke = nn.ModuleList([TransformerBlock(C, koepfe, dropout) for _ in range(bloecke)])
        self.norm = nn.LayerNorm(C)
        self.ausgabe = nn.Linear(C, V)

    def forward(self, X):
        T = X.shape[-1]
        x = self.zeichen(X) + self.position(torch.arange(T))
        for block in self.bloecke:
            x = block(x)
        return self.ausgabe(self.norm(x))
""")
,
code(r"""
nb6.pruefe_aufgabe_4(Transformer)
""")
,
tipps(
    hinweis=r"""
    - **__init__:** Die meisten Zeilen kennst du aus dem `AufmerksamkeitsNetz` in Notebook 5.
      Neu ist die Liste der Blöcke. Sie funktioniert wie die Liste der Köpfe in Aufgabe 6.1: eine `nn.ModuleList`
      mit einer List Comprehension, diesmal mit `bloecke` Stück `TransformerBlock(C, koepfe, dropout)`.
    - **forward:** Erst Zeichen und Position einbetten wie in Notebook 5. Dann schickst du `x` der Reihe nach durch jeden Block.
      Jeder Block bekommt das Ergebnis des vorherigen. Zum Schluss normieren und die Logits ausrechnen.
    """,
    fast=r"""
    ```python
    def __init__(self, V, kontext, C, koepfe, bloecke, dropout=0.0):
        super().__init__()
        self.kontext = kontext
        self.zeichen = nn.Embedding(V, C)
        self.position = nn.Embedding(kontext, C)
        self.bloecke = nn.ModuleList([... for _ in range(bloecke)])
        self.norm = nn.LayerNorm(C)
        self.ausgabe = nn.Linear(C, V)

    def forward(self, X):
        T = X.shape[-1]
        x = self.zeichen(X) + self.position(torch.arange(T))
        for block in self.bloecke:
            x = ...
        return self.ausgabe(...)
    ```
    """,
    loesung=r"""
    ```python
    class Transformer(nn.Module):
        def __init__(self, V, kontext, C, koepfe, bloecke, dropout=0.0):
            super().__init__()
            self.kontext = kontext
            self.zeichen = nn.Embedding(V, C)
            self.position = nn.Embedding(kontext, C)
            self.bloecke = nn.ModuleList([TransformerBlock(C, koepfe, dropout) for _ in range(bloecke)])
            self.norm = nn.LayerNorm(C)
            self.ausgabe = nn.Linear(C, V)

        def forward(self, X):
            T = X.shape[-1]
            x = self.zeichen(X) + self.position(torch.arange(T))
            for block in self.bloecke:
                x = block(x)
            return self.ausgabe(self.norm(x))
    ```
    - Der Parameter `bloecke` ist eine Zahl, zum Beispiel 3. Das Attribut `self.bloecke` ist die Liste mit 3 Blöcken.
      Jeder Block hat eigene Gewichte.
    - Die Schleife `x = block(x)` stapelt die Blöcke übereinander. Weil jeder Block dieselbe Form zurückgibt, die er bekommt, passen sie beliebig oft zusammen.
    - Ganz oben normiert `self.norm` noch einmal, dann macht `self.ausgabe` aus den `C` Zahlen jedes Zeichens eine Zahl pro Zeichen im Vokabular.

    Vergleiche mit dem Schaubild oben: Du hast es von unten nach oben in Code übersetzt.
    """,
)
,

# =============================================================
# TEIL 6: TRAINIEREN
# =============================================================

md(r"""
---
# Teil 6: Der Transformer lernt

Die Hilfsfunktionen kennst du aus Notebook 5. Neu ist nur, dass `schaetze_verlust` das Netz für die Messung in den
Testmodus schaltet (Dropout aus) und danach wieder in den Trainingsmodus.

Die Funktion `trainiere_transformer` ist die Trainingsschleife aus Notebook 5, verpackt in eine Funktion.
""")
,
code(r"""
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


def trainiere_transformer(netz, schritte, kurve, lernrate=3e-3, messen_alle=200):
    optimierer = torch.optim.AdamW(netz.parameters(), lr=lernrate)
    for schritt in range(schritte + 1):
        X, Y = ziehe_bloecke(ids_training, netz.kontext, 32)
        verlust = verlust_bloecke(netz, X, Y)
        optimierer.zero_grad()
        verlust.backward()
        optimierer.step()
        if schritt % messen_alle == 0:
            kurve.punkt(schritt, schaetze_verlust(netz, ids_training), schaetze_verlust(netz, ids_test))
""")
,
md(r"""
Zum Vergleich trainieren wir noch einmal das `ZeichenNetz` aus Notebook 3:
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
### Erster Versuch: ohne Dropout

Ein Transformer mit 32 Koordinaten, 4 Köpfen und 2 Blöcken. Das Training dauert etwa eine halbe Minute.
""")
,
code(r"""
torch.manual_seed(1)
transformer = Transformer(V, kontext=32, C=32, koepfe=4, bloecke=2, dropout=0.0)
print("Anzahl Gewichte:", sum(p.numel() for p in transformer.parameters()))

kurve = grafik2.LiveKurve(titel="Transformer ohne Dropout", ziel=zeichen_netz_test, ziel_text="ZeichenNetz")
trainiere_transformer(transformer, 2000, kurve)
""")
,
md(r"""
Am Anfang lernt der Transformer schnell und zieht am `ZeichenNetz` vorbei. Aber dann geht die Schere auf:
Der Trainingsverlust sinkt weiter, der Testverlust steigt wieder. Overfitting! Unser Text hat nur 11.000 Zeichen,
das ist für einen Transformer sehr wenig.

### Zweiter Versuch: mit Dropout
""")
,
code(r"""
torch.manual_seed(1)
transformer = Transformer(V, kontext=32, C=32, koepfe=4, bloecke=2, dropout=0.2)

kurve = grafik2.LiveKurve(titel="Transformer mit Dropout 0.2", ziel=zeichen_netz_test, ziel_text="ZeichenNetz")
trainiere_transformer(transformer, 2000, kurve)
""")
,
md(r"""
Mit Dropout liegen die beiden Linien enger zusammen, und der Testverlust ist am Ende besser. Der Transformer ist jetzt
klar besser als dein `ZeichenNetz`.

Aber der Abstand zwischen Training und Test zeigt: Der Text ist zu klein. Ein Transformer kann viel mehr, wenn er mehr
zu lesen bekommt. Genau das machst du in Notebook 7.
""")
,

# =============================================================
# TEIL 7: DIE KÖPFE
# =============================================================

md(r"""
---
# Teil 7: Worauf schauen die Köpfe?

Jeder der 4 Köpfe im ersten Block hat seine eigenen Fragen und Schlagwörter gelernt.
Die nächste Zelle berechnet ihre Aufmerksamkeit für einen kurzen Text, mit deinen Funktionen `punkte` und `maskieren`.
""")
,
code(r"""
satz = "die luft ist kühl."
gewichte = grafik6.koepfe_gewichte(transformer, vocabulary.encode(satz), punkte, maskieren)
grafik6.koepfe_bild(gewichte, satz)
""")
,
md(r"""
Vergleiche die Köpfe miteinander. Schauen sie alle gleich? Gibt es einen Kopf, der vor allem auf das Zeichen direkt davor schaut?
Einen, der weiter zurückschaut? Einen, der Leerzeichen besonders beachtet?

Man kann sich jeden Kopf einzeln genauer anschauen:
""")
,
code(r"""
grafik4.aufmerksamkeit_erkunden(gewichte[0], satz, "Kopf 1: Worauf schaut dieses Zeichen?")
""")
,
md(r"""
Zum Schluss noch eine Kostprobe:
""")
,
code(r"""
transformer.eval()
print(generiere(transformer, vocabulary, "d", 400))
transformer.train()
""")
,
md(r"""
Deine Funktion `generiere` aus Notebook 5 funktioniert ohne Änderung, denn der Transformer liefert genau wie das
`AufmerksamkeitsNetz` Logits für jede Position.

---
# Abschluss: Deinen Code speichern
""")
,
code(r"""
nb6.speichern(
    MehrereKoepfe,
    FeedForward,
    TransformerBlock,
    Transformer,
)
""")
,
md(r"""
## Zusammenfassung

| Begriff | Bedeutung |
|---|---|
| **Mehrere Köpfe** (Multi-Head Attention) | mehrere Köpfe nebeneinander, jeder achtet auf etwas anderes |
| `nn.ModuleList` | eine Liste von Bausteinen, deren Gewichte PyTorch findet |
| **FeedForward** | die verborgene Schicht aus Notebook 3: Jedes Zeichen denkt über das Gesammelte nach |
| **Abkürzung** (Residual) | `x = x + teil(x)`: Jeder Teil schreibt nur eine Ergänzung dazu |
| **LayerNorm** | bringt die Zahlen jedes Zeichens auf eine einheitliche Größe |
| **Dropout** | schaltet beim Training zufällig Zahlen ab, gegen Auswendiglernen |
| `netz.train()`, `netz.eval()` | Trainingsmodus und Testmodus |
| **Transformer-Block** | erst sammeln (Köpfe), dann nachdenken (FeedForward), jeweils mit LayerNorm und Abkürzung |
| **Transformer** | Einbettung, mehrere Blöcke übereinander, LayerNorm, Ausgabe-Schicht |

Das ist der Aufbau von GPT. GPT-2 aus dem Jahr 2019 hat in der kleinsten Version 12 Blöcke mit je 12 Köpfen
und 768 Koordinaten pro Wortstück. Der Bauplan ist derselbe wie bei deinem Transformer.

## Ausblick auf Notebook 7

Dein Transformer ist fertig, aber er hat zu wenig zu lesen. Im letzten Notebook bekommt er einen viel größeren Text:
fast 500.000 Zeichen aus den Märchen der Brüder Grimm. Du trainierst ihn ein paar Minuten lang und lässt ihn dann
seine eigenen Märchen schreiben.
""")
,
]
