"""
Animationen für Vortrag 1: Zeichenmodelle.

Rendern mit ./rendern.sh vortrag1.py <Szene>, Szenen: Vokabular, BigrammeZaehlen
"""

from pathlib import Path

from manim import (
    DOWN, LEFT, RIGHT, UP, UL, DL,
    AnimationGroup, Create, FadeIn, FadeOut, Indicate, LaggedStart, ReplacementTransform, Transform, Write,
    Code, RoundedRectangle, Text, VGroup,
    Scene, config, register_font,
)

# Farben wie in den Folien (styles/index.css)
HINTERGRUND = "#fbfaf7"
FLAECHE = "#ffffff"
FLAECHE_HELL = "#f1efea"
LINIE = "#e1ded6"
TEXT = "#16181d"
LEISE = "#575d6b"
SEHR_LEISE = "#9a9fab"
BLAU = "#2a78d6"
ORANGE = "#eb6834"

SANS = "Inter"
MONO = "JetBrains Mono"
SCHRIFTEN = Path(__file__).parent / "schriften"

config.background_color = HINTERGRUND


def zeige(zeichen):
    return "␣" if zeichen == " " else zeichen


def kachel(zeichen, groesse=0.62, schrift=30, rahmen=LINIE, fuellung=FLAECHE):
    """Ein Zeichen in einem abgerundeten Kästchen."""
    kasten = RoundedRectangle(width=groesse, height=groesse, corner_radius=0.1,
                              stroke_color=rahmen, stroke_width=2, fill_color=fuellung, fill_opacity=1)
    farbe = SEHR_LEISE if zeichen == " " else TEXT
    buchstabe = Text(zeige(zeichen), font=MONO, font_size=schrift, color=farbe)
    buchstabe.move_to(kasten)
    return VGroup(kasten, buchstabe)


class Folge(VGroup):
    """Ein Nachfolger in einer Zeile des Zählers: Zeichen und Anzahl."""

    def __init__(self, zeichen, anzahl):
        super().__init__()
        self.zeichen = zeichen
        self.anzahl = anzahl
        self.kasten = RoundedRectangle(width=1.05, height=0.5, corner_radius=0.12,
                                       stroke_color=LINIE, stroke_width=2, fill_color=FLAECHE_HELL, fill_opacity=1)
        self.buchstabe = Text(zeige(zeichen), font=MONO, font_size=24,
                              color=SEHR_LEISE if zeichen == " " else TEXT)
        self.zahl = self.zahl_text(anzahl)
        self.add(self.kasten, self.buchstabe, self.zahl)
        self.anordnen()

    def zahl_text(self, wert):
        return Text(str(wert), font=MONO, font_size=22, color=ORANGE, weight="BOLD")

    def anordnen(self):
        self.buchstabe.move_to(self.kasten).shift(LEFT * 0.22)
        self.zahl.move_to(self.kasten).shift(RIGHT * 0.25)


