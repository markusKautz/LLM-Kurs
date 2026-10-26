"""
Grafiken für Notebook 3.

Du musst diese Datei nicht verstehen, um den Kurs zu machen. Wenn du
neugierig bist, darfst du aber gerne hineinschauen.
"""

import html

import matplotlib.pyplot as plt
import numpy as np
import torch
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
from IPython.display import HTML, display

from .grafik import BLAU, ORANGE, GRAU, TEXT, TEXT_HELL, HINTERGRUND, zeichen_name

VOKALE = set("aeiouäöü")


def _np(wert):
    if isinstance(wert, torch.Tensor):
        return wert.detach().cpu().numpy()
    return np.asarray(wert)


def _farbe(zeichen):
    if zeichen in VOKALE:
        return ORANGE
    if zeichen.isalpha():
        return BLAU
    return TEXT_HELL


# =============================================================
# TRAININGSBEISPIELE ALS TABELLE
# =============================================================

def kontext_tabelle(X, Y, vocabulary, anzahl=10):
    """Zeigt die ersten Trainingsbeispiele: Kontext und das Zeichen, das folgen soll."""
    zelle = "padding:4px 12px;font-family:monospace;font-size:16px;"
    zeilen = [
        f'<tr><th style="{zelle}color:{TEXT_HELL}">X (Kontext)</th>'
        f'<th style="{zelle}color:{TEXT_HELL}"></th><th style="{zelle}color:{TEXT_HELL}">Y (Ziel)</th>'
        f'<th style="{zelle}color:{TEXT_HELL}">als IDs</th></tr>'
    ]
    for x, y in zip(X[:anzahl].tolist(), Y[:anzahl].tolist()):
        kontext = "".join(zeichen_name(vocabulary.id_zu_zeichen[i]) for i in x)
        ziel = zeichen_name(vocabulary.id_zu_zeichen[y])
        zeilen.append(
            f'<tr><td style="{zelle}background:{BLAU};color:white;border-radius:4px">{html.escape(kontext)}</td>'
            f'<td style="{zelle}color:{TEXT_HELL}">→</td>'
            f'<td style="{zelle}background:{ORANGE};color:white;border-radius:4px;text-align:center">{html.escape(ziel)}</td>'
            f'<td style="{zelle}color:{TEXT_HELL}">{x} → {y}</td></tr>'
        )
    display(HTML(f'<table style="border-collapse:separate;border-spacing:4px">{"".join(zeilen)}</table>'))


# =============================================================
# AUFBAU DES NETZES
# =============================================================

def netz_bild(kontext, koordinaten, neuronen, V):
    """Schaubild: Wie fließen die Zahlen durch das Netz?"""
    stufen = [
        (f"{kontext} Zeichen", "IDs aus dem Text", GRAU),
        (f"{kontext * koordinaten} Zahlen", f"je {koordinaten} Koordinaten\npro Zeichen", BLAU),
        (f"{neuronen} Neuronen", "@ W1 + b1,\ndann ReLU", BLAU),
        (f"{V} Logits", "@ W2 + b2", BLAU),
        ("Verteilung", f"Softmax:\n{V} Wahrscheinlichkeiten", ORANGE),
    ]
    fig, ax = plt.subplots(figsize=(12, 2.8))
    ax.set_xlim(0, len(stufen) * 2.4)
    ax.set_ylim(0, 2.6)
    ax.axis("off")
    for i, (titel, unten, farbe) in enumerate(stufen):
        x = i * 2.4 + 0.2
        ax.add_patch(FancyBboxPatch((x, 1.0), 1.8, 1.2, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    facecolor=farbe, edgecolor="none"))
        ax.text(x + 0.9, 1.6, titel, ha="center", va="center", color="white", fontsize=12, fontweight="bold")
        ax.text(x + 0.9, 0.55, unten, ha="center", va="center", color=TEXT_HELL, fontsize=10)
        if i < len(stufen) - 1:
            ax.annotate("", xy=(x + 2.38, 1.6), xytext=(x + 1.84, 1.6),
                        arrowprops={"arrowstyle": "-|>", "color": TEXT_HELL, "linewidth": 1.5})
    plt.show()


# =============================================================
# RELU
# =============================================================

def relu_kurve(relu):
    """Zeichnet deine Funktion relu für Zahlen von -3 bis 3."""
    x = torch.linspace(-3, 3, 121)
    y = _np(relu(x))
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    ax.plot(_np(x), y, color=BLAU, linewidth=2.5)
    ax.axhline(0, color=TEXT_HELL, linewidth=0.8)
    ax.axvline(0, color=TEXT_HELL, linewidth=0.8)
    ax.text(-1.6, 0.25, "negativ: wird 0\n(Neuron aus)", ha="center", color=TEXT_HELL, fontsize=10)
    ax.text(1.5, 2.6, "positiv: bleibt\n(Neuron an)", ha="center", color=TEXT_HELL, fontsize=10)
    ax.set_xlabel("Eingabe")
    ax.set_ylabel("relu(Eingabe)")
    ax.set_title("ReLU")
    ax.set_ylim(-0.5, 3.2)
    plt.show()


# =============================================================
# KARTE DER ZEICHEN
# =============================================================

def zeichen_karte(C, zeichen, titel="Die Karte der Zeichen"):
    """Zeichnet jedes Zeichen an seine beiden Koordinaten aus der Tabelle C."""
    C = _np(C)
    if C.shape[1] != 2:
        print(f"Die Karte geht nur mit 2 Koordinaten pro Zeichen. Dieses Netz hat {C.shape[1]}.")
        return
    fig, ax = plt.subplots(figsize=(8, 7))
    for (x, y), z in zip(C, zeichen):
        ax.scatter([x], [y], s=380, color=_farbe(z), alpha=0.9, edgecolors=HINTERGRUND, linewidths=2, zorder=2)
        ax.text(x, y, zeichen_name(z), ha="center", va="center", color="white", fontsize=11,
                fontweight="bold", zorder=3)
    ax.set_title(titel)
    ax.set_xlabel("Koordinate 1")
    ax.set_ylabel("Koordinate 2")
    rand = 0.08 * (C.max(axis=0) - C.min(axis=0))
    ax.set_xlim(C[:, 0].min() - rand[0], C[:, 0].max() + rand[0])
    ax.set_ylim(C[:, 1].min() - rand[1], C[:, 1].max() + rand[1])
    legende = [
        Line2D([], [], marker="o", linestyle="", markersize=11, color=ORANGE, label="Vokale"),
        Line2D([], [], marker="o", linestyle="", markersize=11, color=BLAU, label="Konsonanten"),
        Line2D([], [], marker="o", linestyle="", markersize=11, color=TEXT_HELL, label="Leerzeichen, Satzzeichen"),
    ]
    ax.legend(handles=legende, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    plt.tight_layout()
    plt.show()


# =============================================================
# VORHERSAGE ALS BALKEN
# =============================================================

def top_vorhersagen(verteilung, titel, anzahl=10):
    """Balkendiagramm der wahrscheinlichsten Zeichen aus einem Dictionary {zeichen: p}."""
    paare = sorted(verteilung.items(), key=lambda paar: -paar[1])[:anzahl]
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.bar([zeichen_name(z) for z, _ in paare], [p for _, p in paare], color=BLAU, width=0.6)
    for x, (_, p) in enumerate(paare):
        ax.text(x, p + 0.01, f"{p:.0%}", ha="center", va="bottom", fontsize=9, color=TEXT_HELL)
    ax.set_ylim(0, max(p for _, p in paare) * 1.2)
    ax.set_title(titel)
    ax.grid(axis="x", visible=False)
    plt.show()
