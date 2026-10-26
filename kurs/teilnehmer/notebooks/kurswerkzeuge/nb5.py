"""Prüfungen für Notebook 5. Diese Datei musst du nicht verändern."""

import math

import torch
from torch import nn

from .pruefen import aufgabe, erwarte, zeige, speichern as _speichern
from .tensorpruefung import TestVokabular, form, ist_tensor, liste, nah, pruefe_vorarbeit as _vorarbeit


def pruefe_vorarbeit():
    _vorarbeit(1, 2, 3, 4)


def _aufmerksamkeit(q, k, v):
    """Musterlösung zum Vergleichen."""
    T = q.shape[-2]
    punkte = q @ k.mT / math.sqrt(k.shape[-1])
    punkte = punkte.masked_fill(torch.tril(torch.ones(T, T)) == 0, float("-inf"))
    return torch.softmax(punkte, dim=-1) @ v


# =============================================================
# 5.1 PASSUNG
# =============================================================

@aufgabe("5.1", "Wie gut passen zwei Zeichen zusammen?")
def pruefe_aufgabe_1(passung):
    ergebnis = passung(torch.tensor([1.0, 0.0, 2.0]), torch.tensor([1.0, 0.0, 1.0]))
    erwarte(ergebnis is not None, "passung gibt nichts zurück. Hast du das 'return' vergessen?")
    erwarte(
        nah(ergebnis, 3.0),
        "passung([1, 0, 2], [1, 0, 1]) soll 1·1 + 0·0 + 2·1 = 3 sein.\n"
        f"Du lieferst {liste(ergebnis)}.\n"
        "Malnehmen: q * k. Zusammenzählen: .sum()",
    )
    ergebnis = passung(torch.tensor([1.0, 0.0, 2.0]), torch.tensor([-1.0, 1.0, 0.0]))
    erwarte(
        nah(ergebnis, -1.0),
        f"passung([1, 0, 2], [-1, 1, 0]) soll 1·(-1) + 0·1 + 2·0 = -1 sein. Du lieferst {liste(ergebnis)}.",
    )


# =============================================================
# 5.2 PUNKTE
# =============================================================

@aufgabe("5.2", "Alle Punkte auf einmal")
def pruefe_aufgabe_2(punkte):
    q = torch.tensor([[1.0, 0.0], [0.0, 2.0]])
    k = torch.tensor([[1.0, 3.0], [2.0, 0.0]])
    ergebnis = punkte(q, k)
    ist_tensor(ergebnis, "Das Ergebnis")
    form(ergebnis, (2, 2), "Das Ergebnis (2 Fragen, 2 Schlagwörter)")
    ohne_teilen = torch.tensor([[1.0, 2.0], [6.0, 0.0]])
    erwarte(
        not nah(ergebnis, ohne_teilen),
        "Fast! Teile das Ergebnis noch durch die Wurzel aus der Länge der Schlagwörter: / math.sqrt(k.shape[-1])",
    )
    erwarte(
        not nah(ergebnis, ohne_teilen.T / math.sqrt(2)),
        "Zeilen und Spalten sind vertauscht. Es heißt q @ k.mT, nicht k @ q.mT.",
    )
    erwarte(
        nah(ergebnis, ohne_teilen / math.sqrt(2)),
        "Für q = [[1, 0], [0, 2]] und k = [[1, 3], [2, 0]] erwarte ich [[1, 2], [6, 0]] / √2.\n"
        f"Du lieferst {liste(ergebnis)}.\n"
        "Die Rechnung ist q @ k.mT / math.sqrt(k.shape[-1])",
    )

    q, k = torch.randn(2, 3, 4), torch.randn(2, 3, 4)
    try:
        ergebnis = punkte(q, k)
    except RuntimeError:
        ergebnis = None
    erwarte(
        ergebnis is not None and nah(ergebnis, q @ k.mT / 2.0, 1e-5),
        "Mit einem Stapel aus mehreren Tabellen (Form (2, 3, 4)) stimmt das Ergebnis nicht.\n"
        "Verwende k.mT (nicht k.T) und k.shape[-1] (nicht k.shape[1]).",
    )


