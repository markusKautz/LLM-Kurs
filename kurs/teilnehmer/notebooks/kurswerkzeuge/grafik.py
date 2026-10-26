"""
Grafiken und Animationen für die Notebooks.

Du musst diese Datei nicht verstehen, um den Kurs zu machen. Wenn du
neugierig bist, darfst du aber gerne hineinschauen: Hier steht ganz
normaler Python-Code mit der Bibliothek matplotlib.
"""

import html
import math
import random

import ipywidgets as widgets
import matplotlib.pyplot as plt
from matplotlib import animation
from IPython.display import HTML, display

# Farben für alle Grafiken im Kurs
BLAU = "#2a78d6"
ORANGE = "#eb6834"
GRAU = "#b8b7b1"
TEXT = "#0b0b0b"
TEXT_HELL = "#52514e"
HINTERGRUND = "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": HINTERGRUND,
    "axes.facecolor": HINTERGRUND,
    "axes.edgecolor": GRAU,
    "axes.labelcolor": TEXT_HELL,
    "axes.titlecolor": TEXT,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.color": "#e4e3df",
    "grid.linewidth": 0.8,
    "xtick.color": TEXT_HELL,
    "ytick.color": TEXT_HELL,
    "font.size": 11,
    "legend.frameon": False,
    "animation.embed_limit": 50,
})


def zeichen_name(zeichen):
    """Macht unsichtbare Zeichen sichtbar."""
    return {" ": "␣", "\n": "↵", "\t": "⇥"}.get(zeichen, zeichen)


def _text_html(text):
    return html.escape(text).replace("\n", "↵<br>")


# =============================================================
# ZEICHENHÄUFIGKEIT
# =============================================================

def zeichen_haeufigkeit(text):
    """Balkendiagramm: Wie oft kommt jedes Zeichen im Text vor?"""
    anzahl = {}
    for zeichen in text:
        anzahl[zeichen] = anzahl.get(zeichen, 0) + 1
    sortiert = sorted(anzahl.items(), key=lambda paar: -paar[1])

    fig, ax = plt.subplots(figsize=(12, 3.8))
    ax.bar(
        [zeichen_name(z) for z, _ in sortiert],
        [n for _, n in sortiert],
        color=BLAU,
        width=0.7,
    )
    ax.set_title("Wie oft kommt jedes Zeichen vor?")
    ax.set_ylabel("Anzahl im Text")
    ax.grid(axis="x", visible=False)
    ax.text(
        1, 1.02, "␣ = Leerzeichen   ↵ = Zeilenumbruch",
        transform=ax.transAxes, ha="right", color=TEXT_HELL, fontsize=10,
    )
    plt.show()


# =============================================================
# ZÄHLEN ALS ANIMATION
# =============================================================

