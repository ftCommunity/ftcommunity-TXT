---
nav-title: Passwort-/Anmelderegeln
nav-pos: 2
---
# Benutzer, Passwörter und "Root"-Zugriff auf dem TXT

## Auslieferungszustand der Benutzer
Standardmässig kommt die Community-Firmware mit zwei Benutzern: **ftc** und **root** (*und ROBOPro, aber nur für Kompabilitätszwecke*).

- Benutzer ftc hat **kein Passwort**
- Benutzer root ist **deaktiviert**

## Die "Zwei-Wege" Authentifizierung 
Die Community-Firmware (*ab Version 0.9.3*) zeigt einen Dialog auf dem TXT-Display, um zu bestätigen, dass der Netzwerkzugriff von dem aktiven Nutzer stammt.

Man braucht also Zugang zum Bildschirm, um per SSH auf den TXT zugreifen zu können. Um das zu vermeiden, musst Du ein Passwort setzen.

## Den "root"-Benutzer aktivieren

Dafür musst du von einem SSH-Clienten eine Verbindung zum TXT mit dem **"ftc"-Benutzer** herstellen: 

```ssh ftc@192.168.7.2```

(*Erklärung: Befehl Benutzer@IP-Adresse*)

**Kein** Passwort wird benötigt! Du musst nur auf dem **Bildschirm bestätigen**, dass es sich um **deine Anfrage** handelt!


Jetzt kannst du den "root"-Benutzer aktivieren und mit einem Passwort versehen.
- Das geht mit: `sudo passwd root`
- Dort musst du **2x** dein Passwort eingeben, um sicher zu gehen, dass du dich **nicht verschrieben** hast!

Jetzt kann der User root mit seinem Passwort per SSH auf den TXT zugreifen ohne Bestätigung auf dem TXT-Display.
