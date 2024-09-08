# Robot Control

## Teleoperated
The teleop mode is designed for a wired or wireless Xbox controller.

Connect the device through the bluetooth menu, if that does not work follow the tutorial

To set up this controller, the following must be done:
- Install xboxdrv
```
sudo apt install xboxdrv
```
- Disable Enhanced Re-Transmission Mode (ERTM)
```
echo 'options bluetooth disable_ertm=Y' | sudo tee -a /etc/modprobe.d/bluetooth.conf
```
- Reboot the Raspberry Pi
```
sudo reboot
```
- Start Bluetooth tools
```
sudo bluetoothctl
```
- Scan for devices
```
agent on
default-agent
scan on
```
- Locate the MAC address of your controller
```
[NEW] Device FF:FF:FF:FF:FF:FF Wireless Controller
```
- Connect and trust using the following commands
```
connect <your-mac-address>
trust <your-mac-address>
```