"""
Erzeugt die Notebooks für Teilnehmer und Trainer aus den Inhaltsdateien.

    python erzeuge_notebooks.py            Notebooks erzeugen
    python erzeuge_notebooks.py --testen   zusätzlich die Musterlösungen ausführen
                                           und prüfen, ob alle Aufgaben bestehen
    python erzeuge_notebooks.py --paket    zusätzlich LLM-Kurs.zip für die Lehrlinge packen
                                           und LLM-Kurs-Notebook1.zip nur mit Notebook 1
                                           und LLM-Kurs-Notebooks2bis7.zip zum Nachliefern

Benötigt: nbformat
Für --testen zusätzlich: nbclient und die Pakete aus teilnehmer/requirements.txt
"""

import argparse
import importlib.util
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import nbformat

from inhalt import nb01, nb02, nb03, nb04, nb05, nb06, nb07

HIER = Path(__file__).resolve().parent
TEILNEHMER = HIER.parent / "teilnehmer" / "notebooks"
LOESUNGEN = HIER / "loesungen"
PAKET = HIER / "LLM-Kurs.zip"
PAKET_NB1 = HIER / "LLM-Kurs-Notebook1.zip"
PAKET_REST = HIER / "LLM-Kurs-Notebooks2bis7.zip"

# Was die Lehrlinge bekommen, relativ zum Ordner teilnehmer
PAKET_INHALT = ["Kurs starten.bat", "Kurs beenden.bat", "Dockerfile", ".dockerignore", "requirements.txt", "notebooks"]

NOTEBOOKS = [
    ("01_zaehlen_und_wahrscheinlichkeit", nb01.ZELLEN),
    ("02_lernen_mit_pytorch", nb02.ZELLEN),
    ("03_ein_groesseres_netz", nb03.ZELLEN),
    ("04_zurueckschauen", nb04.ZELLEN),
    ("05_aufmerksamkeit", nb05.ZELLEN),
    ("06_der_transformer", nb06.ZELLEN),
    ("07_das_grosse_training", nb07.ZELLEN),
]


def baue(zellen, fassung):
    notebook = nbformat.v4.new_notebook()
    notebook.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    }
    for zelle in zellen:
        if zelle["art"] == "markdown":
            notebook.cells.append(nbformat.v4.new_markdown_cell(zelle["text"]))
        elif zelle["art"] == "code":
            notebook.cells.append(nbformat.v4.new_code_cell(zelle["text"]))
        else:
            notebook.cells.append(nbformat.v4.new_code_cell(
                zelle[fassung],
                metadata={"tags": ["aufgabe"]},
            ))
    return notebook


def _codezeilen(text):
    """Die Zeilen eines Codes ohne Leerzeilen, Kommentare und Einrückung."""
    zeilen = (zeile.split("  #")[0].strip() for zeile in text.splitlines())
    return [zeile for zeile in zeilen if zeile and not zeile.startswith("#")]


def pruefe_loesungstipps(name, zellen):
    """Der letzte Tipp muss die Musterlösung der Aufgabe darüber zeigen."""
    fehler = []
    loesung = None
    for zelle in zellen:
        if zelle["art"] == "aufgabe":
            loesung = set(_codezeilen(zelle["loesung"]))
        elif "loesungstipp" in zelle:
            bloecke = re.findall(r"```python\n(.*?)```", zelle["loesungstipp"], re.S)
            passt = any(set(_codezeilen(block)) <= loesung for block in bloecke) if loesung else False
            if not passt:
                fehler.append(f"{name}: Lösungstipp passt nicht zur Musterlösung:\n{zelle['loesungstipp'][:300]}")
    return fehler


def erzeuge():
    fehler = [f for name, zellen in NOTEBOOKS for f in pruefe_loesungstipps(name, zellen)]
    if fehler:
        sys.exit("\n\n".join(fehler))

    LOESUNGEN.mkdir(exist_ok=True)
    for name, zellen in NOTEBOOKS:
        vorlage = TEILNEHMER / f"{name}.ipynb"
        loesung = LOESUNGEN / f"{name}_loesung.ipynb"
        nbformat.write(baue(zellen, "vorlage"), vorlage)
        nbformat.write(baue(zellen, "loesung"), loesung)
        print(f"geschrieben: {vorlage.relative_to(HIER.parent)}")
        print(f"geschrieben: {loesung.relative_to(HIER.parent)}")


