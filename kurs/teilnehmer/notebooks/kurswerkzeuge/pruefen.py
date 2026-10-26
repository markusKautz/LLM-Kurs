"""
Grundlagen für die Prüfzellen in allen Notebooks.

Diese Datei musst du nicht lesen oder verändern. Sie sorgt dafür, dass
- jede Prüfzelle eine verständliche Rückmeldung anzeigt,
- dein Fortschritt gespeichert wird,
- dein Code am Ende eines Notebooks in eine .py-Datei geschrieben wird,
  damit du ihn im nächsten Notebook weiterverwenden kannst.
"""

import ast
import html
import inspect
import json
import linecache
import sys
import traceback
from pathlib import Path

from IPython.display import HTML, display

MEINCODE = Path(__file__).resolve().parent.parent / "meincode"
FORTSCHRITT = MEINCODE / "fortschritt.json"

# Alle Prüfungen, sortiert nach Notebook:
# { 1: { "1.1": prueffunktion, ... }, 2: {...} }
_PRUEFUNGEN = {}


class NichtBestanden(Exception):
    """Wird ausgelöst, wenn ein Test fehlschlägt. Die Nachricht sieht der Lehrling."""


def erwarte(bedingung, nachricht):
    """Löst NichtBestanden aus, wenn die Bedingung nicht erfüllt ist."""
    if not bedingung:
        raise NichtBestanden(nachricht)


def zeige(wert):
    """Zeigt einen Wert so an, wie man ihn in Python schreiben würde."""
    text = repr(wert)
    if len(text) > 200:
        text = text[:200] + " ..."
    return text


# =============================================================
# ANZEIGE
# =============================================================

_FARBEN = {
    "ok": ("#e6f4ea", "#1e7b34", "Bestanden"),
    "fehler": ("#fdecea", "#b3261e", "Noch nicht bestanden"),
    "offen": ("#fff4e0", "#8a5300", "Noch nicht bearbeitet"),
}


def _kasten(art, titel, text_html):
    hintergrund, rahmen, status = _FARBEN[art]
    display(HTML(
        f'<div class="kurs-pruefung kurs-{art}" style="background:{hintergrund};'
        f'border-left:6px solid {rahmen};padding:10px 14px;margin:6px 0;'
        f'color:#1a1a1a;font-family:sans-serif;line-height:1.5">'
        f'<b style="color:{rahmen}">{status}:</b> <b>{html.escape(titel)}</b>'
        f'<div style="margin-top:4px">{text_html}</div></div>'
    ))


def _fehlerstelle(fehler):
    """Sucht die letzte Zeile im Traceback, die aus dem Notebook stammt."""
    stelle = None
    for rahmen in traceback.extract_tb(fehler.__traceback__):
        if "ipykernel" in rahmen.filename or rahmen.filename.startswith("<"):
            stelle = rahmen
    if stelle is None:
        return ""
    return (
        f"<br>Die Stelle in deinem Code: "
        f"<code>{html.escape(stelle.line or '')}</code> "
        f"(in <code>{html.escape(stelle.name)}</code>)"
    )


# =============================================================
# FORTSCHRITT
# =============================================================

