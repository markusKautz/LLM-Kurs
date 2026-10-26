"""
Grafiken für Notebook 4 und 5.

Du musst diese Datei nicht verstehen, um den Kurs zu machen. Wenn du
neugierig bist, darfst du aber gerne hineinschauen.
"""

import html

import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import torch
from IPython.display import HTML, display

from .grafik import BLAU, ORANGE, GRAU, TEXT, TEXT_HELL, HINTERGRUND, zeichen_name


def _np(wert):
    if isinstance(wert, torch.Tensor):
        return wert.detach().cpu().numpy()
    return np.asarray(wert)


# =============================================================
# FESTES FENSTER: ERGEBNISSE
# =============================================================

def fenster_ergebnisse(ergebnisse):
    """Balken für Trainings- und Testverlust bei verschiedenen Fenstergrößen.

    ergebnisse: Liste von (kontext, anzahl_gewichte, verlust_training, verlust_test)
    """
    namen = [f"{k} Zeichen\n({g:,} Gewichte)".replace(",", ".") for k, g, _, _ in ergebnisse]
    x = np.arange(len(ergebnisse))
    fig, ax = plt.subplots(figsize=(9, 4))
    for verschiebung, index, farbe, name in ((-0.18, 2, BLAU, "Training"), (0.18, 3, ORANGE, "Test")):
        werte = [e[index] for e in ergebnisse]
        ax.bar(x + verschiebung, werte, width=0.34, color=farbe, label=name)
        for xi, wert in zip(x, werte):
            ax.text(xi + verschiebung, wert + 0.05, f"{wert:.2f}", ha="center", va="bottom", fontsize=10, color=TEXT_HELL)
    ax.set_xticks(x, namen)
    ax.set_ylabel("Verlust")
    ax.set_title("Festes Fenster: mehr Kontext, aber schlechter auf neuem Text")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper left")
    plt.show()


# =============================================================
# TABELLEN UND GEWICHTE
# =============================================================

def tabelle(x, zeilen, titel):
    """Eine kleine Tabelle mit Zahlen, jede Zeile mit einem Namen."""
    x = _np(x)
    zelle = "padding:4px 12px;font-family:monospace;font-size:15px;text-align:right;"
    kopf = "".join(f'<th style="{zelle}color:{TEXT_HELL};font-weight:normal">Spalte {j}</th>' for j in range(x.shape[1]))
    reihen = [f'<tr><th></th>{kopf}</tr>']
    for name, zeile in zip(zeilen, x):
        werte = "".join(f'<td style="{zelle}border:1px solid {GRAU};color:{TEXT}">{wert:.2f}</td>' for wert in zeile)
        reihen.append(f'<tr><th style="{zelle}color:{BLAU}">{html.escape(name)}</th>{werte}</tr>')
    display(HTML(
        f'<div style="font-family:sans-serif;color:{TEXT}"><b>{html.escape(titel)}</b>'
        f'<table style="border-collapse:collapse;margin-top:6px">{"".join(reihen)}</table></div>'
    ))


def gewichte_bild(A, zeichen, titel, ax=None):
    """Zeigt eine T x T-Matrix: Zeile = welches Zeichen schaut, Spalte = worauf es schaut."""
    A = _np(A)
    namen = [zeichen_name(z) for z in zeichen]
    T = len(namen)
    eigene_figur = ax is None
    if eigene_figur:
        fig, ax = plt.subplots(figsize=(0.62 * T + 2.2, 0.55 * T + 1.6))
    zukunft = np.triu(np.ones((T, T)), k=1).astype(bool)
    bild = np.where(zukunft, np.nan, A)
    farbskala = plt.get_cmap("Blues").copy()
    farbskala.set_bad("#efeeea")
    ax.imshow(bild, cmap=farbskala, vmin=0, vmax=1, aspect="equal")
    if T <= 14:
        for i in range(T):
            for j in range(T):
                if zukunft[i, j]:
                    continue
                wert = A[i, j]
                ax.text(j, i, f"{wert:.0%}" if wert >= 0.005 else "0", ha="center", va="center", fontsize=9,
                        color="white" if wert > 0.55 else TEXT)
    schrift = 10 if T <= 20 else 7
    ax.set_xticks(range(T), namen, fontsize=schrift)
    ax.set_yticks(range(T), namen, fontsize=schrift)
    ax.xaxis.tick_top()
    ax.tick_params(length=0)
    ax.grid(False)
    for seite in ax.spines.values():
        seite.set_visible(False)
    ax.set_xlabel("... schaut auf dieses Zeichen", fontsize=10)
    ax.xaxis.set_label_position("top")
    ax.set_ylabel("Dieses Zeichen ...", fontsize=10)
    ax.set_title(titel, pad=12)
    if eigene_figur:
        plt.tight_layout()
        plt.show()


