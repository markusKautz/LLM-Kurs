"""Prüfungen für Notebook 6. Diese Datei musst du nicht verändern."""

import torch
from torch import nn

from .pruefen import aufgabe, erwarte, speichern as _speichern
from .tensorpruefung import form, ist_tensor, nah, pruefe_vorarbeit as _vorarbeit


def pruefe_vorarbeit():
    _vorarbeit(1, 2, 3, 4, 5)


def _anzahl_gewichte(netz):
    return sum(p.numel() for p in netz.parameters())


# =============================================================
# 6.1 MEHRERE KÖPFE
# =============================================================

@aufgabe("6.1", "Mehrere Köpfe")
def pruefe_aufgabe_1(MehrereKoepfe):
    torch.manual_seed(0)
    teil = MehrereKoepfe(8, 4)
    erwarte(isinstance(teil, nn.Module), "MehrereKoepfe soll von nn.Module erben.")
    koepfe = getattr(teil, "koepfe", None)
    erwarte(koepfe is not None, "Dein Baustein braucht ein Attribut self.koepfe.")
    erwarte(
        isinstance(koepfe, nn.ModuleList),
        "self.koepfe soll eine nn.ModuleList sein, keine normale Liste.\n"
        "Nur dann findet PyTorch die Gewichte der Köpfe: nn.ModuleList([... for _ in range(anzahl)])",
    )
    erwarte(len(koepfe) == 4, f"Bei anzahl=4 soll es 4 Köpfe geben, du hast {len(koepfe)}.")
    erwarte(
        all(kopf.query.out_features == 2 for kopf in koepfe),
        "Jeder Kopf soll C // anzahl Zahlen liefern. Bei C = 8 und 4 Köpfen sind das 2: AufmerksamkeitsKopf(C, C // anzahl)",
    )
    projektion = getattr(teil, "projektion", None)
    erwarte(
        isinstance(projektion, nn.Linear) and (projektion.in_features, projektion.out_features) == (8, 8),
        "Dein Baustein braucht ein Attribut self.projektion = nn.Linear(C, C).",
    )

    x = torch.randn(5, 8)
    ergebnis = teil(x)
    ist_tensor(ergebnis, "Das Ergebnis")
    form(ergebnis, (5, 8), "Das Ergebnis (5 Zeichen, C = 8)")
    erwartet = projektion(torch.cat([kopf(x) for kopf in koepfe], dim=-1))
    erwarte(
        nah(ergebnis, erwartet, 1e-5),
        "Das Ergebnis stimmt nicht. forward soll die Ergebnisse aller Köpfe nebeneinanderhängen\n"
        "und durch die Projektion schicken:\n"
        "  return self.projektion(torch.cat([kopf(x) for kopf in self.koepfe], dim=-1))",
    )
    erwarte(
        tuple(teil(torch.randn(3, 5, 8)).shape) == (3, 5, 8),
        "Mit einem Stapel aus 3 Texten klappt es nicht. Verwende torch.cat(..., dim=-1).",
    )


# =============================================================
# 6.2 FEEDFORWARD
# =============================================================

@aufgabe("6.2", "Nachdenken: FeedForward")
def pruefe_aufgabe_2(FeedForward):
    torch.manual_seed(0)
    teil = FeedForward(6)
    erwarte(isinstance(teil, nn.Module), "FeedForward soll von nn.Module erben.")
    for name, groesse in [("schicht1", (6, 24)), ("schicht2", (24, 6))]:
        schicht = getattr(teil, name, None)
        erwarte(isinstance(schicht, nn.Linear), f"Dein Baustein braucht ein Attribut self.{name} vom Typ nn.Linear.")
        erwarte(
            (schicht.in_features, schicht.out_features) == groesse,
            f"self.{name} soll nn.Linear{groesse} sein, wenn C = 6 ist. Die Neuronen-Schicht ist 4 * C groß.",
        )
    x = torch.randn(4, 6)
    ergebnis = teil(x)
    ist_tensor(ergebnis, "Das Ergebnis")
    form(ergebnis, (4, 6), "Das Ergebnis")
    erwartet = teil.schicht2(torch.clamp(teil.schicht1(x), min=0))
    erwarte(
        nah(ergebnis, erwartet, 1e-5),
        "Das Ergebnis stimmt nicht. forward soll self.schicht2(relu(self.schicht1(x))) zurückgeben.",
    )


# =============================================================
# 6.3 TRANSFORMER-BLOCK
# =============================================================

def _block_von_hand(block, x):
    x = x + block.dropout(block.aufmerksamkeit(block.norm1(x)))
    return x + block.dropout(block.feedforward(block.norm2(x)))


