"""Prüfungen für Notebook 3. Diese Datei musst du nicht verändern."""

import math

import torch
from torch import nn
import torch.nn.functional as F

from .pruefen import aufgabe, erwarte, zeige, speichern as _speichern
from .tensorpruefung import TestVokabular, form, ist_tensor, liste, nah, pruefe_vorarbeit as _vorarbeit


def pruefe_vorarbeit():
    _vorarbeit(1, 2)


# =============================================================
# 3.1 TRAININGSBEISPIELE
# =============================================================

@aufgabe("3.1", "Trainingsbeispiele mit mehr Kontext")
def pruefe_aufgabe_1(baue_beispiele):
    ergebnis = baue_beispiele([5, 6, 7, 8, 9], 3)
    erwarte(
        isinstance(ergebnis, tuple) and len(ergebnis) == 2,
        "baue_beispiele soll zwei Dinge zurückgeben: return eingaben, ziele",
    )
    X, Y = ergebnis
    ist_tensor(X, "X")
    ist_tensor(Y, "Y")
    erwarte(
        X.dtype == torch.int64 and Y.dtype == torch.int64,
        f"X und Y sollen ganze Zahlen enthalten (int64), sind aber {X.dtype} und {Y.dtype}.\n"
        "torch.tensor(...) mit einer Liste ganzer Zahlen liefert automatisch int64.",
    )
    erwarte(
        nah(X, [[5, 6, 7], [6, 7, 8]]) and nah(Y, [8, 9]),
        "Für die IDs [5, 6, 7, 8, 9] und Kontext 3 erwarte ich:\n"
        "  X = [[5, 6, 7], [6, 7, 8]]\n"
        "  Y = [8, 9]\n"
        f"Du lieferst X = {liste(X)} und Y = {liste(Y)}.\n"
        "Das letzte Zeichen hat kein Ziel mehr. Die Schleife läuft deshalb nur bis len(ids) - kontext.",
    )

    X, Y = baue_beispiele([1, 2, 3], 1)
    erwarte(
        nah(X, [[1], [2]]) and nah(Y, [2, 3]),
        f"Für [1, 2, 3] und Kontext 1 erwarte ich X = [[1], [2]] und Y = [2, 3]. Du lieferst {liste(X)} und {liste(Y)}.",
    )


# =============================================================
# 3.2 EINBETTEN
# =============================================================

@aufgabe("3.2", "Zeichen in Koordinaten übersetzen")
def pruefe_aufgabe_2(einbetten):
    C = torch.tensor([[0.0, 1.0], [10.0, 11.0], [20.0, 21.0]], requires_grad=True)
    X = torch.tensor([[2, 0], [1, 1]])
    ergebnis = einbetten(C, X)
    ist_tensor(ergebnis, "Das Ergebnis")
    erwarte(
        tuple(ergebnis.shape) != (2, 2, 2),
        "Dein Ergebnis hat die Form (2, 2, 2): ein Würfel statt einer Tabelle.\n"
        "Hänge die Koordinaten der Zeichen nebeneinander, mit torch.cat(..., dim=1).",
    )
    form(ergebnis, (2, 4), "Das Ergebnis (2 Beispiele mit je 2 Zeichen und 2 Koordinaten)")
    erwarte(
        nah(ergebnis, [[20, 21, 0, 1], [10, 11, 10, 11]]),
        "Mit C = [[0, 1], [10, 11], [20, 21]] und X = [[2, 0], [1, 1]] erwarte ich\n"
        "  [[20, 21, 0, 1], [10, 11, 10, 11]]\n"
        "Erste Zeile: Zeichen 2 hat die Koordinaten [20, 21], Zeichen 0 hat [0, 1].\n"
        f"Du lieferst {liste(ergebnis)}.",
    )
    erwarte(
        ergebnis.requires_grad,
        "PyTorch kann durch dein Ergebnis nicht mehr zurückrechnen.\n"
        "Verwende nur Rechnungen mit Tensoren, keine .tolist() oder .item().",
    )

    X = torch.tensor([[0, 1, 2]])
    erwarte(
        nah(einbetten(C, X), [[0, 1, 10, 11, 20, 21]]),
        "Mit 3 Zeichen pro Beispiel stimmt das Ergebnis nicht. Läuft deine Schleife über alle Spalten von X?",
    )


# =============================================================
# 3.3 RELU
# =============================================================

