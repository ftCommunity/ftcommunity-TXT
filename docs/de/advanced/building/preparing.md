---
nav-title: Vorbereitung des TXTs
nav-pos: 2
---

## Update auf die neueste offizielle Firmware für TXT-Controller
Der erste Schritt sollte sein, die offizielle Firmware auf die neueste Version zu aktualisieren. Der einfachste Weg, dies zu erreichen, besteht darin, ROBOPro auf die neueste Version zu aktualisieren und die integrierte Firmware-Update-Methode zu verwenden.

Die neueste Version von ROBOPro finden Sie auf der fischertechnik-Website unter “Service” -> “Downloads” -> “ROBOTICS” -> Section “ROBOPro” ([direkter Link](https://www.fischertechnik.de/de-de/service/downloads/robotics)).

Die neueste Version, die am 16. Juni 2018 verfügbar war, war Version 4.2.4.

[direkter Download](https://www.fischertechnik.de/-/media/fischertechnik/fite/service/downloads/robotics/robo-pro/documents/update-robopro.ashx) (ca. 222 MB)

## Aktivieren Sie das Booten von einer Micro-SD-Karte

### Mit ROBOPro 4.2.4 oder höher
Ab ROBOPro 4.2.4 kann das Booten von der SD-Karte durch Befolgen der Anweisungen von Fischertechnik aktiviert werden
* [Englisch](https://www.fischertechnik.de/-/media/fischertechnik/fite/service/downloads/robotics/txt-controller/documents/activation_bootloaders_english.ashx)
* [Deutsch](https://www.fischertechnik.de/-/media/fischertechnik/fite/service/downloads/robotics/txt-controller/documents/freischaltung_des_bootloaders_deutsch.ashx)

Zusammenfassung:

* Stellen Sie eine Netzwerkverbindung zum Verbinden mit dem TXT per SSH her (siehe [[Prerequisites]] für IP-Adressen)
    * Benutzername: ROBOPro
    * Passwort: ROBOPro

* Führen Sie den folgenden Befehl aus: 

    ``````````
    sudo /usr/sbin/boot_sd_nand
    ``````````

### Für ältere Versionen von ROBOPro
Wenn Sie eine ältere Version von ROBOPro verwenden, muss das Booten von der SD-Karte manuell als Root-Benutzer auf dem TXT aktiviert werden.
#### Root-Passwort des TXTs holen
Hintergrund: Das Root-Passwort für das eingebettete Linux auf dem TXT-Controller wird zufällig bei der Herstellung festgelegt. Um die Änderungen vorzunehmen, die das Booten der Community-Firmware von der microSD ermöglichen, ist der Root-Zugriff auf den TXT erforderlich - daher benötigt man das Passwort.

Das Passwort kann, nachdem root-password display aktiviert wurde, vom TXT auf seinem Info-Bildschirm angezeigt werden:

* Stellen Sie eine Netzwerkverbindung zum Verbinden mit dem TXT per SSH her (siehe [[Prerequisites]] für IP-Adressen)
    * Benutzername: ROBOPro
    * Passwort: ROBOPro

* Führen Sie den folgenden Befehl aus: 
    ``````````
    echo "showroot=1" > .TxtAccess.ini
    ``````````

* Starten Sie den TXT neu

Jetzt können Sie das root-Passwort in “Settings” -> “Info” -> “Root password” lesen.

Weitere Details zur Aktivierung / Deaktivierung der root-Passwortanzeige finden Sie auf der fischertechnik-Website unter “Service” -> “Downloads” -> “ROBOTICS” -> Section “TXT Controller” -> “Security Inform / ROOT Zugang” ([Direkter Link](https://www.fischertechnik.de/de-de/service/downloads/robotics))

#### Ändern der Boot-Optionen des TXTs


Bevor Sie die ftcommunity-Firmware ausführen können, müssen Sie den TXT umkonfigurieren, um das Starten einer Firmware von der SD-Karte zu ermöglichen. Dies muss nur einmal durchgeführt werden.

**Achtung: Dies ist der einzige Schritt, bei dem der TXT beschädigt werden könnte. Stellen Sie daher sicher, dass Sie die Befehle genau wie gezeigt ausführen.**

* Melden Sie sich per SSH am TXT an (siehe oben unter "Root-Passwort des TXTs holen")
  * Nutzername: root
  * Passwort: Das oben erhaltene TXT-Root-Passwort
* Führen Sie dann die folgenden vier Befehle aus (beginnend mit fw_setenv und einschließlich " am Ende):

```
fw_setenv bootcmd "run sdboot;run nandboot"
```

Hinweis: Vergleichen Sie die Zeile sorgfältig und führen Sie diesen Befehl nicht aus, bis er genau der Zeile darüber entspricht. Wenn Sie 'bootcmd' mit defekten Einstellungen ändern, wird Ihr TXT gebrickt und Sie müssen den seriellen Konsolenzugriff auf den TXT einrichten, um die Bootloader-Konfiguration zu reparieren und den TXT wieder nutzbar zu machen.
