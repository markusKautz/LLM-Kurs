"""Prüfungen für Notebook 7. Diese Datei musst du nicht verändern."""

import torch
from torch import nn

from .pruefen import aufgabe, erwarte, zeige, speichern as _speichern
from .tensorpruefung import TestVokabular, nah, pruefe_vorarbeit as _vorarbeit


def pruefe_vorarbeit():
    _vorarbeit(1, 2, 3, 4, 5, 6)


# =============================================================
# 7.1 GEWICHTE ZÄHLEN
# =============================================================

@aufgabe("7.1", "Gewichte zählen")
def pruefe_aufgabe_1(zaehle_gewichte):
    ergebnis = zaehle_gewichte(nn.Linear(3, 4))
    erwarte(ergebnis is not None, "zaehle_gewichte gibt nichts zurück. Hast du das 'return' vergessen?")
    erwarte(
        isinstance(ergebnis, int),
        f"Das Ergebnis soll eine ganze Zahl (int) sein, ist aber {type(ergebnis).__name__}.\n"
        "p.numel() liefert schon eine normale Zahl, sum(...) auch.",
    )
    erwarte(
        ergebnis == 16,
        "nn.Linear(3, 4) hat 3 · 4 = 12 Gewichte und 4 Verschiebungen, zusammen 16.\n"
        f"Du lieferst {ergebnis}. Zählst du mit p.numel() die Zahlen in jedem Tensor aus netz.parameters()?",
    )
    netz = nn.Sequential(nn.Embedding(10, 2), nn.Linear(2, 5))
    erwarte(
        zaehle_gewichte(netz) == 35,
        f"Für ein Netz aus nn.Embedding(10, 2) und nn.Linear(2, 5) erwarte ich 20 + 15 = 35. Du lieferst {zaehle_gewichte(netz)}.",
    )


# =============================================================
# 7.2 TEMPERATUR
# =============================================================

class _TestNetz(nn.Module):
    """Gibt an jeder Position dem nächsten Zeichen im Alphabet 2 Punkte, dem übernächsten 1 Punkt."""

    kontext = 3

    def forward(self, X):
        erwarte(
            isinstance(X, torch.Tensor) and X.dim() == 2 and X.shape[0] == 1 and 1 <= X.shape[1] <= 3,
            "Das Netz erwartet eine Tabelle mit einem Block aus höchstens netz.kontext IDs, Form (1, T).\n"
            "Tipp: torch.tensor([ids]) mit ids = vocabulary.encode(text[-netz.kontext:])",
        )
        T = X.shape[1]
        logits = torch.zeros((1, T, 3))
        for t in range(T):
            logits[0, t, (X[0, t] + 1) % 3] = 2.0
            logits[0, t, (X[0, t] + 2) % 3] = 1.0
        return logits


def _erwartet(temperatur):
    # Nach "a": b bekommt 2 Punkte, c 1 Punkt, a 0 Punkte
    return torch.softmax(torch.tensor([0.0, 2.0, 1.0]) / temperatur, dim=-1).tolist()


@aufgabe("7.2", "Die Temperatur")
def pruefe_aufgabe_2(naechste_verteilung, generiere):
    netz, vocabulary = _TestNetz(), TestVokabular()

    try:
        verteilung = naechste_verteilung(netz, vocabulary, "ca")
    except TypeError as fehler:
        erwarte(
            "temperatur" not in str(fehler),
            "naechste_verteilung soll auch ohne Temperatur funktionieren.\n"
            "Gib dem Parameter einen Standardwert: def naechste_verteilung(netz, vocabulary, text, temperatur=1.0):",
        )
        raise
    erwarte(
        isinstance(verteilung, dict) and set(verteilung) == {"a", "b", "c"},
        f"naechste_verteilung soll ein Dictionary mit den Zeichen als Schlüssel zurückgeben. Du lieferst {zeige(verteilung)}.",
    )
    erwarte(
        all(isinstance(wert, float) for wert in verteilung.values()),
        "Die Wahrscheinlichkeiten sollen normale Zahlen (float) sein. Tipp: .tolist()",
    )
    werte = [verteilung["a"], verteilung["b"], verteilung["c"]]
    erwarte(
        nah(werte, _erwartet(1.0), 1e-4),
        "Ohne Angabe soll die Temperatur 1 sein, dann ändert sich nichts an den Wahrscheinlichkeiten.\n"
        f"Erwartet etwa {[round(w, 3) for w in _erwartet(1.0)]}, du lieferst {[round(w, 3) for w in werte]}.\n"
        "Gib dem Parameter einen Standardwert: temperatur=1.0",
    )

    for temperatur in (0.5, 2.0):
        verteilung = naechste_verteilung(netz, vocabulary, "ca", temperatur)
        werte = [verteilung["a"], verteilung["b"], verteilung["c"]]
        falsch_herum = torch.softmax(torch.tensor([0.0, 2.0, 1.0]) * temperatur, dim=-1).tolist()
        erwarte(
            not nah(werte, falsch_herum, 1e-4),
            "Du multiplizierst mit der Temperatur. Die Logits sollen durch die Temperatur geteilt werden: logits / temperatur",
        )
        erwarte(
            nah(werte, _erwartet(temperatur), 1e-4),
            f"Bei Temperatur {temperatur} erwarte ich etwa {[round(w, 3) for w in _erwartet(temperatur)]}, "
            f"du lieferst {[round(w, 3) for w in werte]}.\n"
            "Teile die Logits der letzten Position durch die Temperatur, bevor du die Softmax anwendest.",
        )

    ergebnis = generiere(netz, vocabulary, "a", 4, 0.01)
    erwarte(
        ergebnis == "abcab",
        "Bei einer winzigen Temperatur (0.01) wird fast immer das wahrscheinlichste Zeichen gezogen.\n"
        f"generiere(netz, vocabulary, 'a', 4, 0.01) sollte deshalb 'abcab' liefern, liefert aber {zeige(ergebnis)}.\n"
        "Gibst du die Temperatur an naechste_verteilung weiter?",
    )
    ergebnis = generiere(netz, vocabulary, "a", 4)
    erwarte(
        isinstance(ergebnis, str) and len(ergebnis) == 5 and ergebnis.startswith("a"),
        f"generiere ohne Temperatur soll auch funktionieren (Standardwert 1.0). Du lieferst {zeige(ergebnis)}.",
    )


# =============================================================
# ABSCHLUSS
# =============================================================

def speichern(*objekte):
    _speichern(
        notebook=7,
        objekte=objekte,
        dateiname="notebook7",
        importe=["import torch", "", "from meincode.notebook1 import ziehe_zeichen"],
    )
