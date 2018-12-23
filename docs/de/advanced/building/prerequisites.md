---
nav-title: Voraussetzungen
nav-pos: 1
---

# Voraussetzungen

Du brauchst ein paar Dinge, um die Community-Firmware erstellen zu können.

## Benötigt:
1.  Ein Linux-System mit mindestens 20GB freiem Speicherplatz (*sowie einen schnellen CPU und eine schnelle Internetverbindung*)

    (***Die folgende Anleitung basiert auf Ubuntu, sollte jedoch auch auf anderen Distributionen funktionieren***).

2. Eine microSD-Karte auf der die ftcommunity-TXT-Firmware installiert werden kann. Jede SD(HC) microSD-Karte sollte funktionieren! 

	(*Karten mit anderen technischen Spezifikationen (z.B. microSD-XC) wurden nicht getestet*). 
	Um sicher zu sein, wird empfohlen, eine microSD(HC)-Karte mit 32GB oder weniger zu verwenden.

    Da die ftcommunity-TXT-Firmware selbst nur 200MB Speicherplatz verbraucht, ist sogar eine 2GB-Karte mehr als ausreichend.

3. Ein ssh-Client, um sich mit dem TXT zu verbinden:
	-  auf Windows [PuTTY](http://www.chiark.greenend.org.uk/~sgtatham/putty/download.htm)
	-  auf iOS kann z.B. “Serverauditor” benutzt werden
4. Eine Netzwerkverbindung zum TXT:
    * USB-basierte Netzwerkverbindung: IP 192.168.7.2
    * WLAN Verbindung: IP 192.168.8.2
        * WLAN muss möglicherweise zuerst eingeschaltet werden: “Settings” -> “Network” -> WLAN Setup
        * In diesem Modus dient der TXT als Access-Point
        * Die Netzwerk-SSID ist der Name des TXT, welcher auf dem Hauptbildschirm angezeigt wird
        * Der WPA-Key befindet sich im Menü unter “Settings” -> “Network” -> WLAN Setup
    * BT-basierte Netzwerkverbindung IP 192.168.9.2
        * BT muss zuerst eingeschaltet werden: “Settings” -> “Network”
