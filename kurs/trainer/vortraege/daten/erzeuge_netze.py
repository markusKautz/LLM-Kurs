"""
Trainiert die Netze für Vortrag 2 und speichert, was die Folien zeigen.

    ../.venv/bin/python daten/erzeuge_netze.py      (braucht PyTorch, z. B. aus trainer/.venv)

Wie in Notebook 3: Ein Netz sieht 3 Zeichen, schlägt für jedes Zeichen Koordinaten nach,
rechnet eine Schicht mit ReLU und gibt für jedes Zeichen im Vokabular eine Zahl (Logit) aus.

public/modelle/netz_karte.json     Netz mit 2 Koordinaten: Zwischenstände der Zeichenkarte und Lernkurve
public/modelle/netz_text.json      Netz mit 10 Koordinaten: alle Gewichte, damit der Browser live Text erzeugt
public/modelle/overfitting.json    kleiner und riesiger Netz auf dem kurzen Notebook-Text: Training und Test
public/modelle/vergleich.json      Testverluste der Modelle und ein unbekannter Kontext
"""

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import torch
from torch import nn
import torch.nn.functional as F

HIER = Path(__file__).resolve().parent
TEXTE = HIER.parents[2] / "teilnehmer" / "notebooks" / "daten"
ZIEL = HIER.parent / "public" / "modelle"

torch.manual_seed(7)


class ZeichenNetz(nn.Module):
    def __init__(self, V, kontext, koordinaten, neuronen):
        super().__init__()
        self.kontext = kontext
        self.einbettung = nn.Embedding(V, koordinaten)
        self.schicht1 = nn.Linear(kontext * koordinaten, neuronen)
        self.schicht2 = nn.Linear(neuronen, V)

    def forward(self, X):
        x = self.einbettung(X).flatten(1)
        return self.schicht2(torch.relu(self.schicht1(x)))


def beispiele(ids, kontext):
    ids = torch.tensor(ids)
    X = torch.stack([ids[i:i + kontext] for i in range(len(ids) - kontext)])
    return X, ids[kontext:]


@torch.no_grad()
def verlust(netz, X, Y, hoechstens=40000):
    netz.eval()
    if len(X) > hoechstens:
        auswahl = torch.randperm(len(X), generator=torch.Generator().manual_seed(1))[:hoechstens]
        X, Y = X[auswahl], Y[auswahl]
    wert = F.cross_entropy(netz(X), Y).item()
    netz.train()
    return wert


def trainiere(netz, Xtr, Ytr, Xte, Yte, schritte, lernrate, groesse=64, alle=200, bei_messung=None):
    optimierer = torch.optim.SGD(netz.parameters(), lr=lernrate)
    stapel, messungen = [], []
    for schritt in range(schritte + 1):
        if schritt % alle == 0:
            messung = {"schritt": schritt, "training": verlust(netz, Xtr, Ytr), "test": verlust(netz, Xte, Yte)}
            if bei_messung:
                bei_messung(messung)
            messungen.append(messung)
        if schritt == schritte:
            break
        if schritt == int(schritte * 0.75):
            for gruppe in optimierer.param_groups:
                gruppe["lr"] = lernrate / 10
        auswahl = torch.randint(0, len(Xtr), (groesse,))
        wert = F.cross_entropy(netz(Xtr[auswahl]), Ytr[auswahl])
        optimierer.zero_grad()
        wert.backward()
        optimierer.step()
        stapel.append(round(wert.item(), 3))
    return stapel, messungen


def runde(tensor, stellen=4):
    return [[round(v, stellen) for v in zeile] for zeile in tensor.tolist()] if tensor.dim() == 2 else [round(v, stellen) for v in tensor.tolist()]