@aufgabe("3.3", "ReLU")
def pruefe_aufgabe_3(relu):
    eingabe = torch.tensor([[-2.0, 0.0, 3.0], [1.5, -0.1, 0.0]])
    ergebnis = relu(eingabe)
    ist_tensor(ergebnis, "Das Ergebnis")
    form(ergebnis, (2, 3), "Das Ergebnis")
    erwarte(
        nah(ergebnis, [[0.0, 0.0, 3.0], [1.5, 0.0, 0.0]]),
        "Negative Zahlen sollen 0 werden, alle anderen bleiben gleich.\n"
        f"Für [[-2, 0, 3], [1.5, -0.1, 0]] erwarte ich [[0, 0, 3], [1.5, 0, 0]]. Du lieferst {liste(ergebnis)}.",
    )
    erwarte(
        nah(eingabe, [[-2.0, 0.0, 3.0], [1.5, -0.1, 0.0]]),
        "Deine Funktion verändert die Eingabe. Berechne lieber einen neuen Tensor.",
    )
    x = torch.tensor([-1.0, 2.0], requires_grad=True)
    erwarte(
        relu(x).requires_grad,
        "PyTorch kann durch dein Ergebnis nicht mehr zurückrechnen. Verwende nur Rechnungen mit Tensoren.",
    )


# =============================================================
# 3.4 HANDNETZ
# =============================================================

def _von_hand(netz, X):
    teile = [netz.C[X[:, i]] for i in range(X.shape[1])]
    x = torch.cat(teile, dim=1)
    return torch.clamp(x @ netz.W1 + netz.b1, min=0) @ netz.W2 + netz.b2


@aufgabe("3.4", "Das Netz von Hand")
def pruefe_aufgabe_4(HandNetz):
    torch.manual_seed(0)
    netz = HandNetz(5, 2, 3, 4)
    for name in ["C", "W1", "b1", "W2", "b2"]:
        erwarte(hasattr(netz, name), f"Dein Netz hat kein Attribut self.{name} mehr. Lass __init__ so, wie es vorgegeben ist.")

    X = torch.tensor([[0, 1], [4, 4], [2, 3]])
    logits = netz.logits(X)
    ist_tensor(logits, "netz.logits(X)")
    form(logits, (3, 5), "Das Ergebnis (3 Beispiele, 5 Zeichen)")
    erwarte(
        nah(logits, _von_hand(netz, X), 1e-4),
        "Die Logits stimmen nicht. Der Weg ist:\n"
        "  1. x = einbetten(self.C, X)\n"
        "  2. h = relu(x @ self.W1 + self.b1)\n"
        "  3. return h @ self.W2 + self.b2",
    )

    gewichte = netz.gewichte()
    erwarte(
        isinstance(gewichte, list) and len(gewichte) == 5,
        f"gewichte() soll eine Liste mit 5 Tensoren zurückgeben. Du lieferst {zeige(gewichte)}.",
    )
    erwarte(
        all(any(g is original for g in gewichte) for original in [netz.C, netz.W1, netz.b1, netz.W2, netz.b2]),
        "gewichte() soll genau [self.C, self.W1, self.b1, self.W2, self.b2] zurückgeben.",
    )

    vorher = netz.W2.detach().clone()
    ziele = torch.tensor([1, 0, 4])
    erster = netz.trainingsschritt(X, ziele, 0.5)
    erwarte(
        isinstance(erster, float),
        f"trainingsschritt soll den Verlust als normale Zahl zurückgeben, nicht als {type(erster).__name__}. Tipp: .item()",
    )
    erwarte(
        not nah(netz.W2, vorher),
        "Nach trainingsschritt haben sich die Gewichte nicht verändert.\n"
        "Rufst du verlust.backward() und gradientenschritt(self.gewichte(), lernrate) auf?",
    )
    for _ in range(100):
        letzter = netz.trainingsschritt(X, ziele, 0.5)
    erwarte(
        letzter < erster / 3,
        f"Nach 100 Schritten sollte der Verlust deutlich sinken. Er ging nur von {erster:.3f} auf {letzter:.3f}.",
    )


# =============================================================
# 3.5 ZEICHENNETZ
# =============================================================