@aufgabe("6.3", "Der Transformer-Block")
def pruefe_aufgabe_3(TransformerBlock):
    torch.manual_seed(0)
    block = TransformerBlock(8, 2, 0.0)
    erwarte(isinstance(block, nn.Module), "TransformerBlock soll von nn.Module erben.")
    for name, art in [("norm1", nn.LayerNorm), ("norm2", nn.LayerNorm), ("dropout", nn.Dropout)]:
        erwarte(isinstance(getattr(block, name, None), art), f"Dein Block braucht ein Attribut self.{name} vom Typ nn.{art.__name__}.")
    erwarte(
        hasattr(block, "aufmerksamkeit") and len(getattr(block.aufmerksamkeit, "koepfe", [])) == 2,
        "Dein Block braucht ein Attribut self.aufmerksamkeit = MehrereKoepfe(C, koepfe).",
    )
    erwarte(
        hasattr(block, "feedforward") and hasattr(block.feedforward, "schicht1"),
        "Dein Block braucht ein Attribut self.feedforward = FeedForward(C).",
    )

    x = torch.randn(5, 8)
    ergebnis = block(x)
    ist_tensor(ergebnis, "Das Ergebnis")
    form(ergebnis, (5, 8), "Das Ergebnis")
    ohne_abkuerzung = block.feedforward(block.norm2(block.aufmerksamkeit(block.norm1(x))))
    erwarte(
        not nah(ergebnis, ohne_abkuerzung, 1e-5),
        "Die Abkürzungen fehlen. Zähle das Ergebnis jedes Teils zu x dazu: x = x + ...",
    )
    erwarte(
        nah(ergebnis, _block_von_hand(block, x), 1e-5),
        "Das Ergebnis stimmt nicht. forward ist:\n"
        "  x = x + self.dropout(self.aufmerksamkeit(self.norm1(x)))\n"
        "  x = x + self.dropout(self.feedforward(self.norm2(x)))\n"
        "  return x",
    )

    block = TransformerBlock(8, 2, 0.5)
    erwarte(
        block.dropout.p == 0.5,
        "Der Block soll den Wert dropout an nn.Dropout weitergeben: nn.Dropout(dropout)",
    )
    block.train()
    erwarte(
        not nah(block(x), block(x)),
        "Beim Training sollte Dropout zufällig Zahlen abschalten, zwei Aufrufe liefern dann verschiedene Ergebnisse.\n"
        "Verwendest du self.dropout in forward?",
    )
    block.eval()
    erwarte(nah(block(x), block(x)), "Im Testmodus (netz.eval()) soll der Block immer dasselbe liefern.")


# =============================================================
# 6.4 TRANSFORMER
# =============================================================

@aufgabe("6.4", "Der Transformer")
def pruefe_aufgabe_4(Transformer):
    torch.manual_seed(0)
    netz = Transformer(7, 6, 8, 2, 3, dropout=0.0)
    erwarte(isinstance(netz, nn.Module), "Transformer soll von nn.Module erben.")
    erwarte(getattr(netz, "kontext", None) == 6, "Speichere den Kontext im Netz: self.kontext = kontext")
    for name, art, groesse in [("zeichen", nn.Embedding, (7, 8)), ("position", nn.Embedding, (6, 8)), ("ausgabe", nn.Linear, (7, 8))]:
        baustein = getattr(netz, name, None)
        erwarte(isinstance(baustein, art), f"Dein Netz braucht ein Attribut self.{name} vom Typ nn.{art.__name__}.")
        erwarte(tuple(baustein.weight.shape) == groesse, f"self.{name} hat nicht die richtige Größe. Schau in die Tabelle in der Aufgabe.")
    erwarte(isinstance(getattr(netz, "norm", None), nn.LayerNorm), "Dein Netz braucht ein Attribut self.norm = nn.LayerNorm(C).")
    bloecke = getattr(netz, "bloecke", None)
    erwarte(
        isinstance(bloecke, nn.ModuleList) and len(bloecke) == 3,
        "self.bloecke soll eine nn.ModuleList mit 'bloecke' Transformer-Blöcken sein.",
    )

    X = torch.tensor([[0, 1, 2, 3, 4, 5], [6, 6, 5, 1, 0, 2]])
    netz.eval()
    logits = netz(X)
    ist_tensor(logits, "netz(X)")
    form(logits, (2, 6, 7), "netz(X) für 2 Blöcke mit 6 Zeichen und V = 7")
    x = netz.zeichen(X) + netz.position(torch.arange(6))
    for block in bloecke:
        x = block(x)
    erwarte(
        nah(logits, netz.ausgabe(netz.norm(x)), 1e-5),
        "Die Logits stimmen nicht. Der Weg in forward ist:\n"
        "  1. x = self.zeichen(X) + self.position(torch.arange(T))\n"
        "  2. for block in self.bloecke: x = block(x)\n"
        "  3. return self.ausgabe(self.norm(x))",
    )
    erwarte(
        tuple(netz(X[:, :2]).shape) == (2, 2, 7),
        "Mit kürzeren Blöcken klappt es nicht. Nimm T = X.shape[-1] für torch.arange(T).",
    )
    erwarte(
        Transformer(7, 6, 8, 2, 3, dropout=0.3).bloecke[0].dropout.p == 0.3,
        "Gib dropout an jeden TransformerBlock weiter.",
    )


# =============================================================
# ABSCHLUSS
# =============================================================

def speichern(*objekte):
    _speichern(
        notebook=6,
        objekte=objekte,
        dateiname="notebook6",
        importe=[
            "import torch",
            "from torch import nn",
            "",
            "from meincode.notebook3 import relu",
            "from meincode.notebook5 import AufmerksamkeitsKopf",
        ],
    )
