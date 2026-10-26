"""Prüfungen für Notebook 2. Diese Datei musst du nicht verändern."""

import math

import torch
from IPython.display import HTML, display

from .pruefen import MEINCODE, aufgabe, erwarte, zeige, speichern as _speichern


def _nah(a, b, toleranz=1e-5):
    try:
        a = torch.as_tensor(a.detach() if isinstance(a, torch.Tensor) else a, dtype=torch.float64)
        b = torch.as_tensor(b, dtype=torch.float64)
        return a.shape == b.shape and torch.allclose(a, b, atol=toleranz, rtol=0)
    except (TypeError, ValueError, RuntimeError):
        return False


def _liste(wert):
    """Tensor als gut lesbare Liste für Fehlermeldungen."""
    if isinstance(wert, torch.Tensor):
        return [round(x, 4) if isinstance(x, float) else x for x in wert.detach().flatten().tolist()] \
            if wert.dim() <= 1 else [[round(x, 4) for x in zeile] for zeile in wert.detach().tolist()]
    return wert


def _ist_tensor(wert, name):
    erwarte(
        wert is not None,
        f"{name} ist None. Hast du das 'return' vergessen?",
    )
    erwarte(
        isinstance(wert, torch.Tensor),
        f"{name} soll ein Tensor sein, ist aber {type(wert).__name__}.\n"
        "Tipp: torch.tensor(...), torch.zeros(...) und alle Rechnungen mit Tensoren liefern Tensoren.",
    )


def _form(wert, form, name):
    erwarte(
        tuple(wert.shape) == form,
        f"{name} soll die Form {form} haben, hat aber {tuple(wert.shape)}.",
    )


def pruefe_vorarbeit():
    """Stoppt mit einer verständlichen Meldung, wenn Notebook 1 nicht abgeschlossen ist."""
    if (MEINCODE / "notebook1.py").exists():
        return
    display(HTML(
        '<div style="background:#fdecea;border-left:6px solid #b3261e;padding:10px 14px;'
        'color:#1a1a1a;font-family:sans-serif">'
        '<b style="color:#b3261e">Notebook 1 fehlt:</b> Die Datei <code>meincode/notebook1.py</code> '
        'gibt es noch nicht. Schließe zuerst Notebook 1 ab und führe dort die letzte Zelle '
        '(<code>nb1.speichern(...)</code>) aus.</div>'
    ))
    raise FileNotFoundError("meincode/notebook1.py fehlt. Schließe zuerst Notebook 1 ab.")


# =============================================================
# 2.1 ZEILEN NORMIEREN
# =============================================================

@aufgabe("2.1", "Zeilen einer Matrix normieren")
def pruefe_aufgabe_1(zeilen_normieren):
    eingabe = torch.tensor([[1.0, 3.0], [2.0, 6.0]])
    ergebnis = zeilen_normieren(eingabe)
    _ist_tensor(ergebnis, "Das Ergebnis")
    _form(ergebnis, (2, 2), "Das Ergebnis")
    erwarte(
        _nah(ergebnis, [[0.25, 0.75], [0.25, 0.75]]),
        "Für [[1, 3], [2, 6]] erwarte ich [[0.25, 0.75], [0.25, 0.75]].\n"
        f"Du lieferst {_liste(ergebnis)}.\n"
        "Hast du dim=1 und keepdim=True verwendet? Ohne keepdim teilt PyTorch spaltenweise statt zeilenweise.",
    )
    erwarte(
        _nah(eingabe, [[1.0, 3.0], [2.0, 6.0]]),
        "Deine Funktion verändert die übergebene Matrix. Berechne lieber eine neue.",
    )

    ergebnis = zeilen_normieren(torch.tensor([[1.0, 1.0, 2.0], [0.0, 5.0, 0.0], [3.0, 0.0, 1.0]]))
    erwarte(
        _nah(ergebnis.sum(dim=1), [1.0, 1.0, 1.0]),
        f"Jede Zeile muss sich zu 1 aufsummieren. Bei dir: {_liste(ergebnis.sum(dim=1))}.",
    )