@aufgabe("3.5", "Das Netz mit PyTorch-Bausteinen")
def pruefe_aufgabe_5(ZeichenNetz):
    torch.manual_seed(0)
    netz = ZeichenNetz(5, 2, 3, 4)
    erwarte(
        isinstance(netz, nn.Module),
        "ZeichenNetz soll von nn.Module erben: class ZeichenNetz(nn.Module):",
    )
    erwarte(getattr(netz, "kontext", None) == 2, "Speichere den Kontext im Netz: self.kontext = kontext")
    for name, art in [("einbettung", nn.Embedding), ("schicht1", nn.Linear), ("schicht2", nn.Linear)]:
        erwarte(
            isinstance(getattr(netz, name, None), art),
            f"Dein Netz braucht ein Attribut self.{name} vom Typ nn.{art.__name__}.",
        )
    erwarte(
        tuple(netz.einbettung.weight.shape) == (5, 3),
        f"self.einbettung soll für jedes der V Zeichen 'koordinaten' Zahlen haben: nn.Embedding(V, koordinaten).\n"
        f"Bei dir hat die Tabelle die Form {tuple(netz.einbettung.weight.shape)} statt (5, 3).",
    )
    erwarte(
        (netz.schicht1.in_features, netz.schicht1.out_features) == (6, 4),
        "self.schicht1 bekommt kontext * koordinaten Zahlen und hat 'neuronen' Ausgaben:\n"
        "nn.Linear(kontext * koordinaten, neuronen)",
    )
    erwarte(
        (netz.schicht2.in_features, netz.schicht2.out_features) == (4, 5),
        "self.schicht2 macht aus den Neuronen ein Logit pro Zeichen: nn.Linear(neuronen, V)",
    )

    X = torch.tensor([[0, 1], [4, 4], [2, 3]])
    logits = netz(X)
    ist_tensor(logits, "netz(X)")
    form(logits, (3, 5), "Das Ergebnis (3 Beispiele, 5 Zeichen)")
    E = netz.einbettung.weight
    x = torch.cat([E[X[:, i]] for i in range(2)], dim=1)
    erwartet = netz.schicht2(torch.clamp(netz.schicht1(x), min=0))
    erwarte(
        nah(logits, erwartet, 1e-5),
        "Die Logits stimmen nicht. Der Weg in forward ist:\n"
        "  1. x = einbetten(self.einbettung.weight, X)\n"
        "  2. h = relu(self.schicht1(x))\n"
        "  3. return self.schicht2(h)",
    )
    logits.sum().backward()
    erwarte(
        netz.einbettung.weight.grad is not None,
        "Die Einbettung bekommt keinen Gradienten. Verwende self.einbettung.weight direkt, ohne Kopie.",
    )


# =============================================================
# 3.6 MINIBATCH
# =============================================================

@aufgabe("3.6", "Einen Minibatch ziehen")
def pruefe_aufgabe_6(ziehe_minibatch):
    X = torch.arange(200).view(100, 2)
    Y = torch.arange(100) * 10
    ergebnis = ziehe_minibatch(X, Y, 8)
    erwarte(
        isinstance(ergebnis, tuple) and len(ergebnis) == 2,
        "ziehe_minibatch soll zwei Dinge zurückgeben: return X[auswahl], Y[auswahl]",
    )
    Xb, Yb = ergebnis
    ist_tensor(Xb, "Der Minibatch Xb")
    form(Xb, (8, 2), "Xb (bei groesse=8)")
    form(Yb, (8,), "Yb (bei groesse=8)")
    erwarte(
        nah(Yb, Xb[:, 0] * 5),
        "Eingaben und Ziele passen nicht mehr zusammen. Verwende für X und Y dieselbe Auswahl an Positionen.",
    )
    gezogen = [ziehe_minibatch(X, Y, 8)[1] for _ in range(5)]
    erwarte(
        any(not nah(g, gezogen[0]) for g in gezogen),
        "Jeder Aufruf soll einen anderen, zufälligen Minibatch liefern. Tipp: torch.randint(0, len(X), (groesse,))",
    )
    erwarte(
        any(g.max() > 150 for g in gezogen),
        "Es werden immer nur die ersten Beispiele gezogen. Alle Positionen von 0 bis len(X) - 1 sollen möglich sein.",
    )


# =============================================================
# 3.7 TRAINIEREN
# =============================================================

class _AufzeichnendesNetz(nn.Module):
    def __init__(self):
        super().__init__()
        self.schicht = nn.Linear(2, 3)
        self.groessen = []

    def forward(self, X):
        self.groessen.append(X.shape[0])
        return self.schicht(X)


