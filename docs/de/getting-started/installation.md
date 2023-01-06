---
nav-title: Installation
nav-pos: 1
---
# Voraussetzungen

* Eine MicroSD-Karte (microSD oder microSDHC, d.h. bis 32GB. **Größere Karten werden vom TXT unter Umständen nicht erkannt**). Die Größe ist nicht so wichtig (die Community-Firmware braucht weniger als 100MB). **Bsp.:** auf einer **2GB** großen MicroSD-Karte hätten ca. **1800** Programm (bei 1MB pro Programm) und das Betriebssytem Platz.

* Eine Möglichkeit, ZIP-Dateien auf der MicroSD-Karte auszupacken.

# Installation

1. Zunächst musst du die Standardfirmware des TXT auf Version 4.2.4 oder neuer upgraden (_das geht mit RoboPro_). Wir empfehlen die aktuellste Version der Standardfirmware (derzeit Version 4.4.4). Die aktuelle Version von RoboPro findest du [hier bei Fischertechnik](https://www.fischertechnik.de/-/media/fischertechnik/fite/service/downloads/robotics/robo-pro/documents/update-robopro.ashx).

1. Anschließend musst du den Bootloader freischalten. Mit der Standard-Firmware 4.4.3 aktivierst du dazu unter _Einstellungen / Sicherheit_ den Schalter _Boot SD_. Falls du noch die Standard-Firmware 4.2.4 benutzt, folge den Anweisungen in der  [Anleitung von Fischertechnik](https://www.fischertechnik.de/-/media/fischertechnik/fite/service/downloads/robotics/txt-controller/documents/freischaltung_des_bootloaders_deutsch.ashx).

1. Auf deinem Computer lädst du dann hier [https://github.com/ftCommunity/ftcommunity-TXT/releases/latest](https://github.com/ftCommunity/ftcommunity-TXT/releases/latest) das ZIP-Archiv mit der Community-Firmware herunter (_aktuell ist die Datei "ftcommunity-txt-0.9.5.zip"_) und speicherst die Datei ab.

1. Du packst das Archiv aus (mit einem Zip-Programm auf deinem Computer) und kopierst die drei enthaltenen Dateien auf eine FAT32 formatierte MicroSD-Karte.

1. Jetzt setzt du nur noch die MicroSD-Karte in den TXT ein und drückst den Startknopf. Nach kurzer Zeit erscheint ein gelber Ladebalken und im unteren Bereich des Bildschirms die Aufschrift "Community Edition":

 ![Bootupscreen](https://raw.githubusercontent.com/ftCommunity/ftcommunity-TXT/master/board/fischertechnik/TXT/rootfs/etc/ftc-logo.png)

Der erste Start kann eine Weile dauern, weil die Karte erst initialisiert wird. Spätere Starts gehen dann schneller.

 
# Aktualisierung
 
Um eine SD-Karte mit einer bestehenden Version auf die neueste Version der CFW zu aktualisieren, entnimmst du sie dem TXT und steckst sie in den SD-Leser deines Computers. Jetzt ersetzt du die folgenden drei Dateien mit der aktuellen Version, die du aus dem heruntergeladenem Archiv auspackst:

    uImage
    am335x-kno_txt.dtb
    rootfs.img
    
Apps und Daten, die sich schon auf der SD-Karte befinden, bleiben erhalten.

