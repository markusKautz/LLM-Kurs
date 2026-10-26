"""
Zählt die Modelle und Kennzahlen, die in den Folien live verwendet werden.

    python daten/erzeuge_modelle.py

Alles kommt aus dem Märchentext der Teilnehmer (notebooks/daten/maerchen.txt).

public/modelle/maerchen{n}.json   {kontext: {zeichen: anzahl}} für n = 0 bis 5
public/modelle/kennzahlen.json    Vokabular, Bigramm-Matrix, Markow-Zählung, Kontext-Explosion, Verluste,
                                  Auszug aus dem Text, Datenhunger
"""

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

HIER = Path(__file__).resolve().parent
TEXTE = HIER.parents[2] / "teilnehmer" / "notebooks" / "daten"
ZIEL = HIER.parent / "public" / "modelle"
GROESSTES_N = 5


def zaehle(text, n):
    zaehler = defaultdict(Counter)
    for i in range(len(text) - n):
        zaehler[text[i:i + n]][text[i + n]] += 1
    return zaehler


def verlust(zaehler, text, n):
    """Durchschnittlicher Verlust und Anteil der Stellen, an denen das Modell p = 0 gibt."""
    summe, nullen, anzahl = 0.0, 0, len(text) - n
    for i in range(anzahl):
        folge = zaehler.get(text[i:i + n])
        p = folge[text[i + n]] / sum(folge.values()) if folge else 0.0
        if p == 0:
            nullen += 1
        else:
            summe += -math.log(p)
    durchschnitt = None if nullen else summe / anzahl
    return durchschnitt, nullen / anzahl


def schreibe(name, daten):
    datei = ZIEL / name
    datei.write_text(json.dumps(daten, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{datei.name}: {datei.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    ZIEL.mkdir(parents=True, exist_ok=True)
    text = (TEXTE / "maerchen.txt").read_text(encoding="utf-8")
    zeichen = sorted(set(text))
    V = len(zeichen)

    for n in range(GROESSTES_N + 1):
        schreibe(f"maerchen{n}.json", zaehle(text, n))

    # Bigramm-Matrix: Zeile = aktuelles Zeichen, Spalte = nächstes Zeichen
    paare = zaehle(text, 1)
    matrix = [[paare[a][b] for b in zeichen] for a in zeichen]

    # Training und Test wie in Notebook 1: 90 % und 10 %
    grenze = int(len(text) * 0.9)
    training, test = text[:grenze], text[grenze:]
    explosion, verluste = [], []
    for n in range(0, 7):
        modell = zaehle(training, n)
        test_kontexte = [test[i:i + n] for i in range(len(test) - n)]
        unbekannt = sum(k not in modell for k in test_kontexte) / len(test_kontexte)
        explosion.append({"n": n, "moeglich": V ** n, "gesehen": len(modell), "unbekannt": unbekannt})
        v_train, _ = verlust(modell, training, n)
        v_test, nullen = verlust(modell, test, n)
        verluste.append({"n": n, "training": v_train, "test": v_test, "nullen": nullen})

    # Wie Markow 1913: nur Buchstaben, ohne Leerzeichen und Satzzeichen.
    # Zählt, wie oft Vokal (V) und Konsonant (K) aufeinander folgen.
    vokale = set("aeiouäöü")
    buchstaben = [z for z in text if z.isalpha()]
    art = ["V" if z in vokale else "K" for z in buchstaben]
    markow = Counter(a + b for a, b in zip(art, art[1:]))

    # Datenhunger: Wie viele Kontexte im Test sind unbekannt, wenn das Training kleiner ist?
    stufen = []
    for anteil in (0.1, 0.25, 0.5, 1.0):
        teil = training[:int(len(training) * anteil)]
        unbekannt = {}
        for n in range(3, 7):
            gesehen = {teil[i:i + n] for i in range(len(teil) - n)}
            test_kontexte = [test[i:i + n] for i in range(len(test) - n)]
            unbekannt[n] = sum(k not in gesehen for k in test_kontexte) / len(test_kontexte)
        stufen.append({"zeichen": len(teil), "unbekannt": unbekannt})
    sechser = Counter(training[i:i + 6] for i in range(len(training) - 6))
    datenhunger = {
        "stufen": stufen,
        "kontexte": len(sechser),
        "einmal": sum(anzahl == 1 for anzahl in sechser.values()),
    }

    # Ein Stück vom Anfang von "Hänsel und Gretel", so wie das Modell den Text liest
    anfang = text.index("vor einem großen walde wohnte ein armer holzhacker")

    schreibe("kennzahlen.json", {
        "markow": {"buchstaben": len(buchstaben), **markow},
        "zeichen": zeichen,
        "laenge": len(text),
        "haeufigkeit": [text.count(z) for z in zeichen],
        "bigramme": matrix,
        "explosion": explosion,
        "verluste": verluste,
        "woerter": len(text.split()),
        "auszug": text[anfang:anfang + 3000],
        "datenhunger": datenhunger,
    })
    for zeile in explosion:
        print(zeile)
    for zeile in verluste:
        print(zeile)
    for zeile in stufen:
        print(zeile)
    print(f"6er-Kontexte: {datenhunger['kontexte']}, davon nur einmal gesehen: {datenhunger['einmal']}")