def zaehlen_animation(text):
    """
    Zeigt Schritt für Schritt, wie Zeichenpaare gezählt werden.
    Mit dem Play-Knopf läuft die Animation von selbst.
    """
    schritte = len(text) - 1

    def zeichne(schritt):
        zaehler = {}
        for i in range(schritt + 1):
            a, b = text[i], text[i + 1]
            zaehler.setdefault(a, {})
            zaehler[a][b] = zaehler[a].get(b, 0) + 1

        aktuell, naechstes = text[schritt], text[schritt + 1]

        # Text mit markiertem Paar
        teile = []
        for i, zeichen in enumerate(text):
            sichtbar = html.escape(zeichen_name(zeichen) if zeichen == " " else zeichen)
            if i == schritt:
                teile.append(f'<span style="background:{BLAU};color:white;padding:2px 3px;border-radius:3px">{sichtbar}</span>')
            elif i == schritt + 1:
                teile.append(f'<span style="background:{ORANGE};color:white;padding:2px 3px;border-radius:3px">{sichtbar}</span>')
            else:
                teile.append(f'<span style="color:{TEXT_HELL};padding:2px 1px">{sichtbar}</span>')

        # Tabelle der bisherigen Zählung
        zeilen = []
        for a in sorted(zaehler):
            eintraege = []
            for b in sorted(zaehler[a]):
                stil = "font-weight:bold;"
                if a == aktuell and b == naechstes:
                    stil += f"background:{ORANGE};color:white;border-radius:3px;"
                eintraege.append(
                    f'<span style="{stil}padding:1px 5px;margin-right:6px">'
                    f'{html.escape(zeichen_name(b))}: {zaehler[a][b]}</span>'
                )
            rahmen = f"border-left:4px solid {BLAU};" if a == aktuell else "border-left:4px solid transparent;"
            zeilen.append(
                f'<tr><td style="{rahmen}padding:3px 10px;font-family:monospace;font-size:15px;text-align:left">'
                f'nach <b>{html.escape(zeichen_name(a))}</b></td>'
                f'<td style="padding:3px 6px;font-family:monospace;text-align:left">{"".join(eintraege)}</td></tr>'
            )

        ausgabe.value = (
            f'<div style="font-family:monospace;font-size:20px;letter-spacing:1px;margin:8px 0 14px 0;color:{TEXT}">{"".join(teile)}</div>'
            f'<div style="color:{TEXT_HELL};margin-bottom:6px;font-family:sans-serif">Schritt {schritt + 1} von {schritte}: '
            f'Nach <b style="color:{BLAU}">{html.escape(zeichen_name(aktuell))}</b> kommt '
            f'<b style="color:{ORANGE}">{html.escape(zeichen_name(naechstes))}</b>. '
            f'Dieser Zähler wird um 1 erhöht.</div>'
            f'<table style="border-collapse:collapse;color:{TEXT}">{"".join(zeilen)}</table>'
        )

    ausgabe = widgets.HTML()
    play = widgets.Play(min=0, max=schritte - 1, interval=900, description="Abspielen")
    regler = widgets.IntSlider(min=0, max=schritte - 1, description="Schritt", readout=False)
    widgets.jslink((play, "value"), (regler, "value"))
    regler.observe(lambda aenderung: zeichne(aenderung["new"]), names="value")
    zeichne(0)
    display(widgets.VBox([widgets.HBox([play, regler]), ausgabe]))


# =============================================================
# BIGRAMM-HEATMAP
# =============================================================

def bigramm_heatmap(zaehler):
    """Zeigt alle gezählten Zeichenpaare als farbige Tabelle."""
    zeichen = sorted(set(zaehler) | {b for folge in zaehler.values() for b in folge})
    zeichen = [z for z in zeichen if z != "\n"]
    index = {z: i for i, z in enumerate(zeichen)}

    matrix = [[0] * len(zeichen) for _ in zeichen]
    for a, folge in zaehler.items():
        for b, anzahl in folge.items():
            if a in index and b in index:
                matrix[index[a]][index[b]] = anzahl

    fig, ax = plt.subplots(figsize=(10, 9))
    bild = ax.imshow(matrix, cmap="Blues", vmin=0, vmax=max(map(max, matrix)) * 0.6)
    namen = [zeichen_name(z) for z in zeichen]
    ax.set_xticks(range(len(zeichen)), namen)
    ax.set_yticks(range(len(zeichen)), namen)
    ax.tick_params(length=0)
    ax.grid(False)
    for seite in ax.spines.values():
        seite.set_visible(False)
    ax.xaxis.set_label_position("top")
    ax.xaxis.tick_top()
    ax.set_xlabel("... folgt dieses Zeichen", fontsize=12)
    ax.set_ylabel("Nach diesem Zeichen ...", fontsize=12)
    leiste = fig.colorbar(bild, ax=ax, shrink=0.6)
    leiste.set_label("Anzahl")
    leiste.outline.set_visible(False)
    plt.show()


# =============================================================
# VERTEILUNG ERKUNDEN
# =============================================================

def _balken_verteilung(ax, verteilung, markiert=None, maximal=12):
    eintraege = sorted(verteilung.items(), key=lambda paar: -paar[1])[:maximal]
    namen = [zeichen_name(z) for z, _ in eintraege]
    werte = [p for _, p in eintraege]
    farben = [ORANGE if z == markiert else BLAU for z, _ in eintraege]
    ax.bar(namen, werte, color=farben, width=0.7)
    for x, wert in enumerate(werte):
        ax.text(x, wert + 0.01, f"{wert:.0%}", ha="center", va="bottom", fontsize=9, color=TEXT_HELL)
    ax.set_ylim(0, max(werte) * 1.2 if werte else 1)
    ax.set_ylabel("Wahrscheinlichkeit")
    ax.grid(axis="x", visible=False)