def _lade_fortschritt():
    try:
        return json.loads(FORTSCHRITT.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _setze_fortschritt(nummer, bestanden):
    fortschritt = _lade_fortschritt()
    fortschritt[nummer] = bestanden
    MEINCODE.mkdir(exist_ok=True)
    FORTSCHRITT.write_text(
        json.dumps(fortschritt, indent=2, sort_keys=True),
        encoding="utf-8",
    )


# =============================================================
# AUFGABEN REGISTRIEREN UND AUSFÜHREN
# =============================================================

def aufgabe(nummer, titel):
    """
    Macht aus einer Testfunktion eine Prüfzelle.

    Die Testfunktion bekommt den Code des Lehrlings übergeben und löst
    NichtBestanden aus, wenn etwas nicht stimmt.
    """
    notebook = int(nummer.split(".")[0])

    def dekorator(test):
        def pruefe(*objekte, still=False):
            ergebnis = _fuehre_aus(test, objekte)
            _setze_fortschritt(nummer, ergebnis is None)
            if not still:
                _melde(nummer, titel, ergebnis)
            return ergebnis is None

        pruefe.nummer = nummer
        pruefe.titel = titel
        pruefe.parameter = list(inspect.signature(test).parameters)
        _PRUEFUNGEN.setdefault(notebook, {})[nummer] = pruefe
        return pruefe

    return dekorator


def _fuehre_aus(test, objekte):
    """Gibt None zurück, wenn alles stimmt, sonst (art, text_html)."""
    try:
        test(*objekte)
    except NichtBestanden as fehler:
        return ("fehler", html.escape(str(fehler)).replace("\n", "<br>"))
    except NotImplementedError:
        return (
            "offen",
            "Hier steht noch <code>raise NotImplementedError(...)</code>. "
            "Ersetze diese Zeile durch deinen eigenen Code und führe die "
            "Zelle mit deinem Code noch einmal aus, bevor du prüfst.",
        )
    except RecursionError:
        return (
            "fehler",
            "Deine Funktion ruft sich endlos selbst auf (RecursionError).",
        )
    except Exception as fehler:
        return (
            "fehler",
            f"Dein Code hat einen Fehler ausgelöst: "
            f"<code>{type(fehler).__name__}: {html.escape(str(fehler))}</code>"
            f"{_fehlerstelle(fehler)}",
        )
    return None


def _melde(nummer, titel, ergebnis):
    if ergebnis is None:
        _kasten("ok", f"Aufgabe {nummer}: {titel}", "Alle Tests sind erfolgreich. Weiter so!")
    else:
        art, text = ergebnis
        _kasten(art, f"Aufgabe {nummer}: {titel}", text)


# =============================================================
# CODE SPEICHERN
# =============================================================

def _quelltext(objekt):
    """Holt den Quelltext einer Funktion oder Klasse aus dem Notebook."""
    try:
        return inspect.getsource(objekt)
    except (OSError, TypeError):
        pass

    # Klassen aus Notebook-Zellen findet inspect nicht. Ihre Methoden
    # wissen aber, in welcher Zelle sie stehen. Aus dieser Zelle
    # schneiden wir die Klasse heraus.
    for wert in vars(objekt).values():
        code = getattr(wert, "__code__", None)
        if code is None:
            continue
        zelle = "".join(linecache.getlines(code.co_filename))
        for knoten in ast.walk(ast.parse(zelle)):
            if isinstance(knoten, ast.ClassDef) and knoten.name == objekt.__name__:
                return ast.get_source_segment(zelle, knoten) + "\n"

    raise OSError(f"Quelltext von {objekt.__name__} nicht gefunden.")


def speichern(notebook, objekte, dateiname, importe=()):
    """
    Prüft alle Aufgaben des Notebooks noch einmal und schreibt dann
    die Funktionen und Klassen in meincode/<dateiname>.py.
    """
    nach_name = {objekt.__name__: objekt for objekt in objekte}
    offen = []

    for nummer, pruefe in sorted(_PRUEFUNGEN.get(notebook, {}).items()):
        argumente = [nach_name.get(name) for name in pruefe.parameter]
        if None in argumente or not pruefe(*argumente, still=True):
            offen.append(f"Aufgabe {nummer}: {pruefe.titel}")

    if offen:
        _kasten(
            "fehler",
            "Speichern nicht möglich",
            "Diese Aufgaben sind noch nicht bestanden:<br>"
            + "<br>".join(html.escape(eintrag) for eintrag in offen)
            + "<br>Führe deine Code-Zellen und die Prüfzellen dieser "
            "Aufgaben noch einmal aus.",
        )
        return

    teile = [
        f'"""\nDein Code aus Notebook {notebook}.\n'
        f'Automatisch gespeichert. Ändere ihn am besten im Notebook.\n"""\n'
    ]
    teile += [f"{zeile}\n" for zeile in importe]
    for objekt in objekte:
        teile.append("\n\n" + _quelltext(objekt).rstrip() + "\n")

    MEINCODE.mkdir(exist_ok=True)
    datei = MEINCODE / f"{dateiname}.py"
    datei.write_text("".join(teile), encoding="utf-8")

    # Falls das Modul schon einmal importiert wurde: alte Version vergessen
    sys.modules.pop(f"meincode.{dateiname}", None)

    _kasten(
        "ok",
        f"Notebook {notebook} abgeschlossen",
        f"Dein Code steht jetzt in <code>meincode/{dateiname}.py</code>. "
        f"Im nächsten Notebook arbeitest du damit weiter.",
    )