def fehlende_pakete():
    """Pakete, die zum Ausführen der Musterlösungen gebraucht werden."""
    benoetigt = ["nbclient", "ipykernel", "numpy", "matplotlib", "ipywidgets", "torch"]
    return [paket for paket in benoetigt if importlib.util.find_spec(paket) is None]


def teste():
    """Führt die Musterlösungen in einer Kopie des Teilnehmer-Ordners aus."""
    fehlend = fehlende_pakete()
    if fehlend:
        print(
            "\nZum Testen fehlen diese Pakete: " + ", ".join(fehlend) + "\n"
            "Am einfachsten in einer eigenen Umgebung im Ordner trainer:\n\n"
            "    python -m venv .venv\n"
            "    source .venv/bin/activate\n"
            "    pip install -r ../teilnehmer/requirements.txt nbclient\n"
            "    pip install --index-url https://download.pytorch.org/whl/cpu torch==2.14.1\n"
        )
        return False

    from nbclient import NotebookClient

    alles_ok = True
    with tempfile.TemporaryDirectory() as temp:
        arbeitsordner = Path(temp) / "notebooks"
        shutil.copytree(
            TEILNEHMER, arbeitsordner,
            ignore=shutil.ignore_patterns("__pycache__", "notebook*.py", "fortschritt.json", "*.ipynb"),
        )

        for name, zellen in NOTEBOOKS:
            print(f"\nteste {name} ...")
            notebook = baue(zellen, "loesung")
            NotebookClient(
                notebook, timeout=900, kernel_name="python3",
                resources={"metadata": {"path": str(arbeitsordner)}},
            ).execute()

            # Jede Prüfzelle muss "Bestanden" melden
            probleme = []
            for nummer, zelle in enumerate(notebook.cells):
                for ausgabe in zelle.get("outputs", []):
                    inhalt = str(ausgabe.get("data", {}).get("text/html", ""))
                    if "kurs-fehler" in inhalt or "kurs-offen" in inhalt:
                        probleme.append(f"  Zelle {nummer}: {inhalt[:300]}")
            if probleme:
                alles_ok = False
                print("FEHLER in der Musterlösung:")
                print("\n".join(probleme))
            else:
                print("alle Prüfungen bestanden")

            # Speichern muss eine importierbare Datei erzeugt haben
            gespeichert = sorted((arbeitsordner / "meincode").glob("notebook*.py"))
            print("gespeichert:", ", ".join(datei.name for datei in gespeichert) or "nichts")

    return alles_ok


def packe(ziel, notebooks=None, inhalt=PAKET_INHALT):
    """Packt den Teilnehmer-Ordner ohne Arbeitsstände in eine ZIP-Datei.

    notebooks: Namen der Notebooks, die hinein sollen. None heißt alle.
    inhalt: Dateien und Ordner relativ zum Ordner teilnehmer.
    """
    quelle = TEILNEHMER.parent
    with zipfile.ZipFile(ziel, "w", zipfile.ZIP_DEFLATED) as paket:
        for eintrag in inhalt:
            pfad = quelle / eintrag
            dateien = [pfad] if pfad.is_file() else sorted(p for p in pfad.rglob("*") if p.is_file())
            for datei in dateien:
                relativ = datei.relative_to(quelle)
                teile = set(relativ.parts)
                if "__pycache__" in teile or ".ipynb_checkpoints" in teile:
                    continue
                if relativ.parts[:2] == ("notebooks", "meincode") and datei.name != "__init__.py":
                    continue
                if notebooks is not None and datei.suffix == ".ipynb" and datei.stem not in notebooks:
                    continue
                paket.write(datei, Path("LLM-Kurs") / relativ)
    print(f"gepackt: {ziel.relative_to(HIER.parent)} ({ziel.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--testen", action="store_true", help="Musterlösungen ausführen und prüfen")
    parser.add_argument("--paket", action="store_true", help="die ZIP-Pakete für die Lehrlinge packen")
    argumente = parser.parse_args()

    erzeuge()
    if argumente.testen and not teste():
        sys.exit(1)
    if argumente.paket:
        packe(PAKET)
        packe(PAKET_NB1, notebooks=[NOTEBOOKS[0][0]])
        # Nur die Notebooks, damit beim Entpacken in den bestehenden Ordner nichts überschrieben wird
        packe(PAKET_REST, inhalt=[f"notebooks/{name}.ipynb" for name, _ in NOTEBOOKS[1:]])
