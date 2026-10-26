"""
Animationen für Vortrag 2: Neuronale Netze.

Rendern mit ./rendern.sh vortrag2.py <Szene>, Szenen: Bergab, MatrixMal
"""

from manim import (
    DOWN, LEFT, RIGHT, UP, UL,
    Create, FadeIn, FadeOut, Indicate, LaggedStart, ReplacementTransform, Transform,
    Arrow, Dot, Line, RoundedRectangle, Text, VGroup, Axes,
    Scene, ValueTracker, always_redraw, register_font,
)

from vortrag1 import BLAU, FLAECHE, FLAECHE_HELL, LEISE, LINIE, MONO, ORANGE, SANS, SCHRIFTEN, SEHR_LEISE, TEXT


def kopf(scene, kicker, titel):
    k = Text(kicker, font=MONO, font_size=20, color=ORANGE).to_corner(UL, buff=0.6)
    t = Text(titel, font=SANS, font_size=44, weight="BOLD", color=TEXT).next_to(k, DOWN, aligned_edge=LEFT, buff=0.2)
    scene.play(FadeIn(k, shift=RIGHT * 0.3), FadeIn(t, shift=RIGHT * 0.3), run_time=0.8)
    return VGroup(k, t)


def zahl(wert, stellen=1):
    if abs(wert) < 0.5 * 10 ** -stellen:
        wert = 0.0
    return f"{wert:.{stellen}f}".replace(".", ",").replace("-", "−")


class Bergab(Scene):
    """Gradientenabstieg mit einem Gewicht: Verlust = (w − 3)² + 1, Start bei w = 0,5."""

    LERNRATE = 0.3

    def construct(self):
        with register_font(str(SCHRIFTEN / "Inter.ttf")), register_font(str(SCHRIFTEN / "JetBrainsMono.ttf")):
            kopf(self, "SCHRITT 2: BERGAB GEHEN", "Lernen heißt bergab gehen")

            achsen = Axes(
                x_range=[0, 6, 1], y_range=[0, 10, 2], x_length=7.2, y_length=4.6,
                axis_config={"color": LEISE, "stroke_width": 2, "include_tip": False},
            ).to_edge(DOWN, buff=0.75).to_edge(LEFT, buff=1.0)
            zahlen = VGroup(*[
                Text(str(i), font=MONO, font_size=20, color=LEISE).next_to(achsen.c2p(i, 0), DOWN, buff=0.15) for i in range(7)
            ])
            w_titel = Text("Gewicht w", font=SANS, font_size=22, color=LEISE).next_to(achsen.x_axis, DOWN, buff=0.5)
            v_titel = Text("Verlust", font=SANS, font_size=22, color=LEISE).rotate(1.5708).next_to(achsen.y_axis, LEFT, buff=0.3)

            f = lambda w: (w - 3) ** 2 + 1
            kurve = achsen.plot(f, x_range=[0, 6], color=TEXT, stroke_width=5)
            self.play(Create(achsen), FadeIn(zahlen), FadeIn(w_titel), FadeIn(v_titel), run_time=1.0)
            self.play(Create(kurve), run_time=1.4)

            tal = Text("das Tal", font=SANS, font_size=24, weight="BOLD", color=BLAU).next_to(achsen.c2p(3, 1), UP, buff=0.5)
            self.play(FadeIn(tal, shift=UP * 0.2))

            w = ValueTracker(0.5)
            kugel = always_redraw(lambda: Dot(achsen.c2p(w.get_value(), f(w.get_value())), radius=0.14, color=ORANGE))

            def tangente():
                # Immer gleich lang auf dem Bildschirm, egal wie steil
                x = w.get_value()
                s = 2 * (x - 3)
                punkt = achsen.c2p(x, f(x))
                richtung = achsen.c2p(x + 1, f(x) + s) - punkt
                richtung = richtung / (richtung ** 2).sum() ** 0.5
                return Line(punkt - 1.1 * richtung, punkt + 1.1 * richtung, color=ORANGE, stroke_width=4)

            tang = always_redraw(tangente)
            self.play(FadeIn(kugel, scale=0.5), run_time=0.6)
            self.wait(0.4)

            # Rechte Seite: Erklärung
            rechts_x = 3.9
            zeile1 = Text("Steigung an der Kugel", font=SANS, font_size=24, color=LEISE).move_to([rechts_x, 1.5, 0])
            steigung = always_redraw(lambda: Text(zahl(2 * (w.get_value() - 3)), font=MONO, font_size=48, weight="BOLD",
                                                  color=ORANGE).move_to([rechts_x, 0.85, 0]))
            self.play(Create(tang), FadeIn(zeile1), FadeIn(steigung), run_time=1.0)

            richtung = Text("negativ: nach rechts geht es bergab", font=SANS, font_size=20, color=TEXT).move_to([rechts_x, 0.1, 0])
            self.play(FadeIn(richtung, shift=UP * 0.15))
            self.wait(1.2)

            regel = Text("neues w = w − Lernrate × Steigung", font=MONO, font_size=19, color=BLAU).move_to([rechts_x, -0.75, 0])
            self.play(FadeIn(regel, shift=UP * 0.15))
            self.wait(1.0)

            rechnung = None
            for schritt in range(7):
                alt = w.get_value()
                s = 2 * (alt - 3)
                neu = alt - self.LERNRATE * s
                text = f"{zahl(alt, 2)} − 0,3 × ({zahl(s, 2)}) = {zahl(neu, 2)}"
                neue_rechnung = Text(text, font=MONO, font_size=20, color=TEXT).move_to([rechts_x, -1.4, 0])
                spur = Dot(achsen.c2p(alt, f(alt)), radius=0.06, color=ORANGE).set_opacity(0.45)
                self.add(spur)
                tempo = 1.0 if schritt < 3 else 0.5
                animationen = [w.animate.set_value(neu)]
                animationen.append(FadeIn(neue_rechnung) if rechnung is None else ReplacementTransform(rechnung, neue_rechnung))
                self.play(*animationen, run_time=1.2 * tempo)
                rechnung = neue_rechnung
                self.wait(0.5 * tempo)

            ziel = Text("Steigung fast 0: Wir sind im Tal.", font=SANS, font_size=22, weight="BOLD", color=BLAU)
            ziel.move_to([rechts_x, -2.3, 0])
            self.play(FadeIn(ziel, shift=UP * 0.2), Indicate(kugel, color=BLAU, scale_factor=1.6))
            self.wait(2.5)