# =============================================================
# 2.2 BIGRAMM-MATRIX
# =============================================================

@aufgabe("2.2", "Bigramme in einer Matrix zählen")
def pruefe_aufgabe_2(bigramm_matrix):
    ergebnis = bigramm_matrix([0, 1, 0, 1], 3)
    _ist_tensor(ergebnis, "Das Ergebnis")
    _form(ergebnis, (3, 3), "Für 3 Zeichen im Vokabular")
    erwartet = [[0, 2, 0], [1, 0, 0], [0, 0, 0]]
    erwarte(
        _nah(ergebnis, erwartet),
        f"Für die IDs [0, 1, 0, 1] erwarte ich {erwartet}:\n"
        "Nach 0 kommt zweimal 1, nach 1 kommt einmal 0.\n"
        f"Du lieferst {_liste(ergebnis)}.\n"
        "Die Zeile ist das aktuelle Zeichen, die Spalte das nächste.",
    )

    ergebnis = bigramm_matrix([2, 2, 2], 3)
    erwarte(
        _nah(ergebnis, [[0, 0, 0], [0, 0, 0], [0, 0, 2]]),
        f"Für [2, 2, 2] erwarte ich eine 2 an Position [2, 2]. Du lieferst {_liste(ergebnis)}.",
    )
    erwarte(
        _nah(bigramm_matrix([1], 2), torch.zeros((2, 2))),
        "Bei nur einer ID gibt es kein Paar. Erwartet wird eine Matrix voller Nullen.",
    )


# =============================================================
# 2.3 ONE-HOT
# =============================================================

@aufgabe("2.3", "One-Hot-Kodierung")
def pruefe_aufgabe_3(one_hot):
    ergebnis = one_hot([2, 0], 3)
    _ist_tensor(ergebnis, "Das Ergebnis")
    _form(ergebnis, (2, 3), "one_hot([2, 0], 3)")
    erwarte(
        _nah(ergebnis, [[0, 0, 1], [1, 0, 0]]),
        f"one_hot([2, 0], 3) sollte [[0, 0, 1], [1, 0, 0]] sein. Du lieferst {_liste(ergebnis)}.",
    )
    erwarte(
        ergebnis.dtype == torch.float32,
        f"Die Werte sollen Kommazahlen sein (float32), sind aber {ergebnis.dtype}.\n"
        "torch.zeros(...) liefert automatisch float32.",
    )

    ergebnis = one_hot(torch.tensor([1, 1, 3]), 4)
    erwarte(
        _nah(ergebnis, [[0, 1, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]]),
        f"one_hot(torch.tensor([1, 1, 3]), 4) stimmt nicht. Du lieferst {_liste(ergebnis)}.",
    )


# =============================================================
# 2.4 SOFTMAX
# =============================================================

