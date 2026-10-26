"""Prüfungen für Notebook 1. Diese Datei musst du nicht verändern."""

import math
from collections import Counter

from .pruefen import aufgabe, erwarte, zeige, speichern as _speichern


def _ist_nah(a, b, toleranz=1e-6):
    return isinstance(a, (int, float)) and abs(a - b) <= toleranz


# =============================================================
# 1.1 EINZIGARTIGE ZEICHEN
# =============================================================

@aufgabe("1.1", "Einzigartige Zeichen finden")
def pruefe_aufgabe_1(einzigartige_zeichen):
    ergebnis = einzigartige_zeichen("hallo")
    erwarte(
        ergebnis is not None,
        "Deine Funktion gibt nichts zurück (None). Hast du das 'return' vergessen?",
    )
    erwarte(
        isinstance(ergebnis, list),
        f"Deine Funktion soll eine Liste zurückgeben, gibt aber {type(ergebnis).__name__} zurück.\n"
        "Tipp: sorted(...) liefert immer eine Liste.",
    )
    erwarte(
        sorted(ergebnis) == ["a", "h", "l", "o"],
        f"Für 'hallo' erwarte ich die Zeichen a, h, l, o. Du lieferst {zeige(ergebnis)}.",
    )
    erwarte(
        ergebnis == ["a", "h", "l", "o"],
        f"Die Zeichen sind richtig, aber nicht sortiert: {zeige(ergebnis)}.",
    )

    ergebnis = einzigartige_zeichen("ba ab")
    erwarte(
        ergebnis == [" ", "a", "b"],
        f"Für 'ba ab' erwarte ich [' ', 'a', 'b'] (auch das Leerzeichen ist ein Zeichen!). "
        f"Du lieferst {zeige(ergebnis)}.",
    )
    erwarte(
        einzigartige_zeichen("") == [],
        "Für einen leeren Text soll eine leere Liste herauskommen.",
    )


# =============================================================
# 1.2 VOCABULARY
# =============================================================

@aufgabe("1.2", "Die Klasse Vocabulary")
def pruefe_aufgabe_2(Vocabulary):
    v = Vocabulary("hallo welt")
    erwartete_zeichen = [" ", "a", "e", "h", "l", "o", "t", "w"]

    for attribut in ("zeichen", "zeichen_zu_id", "id_zu_zeichen"):
        erwarte(
            hasattr(v, attribut),
            f"Dein Vocabulary hat kein Attribut 'self.{attribut}'. "
            f"Lege es im Konstruktor (__init__) an.",
        )

    erwarte(
        v.zeichen == erwartete_zeichen,
        f"self.zeichen für 'hallo welt' sollte {zeige(erwartete_zeichen)} sein, "
        f"ist aber {zeige(v.zeichen)}.",
    )
    erwarte(
        isinstance(v.zeichen_zu_id, dict) and isinstance(v.id_zu_zeichen, dict),
        "zeichen_zu_id und id_zu_zeichen sollen Dictionaries sein.",
    )
    erwarte(
        v.zeichen_zu_id.get(" ") == 0 and v.zeichen_zu_id.get("w") == 7,
        f"In zeichen_zu_id soll ' ' die ID 0 und 'w' die ID 7 haben "
        f"(die Position in der sortierten Liste). Du hast: {zeige(v.zeichen_zu_id)}",
    )
    erwarte(
        v.id_zu_zeichen.get(0) == " " and v.id_zu_zeichen.get(3) == "h",
        f"In id_zu_zeichen soll 0 zu ' ' und 3 zu 'h' gehören. "
        f"Du hast: {zeige(v.id_zu_zeichen)}",
    )

    erwarte(
        len(v) == 8,
        f"len(vocabulary) soll die Anzahl der Zeichen liefern (8), liefert aber {len(v)}.",
    )

    kodiert = v.encode("hallo")
    erwarte(
        kodiert == [3, 1, 4, 4, 5],
        f"encode('hallo') sollte [3, 1, 4, 4, 5] ergeben, ergibt aber {zeige(kodiert)}.",
    )
    erwarte(
        v.encode("") == [],
        "encode('') soll eine leere Liste ergeben.",
    )

    dekodiert = v.decode([7, 2, 4, 6])
    erwarte(
        dekodiert == "welt",
        f"decode([7, 2, 4, 6]) sollte 'welt' ergeben, ergibt aber {zeige(dekodiert)}.",
    )
    erwarte(
        v.decode(v.encode("hallo welt")) == "hallo welt",
        "decode(encode(text)) soll wieder genau den ursprünglichen Text ergeben.",
    )


