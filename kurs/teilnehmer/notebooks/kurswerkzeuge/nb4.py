"""Prüfungen für Notebook 4. Diese Datei musst du nicht verändern."""

import torch

from .pruefen import aufgabe, erwarte, speichern as _speichern
from .tensorpruefung import form, ist_tensor, liste, nah, pruefe_vorarbeit as _vorarbeit

MINUS_UNENDLICH = float("-inf")


def pruefe_vorarbeit():
    _vorarbeit(1, 2, 3)


# =============================================================
# 4.1 DURCHSCHNITT MIT SCHLEIFE
# =============================================================

@aufgabe("4.1", "Der Durchschnitt aller bisherigen Zeichen")
def pruefe_aufgabe_1(durchschnitt_bisher):
    x = torch.tensor([[1.0, 2.0], [3.0, 4.0], [5.0, 9.0]])
    ergebnis = durchschnitt_bisher(x)
    erwarte(
        nah(x, [[1.0, 2.0], [3.0, 4.0], [5.0, 9.0]]),
        "Deine Funktion verändert die Eingabe x. Dann rechnen spätere Zeilen mit schon veränderten Werten.\n"
        "Lege mit torch.zeros_like(x) eine neue Tabelle für das Ergebnis an.",
    )
    ist_tensor(ergebnis, "Das Ergebnis")
    form(ergebnis, (3, 2), "Das Ergebnis (3 Zeichen, 2 Koordinaten)")
    erwarte(
        nah(ergebnis, [[1.0, 2.0], [2.0, 3.0], [3.0, 5.0]]),
        "Für x = [[1, 2], [3, 4], [5, 9]] erwarte ich [[1, 2], [2, 3], [3, 5]]:\n"
        "  Zeile 0: nur [1, 2]\n"
        "  Zeile 1: Durchschnitt von [1, 2] und [3, 4]\n"
        "  Zeile 2: Durchschnitt aller drei Zeilen\n"
        f"Du lieferst {liste(ergebnis)}.\n"
        "Nimmst du x[:t + 1], also die Zeilen 0 bis einschließlich t? Und .mean(dim=0) für den Durchschnitt nach unten?",
    )
    erwarte(
        nah(x, [[1.0, 2.0], [3.0, 4.0], [5.0, 9.0]]),
        "Deine Funktion verändert die Eingabe x. Lege mit torch.zeros_like(x) eine neue Tabelle an.",
    )
    erwarte(
        nah(durchschnitt_bisher(torch.tensor([[4.0, -1.0, 7.0]])), [[4.0, -1.0, 7.0]]),
        "Bei nur einem Zeichen ist der Durchschnitt das Zeichen selbst.",
    )


# =============================================================
# 4.2 DURCHSCHNITT ALS MATRIX
# =============================================================

@aufgabe("4.2", "Der Durchschnitt als Matrix")
def pruefe_aufgabe_2(mittelwert_matrix):
    ergebnis = mittelwert_matrix(3)
    ist_tensor(ergebnis, "Das Ergebnis")
    form(ergebnis, (3, 3), "mittelwert_matrix(3)")
    erwartet = [[1, 0, 0], [1 / 2, 1 / 2, 0], [1 / 3, 1 / 3, 1 / 3]]
    erwarte(
        nah(ergebnis, erwartet),
        "mittelwert_matrix(3) soll so aussehen:\n"
        "  [[1,   0,   0  ],\n"
        "   [1/2, 1/2, 0  ],\n"
        "   [1/3, 1/3, 1/3]]\n"
        f"Du lieferst {liste(ergebnis)}.\n"
        "Erst torch.tril(torch.ones(T, T)), dann zeilen_normieren.",
    )
    x = torch.randn(5, 4)
    A = mittelwert_matrix(5)
    erwartet = torch.stack([x[:t + 1].mean(dim=0) for t in range(5)])
    erwarte(
        nah(A @ x, erwartet, 1e-5),
        "mittelwert_matrix(5) @ x liefert nicht den Durchschnitt der bisherigen Zeichen.",
    )


# =============================================================
# 4.3 MASKIEREN
# =============================================================

