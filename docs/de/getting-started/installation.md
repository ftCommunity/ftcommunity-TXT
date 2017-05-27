---
nav-title: Installation
---
# Voraussetzungen

* Eine MicroSD-Karte (microSD oder microSDHC, d.h. bis 32GB. **Größere Karten werden vom TXT unter Umständen nicht erkannt**). Die Größe ist nicht so wichtig (_die Community-Firmware braucht weniger als 120MB_). **Bsp.:**Auf eine **2GB** microSD-Karten würden **1800** Programme und das Betriebssystem darauf passen!

* Eine Möglichkeit, ZIP-Dateien auf der MicroSD-Karte auszupacken.

# Installation

1. Zunächst musst Du die Standardfirmware des TXT auf Version 4.2.4 upgraden &mdash; das geht mit RoboPro. Die aktuelle Version von RoboPro findest Du hier: http://www.fischertechnik.de/ResourceImage.aspx?raid=10274

1. Anschließend musst Du den Bootloader freischalten, wie in der Anleitung von Fischertechnik erklärt: http://www.fischertechnik.de/ResourceImage.aspx?raid=10278

1. Danach lädst Du hier https://github.com/ftCommunity/ftcommunity-TXT/releases/latest das ZIP-Archiv mit der Community-Firmware herunter (der Link steht unten auf der Seite, aktuell ist die Datei "ftcommunity-txt-0.9.2.zip")

1. Endpacke das Archiv  und kopierst die drei enthaltenen Dateien auf die microSD-Karte (_Im FAT32 formatier_).

1. Jetzt setzt du nur noch die microSD-Karte in den TXT ein und drückst den Startknopf. Nach kurzer Zeit sollte ein gelber Ladebalken und im unteren Bereich des Bildschirms die Aufschrift "Community Edition" erscheinen:

 ![Bootupscreen](https://raw.githubusercontent.com/ftCommunity/ftcommunity-TXT/master/board/fischertechnik/TXT/rootfs/etc/ftc-logo.png)

 (_Der erste Start kann eine Weile dauern, spätere Starts gehen dann etwas schneller._)