def naechstes_zeichen_erkunden(zaehler, wahrscheinlichkeiten):
    """Tippe einen Kontext ein und sieh, was das Modell als Nächstes erwartet."""
    eingabe = widgets.Text(
        value="d",
        description="Kontext:",
        placeholder="z. B. d",
        continuous_update=False,
    )
    ausgabe = widgets.Output()

    def zeichne(_=None):
        with ausgabe:
            ausgabe.clear_output(wait=True)
            kontext = eingabe.value
            if kontext not in zaehler:
                print(f"Den Kontext {kontext!r} hat das Modell im Training nie gesehen.")
                return
            verteilung = wahrscheinlichkeiten(zaehler[kontext])
            fig, ax = plt.subplots(figsize=(10, 3.2))
            _balken_verteilung(ax, verteilung)
            ax.set_title(f"Was folgt auf {zeichen_name(kontext)!r}? (die {min(12, len(verteilung))} häufigsten)")
            plt.show()

    eingabe.observe(zeichne, names="value")
    zeichne()
    display(widgets.VBox([eingabe, ausgabe]))


# =============================================================
# ZIEHEN ALS ANIMATION
# =============================================================

def ziehen_animation(wahrscheinlichkeiten, ziehe_zeichen, anzahl=1000):
    """
    Zieht immer wieder ein Zeichen mit deiner Funktion ziehe_zeichen.
    Die blauen Balken zeigen, wie oft jedes Zeichen bisher gezogen wurde.
    Die grauen Striche zeigen die Wahrscheinlichkeit.
    """
    zeichen = sorted(wahrscheinlichkeiten, key=lambda z: -wahrscheinlichkeiten[z])
    gezogen = [ziehe_zeichen(wahrscheinlichkeiten) for _ in range(anzahl)]

    # Am Anfang langsam, später in größeren Sprüngen
    zeitpunkte = sorted({max(1, round(anzahl ** (i / 60))) for i in range(61)})

    fig, ax = plt.subplots(figsize=(9, 3.8), dpi=72)
    namen = [zeichen_name(z) for z in zeichen]
    balken = ax.bar(namen, [0] * len(zeichen), color=BLAU, width=0.6, label="Anteil bisher gezogen")
    ax.scatter(
        namen, [wahrscheinlichkeiten[z] for z in zeichen],
        marker="_", s=900, linewidths=3, color=TEXT_HELL, zorder=3, label="Wahrscheinlichkeit",
    )
    ax.set_ylim(0, 1)
    ax.set_ylabel("Anteil")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper right")
    titel = ax.set_title("")

    def bild(n):
        bisher = gezogen[:n]
        for rechteck, z in zip(balken, zeichen):
            rechteck.set_height(bisher.count(z) / n)
        titel.set_text(f"Nach {n} Ziehungen (zuletzt gezogen: {zeichen_name(bisher[-1])!r})")
        return list(balken) + [titel]

    film = animation.FuncAnimation(fig, bild, frames=zeitpunkte, interval=250, blit=False)
    ergebnis = HTML(film.to_jshtml(default_mode="once"))
    plt.close(fig)
    display(ergebnis)


# =============================================================
# GENERIERUNG SCHRITT FÜR SCHRITT
# =============================================================

