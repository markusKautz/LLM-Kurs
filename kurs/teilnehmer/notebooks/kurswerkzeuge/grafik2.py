"""
Grafiken und Animationen für Notebook 2.

Du musst diese Datei nicht verstehen, um den Kurs zu machen. Wenn du
neugierig bist, darfst du aber gerne hineinschauen: Hier steht ganz
normaler Python-Code mit den Bibliotheken matplotlib und PyTorch.
"""

import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import torch
from matplotlib.patches import Rectangle
from IPython.display import HTML, display

from .grafik import BLAU, ORANGE, GRAU, TEXT, TEXT_HELL, HINTERGRUND, zeichen_name


def _namen(zeichen):
    return [zeichen_name(z) for z in zeichen]


def _np(wert):
    """Tensor oder Liste in ein NumPy-Array umwandeln, damit matplotlib es zeichnen kann."""
    if isinstance(wert, torch.Tensor):
        return wert.detach().cpu().numpy()
    return np.asarray(wert)


# =============================================================
# SUMMEN ENTLANG DER ACHSEN
# =============================================================

def summen_achsen(matrix):
    """Zeigt eine Matrix mit den Summen pro Zeile (dim=1) und pro Spalte (dim=0)."""
    matrix = _np(matrix)
    zelle = "padding:6px 14px;text-align:center;font-family:monospace;font-size:15px;"
    zeilen = []
    for zeile in matrix:
        werte = "".join(f'<td style="{zelle}border:1px solid {GRAU};color:{TEXT}">{wert:g}</td>' for wert in zeile)
        zeilen.append(
            f"<tr>{werte}<td style='{zelle}color:{ORANGE};font-weight:bold'>→ {zeile.sum():g}</td></tr>"
        )
    spalten = "".join(
        f'<td style="{zelle}color:{BLAU};font-weight:bold">↓<br>{wert:g}</td>' for wert in matrix.sum(axis=0)
    )
    zeilen.append(f"<tr>{spalten}<td></td></tr>")
    display(HTML(
        f'<div style="display:flex;gap:28px;align-items:center;flex-wrap:wrap;font-family:sans-serif;color:{TEXT}">'
        f'<table style="border-collapse:collapse">{"".join(zeilen)}</table>'
        f'<div style="line-height:1.9">'
        f'<span style="color:{ORANGE};font-weight:bold">matrix.sum(dim=1)</span> = {matrix.sum(axis=1).tolist()}'
        f'<br>summiert jede <b>Zeile</b> (läuft nach rechts)<br><br>'
        f'<span style="color:{BLAU};font-weight:bold">matrix.sum(dim=0)</span> = {matrix.sum(axis=0).tolist()}'
        f'<br>summiert jede <b>Spalte</b> (läuft nach unten)</div></div>'
    ))


# =============================================================
# MATRIZEN ALS BILD
# =============================================================

def _matrix_bild(ax, matrix, zeilen_namen, spalten_namen, vmax=None, cmap="Blues"):
    matrix = _np(matrix)
    bild = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=vmax if vmax is not None else matrix.max(), aspect="auto")
    ax.set_xticks(range(len(spalten_namen)), spalten_namen, fontsize=9)
    ax.set_yticks(range(len(zeilen_namen)), zeilen_namen, fontsize=9)
    ax.tick_params(length=0)
    ax.grid(False)
    for seite in ax.spines.values():
        seite.set_visible(False)
    ax.xaxis.tick_top()
    return bild


def matrix_heatmap(matrix, zeichen, titel):
    """Eine Matrix mit Zeichen als Zeilen- und Spaltennamen."""
    namen = _namen(zeichen)
    matrix = _np(matrix)
    fig, ax = plt.subplots(figsize=(9, 8))
    bild = _matrix_bild(ax, matrix, namen, namen, vmax=matrix.max() * 0.6)
    ax.set_xlabel("... folgt dieses Zeichen", fontsize=12)
    ax.xaxis.set_label_position("top")
    ax.set_ylabel("Nach diesem Zeichen ...", fontsize=12)
    ax.set_title(titel, pad=40)
    leiste = fig.colorbar(bild, ax=ax, shrink=0.6)
    leiste.outline.set_visible(False)
    plt.show()


