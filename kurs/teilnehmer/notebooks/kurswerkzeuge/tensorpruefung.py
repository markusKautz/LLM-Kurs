"""Gemeinsame Hilfsfunktionen für die Prüfungen ab Notebook 3. Diese Datei musst du nicht verändern."""

import torch
from IPython.display import HTML, display

from .pruefen import MEINCODE, erwarte


def nah(a, b, toleranz=1e-5):
    """True, wenn a und b dieselbe Form und fast dieselben Werte haben."""
    try:
        a = torch.as_tensor(a.detach() if isinstance(a, torch.Tensor) else a, dtype=torch.float64)
        b = torch.as_tensor(b.detach() if isinstance(b, torch.Tensor) else b, dtype=torch.float64)
        return a.shape == b.shape and torch.allclose(a, b, atol=toleranz, rtol=0)
    except (TypeError, ValueError, RuntimeError):
        return False


def liste(wert):
    """Tensor als gut lesbare Liste für Fehlermeldungen."""
    if not isinstance(wert, torch.Tensor):
        return wert
    werte = wert.detach().tolist()

    def runde(x):
        if isinstance(x, list):
            return [runde(y) for y in x]
        return round(x, 4) if isinstance(x, float) else x

    return runde(werte)


def ist_tensor(wert, name):
    erwarte(wert is not None, f"{name} ist None. Hast du das 'return' vergessen?")
    erwarte(
        isinstance(wert, torch.Tensor),
        f"{name} soll ein Tensor sein, ist aber {type(wert).__name__}.",
    )


def form(wert, erwartet, name):
    erwarte(
        tuple(wert.shape) == tuple(erwartet),
        f"{name} soll die Form {tuple(erwartet)} haben, hat aber {tuple(wert.shape)}.",
    )


def pruefe_vorarbeit(*nummern):
    """Stoppt mit einer verständlichen Meldung, wenn ein früheres Notebook nicht abgeschlossen ist."""
    for nummer in nummern:
        if (MEINCODE / f"notebook{nummer}.py").exists():
            continue
        display(HTML(
            '<div style="background:#fdecea;border-left:6px solid #b3261e;padding:10px 14px;'
            'color:#1a1a1a;font-family:sans-serif">'
            f'<b style="color:#b3261e">Notebook {nummer} fehlt:</b> Die Datei <code>meincode/notebook{nummer}.py</code> '
            f'gibt es noch nicht. Schließe zuerst Notebook {nummer} ab und führe dort die letzte Zelle '
            f'(<code>nb{nummer}.speichern(...)</code>) aus.</div>'
        ))
        raise FileNotFoundError(f"meincode/notebook{nummer}.py fehlt. Schließe zuerst Notebook {nummer} ab.")


class TestVokabular:
    """Ein winziges Vokabular mit den Zeichen a, b, c."""

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