def schreibe(name, daten):
    datei = ZIEL / name
    datei.write_text(json.dumps(daten, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{datei.name}: {datei.stat().st_size / 1e6:.2f} MB")


def maerchen():
    text = (TEXTE / "maerchen.txt").read_text(encoding="utf-8")
    zeichen = sorted(set(text))
    zu_id = {z: i for i, z in enumerate(zeichen)}
    ids = [zu_id[z] for z in text]
    grenze = int(len(ids) * 0.9)
    return text, zeichen, ids[:grenze], ids[grenze:]


def karte_und_text():
    text, zeichen, training, test = maerchen()
    V, K = len(zeichen), 3
    Xtr, Ytr = beispiele(training, K)
    Xte, Yte = beispiele(test, K)

    # Netz mit 2 Koordinaten: Wir merken uns, wie die Karte während des Trainings entsteht
    netz = ZeichenNetz(V, K, 2, 100)
    staende = []
    stapel, messungen = trainiere(
        netz, Xtr, Ytr, Xte, Yte, schritte=30000, lernrate=0.1, alle=250,
        bei_messung=lambda m: staende.append(runde(netz.einbettung.weight.detach(), 3)),
    )
    print("Karte: Test", round(messungen[-1]["test"], 3))
    schreibe("netz_karte.json", {
        "zeichen": zeichen,
        "staende": staende,
        "messungen": messungen,
        "stapel": stapel[::10],
    })

    # Netz mit 10 Koordinaten für den Text
    netz10 = ZeichenNetz(V, K, 10, 200)
    _, messungen10 = trainiere(netz10, Xtr, Ytr, Xte, Yte, schritte=40000, lernrate=0.1, alle=2000)
    print("Text: Test", round(messungen10[-1]["test"], 3))
    schreibe("netz_text.json", {
        "zeichen": zeichen,
        "kontext": K,
        "einbettung": runde(netz10.einbettung.weight.detach()),
        "W1": runde(netz10.schicht1.weight.detach().T),
        "b1": runde(netz10.schicht1.bias.detach()),
        "W2": runde(netz10.schicht2.weight.detach().T),
        "b2": runde(netz10.schicht2.bias.detach()),
    })
    return zeichen, training, test, netz10, messungen10[-1]["test"]


def vergleich(zeichen, training, test, netz10, test_netz10):
    V = len(zeichen)
    # Zählmodell und Bigramm-Netz wie in Notebook 1 und 2
    zaehler = torch.zeros(V, V)
    for a, b in zip(training, training[1:]):
        zaehler[a, b] += 1
    P = zaehler / zaehler.sum(1, keepdim=True).clamp(min=1)
    a, b = torch.tensor(test[:-1]), torch.tensor(test[1:])
    p_test = P[a, b]
    gezaehlt = None if (p_test == 0).any() else -p_test.log().mean().item()

    W = torch.zeros(V, V, requires_grad=True)
    optimierer = torch.optim.SGD([W], lr=50)
    a_tr, b_tr = torch.tensor(training[:-1]), torch.tensor(training[1:])
    for _ in range(300):
        auswahl = torch.randint(0, len(a_tr), (5000,))
        wert = F.cross_entropy(W[a_tr[auswahl]], b_tr[auswahl])
        optimierer.zero_grad()
        wert.backward()
        optimierer.step()
    bigramm_netz = F.cross_entropy(W[a].detach(), b).item()

    # Ein Kontext aus dem Test, den es im Training nie gab, und bei dem das Netz trotzdem richtig liegt
    kontexte = Counter(tuple(training[i:i + 3]) for i in range(len(training) - 3))
    gesehen = defaultdict(Counter)
    for i in range(len(training) - 3):
        gesehen[tuple(training[i:i + 3])][training[i + 3]] += 1
    kandidaten = []
    netz10.eval()
    with torch.no_grad():
        for i in range(len(test) - 3):
            k = tuple(test[i:i + 3])
            if k in kontexte or not all(zeichen[z].isalpha() or zeichen[z] == " " for z in k):
                continue
            p = torch.softmax(netz10(torch.tensor([list(k)])), -1)[0]
            richtig = test[i + 3]
            if p.argmax().item() == richtig:
                umfeld = "".join(zeichen[z] for z in test[max(0, i - 12):i + 8])
                kandidaten.append({"kontext": "".join(zeichen[z] for z in k), "richtig": zeichen[richtig],
                                   "p": round(p[richtig].item(), 3), "umfeld": umfeld})
    print("unbekannte Kontexte, bei denen das Netz richtig liegt:", len(kandidaten))
    schreibe("vergleich.json", {
        "verluste": [
            {"name": "Zählen, 1 Zeichen", "test": gezaehlt},
            {"name": "Bigramm-Netz", "test": round(bigramm_netz, 3)},
            {"name": "Zeichen-Netz, 3 Zeichen", "test": round(test_netz10, 3)},
        ],
        "unbekannt": kandidaten[:30],
    })


def overfitting():
    text = (TEXTE / "training.txt").read_text(encoding="utf-8")
    zeichen = sorted(set(text))
    zu_id = {z: i for i, z in enumerate(zeichen)}
    ids = [zu_id[z] for z in text]
    grenze = int(len(ids) * 0.9)
    ergebnis = {}
    for name, (K, d, h, lr) in {"klein": (3, 10, 100, 0.1), "riesig": (8, 20, 1000, 0.2)}.items():
        torch.manual_seed(3)
        Xtr, Ytr = beispiele(ids[:grenze], K)
        Xte, Yte = beispiele(ids[grenze:], K)
        netz = ZeichenNetz(len(zeichen), K, d, h)
        _, messungen = trainiere(netz, Xtr, Ytr, Xte, Yte, schritte=12000, lernrate=lr, groesse=32, alle=200)
        gewichte = sum(p.numel() for p in netz.parameters())
        print(name, gewichte, "Gewichte, Ende:", messungen[-1])
        ergebnis[name] = {"kontext": K, "koordinaten": d, "neuronen": h, "gewichte": gewichte, "messungen": messungen}
    ergebnis["zeichen_im_text"] = len(text)
    schreibe("overfitting.json", ergebnis)


if __name__ == "__main__":
    ZIEL.mkdir(parents=True, exist_ok=True)
    zeichen, training, test, netz10, test_netz10 = karte_und_text()
    vergleich(zeichen, training, test, netz10, test_netz10)
    overfitting()
