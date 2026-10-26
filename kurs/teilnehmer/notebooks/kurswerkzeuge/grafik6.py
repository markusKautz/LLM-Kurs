"""
Grafiken für Notebook 6 und 7.

Du musst diese Datei nicht verstehen, um den Kurs zu machen. Wenn du
neugierig bist, darfst du aber gerne hineinschauen.
"""

import html

import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import torch
from matplotlib.patches import FancyBboxPatch
from IPython.display import HTML, display

from .grafik import BLAU, ORANGE, GRAU, TEXT, TEXT_HELL, HINTERGRUND, zeichen_name
from .grafik4 import gewichte_bild


def _np(wert):
    if isinstance(wert, torch.Tensor):
        return wert.detach().cpu().numpy()
    return np.asarray(wert)


# =============================================================
# AUFBAU DES TRANSFORMERS
# =============================================================

def _kasten(ax, x, y, breite, hoehe, text, farbe, schrift="white"):
    ax.add_patch(FancyBboxPatch((x, y), breite, hoehe, boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor=farbe, edgecolor="none"))
    ax.text(x + breite / 2, y + hoehe / 2, text, ha="center", va="center", color=schrift, fontsize=10.5, fontweight="bold")


def _pfeil(ax, x, y_von, y_bis):
    ax.annotate("", xy=(x, y_bis), xytext=(x, y_von), arrowprops={"arrowstyle": "-|>", "color": TEXT_HELL, "linewidth": 1.3})