# =============================================================
# PUNKTE VERTEILEN
# =============================================================

def punkte_regler(maskieren, text="katze"):
    """Regler für die Punkte, die das letzte Zeichen an alle Zeichen davor vergibt."""
    T = len(text)
    namen = [zeichen_name(z) for z in text]

    def zeichne(**punkte_zeile):
        punkte = torch.zeros(T, T)
        punkte[T - 1] = torch.tensor([punkte_zeile[f"p{j}"] for j in range(T)])
        gewichte = torch.softmax(maskieren(punkte), dim=-1)
        fig, (links, rechts) = plt.subplots(1, 2, figsize=(12, 3.8), gridspec_kw={"width_ratios": [1, 1.2]})
        werte = _np(punkte[T - 1])
        links.bar(namen, werte, color=[BLAU if w >= 0 else GRAU for w in werte], width=0.6)
        links.axhline(0, color=TEXT_HELL, linewidth=0.8)
        links.set_ylim(-5.5, 5.5)
        links.set_title(f"Punkte, die {namen[-1]!r} vergibt")
        links.grid(axis="x", visible=False)
        gewicht_zeile = _np(gewichte[T - 1])
        rechts.bar(namen, gewicht_zeile, color=ORANGE, width=0.6)
        for x, wert in enumerate(gewicht_zeile):
            rechts.text(x, wert + 0.02, f"{wert:.0%}", ha="center", va="bottom", fontsize=10, color=TEXT_HELL)
        rechts.set_ylim(0, 1.12)
        rechts.set_title("Gewichte nach maskieren und Softmax")
        rechts.grid(axis="x", visible=False)
        plt.tight_layout()
        plt.show()

    regler = {
        f"p{j}": widgets.FloatSlider(value=0.0, min=-5, max=5, step=0.1, description=f"Punkte {namen[j]}")
        for j in range(T)
    }
    widgets.interact(zeichne, **regler)


# =============================================================
# WORAUF SCHAUT EIN ZEICHEN? (NOTEBOOK 5)
# =============================================================

def _orange_mit_deckkraft(wert):
    return f"rgba(235,104,52,{min(1.0, 0.08 + 0.92 * wert):.2f})"


def aufmerksamkeit_erkunden(gewichte, text, titel="Worauf schaut dieses Zeichen?"):
    """Regler für ein Zeichen im Text. Alle Zeichen davor werden so stark eingefärbt, wie es auf sie schaut."""
    gewichte = _np(gewichte)
    T = len(text)
    regler = widgets.IntSlider(value=T - 1, min=0, max=T - 1, description="Zeichen Nr.", continuous_update=True)
    ausgabe = widgets.HTML()

    def zeichne(_=None):
        t = regler.value
        teile = []
        for j, zeichen in enumerate(text):
            sichtbar = html.escape(zeichen_name(zeichen))
            if j < t:
                wert = gewichte[t, j]
                farbe = "white" if wert > 0.45 else TEXT
                teile.append(f'<span title="{wert:.0%}" style="background:{_orange_mit_deckkraft(wert)};color:{farbe};'
                             f'padding:2px 1px;border-radius:3px">{sichtbar}</span>')
            elif j == t:
                wert = gewichte[t, j]
                teile.append(f'<span title="{wert:.0%}" style="outline:2px solid {BLAU};background:{_orange_mit_deckkraft(wert)};'
                             f'padding:2px 1px;border-radius:3px;font-weight:bold">{sichtbar}</span>')
            else:
                teile.append(f'<span style="color:{GRAU}">{sichtbar}</span>')
        beste = sorted(range(t + 1), key=lambda j: -gewichte[t, j])[:3]
        liste_beste = ", ".join(f"{zeichen_name(text[j])!r} an Stelle {j} ({gewichte[t, j]:.0%})" for j in beste)
        ausgabe.value = (
            f'<div style="font-family:sans-serif;color:{TEXT}"><b>{html.escape(titel)}</b></div>'
            f'<div style="font-family:monospace;font-size:20px;line-height:2;margin:6px 0;color:{TEXT}">{"".join(teile)}</div>'
            f'<div style="font-family:sans-serif;color:{TEXT_HELL}">Das blau umrandete Zeichen {zeichen_name(text[t])!r} '
            f'schaut am meisten auf: {html.escape(liste_beste)}<br>'
            f'Je kräftiger das Orange, desto mehr Aufmerksamkeit. Grau ist die Zukunft.</div>'
        )

    regler.observe(zeichne, names="value")
    zeichne()
    display(widgets.VBox([regler, ausgabe]))