class BigrammeZaehlen(Scene):
    TEXT = "anna und hanna"

    def construct(self):
        with register_font(str(SCHRIFTEN / "Inter.ttf")), register_font(str(SCHRIFTEN / "JetBrainsMono.ttf")):
            self.aufbauen()
            self.zaehlen()
            self.wahrscheinlichkeit()

    # ---------------------------------------------------------
    def aufbauen(self):
        kicker = Text("SCHRITT 2: ZÄHLEN", font=MONO, font_size=20, color=ORANGE).to_corner(UL, buff=0.6)
        titel = Text("Welches Zeichen folgt auf welches?", font=SANS, font_size=44, weight="BOLD", color=TEXT)
        titel.next_to(kicker, DOWN, aligned_edge=LEFT, buff=0.2)
        self.play(FadeIn(kicker, shift=RIGHT * 0.3), FadeIn(titel, shift=RIGHT * 0.3), run_time=0.8)

        self.kacheln = VGroup(*[kachel(z) for z in self.TEXT]).arrange(RIGHT, buff=0.1)
        self.kacheln.move_to(UP * 1.55)
        self.play(LaggedStart(*[FadeIn(k, shift=DOWN * 0.25) for k in self.kacheln], lag_ratio=0.06), run_time=1.2)

        code = (
            "for i in range(len(text) - 1):\n"
            "    aktuell = text[i]\n"
            "    naechstes = text[i + 1]\n"
            "    if aktuell not in zaehler:\n"
            "        zaehler[aktuell] = {}\n"
            "    if naechstes not in zaehler[aktuell]:\n"
            "        zaehler[aktuell][naechstes] = 0\n"
            "    zaehler[aktuell][naechstes] += 1"
        )
        self.code = Code(
            code_string=code, language="python", formatter_style="friendly", add_line_numbers=False,
            background="rectangle",
            background_config={"fill_color": FLAECHE, "stroke_color": LINIE, "stroke_width": 2, "corner_radius": 0.15},
            paragraph_config={"font": MONO, "font_size": 20, "line_spacing": 0.9},
        )
        self.code.scale_to_fit_width(6.3).to_corner(DL, buff=0.6)
        self.markierung = RoundedRectangle(width=6.0, height=0.36, corner_radius=0.06, stroke_width=0,
                                           fill_color=BLAU, fill_opacity=0.0)
        self.markierung.move_to(self.code.code_lines[0])
        self.markierung.set_x(self.code.get_x())

        ueberschrift = Text("zaehler", font=MONO, font_size=24, color=LEISE)
        ueberschrift.move_to(RIGHT * 1.0 + DOWN * 0.15, aligned_edge=LEFT)
        self.zaehler_titel = ueberschrift
        self.zeilen = {}  # aktuelles Zeichen -> (Schlüssel-Kachel, [Folge, ...])

        # Die Markierung liegt zwischen Hintergrund und Text des Codes
        self.code.background.set_z_index(0)
        self.markierung.set_z_index(1)
        self.code.code_lines.set_z_index(2)
        self.add(self.markierung)
        self.play(FadeIn(self.code, shift=UP * 0.2), FadeIn(ueberschrift), run_time=0.8)

    def markiere(self, zeilen, dauer=0.25):
        """Schiebt die blaue Markierung im Code auf eine oder mehrere Zeilen."""
        erste, letzte = self.code.code_lines[zeilen[0]], self.code.code_lines[zeilen[-1]]
        hoehe = erste.get_top()[1] - letzte.get_bottom()[1] + 0.12
        ziel = RoundedRectangle(width=6.0, height=hoehe, corner_radius=0.06, stroke_width=0,
                                fill_color=BLAU, fill_opacity=0.14)
        ziel.move_to([self.code.get_x(), (erste.get_top()[1] + letzte.get_bottom()[1]) / 2, 0])
        return Transform(self.markierung, ziel, run_time=dauer)

    def zeilen_position(self, nummer):
        return self.zaehler_titel.get_left() + DOWN * (0.58 * (nummer + 1)) + RIGHT * 0.25

    # ---------------------------------------------------------
    def zaehlen(self):
        fenster = RoundedRectangle(width=1.42, height=0.82, corner_radius=0.14, stroke_color=ORANGE, stroke_width=4)
        leuchten = fenster.copy().set_stroke(ORANGE, width=12, opacity=0.15)
        rahmen = VGroup(leuchten, fenster)
        rahmen.move_to(VGroup(self.kacheln[0], self.kacheln[1]))
        self.play(Create(fenster), FadeIn(leuchten), self.markiere([0]), run_time=0.7)

        paare = len(self.TEXT) - 1
        for i in range(paare):
            aktuell, naechstes = self.TEXT[i], self.TEXT[i + 1]
            # Die ersten Paare langsam, dann immer schneller
            tempo = 1.0 if i < 3 else (0.55 if i < 6 else 0.3)
            ausfuehrlich = i < 3

            if i > 0:
                self.play(rahmen.animate.move_to(VGroup(self.kacheln[i], self.kacheln[i + 1])),
                          self.markiere([0], 0.3 * tempo), run_time=0.45 * tempo)
            if ausfuehrlich:
                self.play(self.markiere([1, 2]), run_time=0.5)

            # Das Paar fliegt nach unten in den Zähler
            kopie_a = self.kacheln[i].copy()
            kopie_b = self.kacheln[i + 1].copy()

            if aktuell not in self.zeilen:
                nummer = len(self.zeilen)
                schluessel = kachel(aktuell, groesse=0.5, schrift=24, rahmen=BLAU, fuellung=FLAECHE_HELL)
                schluessel.move_to(self.zeilen_position(nummer))
                self.zeilen[aktuell] = (schluessel, [])
                schritte = [self.markiere([3, 4], 0.3 * tempo), ReplacementTransform(kopie_a, schluessel)]
                self.play(*schritte, run_time=0.7 * tempo)
            else:
                schluessel = self.zeilen[aktuell][0]
                self.play(kopie_a.animate.move_to(schluessel).set_opacity(0), self.markiere([3], 0.25 * tempo),
                          run_time=0.5 * tempo)
                self.remove(kopie_a)

            folgen = self.zeilen[aktuell][1]
            folge = next((f for f in folgen if f.zeichen == naechstes), None)
            if folge is None:
                folge = Folge(naechstes, 0)
                vorne = folgen[-1].get_right() if folgen else schluessel.get_right() + RIGHT * 0.05
                folge.move_to(vorne + RIGHT * (0.2 + folge.width / 2))
                folge.set_y(schluessel.get_y())
                folgen.append(folge)
                self.play(self.markiere([5, 6], 0.3 * tempo), ReplacementTransform(kopie_b, folge),
                          run_time=0.7 * tempo)
            else:
                self.play(kopie_b.animate.move_to(folge).set_opacity(0), self.markiere([5], 0.25 * tempo),
                          run_time=0.5 * tempo)
                self.remove(kopie_b)

            # += 1
            folge.anzahl += 1
            neu = folge.zahl_text(folge.anzahl).move_to(folge.zahl)
            self.play(
                self.markiere([7], 0.25 * tempo),
                Transform(folge.zahl, neu),
                Indicate(folge.kasten, color=ORANGE, scale_factor=1.15),
                run_time=0.6 * tempo,
            )

        self.play(FadeOut(rahmen), self.markierung.animate.set_fill(opacity=0), run_time=0.5)
        self.wait(0.6)

    # ---------------------------------------------------------
    def wahrscheinlichkeit(self):
        schluessel, folgen = self.zeilen["n"]
        andere = [m for z, (k, f) in self.zeilen.items() if z != "n" for m in [k, *f]]
        self.play(*[m.animate.set_opacity(0.25) for m in andere], self.code.animate.set_opacity(0.35), run_time=0.8)

        gesamt = sum(f.anzahl for f in folgen)
        umwandlungen = []
        for folge in folgen:
            anteil = round(100 * folge.anzahl / gesamt)
            breiter = RoundedRectangle(width=1.45, height=0.5, corner_radius=0.12, stroke_color=ORANGE, stroke_width=2,
                                       fill_color=FLAECHE_HELL, fill_opacity=1)
            umwandlungen.append((folge, anteil, breiter))

        # Platz schaffen: die Kästchen werden breiter
        links = schluessel.get_right()[0] + 0.25
        animationen = []
        for nummer, (folge, anteil, breiter) in enumerate(umwandlungen):
            breiter.move_to([links + breiter.width / 2 + nummer * (breiter.width + 0.15), schluessel.get_y(), 0])
            prozent = Text(f"{anteil} %", font=MONO, font_size=22, color=ORANGE, weight="BOLD")
            animationen.append(AnimationGroup(
                Transform(folge.kasten, breiter),
                folge.buchstabe.animate.move_to(breiter).shift(LEFT * 0.45),
                Transform(folge.zahl, prozent.move_to(breiter).shift(RIGHT * 0.2)),
            ))
        self.play(LaggedStart(*animationen, lag_ratio=0.25), run_time=1.6)

        satz = Text("Aus Zählen wird Wahrscheinlichkeit: Nach „n“ folgt in 40 % der Fälle ein „a“.",
                    font=SANS, font_size=26, color=TEXT, t2c={"40 %": ORANGE, "Wahrscheinlichkeit": BLAU})
        satz.move_to(UP * 0.62)
        self.play(FadeIn(satz, shift=UP * 0.2), run_time=0.8)
        self.wait(2.5)