def transformer_bild():
    """Schaubild: Wie ein Transformer aufgebaut ist (von unten nach oben gelesen)."""
    fig, ax = plt.subplots(figsize=(9, 8.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 11.4)
    ax.axis("off")

    _kasten(ax, 2.5, 0.2, 5, 0.7, "Zeichen-IDs", GRAU)
    _pfeil(ax, 5, 0.9, 1.3)
    _kasten(ax, 2.5, 1.3, 5, 0.7, "Zeichen + Position (Einbettung)", BLAU)
    _pfeil(ax, 5, 2.0, 2.5)

    # Ein Transformer-Block
    ax.add_patch(FancyBboxPatch((1.2, 2.5), 7.6, 5.6, boxstyle="round,pad=0.05,rounding_size=0.2",
                                facecolor="none", edgecolor=TEXT_HELL, linewidth=1.2, linestyle="--"))
    ax.text(9.1, 5.3, "Transformer-Block\n\nkommt mehrmals\nübereinander", ha="left", va="center", color=TEXT_HELL, fontsize=10.5)
    _kasten(ax, 2.5, 3.0, 5, 0.6, "LayerNorm", GRAU, TEXT)
    _pfeil(ax, 5, 3.6, 3.9)
    _kasten(ax, 2.5, 3.9, 5, 0.8, "Mehrere Köpfe\n(Informationen sammeln)", ORANGE)
    ax.text(5, 5.05, "+ Abkürzung", ha="center", color=TEXT_HELL, fontsize=10)
    _pfeil(ax, 5, 4.7, 5.5)
    _kasten(ax, 2.5, 5.5, 5, 0.6, "LayerNorm", GRAU, TEXT)
    _pfeil(ax, 5, 6.1, 6.4)
    _kasten(ax, 2.5, 6.4, 5, 0.8, "FeedForward\n(nachdenken)", ORANGE)
    ax.text(5, 7.55, "+ Abkürzung", ha="center", color=TEXT_HELL, fontsize=10)

    for y_unten, y_oben in ((2.6, 4.95), (5.2, 7.45)):
        ax.annotate("", xy=(1.9, y_oben), xytext=(1.9, y_unten),
                    arrowprops={"arrowstyle": "-|>", "color": BLAU, "linewidth": 1.5, "connectionstyle": "arc3,rad=0"})
    ax.text(1.7, 5.2, "Abkürzungen", rotation=90, ha="right", va="center", color=BLAU, fontsize=10)

    _pfeil(ax, 5, 8.1, 8.6)
    _kasten(ax, 2.5, 8.6, 5, 0.6, "LayerNorm", GRAU, TEXT)
    _pfeil(ax, 5, 9.2, 9.5)
    _kasten(ax, 2.5, 9.5, 5, 0.7, "nn.Linear: Logits", BLAU)
    _pfeil(ax, 5, 10.2, 10.6)
    ax.text(5, 10.85, "Verteilung für das nächste Zeichen", ha="center", color=TEXT, fontsize=11)
    plt.show()


# =============================================================
# WORAUF SCHAUEN DIE KÖPFE?
# =============================================================

def koepfe_gewichte(netz, ids, punkte, maskieren, block_nummer=0):
    """Berechnet für jeden Kopf eines Blocks die Aufmerksamkeits-Gewichte mit deinen Funktionen."""
    war_im_training = netz.training
    netz.eval()
    with torch.no_grad():
        ids = torch.as_tensor(ids)
        x = netz.zeichen(ids) + netz.position(torch.arange(len(ids)))
        for block in netz.bloecke[:block_nummer]:
            x = block(x)
        block = netz.bloecke[block_nummer]
        h = block.norm1(x)
        ergebnis = []
        for kopf in block.aufmerksamkeit.koepfe:
            ergebnis.append(torch.softmax(maskieren(punkte(kopf.query(h), kopf.key(h))), dim=-1))
    netz.train(war_im_training)
    return ergebnis


def koepfe_bild(gewichte, text, titel="Jeder Kopf schaut anders"):
    """Die Aufmerksamkeit mehrerer Köpfe nebeneinander."""
    anzahl = len(gewichte)
    if len(text) > 20 and anzahl % 2 == 0:
        zeilen, spalten = 2, anzahl // 2
        groesse = (6 * spalten, 6.4 * zeilen)
    else:
        zeilen, spalten = 1, anzahl
        groesse = (4.2 * anzahl, 4.6)
    fig, achsen = plt.subplots(zeilen, spalten, figsize=groesse, squeeze=False)
    for nummer, (ax, g) in enumerate(zip(achsen.flatten(), gewichte)):
        gewichte_bild(g, text, f"Kopf {nummer + 1}", ax=ax)
        if nummer % spalten > 0:
            ax.set_ylabel("")
    fig.suptitle(titel, fontsize=13, fontweight="bold", color=TEXT)
    plt.tight_layout(rect=(0, 0, 1, 0.95 if zeilen == 2 else 0.9))
    plt.show()


# =============================================================
# TEMPERATUR
# =============================================================

def temperatur_regler(naechste_verteilung, generiere, netz, vocabulary, start="es war einmal "):
    """Regler für die Temperatur: Verteilung für das nächste Zeichen und ein erzeugter Text."""
    regler = widgets.FloatSlider(value=1.0, min=0.1, max=2.5, step=0.1, description="Temperatur", continuous_update=False)
    knopf = widgets.Button(description="Neuen Text erzeugen")
    grafik = widgets.Output()
    textfeld = widgets.HTML()

    def zeichne(_=None):
        temperatur = regler.value
        verteilung = naechste_verteilung(netz, vocabulary, start, temperatur)
        paare = sorted(verteilung.items(), key=lambda paar: -paar[1])[:10]
        with grafik:
            grafik.clear_output(wait=True)
            fig, ax = plt.subplots(figsize=(9, 3))
            ax.bar([zeichen_name(z) for z, _ in paare], [p for _, p in paare], color=BLAU, width=0.6)
            for x, (_, p) in enumerate(paare):
                ax.text(x, p + 0.01, f"{p:.0%}", ha="center", va="bottom", fontsize=9, color=TEXT_HELL)
            ax.set_ylim(0, 1.1)
            ax.set_title(f"Nächstes Zeichen nach {start!r} bei Temperatur {temperatur:.1f}")
            ax.grid(axis="x", visible=False)
            plt.show()
        text = generiere(netz, vocabulary, start, 300, temperatur)
        textfeld.value = (
            f'<div style="font-family:monospace;font-size:15px;white-space:pre-wrap;border:1px solid {GRAU};'
            f'border-radius:6px;padding:10px;margin:8px 0;color:{TEXT};background:{HINTERGRUND}">'
            f'<b>{html.escape(start)}</b>{html.escape(text[len(start):])}</div>'
        )

    regler.observe(zeichne, names="value")
    knopf.on_click(zeichne)
    zeichne()
    display(widgets.VBox([widgets.HBox([regler, knopf]), grafik, textfeld]))


# =============================================================
# RÜCKBLICK
# =============================================================

def verlust_treppe(eintraege, titel="Dein Weg zum Transformer"):
    """Waagrechte Balken: Testverlust jedes Modells. eintraege: Liste von (name, verlust)."""
    namen = [name for name, _ in eintraege]
    werte = [wert for _, wert in eintraege]
    fig, ax = plt.subplots(figsize=(9, 0.6 * len(eintraege) + 1.2))
    farben = [GRAU] * (len(eintraege) - 1) + [ORANGE]
    ax.barh(namen, werte, color=farben, height=0.6)
    for y, wert in enumerate(werte):
        ax.text(wert + 0.03, y, f"{wert:.2f}", va="center", fontsize=10, color=TEXT_HELL)
    ax.invert_yaxis()
    ax.set_xlabel("Verlust auf dem Testtext (kleiner ist besser)")
    ax.set_title(titel)
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, max(werte) * 1.15)
    plt.show()
