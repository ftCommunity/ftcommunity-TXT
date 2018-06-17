---
nav-title: Serial Console
nav-pos: 3
---

You can display the serial console from the TXT controler with a USB to TTL adapter. In the following example, a USB to TTL adapter with the chip CP2102 was used. Alternatively you could use an adapter with FT232 chip or similar. It is important that the adapters work on a 3.3 volt basis. First, you should plug the adapter into the desktop PC and check whether there are only 3.3 V between GND <-> RX or GND <-> TX. With 5 volts, the txt controller would be damaged.

The EXT interface from the controller is occupied as follows:

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

When wiring, make sure that RX and TX are cross-connected:

* TX <-> RX
* RX <-> TX
* GND <-> GND

Then the console can be opened with the OSX as follows:

`screen /dev/tty.SLAB_USBtoUART 115200`

Access with [other operating systems](https://wiki.onion.io/Tutorials/Connecting-to-Omega-via-Serial-Terminal) is also possible.

Finally, the TXT can be turned on and you can see the boot process.

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