@aufgabe("2.4", "Softmax")
def pruefe_aufgabe_4(softmax):
    try:
        ergebnis = softmax(torch.tensor([[0.0, 0.0]]))
    except TypeError as fehler:
        erwarte(
            "return_types.max" not in str(fehler),
            "logits.max(dim=1, keepdim=True) liefert zwei Dinge: die Werte und ihre Positionen.\n"
            "Du brauchst nur die Werte: logits.max(dim=1, keepdim=True).values",
        )
        raise
    _ist_tensor(ergebnis, "Das Ergebnis")
    _form(ergebnis, (1, 2), "softmax einer (1, 2)-Matrix")
    erwarte(
        _nah(ergebnis, [[0.5, 0.5]]),
        f"softmax([[0, 0]]) sollte [[0.5, 0.5]] sein. Du lieferst {_liste(ergebnis)}.",
    )

    ergebnis = softmax(torch.tensor([[0.0, math.log(3)]]))
    erwarte(
        _nah(ergebnis, [[0.25, 0.75]]),
        "softmax([[0, log(3)]]) sollte [[0.25, 0.75]] sein: torch.exp macht daraus 1 und 3,\n"
        "geteilt durch die Summe 4 ergibt das 0.25 und 0.75.\n"
        f"Du lieferst {_liste(ergebnis)}.",
    )

    eingabe = torch.tensor([[1.0, 2.0, 3.0], [1.0, 1.0, 1.0]])
    ergebnis = softmax(eingabe)
    erwarte(
        _nah(ergebnis.sum(dim=1), [1.0, 1.0]),
        "Jede Zeile soll für sich eine Verteilung sein und sich zu 1 aufsummieren.\n"
        f"Deine Zeilensummen: {_liste(ergebnis.sum(dim=1))}.\n"
        "Teilst du durch die Summe jeder Zeile (dim=1, keepdim=True)?",
    )
    erwarte(
        _nah(ergebnis[1], [1 / 3, 1 / 3, 1 / 3]),
        f"Für die Zeile [1, 1, 1] erwarte ich [1/3, 1/3, 1/3]. Du lieferst {_liste(ergebnis[1])}.",
    )
    erwarte(
        _nah(eingabe, [[1.0, 2.0, 3.0], [1.0, 1.0, 1.0]]),
        "Deine Funktion verändert die übergebenen Logits. Berechne lieber neue Tensoren.",
    )

    ergebnis = softmax(torch.tensor([[1000.0, 1000.0], [-1000.0, 0.0]]))
    erwarte(
        not torch.isnan(ergebnis).any(),
        "Bei großen Logits wie [[1000, 1000]] kommt bei dir 'nan' heraus,\n"
        "weil torch.exp(1000) für den Computer unendlich ist.\n"
        "Ziehe vor dem exp von jeder Zeile ihr Maximum ab (siehe Erklärung oben).",
    )
    erwarte(
        _nah(ergebnis, [[0.5, 0.5], [0.0, 1.0]]),
        f"softmax([[1000, 1000], [-1000, 0]]) sollte [[0.5, 0.5], [0, 1]] sein. Du lieferst {_liste(ergebnis)}.\n"
        "Ziehst du das Maximum jeder Zeile ab (dim=1, keepdim=True)?",
    )


# =============================================================
# 2.5 KREUZENTROPIE
# =============================================================

@aufgabe("2.5", "Der Verlust für viele Beispiele")
def pruefe_aufgabe_5(kreuzentropie):
    P = torch.tensor([[0.5, 0.5], [0.1, 0.9]])
    ergebnis = kreuzentropie(P, torch.tensor([0, 1]))
    _ist_tensor(ergebnis, "Das Ergebnis")
    erwartet = (-math.log(0.5) - math.log(0.9)) / 2
    summe = -math.log(0.5) - math.log(0.9)
    erwarte(
        not _nah(ergebnis, summe),
        f"Du lieferst die Summe der Verluste ({summe:.4f}). Gesucht ist der Durchschnitt: .mean()",
    )
    erwarte(
        ergebnis.dim() == 0,
        f"Das Ergebnis soll eine einzelne Zahl sein, hat aber die Form {tuple(ergebnis.shape)}.\n"
        "Hast du am Ende .mean() verwendet?",
    )
    erwarte(
        _nah(ergebnis, erwartet),
        "Zeile 0 hat das richtige Zeichen 0 (p = 0.5), Zeile 1 hat das richtige Zeichen 1 (p = 0.9).\n"
        f"Erwartet: (-log(0.5) - log(0.9)) / 2 = {erwartet:.4f}. Du lieferst {ergebnis.item():.4f}.",
    )

    P = torch.tensor([[0.2, 0.3, 0.5], [0.2, 0.3, 0.5], [0.2, 0.3, 0.5]])
    ergebnis = kreuzentropie(P, torch.tensor([2, 0, 1]))
    erwartet = (-math.log(0.5) - math.log(0.2) - math.log(0.3)) / 3
    erwarte(
        _nah(ergebnis, erwartet),
        f"Für drei Zeilen mit den Zielen [2, 0, 1] erwarte ich {erwartet:.4f}. Du lieferst {_liste(ergebnis)}.\n"
        "Holst du mit P[torch.arange(N), ziele] aus jeder Zeile genau einen Wert?",
    )


