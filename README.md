# BMPi

# Introduction
This project uses a RPI zero to replace the Braumesiter wifi module. The bmpi hosts a webserver for the front-end and talks to the Braumeister over UART using AT+ commands.

## Features
 * Send commands to the BM
 * Update firmware

## Parts

### Parts required to make a cable

- USB to serial adapter (pl2303)
    - https://core-electronics.com.au/usb-to-ttl-serial-uart-rs232-adaptor-pl2303hx.html
- Connector
    - https://au.rs-online.com/web/p/industrial-automation-circular-connectors/1152764/

Note: Ensure that the USB to UART is set to 3.3V. For the core-electronics adapter listed above, remove the case of the USB to serial adapter and change it to 3.3v

## Demo Circuit

Rpi Pin               | Connector Pin
--------------------- | ----------------------------
TX (aka GPIO14)       | Pin 2 (TX)
RX (aka GPIO15)       | Pin 3 (RX)
GND                   | Pin 5 (GND)
GPIO16 (bootloader)   | Pin 4 (XCK)
3.3V (bootloader)     | Pin 1 (Vcc)

<img src="https://github.com/roguenorman/bmpi/blob/master/circuit.png"/>

## Upgrading the Braumeister firmware with a cable
!!Make sure the USB adapter is set to 3.3v.
The BM will enter bootloader when XCK is grounded and Vcc is supplied (3.3v)

Windows:
1. Connect cable from PC to BM (XCK grounded and Vcc supplied)
2. Set the com port with: MODE COM7: baud=38400 parity=n data=8 dtr=off rts=off octs=off odsr=off
3. Open SpeidelSoftwareUpdater-Windows.exe (can be downloaded from speidel.com)
4. Select firmware
5. Plug in BM mains (buttons on BM turn yellow)
6. Press start update (buttons on BM turn red)
7. When finished, buttons on BM turn green
8. Unplug usb and mains



## License

Licensed under the GNU Lesser General Public License.
https://www.gnu.org/licenses/lgpl.html