# =============================================================
# 1.3 BIGRAMME ZÄHLEN
# =============================================================

@aufgabe("1.3", "Bigramme zählen")
def pruefe_aufgabe_3(zaehle_bigramme):
    ergebnis = zaehle_bigramme("abab")
    erwarte(
        isinstance(ergebnis, dict),
        f"zaehle_bigramme soll ein Dictionary zurückgeben, gibt aber "
        f"{type(ergebnis).__name__} zurück.",
    )
    erwarte(
        ergebnis == {"a": {"b": 2}, "b": {"a": 1}},
        "Für 'abab' erwarte ich {'a': {'b': 2}, 'b': {'a': 1}}:\n"
        "Nach 'a' kommt zweimal 'b', nach 'b' kommt einmal 'a'.\n"
        f"Du lieferst {zeige(ergebnis)}.",
    )

    ergebnis = zaehle_bigramme("aa b")
    erwartet = {"a": {"a": 1, " ": 1}, " ": {"b": 1}}
    erwarte(
        ergebnis == erwartet,
        f"Für 'aa b' erwarte ich {zeige(erwartet)}. Du lieferst {zeige(ergebnis)}.",
    )

    erwarte(
        zaehle_bigramme("a") == {},
        "Ein Text mit nur einem Zeichen hat kein Zeichenpaar. Erwartet: {}.\n"
        "Achte darauf, wie weit deine Schleife läuft.",
    )
    erwarte(zaehle_bigramme("") == {}, "Für einen leeren Text erwarte ich {}.")


# =============================================================
# 1.4 WAHRSCHEINLICHKEITEN
# =============================================================

@aufgabe("1.4", "Häufigkeiten in Wahrscheinlichkeiten umrechnen")
def pruefe_aufgabe_4(wahrscheinlichkeiten):
    eingabe = {"a": 3, "b": 1}
    ergebnis = wahrscheinlichkeiten(eingabe)
    erwarte(
        isinstance(ergebnis, dict),
        f"Erwartet wird ein Dictionary, du gibst {type(ergebnis).__name__} zurück.",
    )
    erwarte(
        set(ergebnis) == {"a", "b"},
        f"Das Ergebnis soll dieselben Schlüssel haben wie die Eingabe. Du lieferst {zeige(ergebnis)}.",
    )
    erwarte(
        _ist_nah(ergebnis["a"], 0.75) and _ist_nah(ergebnis["b"], 0.25),
        f"Für {{'a': 3, 'b': 1}} erwarte ich {{'a': 0.75, 'b': 0.25}}. "
        f"Du lieferst {zeige(ergebnis)}.",
    )
    erwarte(
        eingabe == {"a": 3, "b": 1},
        "Deine Funktion verändert das übergebene Dictionary. Erstelle lieber ein neues.",
    )

    ergebnis = wahrscheinlichkeiten({"x": 5})
    erwarte(
        _ist_nah(ergebnis.get("x"), 1.0),
        f"Gibt es nur ein Zeichen, muss seine Wahrscheinlichkeit 1.0 sein. Du lieferst {zeige(ergebnis)}.",
    )

    ergebnis = wahrscheinlichkeiten({"a": 1, "b": 2, "c": 3, "d": 4})
    erwarte(
        _ist_nah(sum(ergebnis.values()), 1.0),
        f"Alle Wahrscheinlichkeiten zusammen müssen 1 ergeben. Bei dir: {sum(ergebnis.values())}.",
    )


# =============================================================
# 1.5 ZEICHEN ZIEHEN
# =============================================================

@aufgabe("1.5", "Ein Zeichen zufällig ziehen")
def pruefe_aufgabe_5(ziehe_zeichen):
    ergebnis = ziehe_zeichen({"x": 1.0})
    erwarte(
        ergebnis == "x",
        f"Bei {{'x': 1.0}} muss immer 'x' gezogen werden. Du lieferst {zeige(ergebnis)}.\n"
        "Achte darauf, ein einzelnes Zeichen zurückzugeben, keine Liste.",
    )

    for _ in range(200):
        erwarte(
            ziehe_zeichen({"a": 0.0, "b": 1.0}) == "b",
            "Ein Zeichen mit Wahrscheinlichkeit 0.0 darf nie gezogen werden.",
        )

    anzahl = 10_000
    zaehler = Counter(ziehe_zeichen({"a": 0.8, "b": 0.2}) for _ in range(anzahl))
    anteil_a = zaehler["a"] / anzahl
    erwarte(
        abs(anteil_a - 0.8) < 0.03,
        f"Bei {{'a': 0.8, 'b': 0.2}} sollte 'a' in etwa 80 % der Fälle kommen. "
        f"Bei 10.000 Versuchen kam es in {anteil_a:.1%} der Fälle.\n"
        "Werden die Wahrscheinlichkeiten als Gewichte übergeben?",
    )


