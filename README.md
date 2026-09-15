Klar — hier ist ein umfangreiches `README.md`, das den aktuellen Stand des Projekts dokumentiert und gleichzeitig die geplante Architektur für die nächsten Schritte festhält.

````markdown id="r7m2q"
# Finance RAG

Lokales RAG-/LLM-Projekt zur Analyse persönlicher Banktransaktionen aus PDF-Kontoauszügen.

Das Projekt liest Kontoauszüge verschiedener Banken ein, extrahiert und normalisiert Transaktionen, klassifiziert Ausgaben und baut daraus eine lokale Wissensbasis für semantische Suche und spätere Fragen an ein lokales LLM.

Der gesamte Workflow ist lokal ausgelegt:

- PDF-Dateien werden lokal verarbeitet
- Transaktionsdaten werden lokal gespeichert
- Embeddings werden lokal mit Ollama erzeugt
- Vektorsuche läuft lokal mit ChromaDB
- Kategorisierung kann lokal mit Qwen erfolgen
- Es werden keine Bankdaten an externe KI-Dienste übertragen

---

## Inhaltsverzeichnis

1. [Projektziel](#projektziel)
2. [Aktueller Stand](#aktueller-stand)
3. [Architektur](#architektur)
4. [Technischer Stack](#technischer-stack)
5. [Voraussetzungen](#voraussetzungen)
6. [Projektstruktur](#projektstruktur)
7. [Installation](#installation)
8. [Ollama](#ollama)
9. [PDF-Verarbeitung](#pdf-verarbeitung)
10. [Datenmodell](#datenmodell)
11. [Bankparser](#bankparser)
12. [Transaktionsnormalisierung](#transaktionsnormalisierung)
13. [Händler-Normalisierung](#händler-normalisierung)
14. [Kategorisierung](#kategorisierung)
15. [RAG und Embeddings](#rag-und-embeddings)
16. [Hybrid-Suche](#hybrid-suche)
17. [LLM-Kategorisierung](#llm-kategorisierung)
18. [Datenqualität und Reports](#datenqualität-und-reports)
19. [Aktueller Datensatz](#aktueller-datensatz)
20. [Workflow](#workflow)
21. [Tests und Debugging](#tests-und-debugging)
22. [Wichtige Designentscheidungen](#wichtige-designentscheidungen)
23. [Geplante Weiterentwicklung](#geplante-weiterentwicklung)
24. [Bekannte Einschränkungen](#bekannte-einschränkungen)

---

# Projektziel

Ziel des Projekts ist ein lokales persönliches Finanzsystem, das aus Bank-PDFs strukturierte Transaktionsdaten erzeugt und anschließend Fragen wie folgende beantworten kann:

- Wie hoch waren meine Konsumausgaben?
- Wie viel habe ich für Lebensmittel ausgegeben?
- Wie viel Geld ging für Mobilität drauf?
- Welche Händler verursachen die größten Ausgaben?
- Wie viel wurde für interne Transfers bewegt?
- Wie hoch ist mein bereinigter monatlicher Saldo?
- Welche Transaktionen gehören wahrscheinlich zu einer bestimmten Kategorie?
- Welche bisher unbekannten Händler ähneln bekannten Händlern?
- Welche Ausgaben könnten Einsparpotenzial haben?
- Welche historischen Transaktionen sind für eine neue unbekannte Buchung relevant?

Langfristig soll daraus ein lokaler Finanzassistent entstehen, der Fragen zu den eigenen Finanzdaten beantworten kann.

---

# Aktueller Stand

Der aktuelle Stand umfasst:

- PDF-Extraktion mit PyMuPDF
- automatische Erkennung von comdirect und ING
- separate Parser für beide Banken
- strukturierte `Transaction`-Objekte
- Normalisierung von Transaktionstypen
- Erkennung interner Transfers
- Erkennung von Darlehenszahlungen
- Händler-Normalisierung
- regelbasierte Kategorisierung für bereits eindeutig technische bzw. geschäftslogische Fälle
- Export nach JSON
- lokale Embeddings mit Ollama
- lokale Vektordatenbank mit ChromaDB
- Hybrid-Suche aus exaktem Händler-Match und semantischer Suche
- Kategorie-Inferenz aus ähnlichen historischen Transaktionen
- Testpipeline für RAG + lokales LLM mit Qwen

Die aktuelle Architektur soll weiter in Richtung:

```text
PDF
  |
  v
Extraktion
  |
  v
Bankparser
  |
  v
Normalisierung
  |
  v
Händler-Normalisierung
  |
  v
Technische Regeln
  |
  v
LLM-Kategorisierung + RAG
  |
  v
Strukturierter Finanzdatensatz
  |
  v
ChromaDB
  |
  v
Finanz-RAG / lokaler Assistent
````

entwickelt werden.

---

# Architektur

Das Projekt besteht im Wesentlichen aus fünf Schichten.

## 1. Ingestion

PDF-Dateien werden eingelesen und in strukturierte Blöcke zerlegt.

```text
PDF
 |
 +-- PyMuPDF
       |
       +-- Seiten
       +-- Blöcke
       +-- Koordinaten
       +-- Text
```

## 2. Parsing

Die unterschiedlichen PDF-Layouts der Banken werden durch eigene Parser verarbeitet.

```text
BankDispatcher
 |
 +-- ComdirectParser
 |
 +-- INGParser
```

Das verhindert, dass bank-spezifische Layoutlogik überall im Projekt verteilt wird.

## 3. Normalisierung und Kategorisierung

Nach dem Parsing werden Transaktionen semantisch normalisiert.

Dabei werden unter anderem:

* interne Überweisungen
* Spartransfers
* Darlehenszahlungen
* Gebühren
* Rückerstattungen
* Einkommen
* unbekannte Eingänge
* Konsumausgaben

unterschieden.

## 4. RAG

Bereits kategorisierte historische Konsumausgaben werden als Wissensbasis verwendet.

```text
historische Transaktion
        |
        v
Embedding
        |
        v
ChromaDB
```

Eine neue Anfrage kann anschließend ähnliche historische Transaktionen finden.

## 5. Lokales LLM

Qwen wird verwendet, um auf Basis der aktuellen Transaktion und relevanter historischer Beispiele eine Kategorie zu bestimmen.

```text
aktuelle Transaktion
        |
        +---- Händler
        |
        +---- Verwendungszweck
        |
        +---- Betrag
        |
        +---- RAG-Kontext
                 |
                 v
             Qwen
                 |
                 v
 Kategorie + Unterkategorie + Begründung
```

---

# Technischer Stack

## Betriebssystem

Aktuelle Entwicklungsumgebung:

* Windows 11
* WSL2
* Ubuntu 24.04.4 LTS

## Python

Aktuell wird Python 3.12 verwendet.

Python 3.12 wurde gewählt, weil mehrere Pakete aus dem KI-/RAG-Ökosystem zum Projektstart noch Kompatibilitätsprobleme mit Python 3.14 verursacht haben.

Die Python-Abhängigkeiten werden mit Poetry verwaltet.

## Python-Pakete

Unter anderem werden verwendet:

* `pymupdf`
* `pandas`
* `numpy`
* `chromadb`
* `sentence-transformers`
* `langchain`
* `langchain-community`
* `ollama`
* `python-dotenv`
* `pdfplumber`

Die PDF-Verarbeitung verwendet aktuell primär PyMuPDF.

---

# Voraussetzungen

Benötigt werden:

* Python 3.12
* Poetry
* Ollama
* eine ausreichend leistungsfähige lokale GPU oder CPU
* die persönlichen Kontoauszüge als PDF

Für die aktuelle Entwicklung wird eine NVIDIA GTX 1060 mit 6 GB VRAM verwendet.

Die Modelle sind relativ kompakt gewählt, damit das System lokal betrieben werden kann.

---

# Installation

Repository bzw. Projektverzeichnis:

```bash
cd ~/finance-rag
```

Poetry-Umgebung installieren:

```bash
poetry install
```

Python-Version prüfen:

```bash
poetry run python --version
```

Erwartet wird ungefähr:

```text
Python 3.12.x
```

---

# Ollama

Ollama stellt die lokalen Embedding- und LLM-Modelle bereit.

Aktuell verwendete bzw. getestete Modelle:

```text
embeddinggemma
qwen2.5:3b
qwen2.5:7b
```

Zusätzlich befinden sich weitere Modelle lokal, darunter:

```text
qwen3.5:4b
mistral
```

## Verfügbare Modelle prüfen

```bash
ollama list
```

## Embedding-Modell

Aktuell:

```text
embeddinggemma
```

## LLM

Für die Klassifizierung wird aktuell getestet:

```text
qwen2.5:7b
```

Das vorher verwendete Modell:

```text
qwen2.5:3b
```

zeigte bei einigen Finanzkategorien Schwächen bei der Interpretation von RAG-Kontext.

---

# PDF-Verarbeitung

PDFs werden unter:

```text
data/pdf/
```

abgelegt.

Beispiel:

```text
data/pdf/
├── Finanzreport_Nr._06_per_01.07.2026_A0A756.pdf
├── Finanzreport_Nr._07_per_03.08.2026_46A58D.pdf
├── Girokonto_5421708039_Kontoauszug_20260702.pdf
└── Girokonto_5421708039_Kontoauszug_20260802.pdf
```

Die PDFs sind die ursprüngliche Datenquelle.

Die Anwendung versucht, möglichst viel Information bereits beim Extrahieren zu erhalten:

* Text
* Seitenzahl
* Blockposition
* Reihenfolge
* Transaktionsblöcke

---

# PDF-Extraktion

Die Datei:

```text
src/pdf/extractor.py
```

verwendet PyMuPDF.

Prinzip:

```python
import fitz

doc = fitz.open(pdf_file)

for page in doc:
    blocks = page.get_text("blocks")
```

Jeder Block wird mit seinen Koordinaten und seinem Text gespeichert.

Beispiel:

```text
{
    "x": 123.4,
    "y": 456.7,
    "text": "AMAZON PAYMENTS EUROPE S.C.A."
}
```

Koordinaten sind wichtig, weil Bank-PDFs Informationen teilweise nicht als einfache lineare Textzeilen strukturieren.

---

# Bankparser

Die Parser befinden sich unter:

```text
src/parsers/
```

Aktuell:

```text
src/parsers/
├── base.py
├── comdirect.py
├── ing.py
└── dispatcher.py
```

## Dispatcher

`dispatcher.py` erkennt anhand des PDF-Inhalts, zu welcher Bank das Dokument gehört.

Unterstützte Banken:

```text
comdirect
ing
```

---

# Comdirect Parser

Der Comdirect-Parser verarbeitet das teilweise komplexe Blocklayout des Finanzreports.

Eine Transaktion besteht dort häufig aus mehreren PDF-Blöcken.

Vereinfachtes Beispiel:

```text
02.06.2026
02.06.2026
Lastschrift /
Belastung
...
```

gefolgt von:

```text
AMAZON PAYMENTS
EUROPE S.C.A.
```

und weiteren Informationen sowie dem Betrag.

Die Parserlogik verwendet deshalb nicht nur einzelne Textzeilen, sondern Transaktionsblöcke zwischen zwei Buchungsanfängen.

Erkannte Typen:

* Lastschrift
* Kartenverfügung
* Echtzeitüberweisung
* Überweisung
* Dauerauftrag
* Gutschrift
* Devisen

---

# ING Parser

ING verwendet ein anderes Layout.

Eine Transaktion befindet sich häufig in einem einzelnen PDF-Block.

Beispiel:

```text
01.06.2026
Dauerauftrag/Terminueberw. Rhein-Kreis Neuss
-160,00
01.06.2026
Kassenzeichen...
```

Der Betrag befindet sich dabei erwartungsgemäß in der dritten Zeile des Blocks.

Diese Position wird bewusst verwendet, um zufällige Beträge aus Beschreibungen nicht fälschlich als Transaktionsbetrag zu erkennen.

---

# Datenmodell

Das zentrale Datenmodell befindet sich in:

```text
src/models.py
```

Aktuell:

```python
@dataclass(slots=True)
class Transaction:
    bank: str
    booking_date: str
    value_date: str | None
    transaction_type: str
    merchant: str
    amount: float
    description: str

    normalized_type: str = "unknown"
    is_internal_transfer: bool = False

    category: str | None = None
    subcategory: str | None = None

    category_source: str = "unclassified"
    category_confidence: float | None = None
    category_reason: str | None = None

    merchant_normalized: str | None = None
```

---

# Wichtige Transaktionsfelder

## `merchant`

Original erkannter Händlername.

Beispiel:

```text
AMAZON PAYMENTS EUROPE S.C.A.
```

## `merchant_normalized`

Normalisierter Händlername.

Beispiel:

```text
Amazon
```

## `transaction_type`

Originaler Banktyp:

```text
Lastschrift
Überweisung
Gutschrift
...
```

## `normalized_type`

Semantisch normalisierter Typ:

```text
expense
income
refund
fee
loan_payment
savings
transfer_in
transfer_out
unknown_inflow
```

## `category`

Hauptkategorie:

```text
Lebensmittel
Shopping
Mobilität
Wohnen
...
```

## `subcategory`

Unterkategorie, sofern vorhanden.

## `category_source`

Quelle der Kategorisierung, z. B.:

```text
rule
llm
unclassified
```

Geplant ist eine Erweiterung für:

```text
rag_llm
```

## `category_confidence`

Vom Klassifikator gelieferte Vertrauensangabe.

Wichtig:

Diese Zahl ist derzeit **keine statistisch kalibrierte Wahrscheinlichkeit**.

Sie dient aktuell nur als zusätzliche Information.

---

# Transaktionsnormalisierung

Die Datei:

```text
src/transaction_rules.py
```

enthält bewusst nur Regeln, die sich auf die **Bedeutung des Zahlungsflusses** beziehen.

Beispiele:

## Interne Transfers

Transaktionen zwischen eigenen Konten bzw. bekannte Bewegungen innerhalb der gemeinsamen Finanzstruktur werden als interne Transfers erkannt.

Dabei spielt insbesondere:

```text
Lars Freier
```

eine Rolle.

Einzahlungen und Auszahlungen an diese Person können abhängig vom Vorzeichen als:

```text
transfer_in
transfer_out
```

erkannt werden.

## Ausnahme Darlehen

Eine Zahlung wie:

```text
Dr Lars Freier u. Yvonne Mertens
```

kann anhand des Verwendungszwecks als Darlehenszahlung erkannt werden.

Diese Regel hat Vorrang vor der allgemeinen Transfererkennung.

## Spartransfers

Bekannte Spartransfers werden als:

```text
savings
```

markiert.

## Gebühren

Transaktionen mit eindeutigen Bankgebühren werden als:

```text
fee
```

normalisiert.

## Rückerstattungen

Positive Amazon-Zahlungen werden momentan als Rückerstattungen interpretiert, wenn die Transaktion entsprechend erkannt wird.

---

# Händler-Normalisierung

Die Datei:

```text
src/merchant_normalizer.py
```

normalisiert unterschiedliche Schreibweisen desselben Händlers.

Beispiele:

```text
Bäckerei Schneider
Backerei Schneider
```

werden nach Möglichkeit zusammengeführt.

Weitere bekannte Händler:

```text
ALDI
Lidl
Netto
dm
Rossmann
Shell
SB Tanktreff
Jeans Fritz
H&M
Ernsting's
KiK
hagebaumarkt
TEDi
Amazon
...
```

Zusätzlich behandelt der Normalizer bestimmte Zahlungsdienstleister.

Dazu gehören unter anderem:

```text
Nexi
Unzer
SumUp
```

Der Grund:

Der im Kontoauszug angezeigte Name ist bei diesen Zahlungsdienstleistern nicht immer der eigentliche Händler.

Beispiel:

```text
SumUp
    |
    +-- eigentlicher Händler möglicherweise in description
```

---

# Technische Textbereinigung

Die Datei:

```text
src/text_cleaner.py
```

entfernt technische Bankinformationen aus Texten.

Beispiele:

```text
End-to-End-Ref.
Referenz
Mandat
Gläubiger-ID
Folgenr.
Verfalld.
Karte Nr.
Kartenzahlung
```

Diese Informationen sind für die semantische Suche meistens nicht hilfreich.

Dadurch wird der Embedding-Text stärker auf den tatsächlichen Händler und Verwendungszweck fokussiert.

---

# Kategorisierung

Die Kategorien dienen der Analyse der Konsumausgaben.

Aktuelle Kategorien:

```text
Lebensmittel
Shopping
Telekommunikation
Sonstiges
Drogerie
Kinder
Glücksspiel
Mobilität
Wohnen
Gesundheit
Haushalt
Kleidung & Schuhe
Essen außer Haus
Abos & Software
Behörden & Abgaben
Hobby & Freizeit
Reisen
Rundfunkbeitrag
```

---

# Grundprinzip der Kategorisierung

Die langfristig gewünschte Architektur ist:

```text
                   Transaktion
                       |
              technische Regeln
                       |
            +----------+----------+
            |                     |
      Sonderfall sicher      Konsumausgabe
            |                     |
            |                     v
            |               RAG-Suche
            |                     |
            |                     v
            |                lokales LLM
            |                     |
            +----------+----------+
                       |
                       v
                  Kategorie
```

Die Regeln sollen dabei nicht zu einer riesigen Sammlung von Händlerregeln wachsen.

Insbesondere soll nicht für jeden neuen Händler manuell Folgendes eingetragen werden:

```text
Händler X -> Lebensmittel
Händler Y -> Mobilität
Händler Z -> Shopping
```

Stattdessen soll diese Aufgabe zunehmend vom lokalen LLM mit Hilfe historischer Daten übernommen werden.

---

# RAG und Embeddings

Das Projekt verwendet Ollama für Embeddings.

Aktuell:

```text
embeddinggemma
```

Zuvor wurde:

```text
nomic-embed-text
```

verwendet.

## Warum wurde gewechselt?

Tests mit `nomic-embed-text` führten zu problematischen identischen Embeddings.

Beispiel:

```text
Bäckerei Schneider
Shell Tankstelle
ALDI Supermarkt
```

teilten teilweise exakt denselben Vektor.

Cosine Similarity:

```text
1.0000
```

für eigentlich völlig unterschiedliche Händler.

Dadurch wurden falsche RAG-Treffer erzeugt.

Mit `embeddinggemma` verschwanden diese offensichtlichen identischen Vektoren.

---

# Embedding-Test

Das Testprogramm:

```text
src/test_embeddings.py
```

kann mehrere Texte direkt gegen Ollama testen.

Beispiel:

```text
Bäckerei Schneider
Shell Tankstelle
Jeans Fritz Kleidung
Pänz & Piepmatz Spielwaren
ALDI Supermarkt
```

Dabei werden:

* Embedding-Dimension
* erste Vektorwerte
* paarweise Cosine Similarity

ausgegeben.

Aktuell liefert `embeddinggemma` plausible Unterschiede zwischen den Begriffen.

---

# ChromaDB

Die lokale Vektordatenbank befindet sich in:

```text
database/
```

Collection:

```text
transactions
```

Aktuell werden nur Transaktionen aufgenommen, die:

```text
normalized_type == "expense"
```

und gleichzeitig:

```text
category != "Sonstiges"
```

haben.

Das verhindert, dass unbekannte bzw. unsichere Kategorien als Referenzbeispiele für das LLM verwendet werden.

---

# Aufbau des Vector Stores

Der Befehl:

```bash
poetry run python src/vector_store.py
```

lädt:

```text
data/processed/transactions.json
```

filtert geeignete Transaktionen, erstellt Embeddings und baut die Chroma-Collection neu auf.

Beispielausgabe:

```text
Transaktionen insgesamt: 422
Für RAG geeignet: 238
Erzeuge Embeddings...
ChromaDB aufgebaut: 238 Einträge
```

---

# Hybrid-Suche

Eine wichtige Architekturentscheidung ist die Kombination aus:

1. exakter Händler-Suche
2. semantischer Suche

Die Funktion:

```text
hybrid_search()
```

arbeitet aktuell so:

```text
Suchanfrage
    |
    +-- exakter normalisierter Händler?
    |       |
    |       +-- JA -> historische Händlerdaten
    |
    +-- NEIN -> semantische Suche
```

## Warum?

Eine Anfrage wie:

```text
Shell
```

soll nicht über semantische Ähnlichkeit zu:

```text
ALDI
Trinkgut
Frischecenter
```

führen, obwohl diese zufällig im Embedding-Raum nahe liegen.

Wenn `Shell` bereits als Händler bekannt ist:

```text
Shell
Kategorie: Mobilität
Historische Treffer: 5
```

ist die exakte historische Information wertvoller.

---

# Semantische Suche

Ist der Händler unbekannt, wird die semantische Suche als Fallback verwendet.

Beispiel:

```text
Backerei Bernd
```

kann historische Händler wie:

```text
Bäckerei Schneider
Backerei Bernd SumUp ...
REWE
Trinkgut
ALDI
```

finden.

Das LLM kann daraus zusätzliche Hinweise bekommen.

---

# Kategorie-Inferenz

Die Funktion:

```text
infer_category_from_similar_transactions()
```

ist ein Zwischenbaustein zwischen RAG und LLM.

Sie versucht aus ähnlichen historischen Transaktionen eine mögliche Kategorie abzuleiten.

Dabei gelten bewusst konservative Regeln:

* nur ausreichend ähnliche Treffer werden berücksichtigt
* mindestens zwei historische Treffer müssen die Kategorie stützen
* ein ausreichender Kategorie-Konsens muss vorhanden sein
* ansonsten bleibt die Kategorie unbekannt

Beispiel:

```text
Backerei Bernd
   |
   +-- Bäckerei Schneider -> Lebensmittel
   +-- Backerei Bernd ... -> Lebensmittel
   +-- REWE              -> Lebensmittel
   |
   v
Lebensmittel
```

Dagegen soll ein Fall wie:

```text
Neuer Spielwarenladen
```

nicht automatisch als:

```text
Lebensmittel
```

klassifiziert werden, nur weil zufällig zwei semantisch schwache Treffer aus dieser Kategorie stammen.

---

# LLM-Kategorisierung

Die Datei:

```text
src/llm_categorizer.py
```

nutzt aktuell:

```text
qwen2.5:7b
```

als zu testendes Modell.

Die Aufgabe des LLM:

```text
Aktuelle Transaktion
+
RAG-Kontext
=
Kategorie
```

Das LLM erhält:

* Händler
* normalisierten Händler
* Verwendungszweck
* Betrag
* historische Treffer
* deren Kategorien
* semantische Distanz

---

# LLM-Ausgabe

Das gewünschte Format ist JSON:

```json
{
  "category": "Lebensmittel",
  "subcategory": "Lebensmittel",
  "confidence": 0.91,
  "reason": "Der Händler entspricht den historischen Beispielen..."
}
```

Die Kategorie muss aus der definierten Kategorienliste stammen.

Ungültige Kategorien werden vom Python-Code abgelehnt.

---

# RAG ist Kontext, nicht Wahrheit

Eine wichtige Designregel des Projekts:

```text
Historische RAG-Treffer
```

sind Hinweise.

Sie dürfen nicht blind übernommen werden.

Beispiel:

```text
Aktuell:
Living de Luxe GmbH
Verwendungszweck:
CARWASH-DELUXE GmbH
```

Wenn die semantische Suche zufälligerweise:

```text
EDEKA
dm
NKD
```

liefert, darf daraus nicht automatisch:

```text
Lebensmittel
```

entstehen.

Das LLM muss den tatsächlichen Verwendungszweck analysieren.

---

# Aktuelles Problem bei LLM + RAG

Die bisherigen Tests mit `qwen2.5:3b` zeigen, dass das Modell bei schwachen RAG-Treffern teilweise falsche Schlussfolgerungen zieht.

Beispielsweise wurden Transaktionen teilweise falsch kategorisiert, obwohl die aktuelle Transaktion selbst deutliche Hinweise enthielt.

Außerdem gab es Begründungen, die Informationen enthielten, die gar nicht in den bereitgestellten historischen Beispielen standen.

Deshalb wird aktuell:

* `qwen2.5:7b` getestet
* der RAG-Kontext stärker gefiltert
* die Bedeutung des Verwendungszwecks im Prompt erhöht
* das LLM ausdrücklich angewiesen, keine Informationen zu erfinden

---

# Datenqualität und Reports

Das Hauptanalyseprogramm:

```text
src/analyze_dataset.py
```

gibt einen Datenqualitätsbericht aus.

Beispiel:

```text
DATA QUALITY REPORT
```

Enthalten sind unter anderem:

* Anzahl aller Transaktionen
* Aufteilung nach Bank
* Original-Transaktionstypen
* normalisierte Typen
* Einnahmen
* Rückerstattungen
* Konsumausgaben
* Darlehenszahlungen
* Gebühren
* Spartransfers
* interne Transfers
* unbekannte Eingänge
* bereinigter Saldo
* Kategorien
* größte Ausgaben
* größte Einnahmen
* Rückerstattungen
* unbekannte Eingänge

---

# Aktueller Datensatz

Der aktuelle Testdatensatz umfasst:

```text
422 Transaktionen
```

aus:

```text
ING:       318
comdirect: 104
```

Originale Transaktionstypen:

```text
Lastschrift:               247
Überweisung:               140
Echtzeitüberweisung:        13
Gutschrift:                  7
Gutschrift/Dauerauftrag:     5
Dauerauftrag:                4
Entgelt:                     4
Devisen:                     2
```

Normalisierte Typen:

```text
expense:           259
savings:           117
transfer_out:       12
unknown_inflow:     11
transfer_in:         8
income:              6
fee:                 4
refund:              3
loan_payment:        2
```

---

# Aktuelle Finanzübersicht

Aktueller Stand des Datensatzes:

```text
Einkommen:                 14.840,77 €
Rückerstattungen:              82,85 €
Konsumausgaben:            -10.337,99 €
Hausdarlehen:               -4.150,00 €
Gebühren:                      -5,96 €
Spartransfers:                -53,44 €
Interne Transfers rein:    11.412,00 €
Interne Transfers raus:  -10.022,00 €
Unbekannte Eingänge:         1.944,83 €
Bereinigter Saldo:          2.374,50 €
```

Der bereinigte Saldo soll interne Bewegungen und Spartransfers nicht mit normalen Konsumbewegungen vermischen.

---

# Kategorienübersicht

Aktuell entfallen die Konsumausgaben auf unter anderem:

```text
Lebensmittel
Shopping
Telekommunikation
Sonstiges
Drogerie
Kinder
Glücksspiel
Mobilität
Wohnen
Gesundheit
Haushalt
Kleidung & Schuhe
Essen außer Haus
Abos & Software
Behörden & Abgaben
Hobby & Freizeit
Reisen
Rundfunkbeitrag
```

Ein aktuelles Problem ist weiterhin:

```text
Sonstiges
```

Hier befinden sich einige Transaktionen, bei denen die bisherige regelbasierte Kategorisierung keine sichere Aussage getroffen hat.

Diese Fälle sollen künftig überwiegend vom LLM anhand des RAG-Kontexts kategorisiert werden.

---

# Datenexport

Die Datei:

```text
src/exporter.py
```

exportiert Dataclasses nach JSON.

Aktueller Datensatz:

```text
data/processed/transactions.json
```

Beispielstruktur:

```json
{
  "bank": "comdirect",
  "booking_date": "30.07.2026",
  "value_date": "30.07.2026",
  "transaction_type": "Lastschrift",
  "merchant": "AMAZON PAYMENTS EUROPE S.C.A.",
  "amount": -341.70,
  "description": "...",
  "normalized_type": "expense",
  "is_internal_transfer": false,
  "category": "Shopping",
  "subcategory": "Shopping",
  "category_source": "rule",
  "category_confidence": 1.0,
  "category_reason": "...",
  "merchant_normalized": "Amazon"
}
```

---

# Gesamt-Workflow

Der komplette aktuelle Ablauf kann über:

```bash
poetry run python src/build_dataset.py
```

gestartet werden.

Der Ablauf ist:

```text
data/pdf/*.pdf
       |
       v
extract_blocks()
       |
       v
BankDispatcher
       |
       +------ comdirect
       |
       +------ ING
       |
       v
Transaction-Objekte
       |
       v
normalize_transaction()
       |
       v
normalize_merchant()
       |
       v
Kategorisierung
       |
       v
transactions.json
```

---

# Vector Store Workflow

Nach dem Aufbau der strukturierten Daten:

```bash
poetry run python src/vector_store.py
```

werden die geeigneten historischen Transaktionen indexiert.

```text
transactions.json
       |
       v
Filter:
normalized_type == expense
category != Sonstiges
       |
       v
build_document()
       |
       v
embeddinggemma
       |
       v
ChromaDB
```

---

# Tests

## Embeddings testen

```bash
poetry run python src/test_embeddings.py
```

Testet:

* Modell
* Dimension
* Vektoren
* Cosine Similarity

---

## Vector Store testen

```bash
poetry run python src/test_vector_store.py
```

Testet unter anderem:

```text
Bäckerei Schneider
Shell
Jeans Fritz
Pänz & Piepmatz
Tankstelle
```

sowie unbekannte Händler.

---

## LLM + RAG testen

```bash
poetry run python src/test_llm_rag.py
```

Aktuelle Testfälle umfassen beispielsweise:

```text
STICHTING MOLLIE PAYMENTS
Transdev Vertrieb Gm
HORSTHEMKE BACKBETRIEBE
Living de Luxe GmbH
Dinner Catering GmbH
Gemeinde Zeltingen-Rachtig
Heiko Grunert
```

Diese Tests werden bewusst verwendet, weil die Händler nicht immer direkt aus ihrem Namen klassifizierbar sind.

---

# Kategorien prüfen

```bash
poetry run python src/inspect_categories.py
```

Damit lassen sich insbesondere alle:

```text
Sonstiges
```

Buchungen untersuchen.

---

# Datenqualität

```bash
poetry run python src/analyze_dataset.py
```

liefert einen Gesamtüberblick über den aktuellen Datensatz.

---

# Rebuild des Vector Stores

Falls das Embedding-Modell gewechselt wird, muss der Vector Store neu aufgebaut werden.

Beispiel:

```bash
rm -rf database
poetry run python src/vector_store.py
```

Alternativ löscht `vector_store.py` beim Neubau die bestehende Collection selbst.

Wichtig:

Alte Embeddings dürfen nicht mit Embeddings eines anderen Modells gemischt werden.

---

# Wichtige Designentscheidungen

## Lokal statt Cloud

Finanzdaten sind besonders sensibel.

Daher:

```text
PDF
JSON
Embeddings
Vector Store
LLM
```

alles lokal.

Keine automatische Übertragung kompletter Banktransaktionen an externe APIs.

---

## Bankparser getrennt halten

ING und comdirect haben unterschiedliche PDF-Strukturen.

Die Parser werden deshalb getrennt entwickelt:

```text
ComdirectParser
INGParser
```

Das vereinfacht Wartung und Debugging.

---

## Regeln nicht mit semantischer Klassifikation vermischen

Technische Regeln sind sinnvoll für eindeutig bestimmbare Zahlungsarten:

```text
Darlehen
Gebühren
interne Transfers
Spartransfers
Rückerstattungen
```

Die eigentliche Konsumkategorie soll dagegen zunehmend vom LLM übernommen werden.

---

## Exakter Händler-Match vor semantischer Suche

Bekannte Händler sollen nicht durch semantische Zufallstreffer überschrieben werden.

Beispiel:

```text
Shell
```

muss nicht über Embeddings erst als Tankstelle erkannt werden, wenn die eigene Historie bereits eindeutig sagt:

```text
Shell
Mobilität
```

---

## Lieber unbekannt als falsch

Eine zentrale Qualitätsregel des Projekts:

```text
Unsicher
    |
    v
Sonstiges
```

ist besser als:

```text
Unsicher
    |
    v
falsche Kategorie
```

Eine Finanzanalyse kann durch systematische Fehlklassifikation erheblich verfälscht werden.

---

# Bekannte Einschränkungen

## Händlername kann irreführend sein

Bei Zahlungsdienstleistern:

```text
SumUp
Mollie
Unzer
PayPal
```

ist der sichtbare Name möglicherweise nicht der tatsächliche Händler.

Hier muss stärker auf den Verwendungszweck zurückgegriffen werden.

---

## Semantische Ähnlichkeit ist nicht gleich Geschäftskategorie

Ein Embedding kann zwei Texte semantisch ähnlich finden, obwohl ihre Finanzkategorien unterschiedlich sind.

Beispiel:

```text
Tankstelle
```

kann aufgrund allgemeiner Sprachähnlichkeit auch mit anderen Handelsunternehmen relativ nah sein.

Deshalb darf der rohe Embedding-Abstand nicht direkt als Kategorieentscheidung verwendet werden.

---

## LLM-Konfidenz ist nicht kalibriert

Wenn Qwen:

```json
{
  "confidence": 0.85
}
```

liefert, bedeutet das nicht automatisch:

```text
85 % Wahrscheinlichkeit
```

Es handelt sich zunächst um eine Selbsteinschätzung des Modells.

Für eine spätere robuste Bewertung sollte diese Kennzahl anhand realer Testdaten evaluiert werden.

---

## Datenumfang

Der aktuelle Datensatz umfasst erst wenige Monate.

Dadurch existieren für viele Händler und Kategorien nur wenige historische Beispiele.

Mit zusätzlichen Monaten verbessert sich voraussichtlich die Wissensbasis.

Gleichzeitig können neue Händler auftreten, die überhaupt keine Historie besitzen.

---

# Geplante Weiterentwicklung

## 1. LLM-Kategorisierung produktiv integrieren

Der geplante Workflow:

```text
build_dataset.py
      |
      v
Technische Normalisierung
      |
      v
bereits bekannte Kategorie?
      |
      +--- ja ---> speichern
      |
      +--- nein
             |
             v
          RAG
             |
             v
           Qwen
             |
             v
       Kategorie speichern
```

---

## 2. Kategoriequelle erweitern

Geplant sind Quellen wie:

```text
rule
llm
rag_llm
unclassified
```

Damit später nachvollziehbar bleibt, wie eine Kategorie entstanden ist.

---

## 3. Historische Händlerprofile

Aus mehreren Transaktionen desselben Händlers soll später ein Profil aufgebaut werden:

```text
Händler:
Bäckerei Schneider

Kategorie:
Lebensmittel

Anzahl:
3

Gesamtausgaben:
-14,50 €

Letzter Einkauf:
30.07.2026
```

Diese Profile könnten später eine eigene Retrieval-Ebene darstellen.

---

## 4. Händler-Alias-System verbessern

Varianten desselben Händlers sollen automatisch zusammengeführt werden.

Beispiel:

```text
JEANS FRITZ
JEANS FRITZ/Breslauer Str. 2/Neuss
JEANS FRITZ ELV...
```

werden langfristig auf:

```text
Jeans Fritz
```

normalisiert.

---

## 5. RAG für unbekannte Händler

Neue Händler sollen durch historische ähnliche Transaktionen unterstützt werden.

Beispiel:

```text
neuer Bäcker
    |
    v
historische Bäcker
    |
    v
RAG
    |
    v
Qwen
    |
    v
Lebensmittel
```

---

## 6. Finanzfragen über RAG

Langfristig soll ein lokaler Chat entstehen.

Beispiele:

```text
Wie viel habe ich im Juli für Lebensmittel ausgegeben?
```

```text
Welche fünf Händler hatten im Juli die höchsten Ausgaben?
```

```text
Wie viel habe ich im Juni und Juli für Mobilität ausgegeben?
```

```text
Welche Ausgaben haben sich gegenüber dem Vormonat erhöht?
```

```text
Welche unbekannten Händler wurden neu erkannt?
```

---

# Sicherheit und Datenschutz

Die Datenquelle besteht aus persönlichen Finanzinformationen.

Daher sollten folgende Dateien niemals öffentlich in ein Git-Repository übernommen werden:

```text
data/pdf/
data/processed/transactions.json
database/
```

Ein Beispiel für `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]

# Poetry
.venv/

# Finanzdaten
data/pdf/*
data/processed/*
data/exports/*
database/*

# Lokale Konfiguration
.env

# IDE
.vscode/
.idea/
```

Insbesondere Kontoauszüge und erzeugte Transaktionsdaten sollten nicht versehentlich auf GitHub oder andere öffentliche Plattformen gelangen.

---

# Beispiel für die komplette Nutzung

## 1. PDFs ablegen

```text
data/pdf/
```

## 2. Datensatz erzeugen

```bash
poetry run python src/build_dataset.py
```

## 3. Datenqualität prüfen

```bash
poetry run python src/analyze_dataset.py
```

## 4. Unklassifizierte Ausgaben prüfen

```bash
poetry run python src/inspect_categories.py
```

## 5. Vector Store neu aufbauen

```bash
poetry run python src/vector_store.py
```

## 6. Retrieval testen

```bash
poetry run python src/test_vector_store.py
```

## 7. LLM + RAG testen

```bash
poetry run python src/test_llm_rag.py
```

---

# Entwicklungsphilosophie

Das Projekt verfolgt bewusst einen konservativen Ansatz:

```text
Parsing
    |
    v
Normalisierung
    |
    v
Validierung
    |
    v
RAG
    |
    v
LLM
```

Jede Schicht soll möglichst eine klar abgegrenzte Aufgabe erfüllen.

Insbesondere:

* Parser sollen Daten korrekt extrahieren.
* Normalisierung soll Zahlungsarten und Händler vereinheitlichen.
* RAG soll historische Evidenz liefern.
* Das LLM soll die semantische Interpretation übernehmen.
* Analysecode soll keine Daten stillschweigend verändern.

Dadurch bleibt nachvollziehbar, wie eine finanzielle Aussage zustande gekommen ist.

---

# Aktuelle Projektstruktur

```text
finance-rag/
├── data/
│   ├── pdf/
│   ├── processed/
│   └── exports/
│
├── database/
│
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── ingest.py
│   ├── parser.py
│   ├── categories.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── rag.py
│   ├── models.py
│   ├── exporter.py
│   ├── build_dataset.py
│   ├── analyze_dataset.py
│   ├── inspect_transactions.py
│   ├── inspect_categories.py
│   ├── merchant_normalizer.py
│   ├── text_cleaner.py
│   ├── llm_categorizer.py
│   ├── test_embeddings.py
│   ├── test_vector_store.py
│   ├── test_llm_rag.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── money.py
│   │
│   ├── pdf/
│   │   ├── __init__.py
│   │   └── extractor.py
│   │
│   └── parsers/
│       ├── __init__.py
│       ├── base.py
│       ├── comdirect.py
│       ├── ing.py
│       └── dispatcher.py
│
├── tests/
│
├── pyproject.toml
└── README.md
```

---

# Status

Aktueller Status:

```text
[✓] PDF-Extraktion
[✓] comdirect Parser
[✓] ING Parser
[✓] Dispatcher
[✓] Transaktionsmodell
[✓] Geldbetrag-Parsing
[✓] Transaktionstyp-Normalisierung
[✓] Interne Transfers
[✓] Darlehenszahlungen
[✓] Händler-Normalisierung
[✓] Textbereinigung
[✓] JSON-Export
[✓] Embeddings mit embeddinggemma
[✓] ChromaDB
[✓] Exakte Händlersuche
[✓] Semantische Fallback-Suche
[✓] Kategorie-Inferenz
[~] LLM-Kategorisierung
[~] RAG + LLM im Produktionsworkflow
[ ] Finanz-Chat
[ ] automatische Finanzanalyse
[ ] Sparpotenzial-Analyse
```

`[✓]` = funktioniert bzw. getestet
`[~]` = aktuell in Entwicklung
`[ ]` = geplant

---

# Kurzfassung

Finance RAG ist ein lokales System zur strukturierten Verarbeitung und intelligenten Analyse persönlicher Banktransaktionen.

Der aktuelle Schwerpunkt liegt darauf, die automatische Kategorisierung so aufzubauen, dass:

```text
historische persönliche Finanzdaten
            +
lokale Embeddings
            +
RAG
            +
lokales LLM
            =
robuste lokale Finanzanalyse
```

Dabei wird bewusst vermieden, eine immer größer werdende Sammlung manueller Händlerregeln aufzubauen.

Das langfristige Ziel ist ein vollständig lokaler Finanzassistent, der die eigenen Kontoauszüge versteht, historische Transaktionen wiederfindet und daraus nachvollziehbare Antworten und Analysen erzeugt.

```

Das kannst du direkt als `README.md` im Projektwurzelverzeichnis verwenden.
```



poetry run python src/build_dataset.py
poetry run python src/analyze_dataset.py
poetry run python src/inspect_categories.py