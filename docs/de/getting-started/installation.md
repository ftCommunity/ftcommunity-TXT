---
nav-title: Installation
---
# Voraussetzungen

* Eine MicroSD-Karte (microSD oder microSDHC, d.h. bis 32GB. **Größere Karten werden vom TXT unter Umständen nicht erkannt**). Die Größe ist nicht so wichtig (die Community-Firmware braucht weniger als 100MB). **Bsp.:** auf einer **2GB** großen MicroSD-Karte hätten ca. **1800** Programm (bei 1MB pro Programm) und das Betriebssytem Platz.

* Eine Möglichkeit, ZIP-Dateien auf der MicroSD-Karte auszupacken.

# Installation

1. Zunächst musst du die Standardfirmware des TXT auf Version 4.2.4 upgraden (_das geht mit RoboPro_). Die aktuelle Version von RoboPro findest du [hier bei Fischertechnik](https://www.fischertechnik.de/-/media/fischertechnik/fite/service/downloads/robotics/robo-pro/documents/01-update-robopro-424.ashx)

1. Anschließend musst du den Bootloader freischalten, wie in der [Anleitung von Fischertechnik](https://www.fischertechnik.de/-/media/fischertechnik/fite/service/downloads/robotics/txt-controller/documents/freischaltung_des_bootloaders_deutsch.ashx) erklärt.

1. Danach lädst du hier [https://github.com/ftCommunity/ftcommunity-TXT/releases/latest](https://github.com/ftCommunity/ftcommunity-TXT/releases/latest) das ZIP-Archiv mit der Community-Firmware herunter (_der Link steht unten auf der Seite, aktuell ist die Datei "ftcommunity-txt-0.9.3.zip"_)

1. Du packst das Archiv aus und kopierst die drei enthaltenen Dateien auf eine FAT32 formatierte MicroSD-Karte.

1. Jetzt setzt du nur noch die MicroSD-Karte in den TXT ein und drückst den Startknopf. Nach kurzer Zeit erscheint ein gelber Ladebalken und im unteren Bereich des Bildschirms die Aufschrift "Community Edition":

 ![Bootupscreen](https://raw.githubusercontent.com/ftCommunity/ftcommunity-TXT/master/board/fischertechnik/TXT/rootfs/etc/ftc-logo.png)

 (_Der erste Start kann eine Weile dauern, spätere Starts gehen dann etwas schneller._)
