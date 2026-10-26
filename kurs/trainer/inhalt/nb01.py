"""Inhalt von Notebook 1: Zählen und Wahrscheinlichkeit."""

from .bausteine import aufgabe, code, md, tipps

ZELLEN = [

# =============================================================
# WILLKOMMEN
# =============================================================

md(r"""
# Notebook 1: Wie ein Computer Text vorhersagt

## Zählen und Wahrscheinlichkeit

Willkommen zum Kurs! In sieben Notebooks baust du Schritt für Schritt dein eigenes kleines Sprachmodell.
Am Ende steht ein **Transformer**, also genau die Art von Modell, die hinter ChatGPT, Claude und Co. steckt.
Natürlich viel kleiner, aber mit denselben Grundideen.

### Was ist ein Sprachmodell?

Ein Sprachmodell macht im Kern nur eine einzige Sache:

> **Es bekommt einen Text und sagt voraus, was als Nächstes kommt.**

Wenn du *"Der Hund bellt laut im Gar..."* liest, weißt du sofort, dass wahrscheinlich *"ten"* folgt.
Ein Sprachmodell lernt genau diese Fähigkeit aus vielen Beispielen. Und wenn man immer wieder das nächste
Stück vorhersagt und anhängt, entsteht ganz neuer Text.

Wir arbeiten in diesem Kurs mit **einzelnen Zeichen** (Buchstaben, Leerzeichen, Satzzeichen).
Große Modelle arbeiten mit Wortstücken, das Prinzip ist aber dasselbe.

### Der Fahrplan

| Notebook | Thema | Was du baust |
|---|---|---|
| **1 (dieses)** | Zählen und Wahrscheinlichkeit | Ein Modell, das nur zählt. Und eine Methode, um Modelle zu bewerten. |
| 2 | Ein Netz, das lernt | Ein kleines neuronales Netz mit PyTorch, das selbst lernt, was du hier zählst |
| 3 | Ein größeres Netz | Mehr Kontext und ein Netz, das auch Unbekanntes versteht |
| 4 | Zurückschauen | Jedes Zeichen schaut auf alle Zeichen davor |
| 5 | Aufmerksamkeit | Das Netz entscheidet selbst, worauf es schaut |
| 6 | Der Transformer | Dein eigenes Mini-GPT |
| 7 | Das große Training | Dein Transformer liest Märchen und schreibt eigene |

Jedes Notebook baut auf dem vorherigen auf. Den Code, den du hier schreibst, verwendest du später weiter.
""")
,
md(r"""
## So funktioniert dieses Notebook

Ein Notebook besteht aus **Zellen**. Es gibt zwei Arten:

- **Textzellen** wie diese hier. Sie erklären dir alles.
- **Code-Zellen** mit Python-Code. Du führst sie aus mit **Shift + Enter** (oder dem Play-Knopf links neben der Zelle).

Wichtig: **Führe die Zellen von oben nach unten aus.** Spätere Zellen brauchen oft Dinge aus früheren Zellen.
Wenn etwas komisch wird, hilft fast immer: *Kernel neu starten* und alle Zellen bis zur aktuellen Stelle noch einmal ausführen.

### Aufgaben, Prüfungen und Tipps

Immer wieder kommt ein Abschnitt **"Aufgabe"**. Dort steht eine Code-Zelle mit einer Funktion, die noch nicht fertig ist:

```python
def beispiel():
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe x.y: Hier fehlt noch dein Code")
```

`raise NotImplementedError(...)` kennst du aus C# als `throw new NotImplementedException()`.
Du ersetzt diese Zeile durch deinen eigenen Code und führst die Zelle aus.

Direkt darunter steht eine **Prüfzelle**. Sie testet deinen Code und sagt dir, ob alles stimmt oder was noch nicht passt.
Du kannst die Prüfzelle so oft ausführen, wie du willst.

Wenn du nicht weiterkommst, gibt es zu jeder Aufgabe **aufklappbare Tipps** in drei Stufen:

1. **Hinweis:** in welche Richtung du denken solltest
2. **Fast die Lösung:** der Code mit ein paar Lücken
3. **Die Lösung:** der ganze Code mit Erklärung

Versuch es zuerst ohne. Wenn du nach 10 Minuten nicht weiterkommst, nimm ruhig Tipp 1. Das ist kein Schummeln, sondern lernen.
Auch die ganze Lösung darfst du dir ansehen, wenn du feststeckst. Lies dann die Erklärung genau und tippe den Code selbst ab, statt ihn zu kopieren.
""")
,
md(r"""
## Python für C#-Entwickler

Du kannst schon programmieren, nur Python ist neu. Die gute Nachricht: Python ist kürzer und lockerer als C#.
Hier die wichtigsten Unterschiede auf einen Blick:

| C# | Python | Bemerkung |
|---|---|---|
| `{ ... }` für Blöcke | Einrückung (4 Leerzeichen) | Die Einrückung **ist** die Syntax |
| `int x = 5;` | `x = 5` | Keine Typen, kein Semikolon |
| `List<int> l = new() {1, 2};` | `l = [1, 2]` | Liste |
| `Dictionary<string,int> d = new() {{"a", 1}};` | `d = {"a": 1}` | Dictionary |
| `new HashSet<char>(text)` | `set(text)` | Menge ohne Doppelte |
| `d.ContainsKey("a")` | `"a" in d` | Schlüssel prüfen |
| `d.GetValueOrDefault("a", 0)` | `d.get("a", 0)` | Wert oder Standardwert |
| `list.Count`, `text.Length` | `len(list)`, `len(text)` | Länge von allem |
| `text.Substring(2, 3)` | `text[2:5]` | Ausschneiden (von 2 bis **vor** 5) |
| `text[text.Length - 1]` | `text[-1]` | Negative Indizes zählen von hinten |
| `for (int i = 0; i < 10; i++)` | `for i in range(10):` | `range(10)` liefert 0 bis 9 |
| `foreach (var x in liste)` | `for x in liste:` | |
| `$"Wert: {x}"` | `f"Wert: {x}"` | Formatierte Strings |
| `liste.Select(x => x * 2).ToList()` | `[x * 2 for x in liste]` | List Comprehension |
| `this.name` | `self.name` | `self` steht in jeder Methode als erster Parameter |
| `public Klasse(...) { }` | `def __init__(self, ...):` | Konstruktor |
| `throw new Exception("...")` | `raise Exception("...")` | |
| `null` | `None` | |
| `true`, `false`, `&&`, `\|\|`, `!` | `True`, `False`, `and`, `or`, `not` | |

Probier es aus: Führe die nächste Zelle mit **Shift + Enter** aus.
""")
,
code(r"""
text = "Hallo Welt"

print(len(text))         # Länge
print(text[0])           # erstes Zeichen
print(text[-1])          # letztes Zeichen
print(text[0:5])         # Zeichen 0 bis 4
print(set(text))         # alle verschiedenen Zeichen (ungeordnet)

zaehler = {"a": 3, "b": 1}
print(zaehler["a"])      # Wert zum Schlüssel "a"
print("c" in zaehler)    # gibt es den Schlüssel "c"?
print(zaehler.get("c", 0))

for zeichen in "abc":
    print(f"Zeichen: {zeichen}")
""")
,
md(r"""
Zum Schluss die Werkzeuge für dieses Notebook laden. Diese Zelle musst du immer ausführen, bevor du loslegst.
""")
,
code(r"""
import math
import random

from kurswerkzeuge import grafik, nb1

print("Alles bereit!")
""")
,

# =============================================================
# TEIL 1: DER TRAININGSTEXT
# =============================================================

md(r"""
---
# Teil 1: Der Trainingstext

Jedes Sprachmodell lernt aus Text. Unser Text ist eine Sammlung einfacher deutscher Sätze, etwa 11.000 Zeichen lang.
Zum Vergleich: Große Sprachmodelle lernen aus Billionen von Wortstücken. Für unsere Zwecke reicht das aber völlig.

Lies den Text ein:
""")
,
code(r"""
with open("daten/training.txt", encoding="utf-8") as datei:
    trainingstext = datei.read()

print("Anzahl Zeichen:", len(trainingstext))
print()
print(trainingstext[:500])
""")
,
md(r"""
`with open(...) as datei:` entspricht in C# einem `using (var datei = File.OpenText(...))`.
Die Datei wird am Ende des Blocks automatisch geschlossen.

Für den Computer ist dieser Text einfach eine lange Kette von Zeichen. Er weiß nicht, was ein Wort ist,
was ein Satz ist oder was "Hund" bedeutet. Er sieht nur Zeichen, eins nach dem anderen.

Schauen wir uns an, welche Zeichen wie oft vorkommen:
""")
,
code(r"""
grafik.zeichen_haeufigkeit(trainingstext)
""")
,
md(r"""
Am häufigsten ist `e`, knapp dahinter das Leerzeichen, danach kommen `n`, `i`, `r`, `t`, `s`.
Das ist typisch für Deutsch. Ein Modell, das gar nichts weiß außer dieser Statistik, würde also am liebsten
`e` oder ein Leerzeichen vorhersagen. Das ist schon besser als blindes Raten, aber noch weit entfernt von Sprache.

---
## Aufgabe 1.1: Einzigartige Zeichen finden

Für alles Weitere brauchen wir die Liste aller Zeichen, die im Text vorkommen. Jedes Zeichen genau einmal und sortiert.

Schreibe die Funktion `einzigartige_zeichen(text)`:

- **Eingabe:** ein Text, zum Beispiel `"hallo"`
- **Rückgabe:** eine **sortierte Liste** aller verschiedenen Zeichen, zum Beispiel `['a', 'h', 'l', 'o']`

Das Leerzeichen zählt auch als Zeichen. Beim Sortieren kommt es ganz nach vorne.

**Hilfreich in Python:**
- `set(text)` erstellt eine Menge aller Zeichen. Doppelte fallen dabei weg, die Reihenfolge ist aber zufällig.
- `sorted(irgendwas)` gibt eine sortierte **Liste** zurück.

In C# würdest du `text.Distinct().OrderBy(c => c).ToList()` schreiben.
""")
,
aufgabe(
vorlage=r"""
def einzigartige_zeichen(text):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 1.1: Hier fehlt noch dein Code")
""",
loesung=r"""
def einzigartige_zeichen(text):
    return sorted(set(text))
""")
,
code(r"""
nb1.pruefe_aufgabe_1(einzigartige_zeichen)
""")
,
tipps(
    hinweis=r"""
    Die Aufgabe hat zwei Schritte: erst die doppelten Zeichen loswerden, dann sortieren.

    Probier in einer neuen Zelle `set("hallo")` aus. Was fällt weg? Und was passiert mit der Reihenfolge?
    Danach probier `sorted(set("hallo"))`. Funktionen darf man ineinander schachteln, genau wie in C#.
    """,
    fast=r"""
    ```python
    def einzigartige_zeichen(text):
        return sorted(...)
    ```
    In die Klammer kommt die Menge aller Zeichen aus `text`. `sorted` macht daraus eine sortierte Liste.
    """,
    loesung=r"""
    ```python
    def einzigartige_zeichen(text):
        return sorted(set(text))
    ```
    So funktioniert es, von innen nach außen gelesen:

    - `set(text)` macht aus `"hallo"` die Menge `{'h', 'a', 'l', 'o'}`. Das zweite `l` fällt weg, weil eine Menge jedes Element nur einmal enthält.
      Die Reihenfolge in einer Menge ist aber nicht festgelegt.
    - `sorted(...)` sortiert die Menge und gibt eine **Liste** zurück: `['a', 'h', 'l', 'o']`.

    Das Leerzeichen landet beim Sortieren ganz vorne, weil es im Zeichensatz eine kleinere Nummer hat als alle Buchstaben.
    """,
)
,
code(r"""
alle_zeichen = einzigartige_zeichen(trainingstext)
print(f"Der Trainingstext enthält {len(alle_zeichen)} verschiedene Zeichen:")
print(alle_zeichen)
""")
,

# =============================================================
# TEIL 2: TEXT IN ZAHLEN
# =============================================================

md(r"""
---
# Teil 2: Aus Text werden Zahlen

Computer rechnen mit Zahlen. Spätestens ab Notebook 2, wenn wir neuronale Netze bauen, müssen wir jedes
Zeichen als Zahl darstellen. Die einfachste Idee: Jedes Zeichen bekommt seine **Position in der sortierten Liste** als Nummer, die **ID**.

| Zeichen | `' '` | `'a'` | `'e'` | `'h'` | `'l'` | `'o'` | `'t'` | `'w'` |
|---|---|---|---|---|---|---|---|---|
| **ID** | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |

Mit dieser Tabelle (für den Text `"hallo welt"`) wird:

- `"hallo"` zu `[3, 1, 4, 4, 5]` (das nennt man **encode**, kodieren)
- `[7, 2, 4, 6]` zu `"welt"` (das nennt man **decode**, dekodieren)

Die Menge aller bekannten Zeichen heißt **Vokabular** (englisch: *vocabulary*).
Bei großen Modellen wie GPT besteht das Vokabular aus etwa 100.000 Wortstücken statt aus 35 Zeichen. Die Idee ist dieselbe.

> **Hinweis zu den Namen:** Fachbegriffe wie *Vocabulary*, *encode* und *decode* verwenden wir auf Englisch,
> weil du sie so in jeder Dokumentation und jedem Tutorial wiederfindest. Alles andere schreiben wir auf Deutsch.

---
## Aufgabe 1.2: Die Klasse `Vocabulary`

Schreibe eine Klasse `Vocabulary` mit:

| Teil | Was es tut |
|---|---|
| `__init__(self, text)` | Konstruktor. Legt drei Attribute an (siehe unten). |
| `self.zeichen` | sortierte Liste aller Zeichen. Verwende deine Funktion `einzigartige_zeichen`! |
| `self.zeichen_zu_id` | Dictionary: Zeichen → ID, z. B. `{' ': 0, 'a': 1, ...}` |
| `self.id_zu_zeichen` | Dictionary: ID → Zeichen, z. B. `{0: ' ', 1: 'a', ...}` |
| `encode(self, text)` | Text → Liste von IDs |
| `decode(self, ids)` | Liste von IDs → Text |
| `__len__(self)` | Anzahl der Zeichen im Vokabular. Damit funktioniert `len(vocabulary)`. |

**Python-Klassen für C#-Entwickler:**

```python
class Konto:
    def __init__(self, inhaber):      # Konstruktor
        self.inhaber = inhaber        # Attribute entstehen einfach durch Zuweisung
        self.stand = 0

    def einzahlen(self, betrag):      # self ist wie "this", muss aber immer dastehen
        self.stand += betrag

konto = Konto("Lena")                 # kein "new"
konto.einzahlen(50)
```

**Neu in Python:**
- `enumerate(liste)` liefert Paare aus Index und Wert: `for i, z in enumerate(["a", "b"]):` ergibt `0, 'a'` und dann `1, 'b'`.
- **Dictionary Comprehension**: `{z: i for i, z in enumerate(liste)}` baut in einer Zeile ein Dictionary.
  Das ist wie `liste.Select((z, i) => (z, i)).ToDictionary(p => p.z, p => p.i)` in C#.
- `"".join(liste_von_texten)` klebt Texte zusammen, wie `string.Join("", ...)` in C#.
- `__len__` ist eine *spezielle Methode*. Python ruft sie auf, wenn jemand `len(objekt)` schreibt.
  Das ist vergleichbar mit Operator-Überladung in C#.
""")
,
aufgabe(
vorlage=r"""
class Vocabulary:
    def __init__(self, text):
        # DEIN CODE HIER: self.zeichen, self.zeichen_zu_id, self.id_zu_zeichen anlegen
        raise NotImplementedError("Aufgabe 1.2: Hier fehlt noch dein Code")

    def encode(self, text):
        # DEIN CODE HIER: Liste von IDs zurückgeben
        raise NotImplementedError("Aufgabe 1.2: Hier fehlt noch dein Code")

    def decode(self, ids):
        # DEIN CODE HIER: Text zurückgeben
        raise NotImplementedError("Aufgabe 1.2: Hier fehlt noch dein Code")

    def __len__(self):
        # DEIN CODE HIER: Anzahl der Zeichen zurückgeben
        raise NotImplementedError("Aufgabe 1.2: Hier fehlt noch dein Code")
""",
loesung=r"""
class Vocabulary:
    def __init__(self, text):
        self.zeichen = einzigartige_zeichen(text)
        self.zeichen_zu_id = {zeichen: i for i, zeichen in enumerate(self.zeichen)}
        self.id_zu_zeichen = {i: zeichen for i, zeichen in enumerate(self.zeichen)}

    def encode(self, text):
        return [self.zeichen_zu_id[zeichen] for zeichen in text]

    def decode(self, ids):
        return "".join(self.id_zu_zeichen[i] for i in ids)

    def __len__(self):
        return len(self.zeichen)
""")
,
code(r"""
nb1.pruefe_aufgabe_2(Vocabulary)
""")
,
tipps(
    hinweis=r"""
    Geh die Klasse Teil für Teil durch:

    - **Konstruktor:** `self.zeichen` bekommst du mit deiner Funktion aus Aufgabe 1.1.
      Für die beiden Dictionaries brauchst du zu jedem Zeichen seine Position. Die liefert `enumerate`. Probier in einer neuen Zelle:
      ```python
      for i, z in enumerate(["x", "y", "z"]):
          print(i, z)
      ```
    - **encode:** Für jedes Zeichen im Text die ID in `self.zeichen_zu_id` nachschlagen und alle IDs in einer Liste sammeln.
    - **decode:** Für jede ID das Zeichen in `self.id_zu_zeichen` nachschlagen und alles mit `"".join(...)` zusammenkleben.
    - **__len__:** Wie viele Zeichen stehen in `self.zeichen`?
    """,
    fast=r"""
    ```python
    class Vocabulary:
        def __init__(self, text):
            self.zeichen = einzigartige_zeichen(text)
            self.zeichen_zu_id = {zeichen: i for i, zeichen in enumerate(self.zeichen)}
            self.id_zu_zeichen = ...  # genauso, nur Schlüssel und Wert vertauscht

        def encode(self, text):
            return [self.zeichen_zu_id[zeichen] for zeichen in text]

        def decode(self, ids):
            return "".join(... for i in ids)

        def __len__(self):
            return len(...)
    ```
    Die Schreibweise `{schlüssel: wert for ...}` baut ein Dictionary, `[wert for ...]` eine Liste.
    Beides ist eine Kurzform für eine Schleife, die Schritt für Schritt etwas einträgt.
    """,
    loesung=r"""
    ```python
    class Vocabulary:
        def __init__(self, text):
            self.zeichen = einzigartige_zeichen(text)
            self.zeichen_zu_id = {zeichen: i for i, zeichen in enumerate(self.zeichen)}
            self.id_zu_zeichen = {i: zeichen for i, zeichen in enumerate(self.zeichen)}

        def encode(self, text):
            return [self.zeichen_zu_id[zeichen] for zeichen in text]

        def decode(self, ids):
            return "".join(self.id_zu_zeichen[i] for i in ids)

        def __len__(self):
            return len(self.zeichen)
    ```
    Was die einzelnen Teile tun:

    - `enumerate(self.zeichen)` liefert die Paare `(0, ' ')`, `(1, 'a')`, ... Daraus entstehen zwei Dictionaries:
      einmal Zeichen → ID, einmal ID → Zeichen. Sie sind Spiegelbilder voneinander.
    - `encode` schlägt jedes Zeichen nach. Aus `"ab"` wird zum Beispiel `[1, 2]`.
    - `decode` macht das Gegenteil und klebt die gefundenen Zeichen mit `"".join(...)` zu einem Text zusammen.
    - `__len__` gibt die Länge der Zeichenliste zurück. Python ruft diese Methode auf, wenn jemand `len(vocabulary)` schreibt.

    Eine Probe: `vocabulary.decode(vocabulary.encode("hallo"))` muss wieder `"hallo"` ergeben.
    """,
)
,
md(r"""
Jetzt bauen wir das Vokabular für den ganzen Trainingstext und probieren es aus:
""")
,
code(r"""
vocabulary = Vocabulary(trainingstext)

print("Größe des Vokabulars:", len(vocabulary))

ids = vocabulary.encode("der hund läuft")
print("kodiert:  ", ids)
print("dekodiert:", vocabulary.decode(ids))
""")
,
md(r"""
Diese Zahlen sind ab Notebook 2 das, was ein neuronales Netz "sieht". In diesem Notebook arbeiten wir aber
noch direkt mit den Zeichen, weil das beim Zählen anschaulicher ist.

---
# Teil 3: Das erste Sprachmodell zählt Zeichenpaare

Jetzt kommt die erste Idee für ein Sprachmodell. Sie ist erstaunlich einfach:

> **Schau dir an, welches Zeichen im Trainingstext wie oft auf welches andere folgt.**

Im Deutschen folgt auf `c` fast immer `h` (wie in "ich", "noch", "acht") oder `k` (wie in "zurück").
Auf `q` folgt praktisch immer `u`. Wenn wir das für jedes Zeichen zählen, wissen wir, was nach jedem Zeichen typischerweise kommt.

Ein Paar aus zwei aufeinanderfolgenden Zeichen heißt **Bigramm** (von lateinisch *bi* = zwei, griechisch *gramma* = Buchstabe).

Schau dir in der Animation an, wie das Zählen funktioniert. Drück auf **Play** oder zieh den Regler:
""")
,
code(r"""
grafik.zaehlen_animation("der hund und die katze")
""")
,
md(r"""
Der blaue Kasten ist das **aktuelle Zeichen**, der orangene das **nächste Zeichen**. Bei jedem Schritt wird der Zähler
für dieses Paar um 1 erhöht. Achte darauf, wie sich bei `d` die Zähler sammeln: Nach `d` kommt mal `e`, mal `i`, mal ein Leerzeichen.

### Wie speichern wir die Zählung?

Wir verwenden ein **Dictionary von Dictionaries**. In C# wäre das ein `Dictionary<char, Dictionary<char, int>>`:

```python
{
    "d": {"e": 1, " ": 2, "i": 1},   # nach "d" kam 1x "e", 2x Leerzeichen, 1x "i"
    "e": {"r": 1, " ": 1},
    ...
}
```

Auf einen Zähler greifst du so zu: `zaehler["d"]["e"]` ist die Anzahl, wie oft `e` auf `d` folgte.

---
## Aufgabe 1.3: Bigramme zählen

Schreibe die Funktion `zaehle_bigramme(text)`. Sie gibt das Dictionary von Dictionaries zurück.

Für `"abab"` soll herauskommen: `{'a': {'b': 2}, 'b': {'a': 1}}`

**So gehst du vor:**
1. Leg ein leeres Dictionary `zaehler = {}` an.
2. Geh mit einer Schleife durch alle Positionen `i`, an denen es ein nächstes Zeichen gibt.
   **Achtung:** Beim letzten Zeichen gibt es kein nächstes mehr. Wie weit muss `range(...)` also laufen?
3. Hol dir `aktuell = text[i]` und `naechstes = text[i + 1]`.
4. Falls `aktuell` noch nicht im Dictionary ist, leg dafür ein leeres inneres Dictionary an.
5. Falls `naechstes` im inneren Dictionary noch nicht vorkommt, setz den Zähler auf 0.
6. Erhöhe den Zähler um 1.
""")
,
aufgabe(
vorlage=r"""
def zaehle_bigramme(text):
    zaehler = {}

    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 1.3: Hier fehlt noch dein Code")

    return zaehler
""",
loesung=r"""
def zaehle_bigramme(text):
    zaehler = {}

    for i in range(len(text) - 1):
        aktuell = text[i]
        naechstes = text[i + 1]

        if aktuell not in zaehler:
            zaehler[aktuell] = {}

        if naechstes not in zaehler[aktuell]:
            zaehler[aktuell][naechstes] = 0

        zaehler[aktuell][naechstes] += 1

    return zaehler
""")
,
code(r"""
nb1.pruefe_aufgabe_3(zaehle_bigramme)
""")
,
tipps(
    hinweis=r"""
    **Wie weit läuft die Schleife?** Bei `"abab"` (Länge 4) gibt es Paare an den Positionen 0, 1 und 2, also nur 3 Paare.
    Beim letzten Zeichen gibt es kein nächstes mehr. `range(len(text) - 1)` liefert genau 0, 1, 2.

    **Wie lege ich fehlende Einträge an?** Bevor du einen Zähler erhöhen kannst, muss es ihn geben. Das Muster dafür:
    ```python
    if aktuell not in zaehler:
        zaehler[aktuell] = {}
    ```
    Dasselbe brauchst du noch einmal eine Ebene tiefer, für das innere Dictionary.
    """,
    fast=r"""
    ```python
    for i in range(len(text) - 1):
        aktuell = text[i]
        naechstes = text[i + 1]

        if aktuell not in zaehler:
            zaehler[aktuell] = {}

        if naechstes not in zaehler[aktuell]:
            zaehler[aktuell][naechstes] = ...

        zaehler[aktuell][naechstes] += ...
    ```
    Und die Zeile mit `raise NotImplementedError` muss weg!
    """,
    loesung=r"""
    ```python
    def zaehle_bigramme(text):
        zaehler = {}

        for i in range(len(text) - 1):
            aktuell = text[i]
            naechstes = text[i + 1]

            if aktuell not in zaehler:
                zaehler[aktuell] = {}

            if naechstes not in zaehler[aktuell]:
                zaehler[aktuell][naechstes] = 0

            zaehler[aktuell][naechstes] += 1

        return zaehler
    ```
    Was in jedem Durchlauf passiert, am Beispiel `"abab"` an Position 0:

    1. `aktuell` ist `'a'`, `naechstes` ist `'b'`.
    2. `'a'` steht noch nicht im Dictionary, also bekommt es ein leeres inneres Dictionary: `{'a': {}}`.
    3. `'b'` steht noch nicht in `zaehler['a']`, also startet der Zähler bei 0: `{'a': {'b': 0}}`.
    4. Der Zähler wird um 1 erhöht: `{'a': {'b': 1}}`.

    Kommt dasselbe Paar später noch einmal, sind beide `if` falsch, und es wird nur noch hochgezählt.
    """,
)
,
md(r"""
Jetzt zählen wir alle Bigramme im Trainingstext. Die Grafik zeigt jedes Zeichenpaar als Kästchen.
Je dunkler das Blau, desto häufiger folgt das Zeichen oben auf das Zeichen links.
""")
,
code(r"""
bigramme = zaehle_bigramme(trainingstext)

print("Was folgt auf 'c'?", bigramme["c"])

grafik.bigramm_heatmap(bigramme)
""")
,
md(r"""
**Was fällt dir auf?** Ein paar Dinge zum Entdecken:

- Die Zeile `c` ist fast leer, bis auf `h` und `k`. Genau wie erwartet.
- Die Spalte `␣` (Leerzeichen) ist in vielen Zeilen dunkel: Nach `e`, `n`, `r`, `t` endet oft ein Wort.
- Die Zeile `␣` zeigt, mit welchen Buchstaben Wörter anfangen: oft `d` (der, die, das), `s`, `e`, `w`.
- Ganz viele Kästchen sind weiß. Diese Paare kommen im Text nie vor, zum Beispiel `q` gefolgt von `x`.

Diese Tabelle **ist** unser erstes Sprachmodell. Mehr braucht es nicht. Jetzt müssen wir nur noch lernen, wie wir mit ihr Text erzeugen.

---
# Teil 4: Von Häufigkeiten zu Wahrscheinlichkeiten

Zählungen allein sind unpraktisch. Ob nach `c` nun 120-mal `h` kam oder 12-mal, hängt davon ab, wie lang der Text ist.
Interessanter ist der **Anteil**: In welchem Teil der Fälle folgt `h` auf `c`?

### Die Mathematik dahinter

Wenn auf ein Zeichen $a$ insgesamt $N$ Zeichen folgen und davon $k$-mal das Zeichen $b$, dann ist der Anteil:

$$
P(b \mid a) = \frac{k}{N} = \frac{\text{Anzahl}(a \text{ gefolgt von } b)}{\text{Anzahl}(a \text{ gefolgt von irgendwas})}
$$

Sprich: *"P von b, gegeben a"*. Das ist eine **bedingte Wahrscheinlichkeit**: die Wahrscheinlichkeit für $b$,
**unter der Bedingung**, dass gerade $a$ kam.

**Ein Beispiel:** Nach `d` kam im Text 100-mal ein Zeichen, davon 60-mal `e`, 30-mal `i` und 10-mal `a`. Dann gilt:

| Zeichen | Anzahl | Wahrscheinlichkeit |
|---|---|---|
| `e` | 60 | $60 / 100 = 0{,}6$ |
| `i` | 30 | $30 / 100 = 0{,}3$ |
| `a` | 10 | $10 / 100 = 0{,}1$ |
| **Summe** | **100** | **1,0** |

Zwei Regeln gelten für Wahrscheinlichkeiten **immer**:

1. Jede Wahrscheinlichkeit liegt zwischen 0 (unmöglich) und 1 (sicher).
2. Alle Wahrscheinlichkeiten zusammen ergeben genau 1. Irgendetwas muss ja als Nächstes kommen.

So eine Tabelle von Möglichkeiten mit ihren Wahrscheinlichkeiten heißt **Wahrscheinlichkeitsverteilung**, kurz **Verteilung**.
Diesen Begriff wirst du im ganzen Kurs immer wieder hören: Ein Sprachmodell liefert für das nächste Zeichen immer eine Verteilung.

---
## Aufgabe 1.4: Häufigkeiten umrechnen

Schreibe die Funktion `wahrscheinlichkeiten(haeufigkeiten)`:

- **Eingabe:** ein Dictionary Zeichen → Anzahl, z. B. `{'a': 3, 'b': 1}`
- **Rückgabe:** ein **neues** Dictionary Zeichen → Wahrscheinlichkeit, z. B. `{'a': 0.75, 'b': 0.25}`

**Hilfreich:**
- `haeufigkeiten.values()` liefert alle Werte, `sum(...)` addiert sie.
- `haeufigkeiten.items()` liefert Paare aus Schlüssel und Wert: `for zeichen, anzahl in haeufigkeiten.items():`
- In Python 3 ergibt `3 / 4` automatisch `0.75`. Anders als in C# gibt es keine Ganzzahl-Division, außer du schreibst `//`.
""")
,
aufgabe(
vorlage=r"""
def wahrscheinlichkeiten(haeufigkeiten):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 1.4: Hier fehlt noch dein Code")
""",
loesung=r"""
def wahrscheinlichkeiten(haeufigkeiten):
    gesamt = sum(haeufigkeiten.values())
    return {zeichen: anzahl / gesamt for zeichen, anzahl in haeufigkeiten.items()}
""")
,
code(r"""
nb1.pruefe_aufgabe_4(wahrscheinlichkeiten)
""")
,
tipps(
    hinweis=r"""
    Zwei Schritte:

    1. Die Gesamtzahl ausrechnen. `haeufigkeiten.values()` liefert alle Zähler, `sum(...)` addiert sie.
    2. Ein **neues** Dictionary bauen, in dem jeder Zähler durch die Gesamtzahl geteilt ist.
       Mit `for zeichen, anzahl in haeufigkeiten.items():` bekommst du Schlüssel und Wert gleichzeitig.
    """,
    fast=r"""
    ```python
    gesamt = sum(haeufigkeiten.values())
    ergebnis = {}
    for zeichen, anzahl in haeufigkeiten.items():
        ergebnis[zeichen] = ...
    return ergebnis
    ```
    """,
    loesung=r"""
    ```python
    def wahrscheinlichkeiten(haeufigkeiten):
        gesamt = sum(haeufigkeiten.values())
        return {zeichen: anzahl / gesamt for zeichen, anzahl in haeufigkeiten.items()}
    ```
    Für `{'a': 3, 'b': 1}` ist `gesamt = 4`. Dann wird jeder Zähler durch 4 geteilt: `{'a': 0.75, 'b': 0.25}`.

    Die zweite Zeile ist eine Dictionary Comprehension, die Kurzform der Schleife aus Tipp 2.
    Die lange Form ist genauso richtig:
    ```python
    gesamt = sum(haeufigkeiten.values())
    ergebnis = {}
    for zeichen, anzahl in haeufigkeiten.items():
        ergebnis[zeichen] = anzahl / gesamt
    return ergebnis
    ```
    """,
)
,
md(r"""
Jetzt kannst du erkunden, was unser Bigramm-Modell nach jedem Zeichen erwartet.
Gib ins Feld ein einzelnes Zeichen ein (zum Beispiel `c`, `s`, `ä` oder ein Leerzeichen) und drück Enter:
""")
,
code(r"""
grafik.naechstes_zeichen_erkunden(bigramme, wahrscheinlichkeiten)
""")
,

# =============================================================
# TEIL 5: ZIEHEN
# =============================================================

md(r"""
---
# Teil 5: Zufall mit Gewichten

Wir haben jetzt für jedes Zeichen eine Verteilung über das nächste Zeichen. Wie wählen wir daraus **ein** Zeichen aus?

**Idee 1: Immer das wahrscheinlichste nehmen.** Klingt vernünftig, hat aber einen Haken: Das Modell würde
nach `e` immer dasselbe Zeichen wählen, danach wieder dasselbe und so weiter. Es entstehen endlose Schleifen
wie `"den den den den"`. Das probieren wir später noch aus.

**Idee 2: Zufällig ziehen, aber gewichtet.** Wahrscheinliche Zeichen werden oft gezogen, unwahrscheinliche selten.
Stell dir ein Glücksrad vor, bei dem jedes Zeichen ein Feld hat. Je größer die Wahrscheinlichkeit, desto größer das Feld.
Genau so machen es auch echte Sprachmodelle.

### `random.choices` in Python

Python hat dafür eine fertige Funktion:

```python
random.choices(["a", "b", "c"], weights=[0.7, 0.2, 0.1])
```

Sie liefert eine **Liste** mit einem zufällig gezogenen Element, z. B. `['a']`. Das einzelne Element bekommst du mit `[0]`.
Die beiden Listen müssen gleich lang sein und zusammenpassen: Das erste Gewicht gehört zum ersten Element und so weiter.

---
## Aufgabe 1.5: Ein Zeichen ziehen

Schreibe die Funktion `ziehe_zeichen(verteilung)`:

- **Eingabe:** eine Verteilung, z. B. `{'a': 0.7, 'b': 0.2, 'c': 0.1}`
- **Rückgabe:** ein **einzelnes** zufällig gezogenes Zeichen (ein `str`, keine Liste)

**Hilfreich:** `list(verteilung.keys())` liefert die Zeichen als Liste, `list(verteilung.values())` die Wahrscheinlichkeiten.
Weil ein Dictionary die Reihenfolge beibehält, passen beide Listen zusammen.
""")
,
aufgabe(
vorlage=r"""
def ziehe_zeichen(verteilung):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 1.5: Hier fehlt noch dein Code")
""",
loesung=r"""
def ziehe_zeichen(verteilung):
    zeichen = list(verteilung.keys())
    gewichte = list(verteilung.values())
    return random.choices(zeichen, weights=gewichte)[0]
""")
,
code(r"""
nb1.pruefe_aufgabe_5(ziehe_zeichen)
""")
,
tipps(
    hinweis=r"""
    `random.choices` braucht zwei Listen: die Dinge, aus denen gezogen wird, und ihre Gewichte.
    Beide stecken in der Verteilung: die Zeichen in `verteilung.keys()`, die Wahrscheinlichkeiten in `verteilung.values()`.

    Achtung: `random.choices` gibt immer eine **Liste** zurück, auch wenn nur ein Element gezogen wird.
    """,
    fast=r"""
    ```python
    zeichen = list(verteilung.keys())
    gewichte = list(verteilung.values())
    return random.choices(zeichen, weights=...)[...]
    ```
    """,
    loesung=r"""
    ```python
    def ziehe_zeichen(verteilung):
        zeichen = list(verteilung.keys())
        gewichte = list(verteilung.values())
        return random.choices(zeichen, weights=gewichte)[0]
    ```
    - Die ersten beiden Zeilen holen die Zeichen und ihre Wahrscheinlichkeiten. Weil ein Dictionary die Reihenfolge behält,
      gehört `gewichte[0]` zu `zeichen[0]` und so weiter.
    - `random.choices(zeichen, weights=gewichte)` zieht ein Zeichen. Ein Zeichen mit Gewicht 0.7 kommt in etwa 70 von 100 Fällen dran.
    - Das Ergebnis ist eine Liste mit einem Element, zum Beispiel `['a']`. Mit `[0]` holst du das Zeichen selbst heraus.
    """,
)
,
md(r"""
### Funktioniert das wirklich?

Ein einzelner Zufallszug sagt wenig aus. Bei vielen Zügen sollte sich aber zeigen: Jedes Zeichen wird ungefähr so oft gezogen,
wie seine Wahrscheinlichkeit es vorgibt. Die Animation zieht 1000-mal mit **deiner** Funktion `ziehe_zeichen`.

Die grauen Striche zeigen die Wahrscheinlichkeit, die blauen Balken den Anteil, wie oft das Zeichen bisher gezogen wurde.
""")
,
code(r"""
nach_d = wahrscheinlichkeiten(bigramme["d"])
grafik.ziehen_animation(nach_d, ziehe_zeichen)
""")
,
md(r"""
Am Anfang springen die Balken wild hin und her. Nach wenigen Ziehungen ist der Zufall noch groß.
Je mehr Ziehungen, desto näher kommen die Balken an die grauen Striche heran.

Das ist das **Gesetz der großen Zahlen**: Wenn man ein Zufallsexperiment sehr oft wiederholt,
nähern sich die beobachteten Anteile den echten Wahrscheinlichkeiten an.
Darum war auch unser Zählen sinnvoll: Aus vielen beobachteten Zeichenpaaren können wir die Wahrscheinlichkeiten **schätzen**.

---
# Teil 6: Text generieren

Jetzt haben wir alle Bausteine zusammen. Text erzeugen geht so:

1. Starte mit einem Text, z. B. `"d"`.
2. Nimm das **letzte Zeichen** des bisherigen Texts.
3. Schlag in der Zählung nach, was darauf folgen kann, und rechne die Häufigkeiten in eine Verteilung um.
4. Zieh daraus ein Zeichen und häng es an den Text an.
5. Wiederhole ab Schritt 2, bis genug Zeichen erzeugt sind.

Falls das Modell für ein Zeichen gar keine Nachfolger kennt (es stand nur ganz am Ende des Trainingstexts),
hören wir einfach auf.

Dieses Prinzip, ein Zeichen nach dem anderen zu erzeugen und immer auf das Bisherige zu schauen, heißt **autoregressiv**.
Auch ChatGPT schreibt seine Antworten genau so, Stück für Stück.

---
## Aufgabe 1.6: Text generieren mit Bigrammen

Schreibe die Funktion `generiere_bigramm(zaehler, start, laenge)`:

- `zaehler`: die Bigramm-Zählung (das Dictionary von Dictionaries)
- `start`: der Starttext
- `laenge`: wie viele **neue** Zeichen erzeugt werden sollen
- **Rückgabe:** Starttext plus die neuen Zeichen

Verwende deine Funktionen `wahrscheinlichkeiten` und `ziehe_zeichen`!
""")
,
aufgabe(
vorlage=r"""
def generiere_bigramm(zaehler, start, laenge):
    text = start

    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 1.6: Hier fehlt noch dein Code")

    return text
""",
loesung=r"""
def generiere_bigramm(zaehler, start, laenge):
    text = start

    for _ in range(laenge):
        aktuell = text[-1]

        if aktuell not in zaehler:
            break

        verteilung = wahrscheinlichkeiten(zaehler[aktuell])
        text += ziehe_zeichen(verteilung)

    return text
""")
,
code(r"""
nb1.pruefe_aufgabe_6(generiere_bigramm)
""")
,
tipps(
    hinweis=r"""
    In jedem Schleifendurchlauf kommt ein neues Zeichen dazu:

    1. Das letzte Zeichen des bisherigen Texts holen: `text[-1]`
    2. Steht es nicht in `zaehler`, gibt es keine Fortsetzung. Dann ist Schluss mit `break`, wie in C#.
    3. Sonst die Verteilung berechnen und ein Zeichen ziehen. Dafür hast du schon zwei Funktionen.

    Die Schleife läuft `laenge`-mal. Die Zählvariable brauchst du nicht, deshalb schreibt man in Python `_`: `for _ in range(laenge):`
    """,
    fast=r"""
    ```python
    for _ in range(laenge):
        aktuell = text[-1]
        if aktuell not in zaehler:
            break
        verteilung = wahrscheinlichkeiten(...)
        text += ziehe_zeichen(...)
    ```
    """,
    loesung=r"""
    ```python
    def generiere_bigramm(zaehler, start, laenge):
        text = start

        for _ in range(laenge):
            aktuell = text[-1]

            if aktuell not in zaehler:
                break

            verteilung = wahrscheinlichkeiten(zaehler[aktuell])
            text += ziehe_zeichen(verteilung)

        return text
    ```
    - `zaehler[aktuell]` sind die Zähler für alles, was bisher auf das letzte Zeichen folgte, zum Beispiel `{'b': 2}`.
    - `wahrscheinlichkeiten(...)` macht daraus eine Verteilung, `ziehe_zeichen(...)` zieht daraus ein Zeichen.
    - `text += ...` hängt es an. Im nächsten Durchlauf ist genau dieses Zeichen das neue `text[-1]`.

    Das `break` greift nur, wenn das letzte Zeichen im Training nie vor einem anderen Zeichen stand, zum Beispiel ganz am Textende.
    """,
)
,
md(r"""
Der große Moment: Unser erstes Sprachmodell schreibt! Führ die Zelle ruhig mehrmals aus.
Jedes Mal kommt etwas anderes heraus, weil gezogen wird.
""")
,
code(r"""
print(generiere_bigramm(bigramme, "d", 300))
""")
,
md(r"""
Naja. Es sieht ein bisschen nach Deutsch aus: Die Wortlängen stimmen ungefähr, Buchstabenfolgen wie `ch`, `er`, `en` tauchen auf.
Aber echte Wörter sind selten. Das Modell hat ein Gedächtnis von genau **einem** Zeichen.

In der nächsten Animation siehst du jeden Schritt genau: Blau ist der Kontext, auf den das Modell schaut,
orange das gezogene Zeichen. Die Balken zeigen, welche Zeichen zur Auswahl standen.
""")
,
code(r"""
grafik.generierung_schritt_fuer_schritt(
    start="d",
    schritte=40,
    verteilung_fuer=lambda bisher: wahrscheinlichkeiten(bigramme[bisher[-1]]),
    ziehe_zeichen=ziehe_zeichen,
)
""")
,
md(r"""
`lambda bisher: ...` ist eine kleine Funktion ohne Namen, genau wie `bisher => ...` in C#.

### Warum eigentlich nicht immer das wahrscheinlichste Zeichen?

Hier noch das Experiment aus Teil 5. Statt zu ziehen, nehmen wir immer das Zeichen mit der höchsten Wahrscheinlichkeit:
""")
,
code(r"""
text = "d"
for _ in range(60):
    verteilung = wahrscheinlichkeiten(bigramme[text[-1]])
    text += max(verteilung, key=verteilung.get)   # das Zeichen mit dem größten Wert

print(text)
""")
,
md(r"""
Genau das befürchtete Problem: Das Modell landet in einer Schleife und wiederholt sich endlos.
Deshalb ziehen echte Sprachmodelle zufällig aus der Verteilung.

---
# Teil 7: Mehr Gedächtnis mit N-Grammen

Ein Zeichen Kontext ist zu wenig. Nach `e` kann fast alles kommen. Nach `de` ist die Auswahl schon kleiner,
nach `hun` ist `d` fast sicher.

Die Verallgemeinerung: Wir schauen nicht nur auf das letzte Zeichen, sondern auf die letzten **n** Zeichen.
Diese n Zeichen heißen **Kontext**. So ein Modell heißt **N-Gramm-Modell**.

| n | Kontext | Beispiel im Text "der hund" |
|---|---|---|
| 1 | 1 Zeichen | `"d"` → `"e"`, `"e"` → `"r"`, ... (das ist unser Bigramm-Modell) |
| 2 | 2 Zeichen | `"de"` → `"r"`, `"er"` → `" "`, ... |
| 3 | 3 Zeichen | `"der"` → `" "`, `"er "` → `"h"`, ... |

Statt `text[i]` brauchen wir jetzt ein ganzes Stück aus dem Text. Das geht mit **Slicing**:

```python
text = "der hund"
text[0:3]     # "der"   Zeichen 0, 1, 2 (die 3 ist nicht mehr dabei)
text[2:5]     # "r h"
text[-3:]     # "und"   die letzten 3 Zeichen
```

`text[i:i + n]` schneidet also n Zeichen ab Position `i` aus. In C# wäre das `text.Substring(i, n)`.

---
## Aufgabe 1.7: Die Klasse `NGramModell`

Jetzt baust du alles in eine Klasse ein, die für jedes n funktioniert.

| Teil | Was es tut |
|---|---|
| `__init__(self, text, n)` | Speichert `self.n` und zählt alle Kontexte in `self.zaehler`. Wie `zaehle_bigramme`, nur mit Kontexten der Länge n. |
| `naechstes_zeichen(self, kontext)` | Zieht ein Zeichen, das auf `kontext` folgen kann. Ist der Kontext unbekannt, gibt sie `None` zurück. |
| `generiere(self, start, laenge)` | Wie `generiere_bigramm`, aber mit den letzten n Zeichen als Kontext. Ist der Starttext kürzer als n, löst sie einen `ValueError` aus. |

Für `NGramModell("abcabd", 2)` soll `zaehler` so aussehen:
`{'ab': {'c': 1, 'd': 1}, 'bc': {'a': 1}, 'ca': {'b': 1}}`

**Überleg dir beim Zählen:** Bei einem Text der Länge 6 und n = 2, an welchen Positionen `i` beginnt ein Kontext,
nach dem noch ein Zeichen folgt?
""")
,
aufgabe(
vorlage=r"""
class NGramModell:
    def __init__(self, text, n):
        self.n = n
        self.zaehler = {}

        # DEIN CODE HIER: alle Kontexte der Länge n zählen
        raise NotImplementedError("Aufgabe 1.7: Hier fehlt noch dein Code")

    def naechstes_zeichen(self, kontext):
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 1.7: Hier fehlt noch dein Code")

    def generiere(self, start, laenge):
        # DEIN CODE HIER
        raise NotImplementedError("Aufgabe 1.7: Hier fehlt noch dein Code")
""",
loesung=r"""
class NGramModell:
    def __init__(self, text, n):
        self.n = n
        self.zaehler = {}

        for i in range(len(text) - n):
            kontext = text[i:i + n]
            naechstes = text[i + n]

            if kontext not in self.zaehler:
                self.zaehler[kontext] = {}

            if naechstes not in self.zaehler[kontext]:
                self.zaehler[kontext][naechstes] = 0

            self.zaehler[kontext][naechstes] += 1

    def naechstes_zeichen(self, kontext):
        if kontext not in self.zaehler:
            return None

        verteilung = wahrscheinlichkeiten(self.zaehler[kontext])
        return ziehe_zeichen(verteilung)

    def generiere(self, start, laenge):
        if len(start) < self.n:
            raise ValueError(f"Der Starttext muss mindestens {self.n} Zeichen lang sein.")

        text = start

        for _ in range(laenge):
            zeichen = self.naechstes_zeichen(text[-self.n:])

            if zeichen is None:
                break

            text += zeichen

        return text
""")
,
code(r"""
nb1.pruefe_aufgabe_7(NGramModell)
""")
,
tipps(
    hinweis=r"""
    - **Konstruktor:** Das ist fast genau `zaehle_bigramme`. Der Kontext ist jetzt `text[i:i + n]` statt `text[i]`,
      das nächste Zeichen `text[i + n]` statt `text[i + 1]`. Die Schleife läuft deshalb nur bis `range(len(text) - n)`.
      Statt einer lokalen Variable `zaehler` verwendest du `self.zaehler`.
    - **naechstes_zeichen:** Erst prüfen, ob der Kontext bekannt ist. Wenn nicht: `return None`.
      Sonst wie in `generiere_bigramm` Verteilung berechnen und ein Zeichen ziehen.
    - **generiere:** Zuerst prüfen, ob der Starttext lang genug ist, sonst `raise ValueError(...)`.
      Dann wie `generiere_bigramm`, aber der Kontext sind die letzten n Zeichen: `text[-self.n:]`.
    """,
    fast=r"""
    ```python
    def __init__(self, text, n):
        self.n = n
        self.zaehler = {}
        for i in range(len(text) - n):
            kontext = text[i:i + n]
            naechstes = text[i + n]
            # ab hier wie in zaehle_bigramme, nur mit self.zaehler und kontext
            ...

    def naechstes_zeichen(self, kontext):
        if kontext not in self.zaehler:
            return ...
        verteilung = wahrscheinlichkeiten(...)
        return ziehe_zeichen(verteilung)

    def generiere(self, start, laenge):
        if len(start) < self.n:
            raise ValueError("Der Starttext ist zu kurz.")
        text = start
        for _ in range(laenge):
            zeichen = self.naechstes_zeichen(text[-self.n:])
            if zeichen is None:
                ...
            text += zeichen
        return text
    ```
    Vergleiche mit `None` schreibt man in Python mit `is None`, nicht mit `== None`.
    """,
    loesung=r"""
    ```python
    class NGramModell:
        def __init__(self, text, n):
            self.n = n
            self.zaehler = {}

            for i in range(len(text) - n):
                kontext = text[i:i + n]
                naechstes = text[i + n]

                if kontext not in self.zaehler:
                    self.zaehler[kontext] = {}

                if naechstes not in self.zaehler[kontext]:
                    self.zaehler[kontext][naechstes] = 0

                self.zaehler[kontext][naechstes] += 1

        def naechstes_zeichen(self, kontext):
            if kontext not in self.zaehler:
                return None

            verteilung = wahrscheinlichkeiten(self.zaehler[kontext])
            return ziehe_zeichen(verteilung)

        def generiere(self, start, laenge):
            if len(start) < self.n:
                raise ValueError(f"Der Starttext muss mindestens {self.n} Zeichen lang sein.")

            text = start

            for _ in range(laenge):
                zeichen = self.naechstes_zeichen(text[-self.n:])

                if zeichen is None:
                    break

                text += zeichen

            return text
    ```
    - **Konstruktor:** Bei `"abcabd"` und `n = 2` läuft `i` von 0 bis 3. An Position 0 ist der Kontext `"ab"`, das nächste Zeichen `"c"`.
      An Position 3 ist der Kontext wieder `"ab"`, jetzt mit `"d"`. Danach gibt es kein nächstes Zeichen mehr, deshalb `len(text) - n`.
    - **naechstes_zeichen:** Ein unbekannter Kontext liefert `None`. So erfährt `generiere`, dass es nicht weitergeht.
    - **generiere:** `text[-self.n:]` sind immer die letzten n Zeichen, auch wenn der Text länger wird.
      Ist der Starttext kürzer als n, gäbe es gar keinen vollständigen Kontext. Deshalb der `ValueError` am Anfang.
    """,
)
,
md(r"""
### Experiment: Wie viel Kontext ist gut?

Mit dem Regler stellst du n ein. Das Modell wird für jedes n neu trainiert und schreibt dann 300 Zeichen.
Mit **Neu generieren** bekommst du einen neuen Text mit demselben n.

Probiere n = 1, 2, 3, 4, 5, 6, 8 und 10. Achte auf die beiden Zahlen unter dem Text.
""")
,
code(r"""
grafik.ngram_regler(NGramModell, trainingstext)
""")
,
md(r"""
**Denkfragen.** Überleg dir erst selbst eine Antwort, bevor du aufklappst.

<details>
<summary><b>1. Ab welchem n sieht der Text wie Deutsch aus?</b></summary>

Meistens ab n = 4 oder 5. Dann sind fast alle Wörter echte Wörter und auch kurze Wortfolgen ergeben Sinn.
</details>

<details>
<summary><b>2. Was passiert bei sehr großem n, etwa 8 oder 10? Ist das gut?</b></summary>

Der Text ist perfektes Deutsch, aber fast alles ist **wörtlich aus dem Trainingstext kopiert** (siehe die zweite Zahl).
Das Modell erfindet nichts Neues mehr, es sagt nur noch Gelerntes auf. Bei einem 10-Zeichen-Kontext gibt es im Trainingstext
fast immer nur eine einzige Fortsetzung.

Das nennt man **Überanpassung** (englisch *Overfitting*): Das Modell hat die Trainingsdaten auswendig gelernt,
statt die Regeln dahinter zu verstehen. Ein Lehrling, der nur die Musterlösungen auswendig lernt, kann auch keine neue Aufgabe lösen.
</details>

<details>
<summary><b>3. Warum bricht der Text bei großem n manchmal mitten drin ab?</b></summary>

Weil das Modell auf einen Kontext stößt, den es nur ganz am Ende des Trainingstexts gesehen hat
und für den es deshalb keinen Nachfolger kennt. Dann liefert `naechstes_zeichen` den Wert `None`.
</details>
""")
,
md(r"""
### Das grundsätzliche Problem: Die Explosion der Möglichkeiten

Warum nehmen wir nicht einfach einen riesigen Trainingstext und ein großes n? Rechnen wir nach.

Unser Vokabular hat etwa $V = 35$ Zeichen. Für einen Kontext aus n Zeichen gibt es dann

$$
V^n = \underbrace{35 \cdot 35 \cdot \ldots \cdot 35}_{n\text{-mal}}
$$

mögliche Kombinationen. Für jede Stelle im Kontext gibt es 35 Möglichkeiten, und die multiplizieren sich.

| n | mögliche Kontexte $35^n$ |
|---|---|
| 1 | 35 |
| 2 | 1.225 |
| 4 | 1.500.625 |
| 8 | 2.251.875.390.625 (über 2 Billionen) |

Die Grafik vergleicht das mit der Zahl der Kontexte, die tatsächlich in unserem Text vorkommen.
Achtung, die y-Achse ist **logarithmisch**: Jeder Strich nach oben bedeutet *zehnmal so viel*.
""")
,
code(r"""
grafik.kontexte_explosion(NGramModell, trainingstext, len(vocabulary))
""")
,
md(r"""
Die Lücke zwischen den Linien wird riesig. Bei n = 8 hat unser Modell nur einen winzigen Bruchteil aller möglichen Kontexte
jemals gesehen. Auch mit dem gesamten Internet als Trainingstext wäre das so. Und für jeden **ungesehenen** Kontext weiß
ein N-Gramm-Modell **gar nichts**.

Das ist die zentrale Schwäche des Zählens: **Das Modell kann nicht verallgemeinern.**
Es weiß nicht, dass `"der hund"` und `"der katze"` ähnlich funktionieren. Jeder Kontext ist für sich allein.
Genau dieses Problem lösen neuronale Netze, ab Notebook 3.

---
# Teil 8: Wie gut ist ein Modell? Wir messen den Verlust

Bisher haben wir mit bloßem Auge beurteilt, ob der Text "gut aussieht". Das reicht nicht.
Um Modelle zu vergleichen und später neuronale Netze zu **trainieren**, brauchen wir eine **Zahl**, die sagt, wie gut ein Modell ist.

### Die Idee: Wie überrascht ist das Modell?

Wir geben dem Modell einen echten Text und lassen es an jeder Stelle eine Verteilung für das nächste Zeichen vorhersagen.
Dann schauen wir nach, welche Wahrscheinlichkeit $p$ es dem Zeichen gegeben hat, **das wirklich kam**.

- War $p$ hoch (z. B. 0,9), hat das Modell gut vorhergesagt. Es ist **kaum überrascht**.
- War $p$ niedrig (z. B. 0,01), lag das Modell daneben. Es ist **sehr überrascht**.

Als Maß für diese Überraschung nehmen wir

$$
\text{Verlust}(p) = -\log(p)
$$

Dabei ist $\log$ der **natürliche Logarithmus** (in Python `math.log`). Das Ergebnis heißt **Verlust** (englisch *Loss*).
Ein kleiner Verlust ist gut, ein großer schlecht.

### Kurze Wiederholung: der Logarithmus

Der Logarithmus ist die Umkehrung des Potenzierens. $\log(x)$ beantwortet die Frage:
*"Mit welcher Zahl muss ich $e \approx 2{,}718$ potenzieren, um $x$ zu bekommen?"*

| $x$ | $\log(x)$ | $-\log(x)$ |
|---|---|---|
| 1 | 0 | 0 |
| 0,5 | −0,69 | 0,69 |
| 0,1 | −2,30 | 2,30 |
| 0,01 | −4,61 | 4,61 |
| → 0 | → −∞ | → ∞ |

Für Wahrscheinlichkeiten (zwischen 0 und 1) ist $\log(p)$ immer negativ oder 0. Deshalb das Minus davor.
Probier es mit dem Regler aus:
""")
,
code(r"""
grafik.verlust_kurve()
""")
,
md(r"""
Die Kurve zeigt genau das Verhalten, das wir wollen:

- Bei $p = 1$ (sicher und richtig) ist der Verlust **0**.
- Je kleiner $p$, desto steiler steigt der Verlust an.
- Bei $p = 0$ ist der Verlust **unendlich**. Das Modell hat etwas für unmöglich erklärt, das dann doch passiert ist. Schlimmer geht es nicht.

### Warum ausgerechnet der Logarithmus?

Es gibt einen zweiten, sehr praktischen Grund. Die Wahrscheinlichkeit für einen ganzen Text ist das **Produkt**
der Wahrscheinlichkeiten aller einzelnen Zeichen. Bei vielen Zeichen wird dieses Produkt so winzig, dass der Computer es nicht mehr darstellen kann:
""")
,
code(r"""
produkt = 1.0
for _ in range(1000):
    produkt *= 0.3          # 1000 Zeichen, jedes mit Wahrscheinlichkeit 0.3

print("Produkt der Wahrscheinlichkeiten:", produkt)

summe = 0.0
for _ in range(1000):
    summe += -math.log(0.3)

print("Summe der Verluste:               ", summe)
""")
,
md(r"""
Das Produkt ist für den Computer einfach 0. Die Information ist verloren. Die Summe der Verluste ist dagegen eine ganz normale Zahl.

Das liegt an der wichtigsten Rechenregel des Logarithmus:

$$
\log(a \cdot b) = \log(a) + \log(b)
$$

Aus einem **Produkt** vieler kleiner Zahlen wird eine **Summe**. Und Summen kann der Computer problemlos berechnen.

---
## Aufgabe 1.8: Der Verlust einer Vorhersage

Schreibe die Funktion `verlust(p)`, die $-\log(p)$ berechnet.

**Sonderfall:** `math.log(0)` löst in Python einen Fehler aus. Für $p = 0$ soll deine Funktion deshalb
**unendlich** zurückgeben. In Python schreibt man das `float("inf")` (in C# wäre es `double.PositiveInfinity`).
""")
,
aufgabe(
vorlage=r"""
def verlust(p):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 1.8: Hier fehlt noch dein Code")
""",
loesung=r"""
def verlust(p):
    if p == 0:
        return float("inf")

    return -math.log(p)
""")
,
code(r"""
nb1.pruefe_aufgabe_8(verlust)
""")
,
tipps(
    hinweis=r"""
    Python rechnet den Logarithmus mit `math.log(p)`. Vor das Ergebnis gehört ein Minus.

    Den Sonderfall $p = 0$ musst du **vorher** abfangen, denn `math.log(0)` bricht mit einem Fehler ab.
    """,
    fast=r"""
    ```python
    if p == 0:
        return float("inf")
    return ...
    ```
    """,
    loesung=r"""
    ```python
    def verlust(p):
        if p == 0:
            return float("inf")

        return -math.log(p)
    ```
    - Bei $p = 0$ hat das Modell das richtige Zeichen für unmöglich gehalten. Schlimmer geht es nicht, deshalb unendlich.
    - Sonst ist das Ergebnis $-\log(p)$. Bei $p = 1$ kommt 0 heraus (perfekte Vorhersage), je kleiner $p$, desto größer der Verlust.
    - Die Reihenfolge ist wichtig: Das `if` muss vor `math.log` stehen, sonst kommt der Fehler, bevor die Prüfung greift.
    """,
)
,
md(r"""
### Der durchschnittliche Verlust über einen ganzen Text

Ein einzelner Verlust sagt wenig. Wir berechnen ihn deshalb für **jede Stelle** eines Texts und bilden den **Durchschnitt**.

Für ein N-Gramm-Modell mit Kontextlänge $n$ und einen Text $x_0, x_1, \ldots$ der Länge $L$ gibt es $L - n$ Vorhersagen.
An jeder Position $i$ ist der Kontext $x_i \ldots x_{i+n-1}$ und das richtige nächste Zeichen $x_{i+n}$:

$$
\text{durchschnittlicher Verlust} = \frac{1}{L - n} \sum_{i=0}^{L-n-1} -\log P(x_{i+n} \mid x_i \ldots x_{i+n-1})
$$

Keine Sorge wegen der Formel. Das große $\sum$ heißt nur *"addiere alles für i von 0 bis ..."*, also eine `for`-Schleife.
In Worten:

1. Geh durch alle Positionen `i` im Text (wie beim Zählen).
2. Kontext ist `text[i:i + n]`, das richtige Zeichen ist `text[i + n]`.
3. Bestimme die Wahrscheinlichkeit $p$, die das Modell dem richtigen Zeichen gibt.
4. Addiere `verlust(p)` zur Summe.
5. Teile am Ende durch die Anzahl der Vorhersagen.

**Zwei Fälle, in denen $p = 0$ ist:**
- Der Kontext steht gar nicht in `modell.zaehler`, das Modell kennt ihn nicht.
- Der Kontext ist bekannt, aber das richtige Zeichen kam danach nie vor.

Dieser Verlust hat übrigens einen Fachnamen: **Kreuzentropie** (englisch *Cross-Entropy*).
Genau diese Zahl werden die neuronalen Netze in den nächsten Notebooks beim Training möglichst klein machen.

---
## Aufgabe 1.9: Den durchschnittlichen Verlust berechnen

Schreibe die Funktion `durchschnittlicher_verlust(modell, text)`. `modell` ist ein `NGramModell`.
Du brauchst `modell.n`, `modell.zaehler` und deine Funktionen `wahrscheinlichkeiten` und `verlust`.

**Hilfreich:** `verteilung.get(zeichen, 0.0)` liefert die Wahrscheinlichkeit oder 0.0, falls das Zeichen nicht vorkommt.
""")
,
aufgabe(
vorlage=r"""
def durchschnittlicher_verlust(modell, text):
    # DEIN CODE HIER
    raise NotImplementedError("Aufgabe 1.9: Hier fehlt noch dein Code")
""",
loesung=r"""
def durchschnittlicher_verlust(modell, text):
    n = modell.n
    anzahl = len(text) - n
    summe = 0.0

    for i in range(anzahl):
        kontext = text[i:i + n]
        richtig = text[i + n]

        if kontext in modell.zaehler:
            verteilung = wahrscheinlichkeiten(modell.zaehler[kontext])
            p = verteilung.get(richtig, 0.0)
        else:
            p = 0.0

        summe += verlust(p)

    return summe / anzahl
""")
,
code(r"""
nb1.pruefe_aufgabe_9(durchschnittlicher_verlust, NGramModell)
""")
,
tipps(
    hinweis=r"""
    Geh durch alle Positionen im Text, an denen nach einem Kontext noch ein Zeichen kommt. An jeder Position:

    1. Den Kontext (n Zeichen) und das richtige nächste Zeichen herausschneiden, wie im Konstruktor von `NGramModell`.
    2. Die Wahrscheinlichkeit `p` bestimmen, die das Modell dem richtigen Zeichen gibt. Dabei gibt es zwei Fälle:
       Der Kontext ist bekannt, oder er ist unbekannt (dann ist `p = 0.0`).
    3. `verlust(p)` zu einer Summe addieren.

    Am Ende die Summe durch die Anzahl der Positionen teilen.
    """,
    fast=r"""
    ```python
    n = modell.n
    anzahl = len(text) - n
    summe = 0.0
    for i in range(anzahl):
        kontext = text[i:i + n]
        richtig = text[i + n]

        if kontext in modell.zaehler:
            verteilung = wahrscheinlichkeiten(...)
            p = verteilung.get(richtig, 0.0)
        else:
            p = ...

        summe += verlust(p)
    return summe / anzahl
    ```
    `verteilung.get(richtig, 0.0)` liefert die Wahrscheinlichkeit oder 0.0, falls das Zeichen nach diesem Kontext nie vorkam.
    """,
    loesung=r"""
    ```python
    def durchschnittlicher_verlust(modell, text):
        n = modell.n
        anzahl = len(text) - n
        summe = 0.0

        for i in range(anzahl):
            kontext = text[i:i + n]
            richtig = text[i + n]

            if kontext in modell.zaehler:
                verteilung = wahrscheinlichkeiten(modell.zaehler[kontext])
                p = verteilung.get(richtig, 0.0)
            else:
                p = 0.0

            summe += verlust(p)

        return summe / anzahl
    ```
    - `anzahl` ist die Zahl der Vorhersagen. Bei einem Text mit 10 Zeichen und n = 2 sind das 8.
    - Es gibt zwei Wege zu `p = 0`: Der Kontext ist unbekannt, oder er ist bekannt, aber das richtige Zeichen kam danach nie vor.
      Beide Fälle bekommen den Verlust unendlich.
    - Um unendlich musst du dich nicht extra kümmern: `float("inf") + 5` ist unendlich, und unendlich geteilt durch 10 auch.
      Ein einziger unmöglicher Treffer macht den ganzen Durchschnitt unendlich.
    """,
)
,
md(r"""
### Das entscheidende Experiment: Bekannter und unbekannter Text

Ein Modell soll nicht nur den Text gut vorhersagen, den es schon kennt. Es soll mit **neuem** Text zurechtkommen.
Deshalb teilen Fachleute ihre Daten immer auf:

- **Trainingsdaten** (hier 90 %): Daraus lernt das Modell.
- **Testdaten** (hier 10 %): Die bekommt das Modell beim Lernen nie zu sehen. Damit prüfen wir, wie gut es verallgemeinert.

Stell dir eine Prüfung vor. Wenn genau die Übungsaufgaben drankommen, sagt das Ergebnis wenig. Spannend wird es bei neuen Aufgaben.
""")
,
code(r"""
grenze = int(len(trainingstext) * 0.9)
training = trainingstext[:grenze]
test = trainingstext[grenze:]

print(f"Training: {len(training)} Zeichen")
print(f"Test:     {len(test)} Zeichen")

grafik.verlust_vergleich(NGramModell, durchschnittlicher_verlust, training, test)
""")
,
md(r"""
**Was die Grafik zeigt:**

- **Blau (Training):** Je größer n, desto kleiner der Verlust. Mit viel Kontext kann das Modell den bekannten Text fast perfekt vorhersagen.
  Es hat ihn auswendig gelernt.
- **Orange (Test):** Der Verlust ist bei **jedem** n unendlich (∞), sogar bei n = 1. Irgendwo im Testtext taucht ein Zeichenpaar
  oder Kontext auf, den das Modell nie gesehen hat. Dafür hat es die Wahrscheinlichkeit 0 vorhergesagt.
  Ein einziger solcher Fehler reicht, damit der Durchschnitt unendlich wird.

Das N-Gramm-Modell hat zwei Probleme:

1. **Es kann nicht verallgemeinern.** Unbekannte Kontexte sind für das Modell ein komplettes Rätsel.
2. **Es ist zu selbstsicher.** Was es nie gesehen hat, hält es für unmöglich (Wahrscheinlichkeit 0).

Ein besseres Modell müsste **ähnliche Kontexte ähnlich behandeln** und **nie ganz ausschließen**, dass etwas Unerwartetes kommt.
Genau das können neuronale Netze, und damit geht es in Notebook 2 weiter.
""")
,

# =============================================================
# ABSCHLUSS
# =============================================================

md(r"""
---
# Abschluss: Deinen Code speichern

Die nächste Zelle prüft alle Aufgaben noch einmal und speichert deinen Code in der Datei `meincode/notebook1.py`.
In Notebook 2 lädst du ihn von dort wieder: `from meincode.notebook1 import Vocabulary`.

Falls eine Aufgabe nicht besteht, zeigt dir die Zelle, welche. Dann geh zurück, korrigiere sie und führ diese Zelle erneut aus.
""")
,
code(r"""
nb1.speichern(
    einzigartige_zeichen,
    Vocabulary,
    zaehle_bigramme,
    wahrscheinlichkeiten,
    ziehe_zeichen,
    generiere_bigramm,
    NGramModell,
    verlust,
    durchschnittlicher_verlust,
)
""")
,
md(r"""
## Zusammenfassung

Das hast du in diesem Notebook gelernt und gebaut:

| Begriff | Bedeutung |
|---|---|
| **Sprachmodell** | sagt für einen Text eine Verteilung über das nächste Zeichen voraus |
| **Vokabular** | alle bekannten Zeichen, jedes mit einer ID (encode, decode) |
| **Bigramm, N-Gramm** | Modelle, die zählen, was auf die letzten n Zeichen folgt |
| **Bedingte Wahrscheinlichkeit** | $P(b \mid a)$: Wahrscheinlichkeit für $b$, wenn gerade $a$ kam |
| **Verteilung** | alle Möglichkeiten mit ihren Wahrscheinlichkeiten. Summe ist immer 1. |
| **Ziehen (Sampling)** | zufällig, aber gewichtet nach Wahrscheinlichkeit auswählen |
| **Autoregressiv** | Zeichen für Zeichen erzeugen und immer auf das Bisherige schauen |
| **Verlust (Loss)** | $-\log(p)$: wie überrascht das Modell vom richtigen Zeichen ist |
| **Kreuzentropie** | der durchschnittliche Verlust über einen Text |
| **Training und Test** | Daten aufteilen, um Verallgemeinerung zu prüfen |
| **Overfitting** | Trainingsdaten auswendig lernen statt verallgemeinern |

## Ausblick auf Notebook 2

Im nächsten Notebook baust du ein **neuronales Netz** mit der Bibliothek PyTorch.
Es bekommt die IDs aus deinem `Vocabulary` als Eingabe und lernt selbstständig, eine Verteilung über das nächste Zeichen vorherzusagen.
Du wirst sehen, wie der Verlust aus diesem Notebook beim Lernen Schritt für Schritt kleiner wird. Und warum das Netz
auch bei unbekanntem Text nie "unendlich überrascht" ist.
""")
,
md(r"""
---
## Bonus: Für Schnelle (freiwillig, ohne Prüfung)

**Glättung.** Das Problem mit dem unendlichen Verlust lässt sich mit einem einfachen Trick lindern:
Man tut so, als hätte man **jedes** Zeichen des Vokabulars nach jedem Kontext schon einmal zusätzlich gesehen.
Dann ist keine Wahrscheinlichkeit mehr genau 0. Das heißt **Laplace-Glättung** oder *Add-One-Smoothing*:

$$
P(b \mid \text{kontext}) = \frac{\text{Anzahl}(\text{kontext gefolgt von } b) + 1}{\text{Anzahl}(\text{kontext gefolgt von irgendwas}) + V}
$$

Schreibe eine Funktion `geglaetteter_verlust(modell, text, vocabulary)`, die so rechnet.
Wie verändert sich der Verlust auf dem Testtext für n = 1 bis 6? Welches n ist jetzt am besten?
""")
,
aufgabe(
vorlage=r"""
def geglaetteter_verlust(modell, text, vocabulary):
    # DEIN CODE HIER (freiwillig)
    raise NotImplementedError("Bonus: Hier fehlt noch dein Code")
""",
loesung=r"""
def geglaetteter_verlust(modell, text, vocabulary):
    n = modell.n
    V = len(vocabulary)
    anzahl = len(text) - n
    summe = 0.0

    for i in range(anzahl):
        kontext = text[i:i + n]
        richtig = text[i + n]

        folge = modell.zaehler.get(kontext, {})
        p = (folge.get(richtig, 0) + 1) / (sum(folge.values()) + V)
        summe += verlust(p)

    return summe / anzahl


for n in range(1, 7):
    modell = NGramModell(training, n)
    print(f"n = {n}: Testverlust {geglaetteter_verlust(modell, test, vocabulary):.3f}")
""")
,
]