# =============================================================
# 1.6 TEXT GENERIEREN MIT BIGRAMMEN
# =============================================================

@aufgabe("1.6", "Text generieren mit Bigrammen")
def pruefe_aufgabe_6(generiere_bigramm):
    zaehler = {"a": {"b": 1}, "b": {"c": 1}, "c": {"a": 1}}
    ergebnis = generiere_bigramm(zaehler, "a", 5)
    erwarte(
        isinstance(ergebnis, str),
        f"Erwartet wird ein Text (str), du gibst {type(ergebnis).__name__} zurück.",
    )
    erwarte(
        ergebnis == "abcabc",
        "Mit a→b, b→c, c→a, Start 'a' und 5 neuen Zeichen erwarte ich 'abcabc'.\n"
        f"Du lieferst {zeige(ergebnis)}. Denk daran: Der Starttext gehört zum Ergebnis.",
    )

    ergebnis = generiere_bigramm(zaehler, "ca", 2)
    erwarte(
        ergebnis == "cabc",
        "Bei längerem Starttext zählt nur das LETZTE Zeichen als Kontext.\n"
        f"Mit Start 'ca' und 2 neuen Zeichen erwarte ich 'cabc', du lieferst {zeige(ergebnis)}.",
    )

    ergebnis = generiere_bigramm({"a": {"b": 1}}, "a", 10)
    erwarte(
        ergebnis == "ab",
        "Nach 'b' kennt das Modell kein nächstes Zeichen. Dann soll die Generierung stoppen.\n"
        f"Erwartet 'ab', du lieferst {zeige(ergebnis)}.",
    )


# =============================================================
# 1.7 N-GRAMM-MODELL
# =============================================================

@aufgabe("1.7", "Die Klasse NGramModell")
def pruefe_aufgabe_7(NGramModell):
    modell = NGramModell("abcabd", 2)
    erwarte(
        getattr(modell, "n", None) == 2,
        "Dein Modell soll n im Attribut self.n speichern.",
    )
    erwarte(
        hasattr(modell, "zaehler"),
        "Dein Modell braucht ein Attribut self.zaehler mit den gezählten Kontexten.",
    )
    erwartet = {"ab": {"c": 1, "d": 1}, "bc": {"a": 1}, "ca": {"b": 1}}
    erwarte(
        modell.zaehler == erwartet,
        f"Für 'abcabd' mit n=2 erwarte ich als zaehler\n{zeige(erwartet)}\n"
        f"Du hast\n{zeige(modell.zaehler)}",
    )

    eins = NGramModell("abab", 1)
    erwarte(
        eins.zaehler == {"a": {"b": 2}, "b": {"a": 1}},
        "Mit n=1 soll dein Modell genau wie die Bigramm-Zählung arbeiten.\n"
        f"Für 'abab' erwarte ich {{'a': {{'b': 2}}, 'b': {{'a': 1}}}}, du hast {zeige(eins.zaehler)}.",
    )

    zyklus = NGramModell("abcabcabc", 2)
    naechstes = zyklus.naechstes_zeichen("ab")
    erwarte(
        naechstes == "c",
        f"naechstes_zeichen('ab') sollte 'c' liefern, liefert aber {zeige(naechstes)}.",
    )
    unbekannt = zyklus.naechstes_zeichen("xy")
    erwarte(
        unbekannt is None,
        f"Für einen unbekannten Kontext soll naechstes_zeichen None liefern, liefert aber {zeige(unbekannt)}.",
    )

    ergebnis = zyklus.generiere("ab", 4)
    erwarte(
        ergebnis == "abcabc",
        f"generiere('ab', 4) sollte 'abcabc' liefern, liefert aber {zeige(ergebnis)}.",
    )
    ergebnis = zyklus.generiere("xab", 1)
    erwarte(
        ergebnis == "xabc",
        "Als Kontext zählen immer nur die LETZTEN n Zeichen.\n"
        f"generiere('xab', 1) sollte 'xabc' liefern, liefert aber {zeige(ergebnis)}.",
    )
    ergebnis = NGramModell("abcabd", 2).generiere("bd", 5)
    erwarte(
        ergebnis == "bd",
        f"Nach 'bd' kennt das Modell nichts. generiere('bd', 5) sollte 'bd' liefern, "
        f"liefert aber {zeige(ergebnis)}.",
    )

    try:
        zyklus.generiere("a", 3)
    except ValueError:
        pass
    else:
        erwarte(
            False,
            "Ist der Starttext kürzer als n, soll generiere einen ValueError auslösen:\n"
            "raise ValueError('...')",
        )


