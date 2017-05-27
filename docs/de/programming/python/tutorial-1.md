---
nav-title: The First App
nav-pos: 1
---
# Programmieren in Python: die erste Application

Dieses Tutorial soll den Einstieg erleichtern und die Grundschritte erklären!

Eine Application besteht aus **3** Teilen:

 * Das **Programm**. Dies ist normalerweise ein Python-Script. Es könnte aber auch jede beliebige andere Programmiersprache sein Seit [Python](https://www.python.org) der Standart für die TXT-Programmierung ist wird dieses Tutorial sich ausschließlich darauf beziehen!

 * Ein **Manifest**. Das ist eine kleine Datei die Den Programmnamen, Autor, ... angibt

 * Ein **Icon**. Dieses sollte ein PNG-Bild sein mit 64x64 Pixeln. Es wird sowohl auf dem Betriebssystem als auch auf der Weboberfläche verwendet!

## Das Programm

TDas Programm kann irgendeine ausfühbare (_vom TXT_) Datei sein. Solange das Programm vom Launcher (_Startbildschirm_) ausgeführt wird erwartet der Benutzer eine Anzeige des Programms. Deshalb sollte das Programm zumindestens eine minimalistische Oberfläche enthalten.

Aktuell benützen alle Applicationen das [Qt4-Framework](http://www.qt.io/) für ihre Anzeigen. 
Eine minimale Anwendung kuckt so aus:
```
#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from TouchStyle import *

class FtcGuiApplication(TouchApplication):
    def __init__(self, args):
        TouchApplication.__init__(self, args)

        # Erstelle eine leeres Hauptfenster
        w = TxtWindow("Test")
        w.show()
        self.exec_()        

if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
```

Speichere diese Datei unter [`Test.py`](https://raw.githubusercontent.com/ftCommunity/ftcommunity-apps/master/packages/app_tutorial_1/test.py)

**Erkärung:**
Dieses Programm refenreziert die Klasse TouchApplication, welche die Fenster verwaltet. Jene erstellt ein Fenster und stellt sie dem Nutzer bereit, solange die Application nicht geschlossen wird!

## Das Manifest

Das Manifest ist eine Textdatei mit den **Eigenschaften** der Application

```
[app]
name: Test
category: Tests
author: Joe Developer
icon: icon.png
desc: TXT app tutorial #1
url: https://github.com/ftCommunity/ftcommunity-TXT/wiki/FTC-FW-App-Tutorial-1
exec: test.py
managed: yes
uuid: 191fe5a6-313b-4083-af65-d1ad7fd6d281
version: 1.0
firmware: 0.9.2
```

**Notwendigen Felder:**

 * **name** ist der Name der Application der im Launcher  und im Webinterface verwendet wird (_5-15 Zeichen lang_).
 * **icon** ist der Name des Icons. Normalerweise heißt es "icon.png"
 * **desc** ist eine **kurze** Beschreibung (_aktuell nur in der Weboberfläche verwendet_)
 * **exec** ist der Name des Scripts (_Im Beispiel "Test.py"_)
 * **uuid** ist eine [eindeutige identifikationsnummer](https://de.wikipedia.org/wiki/Universally_Unique_Identifier) die am TXT verwendet wird, damit es keine Konfusionen zwischen Applicationsdaten gibt.Diese können [hier](https://www.famkruithof.net/uuid/uuidgen) generiert werden.
 * **managed** ist aktuell unbenutzt (_sollte aber trotzdem auf "**yes**" gesetzt werden._). Aktuell gibt es nur an ob eine Benutzeroberfläche vorhanden ist. (_Später kann damit das Framework angegeben werden_)
 * **version** ist die Verisionsnummer der Application.
 * **firmware** ist die Firmwarenummer für die die Application getestet wurde.

**Optionale Felder:**

 * **category** wird benutzt um die Applicationen zu Ordnern zusammenzufassen
 * **author** ist der Autor
 * **url** ist der Link zu einer Webseite (_zu der du über das Webinterface gelangen kann_)

Speichere diese Datei als [`manifest`](https://raw.githubusercontent.com/ftCommunity/ftcommunity-apps/master/packages/app_tutorial_1/manifest)

# Das Icon

Das Icon kann jede datei im JPEG- oder PNG-Format sein. Es muss eine Auflösung von **64x64** Pixeln haben

![icon.png](https://raw.githubusercontent.com/ftCommunity/ftcommunity-apps/master/packages/app_tutorial_1/icon.png)

Ein Beispiel kann [hier](https://raw.githubusercontent.com/ftCommunity/ftcommunity-apps/master/packages/app_tutorial_1/icon.png) gefunden werden.

# Verpacken

Jetzt hast du 3 wichtige Datein

 * "Test.py", das Programm
 * "manifest", die Applicationseigenschaften
 * "icon.png" Das Icon

Um diese Datein auf den TXT zu bringen muss ein ZIP-Archiv erstellt werden.(_Z.B. mit [7-Zip](http://www.7-zip.de/download.html_) Alle 3 Datein **müssen** im Hauptordner liegen da sie der TXT sonst **nicht** findet! 

Ein Archiv der Demo ist auch [verfügbar](https://github.com/ftCommunity/ftcommunity-apps/raw/master/packages/app_tutorial_1.zip)

# Hochladen zum TXT

Jetzt nütze deinen PC mit der [Weboberfläche]() des TXTs

![tut1_img1.jpg](tut1_img1.jpg)

Verwende den Dateidialog und bestätige mit ENTER:

![tut1_img2.jpg](tut1_img2.jpg)

Die Application ist nun sichtbar!

![tut1_img6.jpg](tut1_img6.jpg)

Sie ist nun auch im Webinterface zu sehen:

![tut1_img3.jpg](tut1_img3.jpg)

Es zeigt auch Details des Manifests

![tut1_img5.jpg](tut1_img5.jpg)

Natürlich kann die Application von hieraus auch gelöscht werden.

**Fahre fort**: [Programmieren in Python: Entwicklung](tutorial-2.md)
