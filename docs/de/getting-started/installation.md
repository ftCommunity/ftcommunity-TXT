---
nav-title: Installation
---
# Voraussetzungen

* Eine MicroSD-Karte (microSD oder microSDHC, d.h. bis 32GB. **Größere Karten werden vom TXT unter Umständen nicht erkannt**). Die Größe ist nicht so wichtig (die Community-Firmware braucht weniger als 100MB). **Bsp.:** auf einer **2GB** großen MicroSD-Karte hätten ca. **1800** Programm (bei 1MB pro Programm) und das Betriebssytem platz.

* Eine Möglichkeit, ZIP-Dateien auf der MikroSD-Karte auszupacken.

# Installation

1. Zunächst musst Du die Standardfirmware des TXT auf Version 4.2.4 upgraden (_das geht mit RoboPro_). Die aktuelle Version von RoboPro findest Du hier: [http://www.fischertechnik.de/ResourceImage.aspx?raid=10274](http://www.fischertechnik.de/ResourceImage.aspx?raid=10274)

1. Anschließend musst Du den Bootloader freischalten, wie in der Anleitung von Fischertechnik erklärt: [http://www.fischertechnik.de/ResourceImage.aspx?raid=10278](http://www.fischertechnik.de/ResourceImage.aspx?raid=10278)

1. Danach lädst Du hier [https://github.com/ftCommunity/ftcommunity-TXT/releases/latest](https://github.com/ftCommunity/ftcommunity-TXT/releases/latest) das ZIP-Archiv mit der Community-Firmware herunter (_der Link steht unten auf der Seite, aktuell ist die Datei "ftcommunity-txt-0.9.3.zip"_)

1. Du packst das Archiv aus und kopierst die drei enthaltenen Dateien auf eine FAT32 formatierte MicroSD-Karte.

1. Jetzt setzt Du nur noch die microSD-Karte in den TXT ein und drückst den Startknopf. Nach kurzer Zeit erscheint ein gelber Ladebalken und im unteren Bereich des Bildschirms die Aufschrift "Community Edition":

 ![Bootupscreen](https://raw.githubusercontent.com/ftCommunity/ftcommunity-TXT/master/board/fischertechnik/TXT/rootfs/etc/ftc-logo.png)

 (_Der erste Start kann eine Weile dauern, spätere Starts gehen dann etwas schneller._)