# =============================================================
# 2.6 NUMERISCHE ABLEITUNG
# =============================================================

@aufgabe("2.6", "Die Steigung ausrechnen")
def pruefe_aufgabe_6(numerische_ableitung):
    ergebnis = numerische_ableitung(lambda x: x ** 2, 3.0)
    erwarte(
        ergebnis is not None,
        "Deine Funktion gibt nichts zurück (None). Hast du das 'return' vergessen?",
    )
    erwarte(
        _nah(ergebnis, 6.0, 1e-4),
        f"Die Steigung von x² an der Stelle 3 ist 6. Du lieferst {zeige(ergebnis)}.",
    )
    ergebnis = numerische_ableitung(math.sin, 0.0)
    erwarte(
        _nah(ergebnis, 1.0, 1e-4),
        f"Die Steigung von sin an der Stelle 0 ist 1. Du lieferst {zeige(ergebnis)}.",
    )
    ergebnis = numerische_ableitung(lambda x: 5.0, 2.0)
    erwarte(
        _nah(ergebnis, 0.0, 1e-4),
        f"Eine waagrechte Linie hat überall die Steigung 0. Du lieferst {zeige(ergebnis)}.",
    )


# =============================================================
# 2.7 GRADIENTENABSTIEG
# =============================================================

@aufgabe("2.7", "Bergab gehen mit einem Gewicht")
def pruefe_aufgabe_7(gradientenabstieg):
    steigung = lambda w: 2 * (w - 3)
    ergebnis = gradientenabstieg(steigung, 0.0, 0.25, 2)
    erwarte(
        isinstance(ergebnis, list),
        f"Erwartet wird eine Liste aller Positionen, du gibst {type(ergebnis).__name__} zurück.",
    )
    erwarte(
        len(ergebnis) == 3,
        f"Bei 2 Schritten erwarte ich 3 Positionen (Start plus 2 Schritte). Du lieferst {len(ergebnis)}.",
    )
    erwarte(
        _nah(ergebnis, [0.0, 1.5, 2.25]),
        "Start 0, Lernrate 0.25. Die Steigung ist bei w = 0 gleich −6 und bei w = 1.5 gleich −3:\n"
        "  Schritt 1: w = 0 − 0.25 · (−6) = 1.5\n"
        "  Schritt 2: w = 1.5 − 0.25 · (−3) = 2.25\n"
        f"Erwartet [0.0, 1.5, 2.25], du lieferst {zeige(ergebnis)}.\n"
        "Achte auf das Minus: Wir gehen gegen die Steigung.",
    )

    ergebnis = gradientenabstieg(steigung, 10.0, 0.1, 100)
    erwarte(
        _nah(ergebnis[-1], 3.0, 1e-4),
        f"Nach 100 Schritten mit Lernrate 0.1 sollte w fast genau 3 sein. Du landest bei {zeige(ergebnis[-1])}.",
    )


# =============================================================
# 2.8 GRADIENTENSCHRITT
# =============================================================