def generierung_schritt_fuer_schritt(start, schritte, verteilung_fuer, ziehe_zeichen, kontext_laenge=1):
    """
    Zeigt für jedes neue Zeichen:
    - welcher Kontext betrachtet wird (blau),
    - welche Zeichen in Frage kommen (Balken),
    - welches Zeichen gezogen wurde (orange).
    """
    text = start
    verlauf = []
    for _ in range(schritte):
        verteilung = verteilung_fuer(text)
        if not verteilung:
            break
        gewaehlt = ziehe_zeichen(verteilung)
        verlauf.append((text, verteilung, gewaehlt))
        text += gewaehlt

    if not verlauf:
        print("Für diesen Starttext kennt das Modell kein nächstes Zeichen.")
        return

    textfeld = widgets.HTML()
    grafik = widgets.Output()

    def zeichne(schritt):
        bisher, verteilung, gewaehlt = verlauf[schritt]
        davor = bisher[:-kontext_laenge]
        kontext = bisher[-kontext_laenge:]
        textfeld.value = (
            f'<div style="font-family:monospace;font-size:19px;color:{TEXT};line-height:1.6">'
            f'<span style="color:{TEXT_HELL}">{_text_html(davor)}</span>'
            f'<span style="background:{BLAU};color:white;padding:1px 2px;border-radius:3px">{_text_html(kontext)}</span>'
            f'<span style="background:{ORANGE};color:white;padding:1px 2px;border-radius:3px">{_text_html(zeichen_name(gewaehlt))}</span>'
            f'</div><div style="color:{TEXT_HELL};font-family:sans-serif">Schritt {schritt + 1} von {len(verlauf)}: '
            f'Kontext <b style="color:{BLAU}">{html.escape(repr(kontext))}</b>, gezogen wurde '
            f'<b style="color:{ORANGE}">{html.escape(repr(gewaehlt))}</b> '
            f'(Wahrscheinlichkeit {verteilung[gewaehlt]:.0%})</div>'
        )
        with grafik:
            grafik.clear_output(wait=True)
            fig, ax = plt.subplots(figsize=(10, 3))
            _balken_verteilung(ax, verteilung, markiert=gewaehlt)
            ax.set_title("Mögliche nächste Zeichen")
            plt.show()

    play = widgets.Play(min=0, max=len(verlauf) - 1, interval=1400, description="Abspielen")
    regler = widgets.IntSlider(min=0, max=len(verlauf) - 1, description="Schritt", readout=False)
    widgets.jslink((play, "value"), (regler, "value"))
    regler.observe(lambda aenderung: zeichne(aenderung["new"]), names="value")
    zeichne(0)
    display(widgets.VBox([widgets.HBox([play, regler]), textfeld, grafik]))


# =============================================================
# N-GRAMM: REGLER FÜR n
# =============================================================

def _woerter(text):
    return [wort.strip(".,") for wort in text.split() if wort.strip(".,")]


def ngram_regler(NGramModell, text, laenge=300):
    """Ein Regler für n: Wie verändert sich der erzeugte Text?"""
    trainingswoerter = set(_woerter(text))
    modelle = {}

    regler = widgets.IntSlider(value=1, min=1, max=10, description="n =", continuous_update=False)
    knopf = widgets.Button(description="Neu generieren")
    ausgabe = widgets.HTML()

    def zeichne(_=None):
        n = regler.value
        if n not in modelle:
            modelle[n] = NGramModell(text, n)
        modell = modelle[n]
        start_index = random.randrange(0, len(text) - n)
        erzeugt = modell.generiere(text[start_index:start_index + n], laenge)

        woerter = _woerter(erzeugt)[1:-1]
        echt = sum(wort in trainingswoerter for wort in woerter)
        stuecke = [erzeugt[i:i + 20] for i in range(0, len(erzeugt) - 20)]
        kopiert = sum(stueck in text for stueck in stuecke)

        anteil_echt = echt / len(woerter) if woerter else 0
        anteil_kopiert = kopiert / len(stuecke) if stuecke else 0
        ausgabe.value = (
            f'<div style="font-family:monospace;font-size:15px;white-space:pre-wrap;'
            f'border:1px solid {GRAU};border-radius:6px;padding:10px;margin:8px 0;color:{TEXT};background:{HINTERGRUND}">'
            f'{html.escape(erzeugt)}</div>'
            f'<div style="font-family:sans-serif;color:{TEXT};line-height:1.7">'
            f'Bekannte Kontexte: <b>{len(modell.zaehler)}</b><br>'
            f'Wörter, die es im Trainingstext gibt: <b>{anteil_echt:.0%}</b><br>'
            f'20-Zeichen-Stücke, die wörtlich aus dem Training kopiert sind: <b>{anteil_kopiert:.0%}</b></div>'
        )

    regler.observe(zeichne, names="value")
    knopf.on_click(zeichne)
    zeichne()
    display(widgets.VBox([widgets.HBox([regler, knopf]), ausgabe]))


# =============================================================
# KOMBINATORISCHE EXPLOSION
# =============================================================

