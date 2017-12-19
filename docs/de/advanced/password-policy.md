---
nav-title: Passwort-/Anmelderegeln
nav-pos: 2
---
# Benutzer, Passwörter und "Root"-Zugriff auf dem TXT

## Auslieferungszustand der Benutzer
Standardmässig kommt die Community-Firmware mit zwei Benutzern: **ftc** und **root**. (*Und ROBOPro, aber nur für Kompabilitätszwecke!*)

- Benutzer ftc hat **kein Passwort**
- Benutzer root ist **deaktiviert**

## Die "Zwei-Wege" Authentifizierung 
Die Community-Firmware (*ab Version 0.9.3*) zeigt einen Dialog, um zu bestätigen, dass der Netzwerkzugriff von dem aktiven Nutzer stammt.

D.h. dass der Bildschirm frei bleiben muss, um per [SSH](../programming/python/tutorial-2.md) auf den TXT zugreifen zu können!

(*Um diese Aktionen zu vermeiden musst du ein Passwort setzen. Siehe unten!*)

## Den "root"-Benutzer aktivieren
Um den "root"-Benutzer aktivieren zu können, muss **zuerst** für den **"ftc"-Benutzer** ein **Passwort** gesetzt werden!

Dafür musst du von einem SSH-Clienten eine Verbindung zum TXT mit dem **"ftc"-Benutzer** herstellen: 

```ssh ftc@192.168.7.2```

(*Erklärung: Befehl Benutzer@IP-Adresse*)

**Kein** Passwort wird benötigt! Du musst nur auf dem **Bildschirm bestätigen**, dass es sich um **deine Anfrage** handelt!

1. Zuerst muss ein Passwort für den "ftc"-Benutzer gesetzt werden! 
- Das geht mit: `sudo passwd ftc`
- Bestätige auf dem Bildschirm, mit **Ja**, um fortzufahren
- Dort musst du **2x** dein Passwort eingeben, um sicher zu gehen, dass du dich **nicht verschrieben** hast!
2. Jetzt kannst du den "root"-Benutzer aktivieren und mit einem Passwort versehen:
- Das geht mit: `sudo passwd root`
- Bestätige auf dem Bildschirm, mit **Ja**, um fortzufahren
- Dort musst du **2x** dein Passwort eingeben, um sicher zu gehen, dass du dich **nicht verschrieben** hast!