@aufgabe("2.8", "Ein Lernschritt für alle Gewichte")
def pruefe_aufgabe_8(gradientenschritt):
    W = torch.tensor([[1.0, 2.0]], requires_grad=True)
    b = torch.tensor([0.5], requires_grad=True)
    verlust = W.sum() * 2 + b.sum() * 3          # Gradient von W ist überall 2, von b ist er 3
    verlust.backward()

    try:
        gradientenschritt([W, b], 0.1)
    except RuntimeError as fehler:
        erwarte(
            "in-place" not in str(fehler) and "leaf" not in str(fehler),
            "PyTorch beschwert sich, weil du Gewichte veränderst, während es noch mitrechnet.\n"
            "Schreibe die Änderung in einen Block 'with torch.no_grad():'.",
        )
        raise

    erwarte(
        _nah(W, [[0.8, 1.8]]) and _nah(b, [0.2]),
        "Nach einem Schritt mit Lernrate 0.1 erwarte ich W = [[0.8, 1.8]] und b = [0.2]:\n"
        "  neu = alt − 0.1 · Gradient\n"
        f"Bei dir: W = {_liste(W)}, b = {_liste(b)}.\n"
        "Falls sich gar nichts geändert hat: Verändere die Gewichte direkt mit -=,\n"
        "nicht mit 'gewicht = gewicht - ...'. Sonst änderst du nur eine lokale Variable.",
    )
    erwarte(
        W.requires_grad and W.is_leaf,
        "W wird von PyTorch nicht mehr als lernbares Gewicht erkannt.\n"
        "Verändere die Gewichte mit -= innerhalb von 'with torch.no_grad():'.",
    )
    erwarte(
        (W.grad is None or _nah(W.grad, [[0.0, 0.0]])) and (b.grad is None or _nah(b.grad, [0.0])),
        "Nach dem Schritt müssen die Gradienten wieder 0 sein, sonst addiert PyTorch beim\n"
        "nächsten backward() die neuen Gradienten dazu. Verwende gewicht.grad.zero_().",
    )


# =============================================================
# 2.9 BIGRAMM-NETZ
# =============================================================

@aufgabe("2.9", "Die Klasse BigrammNetz")
def pruefe_aufgabe_9(BigrammNetz):
    netz = BigrammNetz(2)
    erwarte(hasattr(netz, "W"), "Dein Netz braucht ein Attribut self.W.")
    _ist_tensor(netz.W, "self.W")
    _form(netz.W, (2, 2), "self.W (für 2 Zeichen)")
    erwarte(
        _nah(netz.W, torch.zeros((2, 2))),
        "self.W soll am Anfang nur Nullen enthalten (torch.zeros).",
    )
    erwarte(
        netz.W.requires_grad,
        "self.W soll lernbar sein: torch.zeros((V, V), requires_grad=True)",
    )

    P = netz.vorhersage([0, 1, 1])
    _ist_tensor(P, "vorhersage(...)")
    _form(P, (3, 2), "vorhersage für 3 IDs")
    erwarte(
        _nah(P, torch.full((3, 2), 0.5)),
        f"Solange W nur Nullen enthält, ist jede Vorhersage gleichverteilt. Erwartet 0.5 überall, du lieferst {_liste(P)}.",
    )

    verlust = netz.trainingsschritt([0], torch.tensor([1]), 1.0)
    erwarte(
        isinstance(verlust, float),
        f"trainingsschritt soll den Verlust als normale Zahl zurückgeben, nicht als {type(verlust).__name__}.\n"
        "Aus einem Tensor mit einer Zahl wird mit .item() eine normale Zahl.",
    )
    erwarte(
        _nah(verlust, math.log(2)),
        f"trainingsschritt soll den Verlust zurückgeben (hier log(2) ≈ 0.6931). Du lieferst {zeige(verlust)}.",
    )
    erwarte(
        _nah(netz.W, [[-0.5, 0.5], [0.0, 0.0]]),
        "Nach einem Schritt mit Lernrate 1 sollte W = [[-0.5, 0.5], [0, 0]] sein.\n"
        f"Dein W: {_liste(netz.W)}\n"
        "Rufst du verlust.backward() und danach gradientenschritt([self.W], lernrate) auf?",
    )

    netz = BigrammNetz(3)
    ein, ziel = [0, 1, 2, 0], torch.tensor([1, 2, 0, 1])
    erster = netz.trainingsschritt(ein, ziel, 1.0)
    for _ in range(50):
        letzter = netz.trainingsschritt(ein, ziel, 1.0)
    erwarte(
        letzter < erster / 3,
        f"Nach 50 Trainingsschritten sollte der Verlust deutlich sinken. Er ging nur von {erster:.3f} auf {letzter:.3f}.\n"
        "Werden die Gradienten nach jedem Schritt auf 0 gesetzt?",
    )


