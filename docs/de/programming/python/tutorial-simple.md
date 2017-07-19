---
nav-title: Einfache Textanwendungen
nav-pos: 1
---
# Programmieren in Python: Einfache Textanwendungen

Die Community-Firmware verwendet eine komplexe grafische Benutzeroberfläche.
Selbst die einfachsten Programme müssen sich daher um eine grafische
Ausgabe kümmern wie im Tutorial [Die erste Anwendung](tutorial-1.md)
beschrieben.

Für sehr einfache Anwendungen und für schnelle Tests ist selbst das aber
oft unverhältnismäßig viel Aufwand. Oft möchte man nur ein einfaches
Pythonprogramm ein paar Schritte ausführen und sich dann beenden lassen.
Ein Beispiel für ein solches minimales Python-Programm ist das klassische
[Hello World](https://www.learnpython.org/en/Hello%2C_World%21):

```
print("Hallo Welt!")

```

Auf einem PC würde man so ein Programm von der Kommandozeile z.B. aus
einem Eingabefenster heraus starten:

```
C:\> python hello.py
Hallo Welt!
```

Auf dem TXT gibt es eine solche Kommandozeile nicht und man kann auch
nicht einfach irgendwo Kommandos eintippen. Aber es sind nur wenige
Handgriffe nötig, um solch eine Einfach-App zu einer echten TXT-App zu
bündeln. Unter
[/text_hello_demo](https://github.com/harbaum/cfw-apps/tree/master/packages/text_hello_demo)
finden sich fünf Dateien. Uns interessiert zunächst nur die Datei
[```hello.py```](https://github.com/harbaum/cfw-apps/blob/master/packages/text_hello_demo/hello.py). Sie
enthält ein sehr einfaches Python-Skript, das lediglich ein paar
einfache Bildschirmausgaben per print()-Anweisung macht.

Wenn man all diese Dateien in ein
[ZIP-Archiv](https://github.com/harbaum/cfw-apps/raw/master/packages/text_hello_demo.zip) einpackt, dann lässt sich dieses Archiv wie eine normale TXT-App
installieren und ausführen. Auf dem TXT erscheint dann eine App namens
```Hello```, die man wie üblich starten kann. Auf dem TXT-Bildschirm
erscheint dann folgende Ausgabe:

![Hello](../../../media/examples/python/tutorial-simple/hello.png)

Diese fünf Dateien lassen sich leicht als Basis für eigene Programme nutzen. Dazu muss man nur wenige Dinge tun:

  1. Die Datei ```hello.py``` muss durch eine eigene Datei ersetzt werden. Der Name ist dabei frei wählbar, er muss nur auf ```.py``` enden. Die Original-```hello.py``` muss dann entfernt werden.
  1. In der Datei ```manifest``` muss der Eintrag ```name``` angepasst werden. Der Name sollte kurz und aussagekräftig sein, er erscheint später unter dem Icon.
  1. In der Datei ```manifest``` muss der Eintrag ```uuid``` angepasst werden. Hier muss eine beliebige neue UUID erzeugt und eingetragen werden. Eine UUID kann man sich z.B. [online](https://www.uuidgenerator.net/) erzeugen.
  1. Alle fünf Dateien müssen wieder in ein ZIP-Archiv eingepackt werden.

Das ist schon alles.

**Hier geht es weiter**: [Programmieren in Python: Die erste Anwendung](tutorial-1.md), [Programmieren in Python: Entwicklung](tutorial-2.md)
