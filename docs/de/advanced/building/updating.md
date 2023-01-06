---
nav-title: Aktualisierung
nav-pos: 4
---
# Letzte Änderungen holen und neuen Build erstellen
Um Änderungen aus der Haupt-Git-Repository von ftcommunity-TXT abzurufen, musst du deine lokale Kopie des Repositorys aktualisieren und das Firmware-Paket neu erstellen. (Dies ist viel schneller als der ursprüngliche Build, da nur die Änderungen heruntergeladen werden und nur geänderte Teile neu kompiliert werden).
## Aktualisieren des lokalen Klons des Git-Repositorys
Wechsele in das Verzeichnis mit der lokalen Kopie der Repository, lade die Änderungen herunter und integriere sie:
`cd ~/ftcommunity-TXT` (oder wo auch immer es sich befindet; Dies ist der Pfad, wenn du dieser Beschreibung von Anfang an folgst.)  
`git pull`

## Erneutes Erstellen der ftcommunity-TXT-Firmware
`make fischertechnik_TXT_defconfig  `  
`make  `

*Hinweis: Wenn das System nicht funktioniert, versuche
`make clean`  
bevor du mit
`make fischertechnik_TXT_defconfig`  
`make  `
weitermachst.

Beachte, dass in diesem Fall das gesamte System neu aufgebaut wird - das dauert eine Weile (zur Orientierung: ~ 4 Stunden auf meinem Intel Core i5 Mobile der zweiten Generation mit 2,5 GHz unter Verwendung von Ubuntu in einer VirtualBox-Umgebung)

# Übertragen der Build-Ausgabe auf die SD-Karte


## Kopiere die Dateien von deinem Computer
Entnimm die SD-Karte aus dem TXT, lege sie in einen SD-Kartenleser in deinem Computer und ersetze die folgenden drei Dateien durch die neueste Version:
- uImage
- am335x-kno_txt.dtb
- rootfs.img

## Update ohne die SD-Karte zu entfernen
... ohne die Karte aus dem TXT zu entfernen, indem du das System ersetzt, während es läuft! (yup, das ist in diesem Fall möglich ...)

Wichtig: Starte die TXT-Community-Firmware.

Für diesen Update-Pfad musst du zuerst ein root-Passwort festlegen. Siehe [TXT-Passwort-Richtlinie](../password-policy#enabeling-the-root-user).

Von einem Linux-System (oder mit einem anderen SSH-Client), auf der Konsole mit dem Arbeitsverzeichnis ftcommunity-TXT-repository (in den hier verwendeten Beispielen: ~/ftcommunity-TXT) und der bereitgestellten IP 192.168.7.2 deines TXTs:

`ssh root@192.168.7.2 mv /media/sdcard/root.img /media/sdcard/root.old`  
`scp output/images/uImage output/images/am335x-kno_txt.dtb output/images/rootfs.img root@192.168.7.2:/media/sdcard/boot`  

Starte nun den TXT neu. Stelle sicher, dass du den TXT ausschaltest, indem du den blauen Ein- / Ausschalter drückst, bis "Herunterfahren ..." auf dem Display angezeigt wird. Lasse den Knopf los, wenn du den Text siehst, ansonsten wird er einige Sekunden später auf die harte Tour ausgeschaltet.