@aufgabe("3.7", "Die Trainingsschleife")
def pruefe_aufgabe_7(trainiere):
    torch.manual_seed(0)
    X = torch.randn(300, 2)
    Y = (X[:, 0] > 0).long() + (X[:, 1] > 1).long()
    netz = _AufzeichnendesNetz()
    vorher = netz.schicht.weight.detach().clone()

    verluste = trainiere(netz, X, Y, 200, 0.5, groesse=16)
    erwarte(
        isinstance(verluste, list),
        f"trainiere soll eine Liste der Verluste zurückgeben, nicht {type(verluste).__name__}.",
    )
    erwarte(
        len(verluste) == 200,
        f"Bei 200 Schritten erwarte ich 200 Verluste in der Liste. Du lieferst {len(verluste)}.",
    )
    erwarte(
        all(isinstance(v, float) for v in verluste),
        "Die Verluste sollen normale Zahlen sein. Tipp: verluste.append(verlust.item())",
    )
    erwarte(
        set(netz.groessen) == {16},
        f"Das Netz soll Minibatches der Größe groesse=16 bekommen. Es kamen diese Größen an: {sorted(set(netz.groessen))}.\n"
        "Verwende ziehe_minibatch(X, Y, groesse) in jedem Schritt.",
    )
    erwarte(
        not nah(netz.schicht.weight, vorher),
        "Die Gewichte des Netzes haben sich nicht verändert. Rufst du optimierer.step() auf?",
    )
    anfang = sum(verluste[:20]) / 20
    ende = sum(verluste[-20:]) / 20
    erwarte(
        ende < anfang * 0.7,
        f"Der Verlust sinkt kaum (von etwa {anfang:.3f} auf {ende:.3f}).\n"
        "Reihenfolge in jedem Schritt: optimierer.zero_grad(), verlust.backward(), optimierer.step()",
    )


# =============================================================
# 3.8 TEXT GENERIEREN
# =============================================================

class _TestNetz(nn.Module):
    """Sagt sicher das Zeichen nach dem letzten im Alphabet voraus: a → b → c → a."""

    kontext = 2

    def forward(self, X):
        erwarte(
            isinstance(X, torch.Tensor) and tuple(X.shape) == (1, 2),
            "Das Netz erwartet eine Tabelle mit einem Beispiel und genau netz.kontext IDs, Form (1, kontext).\n"
            f"Du übergibst {'einen Tensor der Form ' + str(tuple(X.shape)) if isinstance(X, torch.Tensor) else type(X).__name__}.\n"
            "Tipp: torch.tensor([ids]) mit den letzten netz.kontext IDs.",
        )
        logits = torch.full((1, 3), -100.0)
        logits[0, (X[0, -1] + 1) % 3] = 100.0
        return logits


@aufgabe("3.8", "Text generieren mit mehr Kontext")
def pruefe_aufgabe_8(naechste_verteilung, generiere):
    netz, vocabulary = _TestNetz(), TestVokabular()

    verteilung = naechste_verteilung(netz, vocabulary, "cab")
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
        "Die Wahrscheinlichkeiten sollen normale Zahlen (float) sein, keine Tensoren. Tipp: .tolist()",
    )
    erwarte(
        nah([verteilung["a"], verteilung["b"], verteilung["c"]], [0, 0, 1]),
        "Das Testnetz sagt nach ...b sicher 'c' voraus, die Wahrscheinlichkeiten sollen also etwa [0, 0, 1] sein.\n"
        f"Du lieferst {zeige(verteilung)}.\n"
        "Wandelst du die Logits mit softmax in Wahrscheinlichkeiten um?",
    )

    ergebnis = generiere(netz, vocabulary, "ab", 4)
    erwarte(
        ergebnis == "abcabc",
        f"generiere(netz, vocabulary, 'ab', 4) sollte 'abcabc' liefern, liefert aber {zeige(ergebnis)}.\n"
        "Denk daran: Der Starttext gehört zum Ergebnis.",
    )
    ergebnis = generiere(netz, vocabulary, "cccb", 2)
    erwarte(
        ergebnis == "cccbca",
        f"generiere(netz, vocabulary, 'cccb', 2) sollte 'cccbca' liefern, liefert aber {zeige(ergebnis)}.",
    )


# =============================================================
# ABSCHLUSS
# =============================================================

def speichern(*objekte):
    _speichern(
        notebook=3,
        objekte=objekte,
        dateiname="notebook3",
        importe=[
            "import torch",
            "from torch import nn",
            "import torch.nn.functional as F",
            "",
            "from meincode.notebook1 import ziehe_zeichen",
            "from meincode.notebook2 import softmax, kreuzentropie, gradientenschritt",
        ],
    )