class MatrixMal(Scene):
    """x @ W mit dem Beispiel aus Notebook 2: [1, 2] @ [[10, 20, 30], [1, 2, 3]] = [12, 24, 36]."""

    X = [1, 2]
    W = [[10, 20, 30], [1, 2, 3]]

    def zelle(self, wert, farbe=TEXT, rahmen=LINIE, fuellung=FLAECHE, groesse=0.9):
        kasten = RoundedRectangle(width=groesse, height=groesse, corner_radius=0.08, stroke_color=rahmen, stroke_width=2.5,
                                  fill_color=fuellung, fill_opacity=1)
        text = Text(str(wert), font=MONO, font_size=32, color=farbe).move_to(kasten)
        return VGroup(kasten, text)

    def construct(self):
        with register_font(str(SCHRIFTEN / "Inter.ttf")), register_font(str(SCHRIFTEN / "JetBrainsMono.ttf")):
            kopf(self, "SCHRITT 3: RECHNEN MIT TABELLEN", "Die Matrixmultiplikation")

            x = VGroup(*[self.zelle(v) for v in self.X]).arrange(RIGHT, buff=0.08)
            W = VGroup(*[VGroup(*[self.zelle(v) for v in zeile]).arrange(RIGHT, buff=0.08) for zeile in self.W]).arrange(DOWN, buff=0.08)
            ergebnis = VGroup(*[self.zelle("", fuellung=FLAECHE_HELL) for _ in self.W[0]]).arrange(RIGHT, buff=0.08)
            mal = Text("@", font=MONO, font_size=44, color=SEHR_LEISE)
            gleich = Text("=", font=MONO, font_size=44, color=SEHR_LEISE)
            gruppe = VGroup(x, mal, W, gleich, ergebnis).arrange(RIGHT, buff=0.45).move_to(UP * 0.35)
            x.align_to(W[0], UP)
            ergebnis.align_to(W[0], UP)
            mal.match_y(x)
            gleich.match_y(x)

            namen = VGroup(
                Text("x", font=MONO, font_size=26, color=LEISE).next_to(x, UP, buff=0.3),
                Text("W", font=MONO, font_size=26, color=LEISE).next_to(W, UP, buff=0.3),
                Text("Ergebnis", font=MONO, font_size=26, color=LEISE).next_to(ergebnis, UP, buff=0.3),
            )
            formen = VGroup(
                Text("(1, 2)", font=MONO, font_size=20, color=SEHR_LEISE).next_to(x, DOWN, buff=0.3),
                Text("(2, 3)", font=MONO, font_size=20, color=SEHR_LEISE).next_to(W, DOWN, buff=0.3),
                Text("(1, 3)", font=MONO, font_size=20, color=SEHR_LEISE).next_to(ergebnis, DOWN, buff=0.3),
            )
            formen[0].match_y(formen[1])
            formen[2].match_y(formen[1])
            self.play(LaggedStart(FadeIn(x), FadeIn(mal), FadeIn(W), FadeIn(gleich), FadeIn(ergebnis), lag_ratio=0.2),
                      FadeIn(namen), run_time=1.5)
            self.wait(0.6)

            erklaerung = Text("Für jede Spalte von W: Zeile mal Spalte, dann zusammenzählen",
                              font=SANS, font_size=26, color=TEXT).move_to(DOWN * 1.9)
            self.play(FadeIn(erklaerung, shift=UP * 0.2))

            for j in range(3):
                tempo = 1.0 if j == 0 else 0.55
                rahmen_x = RoundedRectangle(width=x.width + 0.2, height=x.height + 0.2, corner_radius=0.12,
                                            stroke_color=ORANGE, stroke_width=5).move_to(x)
                spalte = VGroup(W[0][j], W[1][j])
                rahmen_w = RoundedRectangle(width=spalte.width + 0.2, height=spalte.height + 0.2, corner_radius=0.12,
                                            stroke_color=BLAU, stroke_width=5).move_to(spalte)
                self.play(Create(rahmen_x), Create(rahmen_w), run_time=0.6 * tempo)

                produkte = [self.X[i] * self.W[i][j] for i in range(2)]
                summe = sum(produkte)
                rechnung = Text(
                    f"{self.X[0]}·{self.W[0][j]} + {self.X[1]}·{self.W[1][j]} = {produkte[0]} + {produkte[1]} = {summe}",
                    font=MONO, font_size=30, color=TEXT,
                ).move_to(DOWN * 2.85)
                self.play(FadeIn(rechnung, shift=UP * 0.15), run_time=0.7 * tempo)
                self.wait(0.9 * tempo)

                ziel = self.zelle(summe, farbe=ORANGE, rahmen=ORANGE).move_to(ergebnis[j])
                kopie = rechnung[-len(str(summe)):].copy()
                self.play(ReplacementTransform(kopie, ziel), FadeOut(ergebnis[j]), run_time=0.8 * tempo)
                ergebnis[j] = ziel
                self.play(FadeOut(rahmen_x), FadeOut(rahmen_w), FadeOut(rechnung), run_time=0.4 * tempo)

            self.play(FadeIn(formen), run_time=0.8)
            regel = Text("Die inneren Zahlen müssen gleich sein: (1, 2) @ (2, 3) = (1, 3)", font=SANS, font_size=24, color=BLAU)
            regel.move_to(DOWN * 2.85)
            self.play(FadeIn(regel, shift=UP * 0.15))
            self.wait(1.5)

            satz = Text("x bestimmt, wie stark jede Zeile von W zählt: eine gewichtete Summe.",
                        font=SANS, font_size=26, weight="BOLD", color=TEXT).move_to(DOWN * 1.9)
            self.play(ReplacementTransform(erklaerung, satz))
            self.play(Indicate(x, color=ORANGE, scale_factor=1.1), run_time=1.0)
            self.wait(2.5)