# =============================================================
# 2.10 GENERIEREN
# =============================================================

class _TestVokabular:
    def __init__(self):
        self.zeichen = ["a", "b", "c"]
        self.zeichen_zu_id = {"a": 0, "b": 1, "c": 2}
        self.id_zu_zeichen = {0: "a", 1: "b", 2: "c"}

    def encode(self, text):
        return [self.zeichen_zu_id[z] for z in text]

    def decode(self, ids):
        return "".join(self.id_zu_zeichen[int(i)] for i in ids)

    def __len__(self):
        return 3


class _TestNetz:
    """Sagt nach jedem Zeichen sicher das nächste im Alphabet voraus: a → b → c → a."""

    def vorhersage(self, ids):
        ids = torch.as_tensor(ids)
        erwarte(
            ids.dim() == 1 and len(ids) == 1,
            "netz.vorhersage erwartet eine Liste mit genau einer ID, zum Beispiel [7].\n"
            f"Du übergibst etwas mit der Form {tuple(ids.shape)}.",
        )
        P = torch.zeros((1, 3))
        P[0, (ids[0] + 1) % 3] = 1.0
        return P


@aufgabe("2.10", "Text generieren mit dem Netz")
def pruefe_aufgabe_10(naechste_verteilung, generiere):
    netz, vocabulary = _TestNetz(), _TestVokabular()

    verteilung = naechste_verteilung(netz, vocabulary, "ca")
    erwarte(
        isinstance(verteilung, dict),
        f"naechste_verteilung soll ein Dictionary zurückgeben, gibt aber {type(verteilung).__name__} zurück.",
    )
    erwarte(
        set(verteilung) == {"a", "b", "c"},
        f"Die Schlüssel sollen die Zeichen 'a', 'b', 'c' sein (keine IDs). Du lieferst {zeige(verteilung)}.",
    )
    erwarte(
        all(isinstance(wert, float) for wert in verteilung.values()),
        "Die Wahrscheinlichkeiten sollen normale Zahlen (float) sein, keine Tensoren.\n"
        "Tipp: P.tolist() macht aus einem Tensor eine Liste normaler Zahlen.",
    )
    erwarte(
        _nah([verteilung["a"], verteilung["b"], verteilung["c"]], [0, 1, 0]),
        "Nach 'ca' zählt nur das letzte Zeichen 'a'. Das Testnetz sagt dann sicher 'b' voraus.\n"
        f"Du lieferst {zeige(verteilung)}.",
    )

    ergebnis = generiere(netz, vocabulary, "a", 4)
    erwarte(
        ergebnis == "abcab",
        f"generiere(netz, vocabulary, 'a', 4) sollte 'abcab' liefern, liefert aber {zeige(ergebnis)}.\n"
        "Denk daran: Der Starttext gehört zum Ergebnis.",
    )
    ergebnis = generiere(netz, vocabulary, "cc", 2)
    erwarte(
        ergebnis == "ccab",
        f"generiere(netz, vocabulary, 'cc', 2) sollte 'ccab' liefern, liefert aber {zeige(ergebnis)}.",
    )


# =============================================================
# ABSCHLUSS
# =============================================================

def speichern(*objekte):
    _speichern(
        notebook=2,
        objekte=objekte,
        dateiname="notebook2",
        importe=["import torch", "", "from meincode.notebook1 import ziehe_zeichen"],
    )