# =============================================================
# 5.3 AUFMERKSAMKEIT
# =============================================================

@aufgabe("5.3", "Aufmerksamkeit")
def pruefe_aufgabe_3(aufmerksamkeit):
    torch.manual_seed(0)
    q, k, v = torch.randn(4, 3), torch.randn(4, 3), torch.randn(4, 2)
    ergebnis = aufmerksamkeit(q, k, v)
    ist_tensor(ergebnis, "Das Ergebnis")
    form(ergebnis, (4, 2), "Das Ergebnis (4 Zeichen, Inhalt mit 2 Zahlen)")
    erwarte(
        nah(ergebnis[0], v[0], 1e-5),
        "Das erste Zeichen kann nur auf sich selbst schauen. Seine Zeile muss also genau v[0] sein.\n"
        "Wird die Zukunft maskiert? Verwende gewichteter_durchschnitt aus Notebook 4.",
    )
    erwarte(
        nah(ergebnis, _aufmerksamkeit(q, k, v), 1e-5),
        "Das Ergebnis stimmt nicht. Die Lösung ist eine Zeile:\n"
        "  return gewichteter_durchschnitt(punkte(q, k), v)",
    )
    q, k, v = torch.randn(2, 5, 3), torch.randn(2, 5, 3), torch.randn(2, 5, 3)
    erwarte(
        nah(aufmerksamkeit(q, k, v), _aufmerksamkeit(q, k, v), 1e-5),
        "Mit einem Stapel aus mehreren Tabellen stimmt das Ergebnis nicht.",
    )


# =============================================================
# 5.4 AUFMERKSAMKEITS-KOPF
# =============================================================

@aufgabe("5.4", "Ein Aufmerksamkeits-Kopf")
def pruefe_aufgabe_4(AufmerksamkeitsKopf):
    torch.manual_seed(0)
    kopf = AufmerksamkeitsKopf(6, 4)
    erwarte(isinstance(kopf, nn.Module), "AufmerksamkeitsKopf soll von nn.Module erben.")
    for name in ["query", "key", "value"]:
        schicht = getattr(kopf, name, None)
        erwarte(
            isinstance(schicht, nn.Linear),
            f"Dein Kopf braucht ein Attribut self.{name} vom Typ nn.Linear.",
        )
        erwarte(
            (schicht.in_features, schicht.out_features) == (6, 4),
            f"self.{name} soll aus C Koordinaten H Zahlen machen: nn.Linear(C, H, bias=False)",
        )
        erwarte(
            schicht.bias is None,
            f"self.{name} soll keine Verschiebung haben: nn.Linear(C, H, bias=False)",
        )

    x = torch.randn(5, 6)
    ergebnis = kopf(x)
    ist_tensor(ergebnis, "kopf(x)")
    form(ergebnis, (5, 4), "kopf(x) (5 Zeichen, H = 4)")
    erwartet = _aufmerksamkeit(kopf.query(x), kopf.key(x), kopf.value(x))
    erwarte(
        nah(ergebnis, erwartet, 1e-5),
        "Das Ergebnis stimmt nicht. forward soll\n"
        "  aufmerksamkeit(self.query(x), self.key(x), self.value(x))\n"
        "zurückgeben.",
    )
    x = torch.randn(3, 5, 6)
    erwarte(
        tuple(kopf(x).shape) == (3, 5, 4),
        "Mit einem Stapel aus 3 Texten (Form (3, 5, 6)) stimmt die Form des Ergebnisses nicht.",
    )


# =============================================================
# 5.5 BLÖCKE ZIEHEN
# =============================================================

