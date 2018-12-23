---
nav-title: Aktualisierung
nav-pos: 4
---
# Letzten Änderungen holen und neuen Build machen
Um Änderungen aus der Haupt-Git-Repository von ftcommunity-TXT abzurufen, müssen Sie Ihre lokale Kopie der Repositorys aktualisieren und das Firmware-Paket neu erstellen. (Dies ist viel schneller als der ursprüngliche Build, da nur die Änderungen heruntergeladen werden und nur geänderte Teile neu kompiliert werden).
## Aktualisieren des lokalen Klons der Git-Repository
Wechseln Sie in das Verzeichnis mit der lokalen Kopie der Repository, laden Sie die Änderungen herunter und integrieren Sie sie:
`cd ~/ftcommunity-TXT` (oder wo auch immer es sich befindet; Dies ist der Pfad, wenn Sie dieser Beschreibung von Anfang an folgen.)  
`git pull`

## Erneutes Erstellen der ftcommunity-TXT-Firmware
`make fischertechnik_TXT_defconfig  `  
`make  `

*Hinweis: Wenn das System nicht funktioniert, versuchen Sie
`make clean`  
bevor sie mit
`make fischertechnik_TXT_defconfig`  
`make  `
weitermachen.

Beachten Sie, dass in diesem Fall das gesamte System neu aufgebaut wird - das dauert eine Weile (zur Orientierung: ~ 4 Stunden auf meinem Intel Core i5 Mobile der zweiten Generation mit 2,5 GHz unter Verwendung von Ubuntu in einer VirtualBox-Umgebung)

# Übertragen der Build-Ausgabe auf die SD-Karte


## Kopieren Sie die Dateien von Ihrem Computer
Entnehmen Sie die SD-Karte aus dem TXT, legen Sie sie in einen SD-Kartenleser in Ihrem Computer und ersetzen Sie die folgenden drei Dateien durch die neueste Version:
- uImage
- am335x-kno_txt.dtb
- rootfs.img

## Update ohne die SD-Karte zu entfernen
... ohne die Karte aus dem TXT zu entfernen, indem Sie das System ersetzen, während es läuft! (yup, das ist in diesem Fall möglich ...)

Wichtig: Starten Sie die TXT-Community-Firmware.

Für diesen Update-Pfad müssen Sie zuerst ein root-Passwort festlegen. Siehe [TXT-Passwort-Richtlinie](../password-policy#enabeling-the-root-user).

Von einem Linux-System (oder mit einem anderen SSH-Client), auf der Konsole mit dem Arbeitsverzeichnis ftcommunity-TXT-repository ((in den hier verwendeten Beispielen: ~/ftcommunity-TXT) und der bereitgestellten IP 192.168.7.2 ihres TXTs:

`ssh root@192.168.7.2 mv /media/sdcard/root.img /media/sdcard/root.old`  
`scp output/images/uImage output/images/am335x-kno_txt.dtb output/images/rootfs.img root@192.168.7.2:/media/sdcard/boot`  

Starten Sie nun den TXT neu. Stellen Sie sicher, dass Sie den Computer ausschalten, indem Sie den blauen Ein- / Ausschalter drücken, bis "Herunterfahren ..." im Display angezeigt wird. Lassen Sie den Knopf los, wenn Sie den Text sehen, ansonsten wird er einige Sekunden später auf die harte Tour ausgeschaltet.