@aufgabe("4.3", "Nicht in die Zukunft schauen")
def pruefe_aufgabe_3(maskieren):
    punkte = torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
    ergebnis = maskieren(punkte)
    ist_tensor(ergebnis, "Das Ergebnis")
    form(ergebnis, (3, 3), "Das Ergebnis")
    erwartet = torch.tensor([
        [1.0, MINUS_UNENDLICH, MINUS_UNENDLICH],
        [4.0, 5.0, MINUS_UNENDLICH],
        [7.0, 8.0, 9.0],
    ])
    erwarte(
        not nah(ergebnis, erwartet.nan_to_num(neginf=0.0)),
        "In der Zukunft (rechts oben) steht bei dir 0. Dort muss minus unendlich stehen: float('-inf')\n"
        "Nur dann macht die Softmax daraus wirklich 0.",
    )
    erwarte(
        torch.equal(ergebnis, erwartet),
        "Rechts oberhalb der Diagonale (die Zukunft) soll minus unendlich stehen, der Rest bleibt gleich:\n"
        "  [[1, -inf, -inf],\n"
        "   [4,    5, -inf],\n"
        "   [7,    8,    9]]\n"
        f"Du lieferst {liste(ergebnis)}.",
    )
    erwarte(
        torch.equal(punkte, torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])),
        "Deine Funktion verändert die übergebenen Punkte. masked_fill (ohne Unterstrich) liefert einen neuen Tensor.",
    )

    groesser = maskieren(torch.zeros(5, 5))
    erwarte(
        torch.isinf(groesser).sum().item() == 10,
        "Bei einer 5x5-Tabelle stimmt die Maske nicht. Nimmst du die Größe T aus den Punkten: punkte.shape[-1]?",
    )

    stapel = torch.arange(18.0).view(2, 3, 3)
    try:
        ergebnis = maskieren(stapel)
    except RuntimeError:
        ergebnis = None
    erwarte(
        ergebnis is not None and torch.equal(ergebnis, torch.stack([maskieren(stapel[0]), maskieren(stapel[1])])),
        "Deine Funktion klappt mit einer Tabelle, aber nicht mit einem Stapel aus mehreren Tabellen (Form (2, 3, 3)).\n"
        "Nimm T = punkte.shape[-1] (die letzte Richtung), dann funktioniert es für beides.",
    )


# =============================================================
# 4.4 GEWICHTETER DURCHSCHNITT
# =============================================================

@aufgabe("4.4", "Der gewichtete Durchschnitt")
def pruefe_aufgabe_4(gewichteter_durchschnitt):
    x = torch.tensor([[1.0, 2.0], [3.0, 4.0], [5.0, 9.0]])
    ergebnis = gewichteter_durchschnitt(torch.zeros(3, 3), x)
    ist_tensor(ergebnis, "Das Ergebnis")
    form(ergebnis, (3, 2), "Das Ergebnis (3 Zeichen, 2 Koordinaten)")
    erwarte(
        nah(ergebnis, [[1.0, 2.0], [2.0, 3.0], [3.0, 5.0]]),
        "Wenn alle Punkte gleich sind, soll der normale Durchschnitt herauskommen: [[1, 2], [2, 3], [3, 5]].\n"
        f"Du lieferst {liste(ergebnis)}.\n"
        "Reihenfolge: maskieren, dann torch.softmax(..., dim=-1), dann @ x.",
    )

    punkte = torch.tensor([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [50.0, 0.0, 0.0]])
    ergebnis = gewichteter_durchschnitt(punkte, x)
    erwarte(
        nah(ergebnis[2], [1.0, 2.0], 1e-4),
        "Zeichen 2 gibt Zeichen 0 sehr viele Punkte. Es soll deshalb fast genau x[0] = [1, 2] übernehmen.\n"
        f"Du lieferst für Zeile 2: {liste(ergebnis[2])}.",
    )

    stapel_x = torch.randn(2, 3, 2)
    stapel_punkte = torch.randn(2, 3, 3)
    ergebnis = gewichteter_durchschnitt(stapel_punkte, stapel_x)
    einzeln = torch.stack([gewichteter_durchschnitt(stapel_punkte[i], stapel_x[i]) for i in range(2)])
    erwarte(
        nah(ergebnis, einzeln, 1e-5),
        "Mit einem Stapel aus mehreren Tabellen kommt etwas anderes heraus als mit jeder Tabelle einzeln.\n"
        "Verwende torch.softmax(..., dim=-1). dim=-1 ist immer die letzte Richtung, auch bei einem Stapel.",
    )


# =============================================================
# ABSCHLUSS
# =============================================================

def speichern(*objekte):
    _speichern(
        notebook=4,
        objekte=objekte,
        dateiname="notebook4",
        importe=["import torch", "", "from meincode.notebook2 import zeilen_normieren"],
    )