@aufgabe("5.5", "Trainingsblöcke ziehen")
def pruefe_aufgabe_5(ziehe_bloecke):
    ids = torch.arange(100)
    try:
        ergebnis = ziehe_bloecke(ids, 8, 6)
    except RuntimeError as fehler:
        erwarte(
            "stack" not in str(fehler),
            "Manchmal ragt ein Block über das Ende des Texts hinaus, dann ist Y zu kurz.\n"
            "Ziehe die Startpositionen mit torch.randint(0, len(ids) - kontext, (anzahl,))",
        )
        raise
    erwarte(
        isinstance(ergebnis, tuple) and len(ergebnis) == 2,
        "ziehe_bloecke soll zwei Dinge zurückgeben: return X, Y",
    )
    X, Y = ergebnis
    ist_tensor(X, "X")
    ist_tensor(Y, "Y")
    form(X, (6, 8), "X (6 Blöcke mit je 8 Zeichen)")
    form(Y, (6, 8), "Y (6 Blöcke mit je 8 Zeichen)")
    erwarte(
        bool((X[:, 1:] == X[:, :-1] + 1).all()),
        "Jeder Block soll ein zusammenhängendes Stück des Texts sein: ids[start:start + kontext]",
    )
    erwarte(
        bool((Y == X + 1).all()),
        "Y soll derselbe Block sein, nur um ein Zeichen nach rechts verschoben: ids[start + 1:start + kontext + 1]\n"
        f"Bei dir beginnt der erste Block X mit {X[0, 0].item()} und Y mit {Y[0, 0].item()}.",
    )

    kurz = torch.arange(12)
    try:
        for _ in range(200):
            X, Y = ziehe_bloecke(kurz, 10, 4)
            erwarte(
                tuple(Y.shape) == (4, 10),
                f"Bei einem kurzen Text ist Y zu kurz (Form {tuple(Y.shape)}). Der letzte Start ist len(ids) - kontext - 1.",
            )
    except RuntimeError as fehler:
        erwarte(
            "stack" not in str(fehler) and "size" not in str(fehler),
            "Manchmal ragt ein Block über das Ende des Texts hinaus.\n"
            "Ziehe die Startpositionen mit torch.randint(0, len(ids) - kontext, (anzahl,))",
        )
        raise

    starts = torch.cat([ziehe_bloecke(ids, 8, 6)[0][:, 0] for _ in range(20)])
    erwarte(
        len(set(starts.tolist())) > 10 and starts.max() > 60,
        "Die Startpositionen sollen zufällig über den ganzen Text verteilt sein.",
    )


# =============================================================
# 5.6 AUFMERKSAMKEITS-NETZ
# =============================================================

@aufgabe("5.6", "Das Aufmerksamkeits-Netz")
def pruefe_aufgabe_6(AufmerksamkeitsNetz):
    torch.manual_seed(0)
    netz = AufmerksamkeitsNetz(7, 5, 4)
    erwarte(isinstance(netz, nn.Module), "AufmerksamkeitsNetz soll von nn.Module erben.")
    erwarte(getattr(netz, "kontext", None) == 5, "Speichere den Kontext im Netz: self.kontext = kontext")
    for name, art, form_gewichte in [
        ("zeichen", nn.Embedding, (7, 4)),
        ("position", nn.Embedding, (5, 4)),
        ("schicht", nn.Linear, (16, 4)),
        ("ausgabe", nn.Linear, (7, 16)),
    ]:
        baustein = getattr(netz, name, None)
        erwarte(isinstance(baustein, art), f"Dein Netz braucht ein Attribut self.{name} vom Typ nn.{art.__name__}.")
        erwarte(
            tuple(baustein.weight.shape) == form_gewichte,
            f"self.{name} hat nicht die richtige Größe. Schau in die Tabelle in der Aufgabe.",
        )
    erwarte(
        hasattr(netz, "kopf") and isinstance(netz.kopf, nn.Module) and hasattr(netz.kopf, "query"),
        "Dein Netz braucht ein Attribut self.kopf = AufmerksamkeitsKopf(C, C).",
    )

    X = torch.tensor([[0, 1, 2, 3, 4], [6, 6, 5, 1, 0]])
    logits = netz(X)
    ist_tensor(logits, "netz(X)")
    form(logits, (2, 5, 7), "netz(X) für 2 Blöcke mit 5 Zeichen und V = 7")

    x = netz.zeichen(X) + netz.position(torch.arange(5))
    erwartet = netz.ausgabe(torch.clamp(netz.schicht(netz.kopf(x)), min=0))
    erwarte(
        nah(logits, erwartet, 1e-5),
        "Die Logits stimmen nicht. Der Weg in forward ist:\n"
        "  1. x = self.zeichen(X) + self.position(torch.arange(T))\n"
        "  2. h = relu(self.schicht(self.kopf(x)))\n"
        "  3. return self.ausgabe(h)",
    )
    erwarte(
        tuple(netz(X[:, :3]).shape) == (2, 3, 7),
        "Mit kürzeren Blöcken (3 Zeichen) klappt es nicht. Nimm T = X.shape[-1] für torch.arange(T).",
    )


