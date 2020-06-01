---
nav-title: Erstellung
nav-pos: 3
---

Normalerweise musst du die Firmware nicht selbst erstellen. Stattdessen möchtest du wahrscheinlich nur [vorgefertigte Versionen](https://github.com/ftCommunity/ftcommunity-TXT/releases) herunterladen.

## Einrichten eines Build-Systems

### Grundlegendes Linux / VirtualBox-Setup
Du benötigst jetzt eine Art Linux-System, um den Build-Prozess auszuführen.

Ich benutzte [Ubuntu Desktop x64, Version 15.10](http://www.ubuntu.com/download/desktop) installiert in einer [VirtualBox](https://www.virtualbox.org/wiki/Downloads), die auf Windows 10 Pro x64 als Host ausgeführt wird.  
Die folgenden Schritte wurden unter diesen Bedingungen getestet.

Achte beim Erstellen einer neuen virtuellen Maschine darauf, genügend virtuellen Festplattenspeicher zuzuweisen (8 GB ist sicherlich nicht genug - ich habe 32 GB Speicherplatz und 3072 MB RAM verwendet).

### Installieren der zum Erstellen erforderlichen Tools
Alle weiteren Schritte werden auf dem Linux-System in VirtualBox ausgeführt.

Der Build-Prozess erfordert Mercurial, um die Quelldateien für die Firmware zu erhalten, ist git erforderlich.

Öffne ein Terminal (auf Ubuntu: klicke mit der rechten Maustaste auf den Desktop und wähle "Terminal öffnen") und installiere die fehlenden Pakete:

``````````sudo apt-get install git``````````  
``````````sudo apt-get install mercurial``````````  
*(Hinweis: Dies sind die Befehle für Ubuntu und andere Distributionen, die apt als Paketverwaltungstool verwenden. Deine Distribution verwendet möglicherweise andere Tools, um fehlende Pakete zu installieren.)*

## Aufbau der ftcommunity-TXT-Firmware aus den Quellen
Für alle weiteren Schritte wird vorausgesetzt, dass wir im Home-Verzeichnis ~ des Benutzers beginnen:  
``````````cd ~``````````  
*Hinweis: Deine lokale Kopie des Git-Repositorys befindet sich also im Verzeichnis ~/ftcommunity-TXT(=/home/[INDIVIDUELLER_BENUTZERNAME]/ftcommunity-TXT).*

Hole den Quellcode der ftcommunity-TXT-Firmware aus der git-Repository:
``````````git clone https://github.com/ftCommunity/ftcommunity-TXT.git``````````

Dies erstellt ein neues Verzeichnis mit dem Namen ftcommunity-TXT im aktuellen Verzeichnis (= home).  
Wechsle in dieses Verzeichnis:
``````````cd ftcommunity-TXT``````````

Starte nun den Build-Prozess
``````````make  ``````````
(Beim ersten Lauf dauert dies mehrere Stunden, abhängig von der CPU- und der Download-Geschwindigkeit)

Achtung: Der Internetzugang ist während des Buildprozesses permanent erforderlich, da weitere Dateien (mehrere Gigabyte) heruntergeladen werden müssen.
Wenn du einen Offline-Build erstellen möchtest, verwende
``make source  ``  
im Ordner ``buildroot`` vor dem eigentlichen ``make`` im Hauptordner.  

### Nebenbemerkung - Den Build-Prozess beschleunigen
Um den Prozess zu beschleunigen, kannst du den Build-Prozess starten, indem du den eigentlichen Build-Prozess mit
``````````BR2_JLEVEL=$(($(nproc)+1)) make``````````  
anstelle des einfachen “make” startest.

### Nebenbemerkung - Fehlende i2c-Tools
Bei meinem ersten Versuch ist der Build-Prozess fehlgeschlagen, weil i2c-tools-3.1.2.tar.bz2 nicht erhalten werden konnte. Wenn das geschieht, wird der Buildprozess beendet. Du kannst dann versuchen, die Datei manuell herunterzuladen:  
``````````cd ~/ftcommunity-TXT/dl``````````  
``````````wget http://sources.buildroot.net/i2c-tools-3.1.2.tar.bz2``````````

Starte anschließend den Build-Prozess neu - er wird dort fortgesetzt, wo er aufgehört hat:
``````````cd ~/ftcommunity-TXT``````````  
``````````make  ``````````

### Nebenbemerkung - Weitere Details zum Erstellen eingebetteter Systeme auf der Basis von Buildroot (wie der TXT-Firmware)
Weitere Details zum Aufbau eingebetteter Systeme basierend auf Buildroot findest du [hier](https://buildroot.org/downloads/manual/manual.html#_general_buildroot_usage).
