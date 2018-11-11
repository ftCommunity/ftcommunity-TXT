---
nav-title: Ein Modell steuern
nav-pos: 3
---
# Programmierung in Python: ein Modell steuern

Die vorigen Tutorials haben gezeigt, wie man eine erste App entwickelt ([Python: Die erste Anwendung)](tutorial-1.md)) und wie man sich die Entwicklung erleichtern kann ([Python: Entwicklung](tutorial-2.md)). In diesem Teil wird jetzt gezeigt, wie man ein Modell ansteuert. 
Den Quellcode für die Beispiele aus diesem Tutorial findest du in [Github](https://github.com/ftCommunity/ftcommunity-TXT/tree/master/docs/_includes/examples/python/tutorial-3).

## Die benötigten Bibliotheken einbinden

Die Community-Firmware enthält das [Modul ftrobopy](https://github.com/ftrobopy/ftrobopy), das die Anbindung von Python an die Fischertechnik-spezifischen Ein- und Ausgänge des TXT ermöglicht. Das Modul kann einfach in das Programm aus Tutorial #1 eingefügt werden: 


```
{% include examples/python/tutorial-3/app_tutorial3_1.py %}
```

Wenn du diese App auf deinem TXT wie in Tutorial #1 beschrieben startest, wird das Ergebnis so aussahen wie dort, nur der Name der App ist natürlich anders. Wenn es das macht und keine Fehlermeldung erscheint, dann hat sich die App erfolgreich mit dem Server-Prozess auf dem TXT verbunden und hat Zugriff auf die Ein- und Ausgänge des TXT.


Für die Ausgabe der Fehlermeldung verwenden wir QLabel. Mehr Informationen zu diesem Thema findest du (auf Englisch) in den [PyQt-Tutorials](http://www.tutorialspoint.com/pyqt/index.htm). Auch die Benutzung von [QLabel](http://www.tutorialspoint.com/pyqt/pyqt_qlabel_widget.htm) wird dort erklärt. Die dort angegebenen Beispiele unterscheiden sich etwas von unseren Beispielen, weil wir hier ein spezielles Fensterformat für den TXT verwenden. Die größten Unterschiede beziehen sich nur auf das Hauptfenster. Die Verwendung der Widgets unterscheidet sich kaum zwischen PC und TXT. QLabel z.B. funktioniert auf dem TXT genauso wie auf dem PC.

## Einen Ausgang steuern


Natürlich wollen wir, dass unsere kleine App etwas Schönes macht. Bitte schließe eine Lampe an den Ausgang O1 deines TXT an. Du kannst zum Beispiel das Modell "Fußgänger-Ampel aus dem [ROBOTICS TXT Discovery Set](https://www.fischertechnik.de/en/products/playing/robotics/524328-robotics-txt-discovery-set) verwenden.

Wir programmieren einen Button auf dem TXT-Bildschirm, mit dem man die Lampe an- und ausschaltet. Dazu initialisieren wir die Schnittstellen für die Ausgänge und setzen sie auf vernünftige Werte. Außerdem bauen wir einen Button in die GUI ein:


```
{% include examples/python/tutorial-3/app_tutorial3_2.py %}
```

Wenn du die App auf dem TXT startest, siehst du einen Button auf dem Bildschirm. Damit er auch etwas macht, müssen wir  den Button mit einer Funktion verbinden:


```
{% include examples/python/tutorial-3/app_tutorial3_3.py %}
```


Die fertige App ermöglicht dir, die Lampe ein- und auszuschalten, indem sie den PWN-Wert auf 512 (EIN) oder 0 (AUS) setzt. Dazu haben wir einen Handler eingebaut, der jedes Mal aufgerufen wird, wenn der Benutzer den Button drückt. Damit die Variable ``txt`` bei allen Funktionen in der Klasse verfügbar ist, setzen wir ``self`` davor. Mehr über die Verwendung des Keywords ``self`` und Objektorientierung in Python im Allgemeinen erfährst du zum Beispiel in diesem [Tutorial](http://www.tutorialspoint.com/python/python_classes_objects.htm) (auf Englisch).


## Einen Eingang lesen

Nachdem wir jetzt einen der Ausgänge steuern können, wollen wir auch einen Eingang einlesen. Bitte schließe einen Taster an den Eingang I1 des TXT an.

Es ist nicht möglich, einen Eingang selbst eine Nachricht senden zu lassen. Daher müssen wir regelmäßig den Status des Eingangs abfragen. Die einfachsten Programme würden in einer Dauerschleife fortwährend den Input einlesen und auf Änderungen prüfen. Da die komplette Qt-GUI parallel laüft und auch versorgt werden muss, können wir nicht einfach den Prozess durch eine Dauerschleife übernehmen. Stattdessen müssen wir die Abfrage parallel zu der Verarbeitung der GUI durchführen.

Für immer wiederkehrende Aufgaben stellt Qt Timer zur Verfügung. Ähnlich wie der Button ruft auch der Timer einen Event-Handler auf, der die Aufgabe erledigt. Wir bauen also einen QTimer ein, der 10mal in der Sekunde, also alle 100ms feuert und dann den Status des Inputs liest. Jedes Mal, wenn der Input seinen Zustand zwischen 1 und 0 wechselt, ändern wir den Zustand der Lampe:


```
{% include examples/python/tutorial-3/app_tutorial3_4.py %}
```

Mit dieser App ändert die Lampe ihren Zustand, wenn du den Button auf dem Bildschirm oder den echten Taster am Input I1 drückst.

![tut3_img1](../../../en/programming/python/tut3_img1.png)


# Die App auf dem PC ausführen

Wie im Tutorial [Python: Entwicklung](tutorial-2.md) erklärt, können TXT Apps auch auf dem PC ausgeführt werden. Dabei können auch die Ein- und Ausgänge auf dem TXT genutzt werden. Eigentlich wurde das Modul ftrobopy genau für diesen Zweck geschrieben. Als erstes musst du die Datei ``ftrobopy.py`` in das gleiche Verzeichnis wie ``TouchStyle.py`` aus dem vorigen Tutorial kopieren.
Nun müssen wir der App erkären, wie sie sich vom PC mit dem TXT verbindet, um dessen Ein- und Ausgänge zu verwenden. Dafür musst du in deinem Programm diese Zeile:

```
            self.txt = ftrobopy.ftrobopy("localhost", 65000) # connect to TXT's IO controller
```

durch diese ersetzen:

```
            self.txt = ftrobopy.ftrobopy("192.168.7.2", 65000) # connect to TXT's IO controller
```

wenn dein TXT über USB verbunden ist.

Es ist ziemlich unbequem, diese Zeile jedes Mal zu ändern, wenn du für den App-Start zwischen PC und TXT wechseln willst. Die folgende Version funktioniert für beide Fälle:

```
        txt_ip = os.environ.get('TXT_IP')
        if txt_ip == None: txt_ip = "localhost"
        try:
            txt = ftrobopy.ftrobopy(txt_ip, 65000)
        except:
            txt = None
```

Der Code versucht, die Umgebungsvariable `TXT_IP` zu lesen. Wenn diese Variable existiert, versucht die App sich mit dem TXT zu verbinden. Wenn sie nicht existiert, dann wird die Standardeinstellung "localhost" verwendet, d.h. die App merkt, dass sie auf dem TXT lokal läuft und nutzt die Ein- und Ausgänge direkt.

Auf dem PC musst du diese Umgebungsvariable setzen wie hier unter Linux:


```
$ export TXT_IP=192.168.7.2
```

Unter Linux kannst du diesen Befehl in der Datei `.bashrc` in deinem Home-Verzeichnis setzen, so dass du dich in Zukunft nicht mehr darum kümmern musst. 
Die App läuft jetzt auf dem TXT und auf dem PC. **Wenn du die App auf dem PC ausführen willst, musst du auf deinem TXT die App FT-GUI starten.**
Das vollständige Programm sieht jetzt so aus:

```
{% include examples/python/tutorial-3/app_tutorial3_5.py %}
```