def one_hot_bild(text, vocabulary, one_hot):
    """Zeigt die One-Hot-Matrix eines kurzen Texts."""
    matrix = _np(one_hot(vocabulary.encode(text), len(vocabulary)))
    fig, ax = plt.subplots(figsize=(11, 0.45 * len(text) + 1.2))
    _matrix_bild(ax, matrix, _namen(text), _namen(vocabulary.zeichen), vmax=1.6)
    for zeile, spalte in zip(*np.nonzero(matrix)):
        ax.text(spalte, zeile, "1", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
    ax.set_ylabel("Zeichen im Text")
    ax.set_title(f"one_hot für {text!r}: eine Zeile pro Zeichen, eine Spalte pro Zeichen im Vokabular", pad=26)
    plt.show()


def zeile_auswaehlen(P, zeichen, one_hot):
    """Wähle ein Zeichen: one_hot(Zeichen) @ P liefert genau eine Zeile von P."""
    V = len(zeichen)
    namen = _namen(zeichen)
    P_tensor = torch.as_tensor(P, dtype=torch.float32)
    P = _np(P)
    auswahl = widgets.Dropdown(
        options=[(name, i) for i, name in enumerate(namen)],
        value=zeichen.index("d") if "d" in zeichen else 0,
        description="Zeichen:",
    )
    ausgabe = widgets.Output()

    def zeichne(_=None):
        i = auswahl.value
        vektor = one_hot([i], V)
        ergebnis = _np(vektor @ P_tensor)
        vektor = _np(vektor)
        with ausgabe:
            ausgabe.clear_output(wait=True)
            fig = plt.figure(figsize=(10, 9.5))
            raster = fig.add_gridspec(5, 1, height_ratios=[0.6, 0.35, 7, 0.35, 0.6], hspace=0.15, top=0.95, bottom=0.04)

            oben = fig.add_subplot(raster[0])
            _matrix_bild(oben, vektor, [f"one_hot({namen[i]!r})"], namen, vmax=1.6)
            oben.text(i, 0, "1", ha="center", va="center", color="white", fontsize=9, fontweight="bold")

            for position, zeichen_op in ((1, "@"), (3, "=")):
                op = fig.add_subplot(raster[position])
                op.axis("off")
                op.text(0.5, 0.5, zeichen_op, ha="center", va="center", fontsize=18, color=TEXT_HELL)

            mitte = fig.add_subplot(raster[2])
            _matrix_bild(mitte, P, namen, namen, vmax=P.max() * 0.6)
            mitte.set_xticklabels([])
            mitte.add_patch(Rectangle((-0.5, i - 0.5), V, 1, fill=False, edgecolor=ORANGE, linewidth=2.5))
            mitte.set_ylabel("Matrix P")

            unten = fig.add_subplot(raster[4])
            _matrix_bild(unten, ergebnis, ["Ergebnis"], namen, vmax=P.max() * 0.6)
            unten.xaxis.tick_bottom()
            for spalte in np.argsort(ergebnis[0])[-3:]:
                unten.text(spalte, 0, f"{ergebnis[0, spalte]:.0%}", ha="center", va="center", color="white", fontsize=7)
            plt.show()
            print(f"Das Ergebnis ist genau die Zeile {namen[i]!r} von P: {np.allclose(ergebnis[0], P[i])}")

    auswahl.observe(zeichne, names="value")
    zeichne()
    display(widgets.VBox([auswahl, ausgabe]))


def heatmaps_vergleich(links, rechts, zeichen, titel_links, titel_rechts):
    """Zwei Matrizen nebeneinander mit derselben Farbskala."""
    namen = _namen(zeichen)
    links, rechts = _np(links), _np(rechts)
    vmax = max(links.max(), rechts.max()) * 0.6
    fig, achsen = plt.subplots(1, 2, figsize=(14, 6.8))
    for ax, matrix, titel in ((achsen[0], links, titel_links), (achsen[1], rechts, titel_rechts)):
        _matrix_bild(ax, matrix, namen, namen, vmax=vmax)
        ax.set_title(titel, pad=28)
    plt.tight_layout()
    plt.show()


# =============================================================
# SOFTMAX
# =============================================================

def softmax_regler(softmax):
    """Vier Regler für die Logits. Daneben die Wahrscheinlichkeiten aus deiner softmax-Funktion."""
    zeichen = ["a", "e", "n", "r"]

    def zeichne(a, e, n, r):
        logits = np.array([[a, e, n, r]])
        P = _np(softmax(torch.tensor(logits, dtype=torch.float32)))[0]
        fig, (links, rechts) = plt.subplots(1, 2, figsize=(11, 3.6))
        links.bar(zeichen, logits[0], color=[BLAU if w >= 0 else GRAU for w in logits[0]], width=0.6)
        links.axhline(0, color=TEXT_HELL, linewidth=0.8)
        links.set_ylim(-5.5, 5.5)
        links.set_title("Logits (beliebige Zahlen)")
        links.grid(axis="x", visible=False)
        rechts.bar(zeichen, P, color=BLAU, width=0.6)
        for x, wert in enumerate(P):
            rechts.text(x, wert + 0.02, f"{wert:.1%}", ha="center", va="bottom", fontsize=10, color=TEXT_HELL)
        rechts.set_ylim(0, 1.12)
        rechts.set_title(f"softmax: Wahrscheinlichkeiten (Summe {P.sum():.2f})")
        rechts.grid(axis="x", visible=False)
        plt.tight_layout()
        plt.show()

    regler = {
        name: widgets.FloatSlider(value=wert, min=-5, max=5, step=0.1, description=f"Logit {name}")
        for name, wert in zip(zeichen, [1.0, 2.0, 0.5, -1.0])
    }
    widgets.interact(zeichne, **regler)


# =============================================================
# ABLEITUNG UND GRADIENTENABSTIEG
# =============================================================

def _f(w):
    return (w - 3) ** 2 + 1


def _ableitung(w):
    return 2 * (w - 3)


def _parabel(ax):
    punkte = np.linspace(-1.5, 7.5, 300)
    ax.plot(punkte, _f(punkte), color=BLAU, linewidth=2)
    ax.set_xlim(-1.5, 7.5)
    ax.set_ylim(0, 22)
    ax.set_xlabel("Gewicht w")
    ax.set_ylabel("Verlust f(w)")


def steigung_erkunden():
    """Regler für w: Zeigt die Tangente und die Steigung der Verlustkurve."""

    def zeichne(w):
        steigung = _ableitung(w)
        fig, ax = plt.subplots(figsize=(8.5, 4.2))
        _parabel(ax)
        x = np.array([w - 1.5, w + 1.5])
        ax.plot(x, _f(w) + steigung * (x - w), color=ORANGE, linewidth=2, label="Tangente (Steigung)")
        ax.scatter([w], [_f(w)], s=90, color=ORANGE, zorder=3, edgecolors=HINTERGRUND, linewidths=2)
        if abs(steigung) > 0.05:
            richtung = -np.sign(steigung)
            ax.annotate("", xy=(w + richtung * 1.2, 1.2), xytext=(w, 1.2),
                        arrowprops={"arrowstyle": "-|>", "color": TEXT, "linewidth": 1.5})
            ax.text(w + richtung * 0.6, 2.2, "bergab", ha="center", color=TEXT, fontsize=10)
        ax.set_title(f"w = {w:.1f}    Steigung f'(w) = {steigung:+.1f}")
        ax.legend(loc="upper center")
        plt.show()

    widgets.interact(zeichne, w=widgets.FloatSlider(value=0.5, min=-1, max=7, step=0.1, description="w"))


def gradientenabstieg_animation(gradientenabstieg, start=-0.5, schritte=20):
    """Zeigt Schritt für Schritt, wie deine Funktion gradientenabstieg die Kugel bergab rollen lässt."""
    lernrate = widgets.Dropdown(
        options=[0.02, 0.1, 0.4, 0.9, 1.05],
        value=0.1,
        description="Lernrate:",
    )
    play = widgets.Play(min=0, max=schritte, interval=500, description="Abspielen")
    regler = widgets.IntSlider(min=0, max=schritte, description="Schritt", readout=False)
    widgets.jslink((play, "value"), (regler, "value"))
    ausgabe = widgets.Output()
    verlauf = []

    def berechne(_=None):
        verlauf[:] = gradientenabstieg(_ableitung, start, lernrate.value, schritte)
        if regler.value == 0:
            zeichne()
        else:
            regler.value = 0

    def zeichne(_=None):
        schritt = min(regler.value, len(verlauf) - 1)
        bisher = np.array(verlauf[:schritt + 1], dtype=float)
        with ausgabe:
            ausgabe.clear_output(wait=True)
            fig, ax = plt.subplots(figsize=(8.5, 4.2))
            _parabel(ax)
            sichtbar = np.clip(bisher, -1.4, 7.4)
            ax.plot(sichtbar, np.minimum(_f(bisher), 21.5), color=GRAU, linewidth=1, marker="o", markersize=5, zorder=2)
            w = bisher[-1]
            ax.scatter([sichtbar[-1]], [min(_f(w), 21.5)], s=140, color=ORANGE, zorder=3, edgecolors=HINTERGRUND, linewidths=2)
            ax.set_title(f"Lernrate {lernrate.value}, Schritt {schritt}: w = {w:.3f}, Verlust = {_f(w):.3f}")
            plt.show()

    lernrate.observe(berechne, names="value")
    regler.observe(zeichne, names="value")
    berechne()
    display(widgets.VBox([widgets.HBox([lernrate, play, regler]), ausgabe]))


def gradient_balken(softmax, kreuzentropie):
    """Lässt PyTorch den Gradienten der Logits für ein Beispiel berechnen und zeigt ihn neben P und Y."""
    zeichen = ["a", "e", "n", "r", "␣"]
    ziel = 2
    logits = torch.tensor([[1.5, 2.0, 0.5, 0.0, -1.0]], requires_grad=True)
    P = softmax(logits)
    kreuzentropie(P, torch.tensor([ziel])).backward()

    P = _np(P)[0]
    Y = np.zeros(len(zeichen))
    Y[ziel] = 1
    gradient = _np(logits.grad)[0]

    fig, achsen = plt.subplots(1, 3, figsize=(13, 3.6), sharey=True)
    for ax, werte, titel in (
        (achsen[0], P, "P (Vorhersage des Netzes)"),
        (achsen[1], Y, f"Y (richtig ist {zeichen[ziel]!r})"),
        (achsen[2], gradient, "Gradient (von PyTorch berechnet)"),
    ):
        farben = [ORANGE if w < 0 else BLAU for w in werte]
        ax.bar(zeichen, werte, color=farben, width=0.6)
        ax.axhline(0, color=TEXT_HELL, linewidth=0.8)
        for x, wert in enumerate(werte):
            ax.text(x, wert + (0.03 if wert >= 0 else -0.03), f"{wert:+.2f}" if ax is achsen[2] else f"{wert:.2f}",
                    ha="center", va="bottom" if wert >= 0 else "top", fontsize=9, color=TEXT_HELL)
        ax.set_title(titel)
        ax.grid(axis="x", visible=False)
    achsen[0].set_ylim(-1.15, 1.15)
    plt.tight_layout()
    plt.show()


# =============================================================
# TRAINING LIVE VERFOLGEN
# =============================================================

class LiveKurve:
    """
    Zeichnet den Verlust während des Trainings.

        kurve = LiveKurve(titel="...")
        kurve.punkt(schritt, verlust_training, verlust_test)
    """

    def __init__(self, titel="Training", ziel=None, ziel_text=""):
        self.titel = titel
        self.ziel = ziel
        self.ziel_text = ziel_text
        self.schritte, self.training, self.test = [], [], []
        self.ausgabe = widgets.Output()
        display(self.ausgabe)

    def punkt(self, schritt, training, test=None):
        self.schritte.append(schritt)
        self.training.append(float(training))
        self.test.append(None if test is None else float(test))
        self._zeichne()

    def _zeichne(self):
        with self.ausgabe:
            self.ausgabe.clear_output(wait=True)
            fig, ax = plt.subplots(figsize=(9, 4))
            ax.plot(self.schritte, self.training, color=BLAU, linewidth=2, label="Training")
            ax.annotate(f"{self.training[-1]:.3f}", (self.schritte[-1], self.training[-1]),
                        textcoords="offset points", xytext=(6, -4), color=BLAU, fontsize=10)
            if any(wert is not None for wert in self.test):
                paare = [(s, w) for s, w in zip(self.schritte, self.test) if w is not None]
                ax.plot(*zip(*paare), color=ORANGE, linewidth=2, label="Test")
                ax.annotate(f"{paare[-1][1]:.3f}", paare[-1], textcoords="offset points",
                            xytext=(6, 2), color=ORANGE, fontsize=10)
            if self.ziel is not None:
                ax.axhline(self.ziel, color=TEXT_HELL, linewidth=1.2, linestyle="--")
                ax.text(0, self.ziel, f" {self.ziel_text} ({self.ziel:.3f})", va="bottom", color=TEXT_HELL, fontsize=10)
            ax.set_xlim(0, max(self.schritte[-1], 1) * 1.1)
            alle = self.training + [wert for wert in self.test if wert is not None]
            ax.set_ylim(0, max(alle) * 1.08)
            ax.set_xlabel("Trainingsschritt")
            ax.set_ylabel("Verlust")
            ax.set_title(self.titel)
            ax.legend(loc="upper right")
            plt.show()
