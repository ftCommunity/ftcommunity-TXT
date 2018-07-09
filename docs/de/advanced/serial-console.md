---
nav-title: Serielle Konsole
nav-pos: 3
---

Die serielle Konsole des TXT kann mit einem USB-auf-TTL-Adapter angezeigt werden. 
Im Prinzip sollte jeder gängige Adapter funktionieren, wichtig ist nur, dass der
Adapter mit einem Pegel von 3.3V arbeitet. 

**Achrung:** vor der ersten Benutzung des Adapters unbedingt prüfen, dass zwischen GND <-> RX und 
GND <-> TX tatsächlich nur 3.3V anliegen. Ein Adapter mit 5V kann den TXT irreparabel beschädigen!

Die EXT-Schnittstelle des Controllers ist wie folgt belegt:

```
  RX
  | reserved
  | | I2C-Data
  | | | Extension
  | | | | GND
  | | | | |
  | +–––+ |
+–––+   +–––+
| O O O O O |
| O O O O O |
+–––––––––––+
  | | | | |
  | | | | Extension
  | | | Extension
  | | I2C-Clock
  | reserved
  TX
```

Beim Anschließen darauf achten, dass RX und TX gekreuzt verbunden werden:

* TX <-> RX
* RX <-> TX
* GND <-> GND

Die Konsole kann dann mit einem beliebigen Terminalprogramm geöffnet werden, z.B.:

`screen /dev/tty.SLAB_USBtoUART 115200`

Nach Einschalten des TXT sieht man die Meldungen des Bootloaders:

```
U-Boot SPL 2013.10 (Jul 04 2015 - 08:30:17)
>>> I2C0 On
Could not probe the EEPROM; something fundamentally wrong on the I2C bus.
Could not get board ID.
>>> setup_dplls vor do_setup_dpll
>>> setup_dplls nach do_setup_dpll
Could not probe the EEPROM; something fundamentally wrong on the I2C bus.
Could not get board ID.
>>> Setting MUX Start
>>> Setting MUX End
Could not probe the EEPROM; something fundamentally wrong on the I2C bus.
Could not get board ID.
>>>Start TXT-Mode - V2
LCD-Init_4: 
Could not probe the EEPROM; something fundamentally wrong on the I2C bus.
Could not get board ID.
---> MPU 600 VDD 46 

U-Boot 2013.10 (Jul 04 2015 - 08:30:17)

I2C:   ready
DRAM:  256 MiB
NAND:  128 MiB
MMC:   OMAP SD/MMC: 0, OMAP SD/MMC: 1
Could not probe the EEPROM; something fundamentally wrong on the I2C bus.
Could not get board ID.
Net:   usb_ether

NAND read: device 0 offset 0x700000, size 0x40000
 262144 bytes read: OK
CopyToLcd
LCD Command called
Hit ENTER key to stop autoboot:  0 
```
