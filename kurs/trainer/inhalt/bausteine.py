"""
Bausteine für den Notebook-Inhalt.

md(...)       Erklärtext (Markdown), in beiden Fassungen gleich
code(...)     Code-Zelle, in beiden Fassungen gleich
aufgabe(...)  Code-Zelle, die der Lehrling ausfüllt:
              Vorlage für die Teilnehmer, Lösung für den Trainer
tipps(...)    aufklappbare Tipps: Hinweis, fast die Lösung, die Lösung
"""

from textwrap import dedent


def _sauber(text):
    return dedent(text).strip("\n")


def md(text):
    return {"art": "markdown", "text": _sauber(text)}


def code(text):
    return {"art": "code", "text": _sauber(text)}


def aufgabe(vorlage, loesung):
    return {"art": "aufgabe", "vorlage": _sauber(vorlage), "loesung": _sauber(loesung)}


STUFEN = ("Hinweis", "Fast die Lösung", "Die Lösung")


def tipps(hinweis, fast, loesung):
    """Drei aufklappbare Stufen: ein Hinweis, fast die Lösung, die ganze Lösung mit Erklärung."""
    teile = []
    for nummer, (ueberschrift, text) in enumerate(zip(STUFEN, (hinweis, fast, loesung)), start=1):
        teile.append(
            f"<details>\n<summary><b>Tipp {nummer}: {ueberschrift}</b> (zum Aufklappen klicken)</summary>\n\n"
            f"{_sauber(text)}\n\n</details>"
        )
    zelle = md("\n\n".join(teile))
    zelle["loesungstipp"] = _sauber(loesung)
    return zelle