# =============================================================
# 5.7 TEXT GENERIEREN
# =============================================================

class _TestNetz(nn.Module):
    """Sagt an jeder Position sicher das Zeichen nach diesem im Alphabet voraus: a → b → c → a."""

    kontext = 3

    def forward(self, X):
        erwarte(
            isinstance(X, torch.Tensor) and X.dim() == 2 and X.shape[0] == 1 and 1 <= X.shape[1] <= 3,
            "Das Netz erwartet eine Tabelle mit einem Block aus höchstens netz.kontext IDs, Form (1, T).\n"
            f"Du übergibst {'einen Tensor der Form ' + str(tuple(X.shape)) if isinstance(X, torch.Tensor) else type(X).__name__}.\n"
            "Tipp: torch.tensor([ids]) mit den letzten netz.kontext IDs.",
        )
        T = X.shape[1]
        logits = torch.full((1, T, 3), -100.0)
        for t in range(T):
            logits[0, t, (X[0, t] + 1) % 3] = 100.0
        return logits


@aufgabe("5.7", "Text generieren mit Aufmerksamkeit")
def pruefe_aufgabe_7(naechste_verteilung, generiere):
    netz, vocabulary = _TestNetz(), TestVokabular()
    verteilung = naechste_verteilung(netz, vocabulary, "ba")
    erwarte(
        isinstance(verteilung, dict) and set(verteilung) == {"a", "b", "c"},
        f"naechste_verteilung soll ein Dictionary mit den Zeichen als Schlüssel zurückgeben. Du lieferst {zeige(verteilung)}.",
    )
    erwarte(
        all(isinstance(wert, float) for wert in verteilung.values()),
        "Die Wahrscheinlichkeiten sollen normale Zahlen (float) sein, keine Tensoren. Tipp: .tolist()",
    )
    erwarte(
        nah([verteilung["a"], verteilung["b"], verteilung["c"]], [0, 1, 0]),
        "Nach 'ba' sagt das Testnetz an der letzten Position sicher 'b' voraus.\n"
        f"Du lieferst {zeige(verteilung)}.\n"
        "Das Netz liefert für jede Position Logits. Du brauchst nur die letzte: logits[0, -1]",
    )
    ergebnis = generiere(netz, vocabulary, "a", 5)
    erwarte(
        ergebnis == "abcabc",
        f"generiere(netz, vocabulary, 'a', 5) sollte 'abcabc' liefern, liefert aber {zeige(ergebnis)}.\n"
        "Nimmst du höchstens die letzten netz.kontext Zeichen? text[-netz.kontext:]",
    )


# =============================================================
# ABSCHLUSS
# =============================================================

def speichern(*objekte):
    _speichern(
        notebook=5,
        objekte=objekte,
        dateiname="notebook5",
        importe=[
            "import math",
            "",
            "import torch",
            "from torch import nn",
            "",
            "from meincode.notebook1 import ziehe_zeichen",
            "from meincode.notebook3 import relu",
            "from meincode.notebook4 import gewichteter_durchschnitt",
        ],
    )