class Vokabular(Scene):
    """Text wird zu Zahlen: Zeichen ohne Doppelte, sortieren, durchnummerieren, übersetzen."""

    TEXT = "hallo welt"
    WORT = "hallo"

    def construct(self):
        with register_font(str(SCHRIFTEN / "Inter.ttf")), register_font(str(SCHRIFTEN / "JetBrainsMono.ttf")):
            kicker = Text("SCHRITT 1: TEXT WIRD ZU ZAHLEN", font=MONO, font_size=20, color=ORANGE).to_corner(UL, buff=0.6)
            titel = Text("Computer rechnen nur mit Zahlen", font=SANS, font_size=44, weight="BOLD", color=TEXT)
            titel.next_to(kicker, DOWN, aligned_edge=LEFT, buff=0.2)
            self.play(FadeIn(kicker, shift=RIGHT * 0.3), FadeIn(titel, shift=RIGHT * 0.3), run_time=0.8)

            text = VGroup(*[kachel(z, groesse=0.75, schrift=36) for z in self.TEXT]).arrange(RIGHT, buff=0.12)
            text.move_to(UP * 1.35)
            beschriftung_text = Text("Text", font=MONO, font_size=20, color=LEISE).next_to(text, LEFT, buff=0.4)
            self.play(LaggedStart(*[FadeIn(k, shift=DOWN * 0.25) for k in text], lag_ratio=0.08), FadeIn(beschriftung_text),
                      run_time=1.2)
            self.wait(0.6)

            # 1. Jedes Zeichen nur einmal
            schritt = self.schritt("1. Jedes Zeichen nur einmal")
            einzigartig = []
            for z in self.TEXT:
                if z not in einzigartig:
                    einzigartig.append(z)
            ziele = VGroup(*[kachel(z, groesse=0.75, schrift=36, rahmen=BLAU) for z in einzigartig]).arrange(RIGHT, buff=0.22)
            ziele.move_to(DOWN * 0.75)
            bewegungen = []
            for i, z in enumerate(self.TEXT):
                kopie = text[i].copy()
                ziel = ziele[einzigartig.index(z)]
                erstes = self.TEXT.index(z) == i
                if erstes:
                    bewegungen.append(ReplacementTransform(kopie, ziel))
                else:
                    # Doppelte fliegen auf ihr Gegenstück und verschwinden dort
                    bewegungen.append(kopie.animate.move_to(ziel).set_opacity(0))
                    self.add(kopie)
            self.play(LaggedStart(*bewegungen, lag_ratio=0.18), run_time=3.2)
            hinweis = Text(f"{len(self.TEXT)} Zeichen, aber nur {len(einzigartig)} verschiedene", font=SANS, font_size=24,
                           color=LEISE).next_to(ziele, DOWN, buff=0.5)
            self.play(FadeIn(hinweis, shift=UP * 0.2))
            self.wait(1.4)

            # 2. Sortieren
            self.play(FadeOut(hinweis), self.wechsle(schritt, "2. Sortieren"))
            schritt = self.aktueller
            sortiert = sorted(einzigartig)
            ziel_x = VGroup(*[kachel(z, groesse=0.75, schrift=36) for z in sortiert]).arrange(RIGHT, buff=0.22).move_to(ziele)
            self.play(*[ziele[einzigartig.index(z)].animate.move_to(ziel_x[j]) for j, z in enumerate(sortiert)],
                      run_time=1.6, path_arc=0.6)
            ziele = VGroup(*[ziele[einzigartig.index(z)] for z in sortiert])
            leer = Text("Das Leerzeichen kommt ganz nach vorn", font=SANS, font_size=24, color=LEISE)
            leer.next_to(ziele, DOWN, buff=0.5)
            self.play(Indicate(ziele[0], color=ORANGE, scale_factor=1.25), FadeIn(leer, shift=UP * 0.2), run_time=1.0)
            self.wait(1.2)

            # 3. Durchnummerieren
            self.play(FadeOut(leer), self.wechsle(schritt, "3. Durchnummerieren"))
            schritt = self.aktueller
            nummern = VGroup(*[Text(str(i), font=MONO, font_size=30, color=ORANGE, weight="BOLD").next_to(k, DOWN, buff=0.22)
                               for i, k in enumerate(ziele)])
            self.play(LaggedStart(*[FadeIn(n, shift=UP * 0.2) for n in nummern], lag_ratio=0.15), run_time=1.6)
            name = Text("Vokabular", font=MONO, font_size=20, color=LEISE).next_to(ziele, LEFT, buff=0.4)
            self.play(FadeIn(name))
            self.wait(1.2)

            # 4. Übersetzen: aus "hallo" wird eine Liste von Zahlen
            self.play(self.wechsle(schritt, "4. Übersetzen: Text → Zahlen"))
            ergebnis_titel = Text(f'"{self.WORT}"  →', font=MONO, font_size=30, color=TEXT)
            klammer_auf = Text("[", font=MONO, font_size=36, color=TEXT)
            klammer_zu = Text("]", font=MONO, font_size=36, color=TEXT)
            zahlen = [sortiert.index(z) for z in self.WORT]
            ziffern = [Text(str(n), font=MONO, font_size=36, color=ORANGE, weight="BOLD") for n in zahlen]
            kommas = [Text(",", font=MONO, font_size=36, color=TEXT) for _ in zahlen[:-1]]
            teile = [klammer_auf]
            for i, ziffer in enumerate(ziffern):
                teile.append(ziffer)
                if i < len(kommas):
                    teile.append(kommas[i])
            teile.append(klammer_zu)
            liste = VGroup(*teile).arrange(RIGHT, buff=0.12)
            zeile = VGroup(ergebnis_titel, liste).arrange(RIGHT, buff=0.35).move_to(DOWN * 3.0)
            for komma in kommas:
                komma.align_to(klammer_auf, DOWN).shift(DOWN * 0.08)
            self.play(FadeIn(ergebnis_titel), FadeIn(klammer_auf), FadeIn(klammer_zu), run_time=0.6)

            for i, z in enumerate(self.WORT):
                quelle = text[i]
                ziel_kachel = ziele[sortiert.index(z)]
                rahmen = quelle[0].copy().set_stroke(ORANGE, width=5).set_fill(opacity=0)
                rahmen_ziel = ziel_kachel[0].copy().set_stroke(ORANGE, width=5).set_fill(opacity=0)
                tempo = 1.0 if i < 2 else 0.6
                self.play(Create(rahmen), run_time=0.3 * tempo)
                self.play(ReplacementTransform(rahmen, rahmen_ziel), run_time=0.5 * tempo)
                fliegt = nummern[sortiert.index(z)].copy()
                schritte = [ReplacementTransform(fliegt, ziffern[i]), FadeOut(rahmen_ziel)]
                if i < len(kommas):
                    schritte.append(FadeIn(kommas[i]))
                self.play(*schritte, run_time=0.6 * tempo)
            self.wait(1.0)

            code = Text(f'vocabulary.encode("{self.WORT}")', font=MONO, font_size=22, color=BLAU)
            code.next_to(zeile, UP, buff=0.3)
            self.play(FadeIn(code, shift=UP * 0.15))
            self.wait(2.5)

    def schritt(self, text):
        self.aktueller = Text(text, font=SANS, font_size=30, weight="BOLD", color=BLAU).move_to(UP * 0.32)
        self.play(FadeIn(self.aktueller, shift=LEFT * 0.3), run_time=0.6)
        return self.aktueller

    def wechsle(self, alt, text):
        neu = Text(text, font=SANS, font_size=30, weight="BOLD", color=BLAU).move_to(UP * 0.32)
        self.aktueller = neu
        return ReplacementTransform(alt, neu)