def kontexte_explosion(NGramModell, text, vokabulargroesse, max_n=8):
    """Mögliche Kontexte (Vokabular hoch n) im Vergleich zu den tatsächlich gesehenen."""
    werte_n = list(range(1, max_n + 1))
    moeglich = [vokabulargroesse ** n for n in werte_n]
    gesehen = [len(NGramModell(text, n).zaehler) for n in werte_n]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(werte_n, moeglich, color=ORANGE, linewidth=2, marker="o", markersize=7, label="mögliche Kontexte")
    ax.plot(werte_n, gesehen, color=BLAU, linewidth=2, marker="o", markersize=7, label="im Text gesehene Kontexte")
    ax.set_yscale("log")
    ax.set_xlabel("n (Länge des Kontexts)")
    ax.set_ylabel("Anzahl (logarithmisch)")
    ax.set_title("Mögliche und tatsächlich gesehene Kontexte")
    ax.legend(loc="upper left")
    ax.annotate(f"{moeglich[-1]:,}".replace(",", "."), (werte_n[-1], moeglich[-1]),
                textcoords="offset points", xytext=(-12, 0), ha="right", va="center", color=TEXT_HELL)
    ax.annotate(f"{gesehen[-1]:,}".replace(",", "."), (werte_n[-1], gesehen[-1]),
                textcoords="offset points", xytext=(0, -12), ha="center", va="top", color=TEXT_HELL)
    plt.show()


# =============================================================
# VERLUST
# =============================================================

def verlust_kurve():
    """Regler für eine Wahrscheinlichkeit p und der zugehörige Verlust -log(p)."""
    punkte_p = [i / 1000 for i in range(5, 1001)]
    punkte_verlust = [-math.log(p) for p in punkte_p]

    def zeichne(p):
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(punkte_p, punkte_verlust, color=BLAU, linewidth=2)
        ax.scatter([p], [-math.log(p)], s=90, color=ORANGE, zorder=3, edgecolors=HINTERGRUND, linewidths=2)
        ax.annotate(
            f"p = {p:.2f}\nVerlust = {-math.log(p):.2f}",
            (p, -math.log(p)), textcoords="offset points", xytext=(14, 10), color=TEXT,
        )
        ax.set_xlim(0, 1.02)
        ax.set_ylim(0, 5.5)
        ax.set_xlabel("Wahrscheinlichkeit, die das Modell dem richtigen Zeichen gab (p)")
        ax.set_ylabel("Verlust = −log(p)")
        ax.set_title("Je unwahrscheinlicher die richtige Antwort, desto größer der Verlust")
        plt.show()

    widgets.interact(
        zeichne,
        p=widgets.FloatSlider(value=0.5, min=0.01, max=1.0, step=0.01, description="p", continuous_update=True),
    )


def verlust_vergleich(NGramModell, durchschnittlicher_verlust, trainingstext, testtext, max_n=6):
    """Verlust auf bekanntem und unbekanntem Text für verschiedene n."""
    werte_n = list(range(1, max_n + 1))
    training, test = [], []
    for n in werte_n:
        modell = NGramModell(trainingstext, n)
        training.append(durchschnittlicher_verlust(modell, trainingstext))
        test.append(durchschnittlicher_verlust(modell, testtext))

    endlich = [w for w in training + test if w != float("inf")]
    decke = max(endlich) * 1.35 if endlich else 3

    fig, ax = plt.subplots(figsize=(9, 4.5))
    breite = 0.38
    for versatz, werte, farbe, name in (
        (-breite / 2, training, BLAU, "Trainingstext (bekannt)"),
        (breite / 2, test, ORANGE, "Testtext (unbekannt)"),
    ):
        for n, wert in zip(werte_n, werte):
            x = n + versatz
            if wert == float("inf"):
                ax.bar(x, decke, width=breite - 0.04, color="none", edgecolor=farbe, hatch="//", linewidth=1.5)
                ax.text(x, decke * 0.5, "∞", ha="center", va="center", fontsize=20, color=farbe,
                        bbox={"facecolor": HINTERGRUND, "edgecolor": "none", "pad": 1})
            else:
                ax.bar(x, wert, width=breite - 0.04, color=farbe)
                ax.text(x, wert + decke * 0.01, f"{wert:.2f}", ha="center", va="bottom", fontsize=9, color=TEXT_HELL)
        ax.bar(0, 0, color=farbe, label=name)

    ax.set_xticks(werte_n)
    ax.set_xlim(0.4, max_n + 0.6)
    ax.set_ylim(0, decke * 1.05)
    ax.set_xlabel("n (Länge des Kontexts)")
    ax.set_ylabel("durchschnittlicher Verlust")
    ax.set_title("Bekannter und unbekannter Text im Vergleich", pad=34)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
    plt.show()