# =============================================================
# 1.8 VERLUST EINER VORHERSAGE
# =============================================================

@aufgabe("1.8", "Der Verlust einer Vorhersage")
def pruefe_aufgabe_8(verlust):
    erwarte(
        _ist_nah(verlust(1.0), 0.0),
        f"verlust(1.0) soll 0 sein: Das Modell war sich sicher und hatte recht. Du lieferst {zeige(verlust(1.0))}.",
    )
    erwarte(
        _ist_nah(verlust(0.5), math.log(2)),
        f"verlust(0.5) soll etwa 0.6931 sein. Du lieferst {zeige(verlust(0.5))}.\n"
        "Verwendest du den natürlichen Logarithmus math.log mit Minus davor?",
    )
    erwarte(
        _ist_nah(verlust(0.01), -math.log(0.01)),
        f"verlust(0.01) soll etwa 4.6052 sein. Du lieferst {zeige(verlust(0.01))}.",
    )
    try:
        ergebnis = verlust(0.0)
    except ValueError:
        erwarte(
            False,
            "verlust(0.0) löst einen Fehler aus, weil math.log(0) nicht berechnet werden kann.\n"
            "Prüfe vorher mit 'if p == 0:' und gib in diesem Fall float('inf') zurück.",
        )
    erwarte(
        ergebnis == float("inf"),
        f"verlust(0.0) soll unendlich sein: float('inf'). Du lieferst {zeige(ergebnis)}.",
    )


# =============================================================
# 1.9 DURCHSCHNITTLICHER VERLUST
# =============================================================

@aufgabe("1.9", "Den durchschnittlichen Verlust berechnen")
def pruefe_aufgabe_9(durchschnittlicher_verlust, NGramModell):
    sicher = NGramModell("abab", 1)
    ergebnis = durchschnittlicher_verlust(sicher, "abab")
    erwarte(
        _ist_nah(ergebnis, 0.0),
        "Ein Modell, das auf 'abab' trainiert wurde, sagt in 'abab' jedes Zeichen "
        f"mit Wahrscheinlichkeit 1 voraus. Erwartet 0.0, du lieferst {zeige(ergebnis)}.",
    )

    halb = NGramModell("aab", 1)
    ergebnis = durchschnittlicher_verlust(halb, "aab")
    erwarte(
        _ist_nah(ergebnis, math.log(2)),
        "Training auf 'aab': nach 'a' kommt je zur Hälfte 'a' oder 'b'.\n"
        "Beide Vorhersagen im Text 'aab' haben Wahrscheinlichkeit 0.5.\n"
        f"Erwartet etwa 0.6931, du lieferst {zeige(ergebnis)}.",
    )

    ergebnis = durchschnittlicher_verlust(halb, "ac")
    erwarte(
        ergebnis == float("inf"),
        "Im Text 'ac' folgt auf 'a' ein 'c', das das Modell nie gesehen hat.\n"
        f"Der Verlust muss unendlich sein. Du lieferst {zeige(ergebnis)}.",
    )
    ergebnis = durchschnittlicher_verlust(halb, "ca")
    erwarte(
        ergebnis == float("inf"),
        "Im Text 'ca' kommt der Kontext 'c' vor, den das Modell gar nicht kennt.\n"
        f"Auch dann muss der Verlust unendlich sein. Du lieferst {zeige(ergebnis)}.",
    )


# =============================================================
# ABSCHLUSS
# =============================================================

def speichern(*objekte):
    _speichern(
        notebook=1,
        objekte=objekte,
        dateiname="notebook1",
        importe=["import math", "import random"],
    )
