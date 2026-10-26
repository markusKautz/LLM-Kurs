# LLM-Kurs: Ein Sprachmodell selbst bauen

In sieben Jupyter-Notebooks baust du Schritt für Schritt ein Sprachmodell. Am Anfang zählst du nur Zeichenpaare, am Ende steht ein kleiner Transformer, der Märchen im Stil der Brüder Grimm schreibt. Das Prinzip ist dasselbe wie bei ChatGPT und Co., nur viel kleiner.

Der Kurs richtet sich an Auszubildende und Einsteiger mit Programmiererfahrung (zum Beispiel in C#). Python-Kenntnisse sind nicht nötig, das Wichtigste wird im ersten Notebook erklärt. An Mathematik reicht, was man aus der Schule kennt.

## Inhalt

| Notebook | Thema | Was du baust |
|---|---|---|
| 1 | Zählen und Wahrscheinlichkeit | Vokabular, Bigramm- und N-Gramm-Modell, Verlust messen |
| 2 | Ein Netz, das lernt | Tensoren, Softmax, Gradientenabstieg, ein Bigramm-Netz mit PyTorch |
| 3 | Ein größeres Netz | Einbettungen, verborgene Schicht, Minibatches, ein Netz mit drei Zeichen Kontext |
| 4 | Zurückschauen | Durchschnitt über alle bisherigen Zeichen, Maske gegen den Blick in die Zukunft |
| 5 | Aufmerksamkeit | Query, Key und Value, ein Aufmerksamkeits-Kopf, Positionen |
| 6 | Der Transformer | Mehrere Köpfe, FeedForward, Transformer-Block, das ganze Modell |
| 7 | Das große Training | Training auf Grimms Märchen, Temperatur, Rückblick und Ausblick |

Jedes Notebook besteht aus kurzen Erklärungen und Aufgaben. Die Aufgaben prüfen sich selbst, sodass du sofort siehst, ob deine Lösung stimmt. Was du in einem Notebook geschrieben hast, wird gespeichert und im nächsten weiterverwendet.

## Kurs starten

Du brauchst nur [Docker Desktop](https://www.docker.com/products/docker-desktop/). Python oder PyTorch musst du nicht installieren, das steckt alles im Docker-Image.

**Windows:** Docker Desktop starten, dann im Ordner `kurs/teilnehmer` doppelt auf `Kurs starten.bat` klicken. Beim ersten Start lädt Docker etwa 1 GB herunter. Danach öffnet sich JupyterLab im Browser. Zum Beenden doppelt auf `Kurs beenden.bat` klicken.

**Linux und macOS:**

```bash
cd kurs/teilnehmer
docker build --tag llm-kurs .
docker run --rm --name llm-kurs --publish 127.0.0.1:8888:8888 \
  --volume "$PWD/notebooks:/kurs/notebooks" llm-kurs
```

Danach http://localhost:8888/lab im Browser öffnen.

**VS Code:** Den Ordner `kurs/teilnehmer` öffnen und "Reopen in Container" wählen. Die Konfiguration liegt in `.devcontainer/`.

Ohne Git geht es auch: Unter [Releases](https://github.com/markusKautz/LLM-Kurs/releases) liegt der Kurs als ZIP zum Herunterladen.

Deine Arbeit wird immer im Ordner `notebooks` auf deinem Rechner gespeichert, nicht im Container.

## Aufbau des Repositorys

```
kurs/
├── teilnehmer/           Alles, was die Teilnehmer bekommen
│   ├── notebooks/        Die sieben Notebooks
│   │   ├── daten/        Trainingstexte (u. a. Grimms Märchen)
│   │   ├── kurswerkzeuge/ Prüfungen und Grafiken zu den Aufgaben
│   │   └── meincode/     Hier landet der Code der Teilnehmer
│   ├── Dockerfile
│   └── Kurs starten.bat / Kurs beenden.bat
└── trainer/
    ├── inhalt/           Quelle der Notebooks (nb01.py bis nb07.py)
    ├── erzeuge_notebooks.py
    ├── loesungen/        Musterlösungen
    └── vortraege/        Folien zu den Vorträgen (Slidev)
```

## Für Trainer

### Notebooks erzeugen

Die Notebooks werden nicht direkt bearbeitet, sondern aus den Dateien in `kurs/trainer/inhalt/` erzeugt:

```bash
cd kurs/trainer
pip install nbformat
python erzeuge_notebooks.py            # Notebooks und Musterlösungen schreiben
python erzeuge_notebooks.py --testen   # zusätzlich alle Musterlösungen ausführen und prüfen
python erzeuge_notebooks.py --paket    # zusätzlich die ZIP-Pakete für die Teilnehmer bauen
```

Für `--testen` werden außerdem `nbclient`, PyTorch und die Pakete aus `kurs/teilnehmer/requirements.txt` gebraucht.

### Musterlösungen

Die Musterlösungen liegen in `kurs/trainer/loesungen/`. Sie sind absichtlich öffentlich. Wer nicht weiterkommt, darf nachschauen. Mehr lernt man aber, wenn man es vorher selbst versucht.

### Vorträge

Die Folien sind mit [Slidev](https://sli.dev/) gebaut und enthalten interaktive Vue-Komponenten:

```bash
cd kurs/trainer/vortraege
npm install
npm run vortrag1      # oder: npm run vortrag2
```

Mit `npm run vortrag1-netz` sind die Folien auch von anderen Geräten im Netzwerk erreichbar. Die Animationsvideos in `public/videos/` sind mit [Manim](https://www.manim.community/) erstellt und lassen sich mit `animationen/rendern.sh` neu rendern (benötigt Docker). Die Modelle, die die Folien live anzeigen, erzeugen die Skripte in `daten/`.

## Weiterlernen: Andrej Karpathy

Der Kurs folgt in großen Teilen der Videoreihe [Neural Networks: Zero to Hero](https://www.youtube.com/playlist?list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ) von Andrej Karpathy. Die Videos sind auf Englisch und gehen an vielen Stellen tiefer als der Kurs. Wer mit dem Kurs fertig ist, kann dort gut weitermachen.

| Video | Passt zu |
|---|---|
| [The spelled-out intro to neural networks and backpropagation: building micrograd](https://www.youtube.com/watch?v=VMj-3S1tku0) | Notebook 2: wie Gradienten und Backpropagation funktionieren |
| [The spelled-out intro to language modeling: building makemore](https://www.youtube.com/watch?v=PaCmpygFfXo) | Notebook 1 und 2: Bigramme zählen und als Netz lernen |
| [Building makemore Part 2: MLP](https://www.youtube.com/watch?v=TCH_1BHY58I) | Notebook 3: Einbettungen, verborgene Schicht, Minibatches |
| [Let's build GPT: from scratch, in code, spelled out.](https://www.youtube.com/watch?v=kCc8FmEb1nY) | Notebook 4 bis 7: Aufmerksamkeit und Transformer |
| [Let's build the GPT Tokenizer](https://www.youtube.com/watch?v=zduSFxRajkE) | Ausblick: warum echte Modelle mit Wortstücken statt Zeichen arbeiten |
| [Let's reproduce GPT-2 (124M)](https://www.youtube.com/watch?v=l8pRSuU81PU) | Ausblick: ein echtes GPT-2 nachbauen und trainieren |

## Lizenz

- Code: MIT, siehe [LICENSE-CODE](LICENSE-CODE)
- Kursinhalte (Texte, Grafiken, Videos): CC BY 4.0, siehe [LICENSE-INHALT](LICENSE-INHALT)
- Schriften Inter und JetBrains Mono: SIL Open Font License 1.1
- Märchentexte: Kinder- und Hausmärchen der Brüder Grimm, gemeinfrei

Details stehen in [LICENSE](LICENSE).
