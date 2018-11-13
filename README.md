# Overview
This project allows to read raw data from the Myo armband with the Raspberry Pi 3 or Zero W. The code uses the bluez library to connect via bluetooth low energy (BLE) the Myo to the Raspberry.

The reading protocol is based on the work of dzhu (https://github.com/dzhu/myo-raw).

# Requirements
- python >=2.7
- bluez 5.43
- pexpect
- serial
- numpy
- Raspberry Pi 3 or Zero W
- Myo armband from Thalmic Labs

# Included files
## myo_rpi_ble.py (read raw EMG/IMU data)
myo_rpi_ble.py must be launched on the Raspberry and it reads raw data from the Myo armband. It uses the pexpect library to spawn commands in gatttool. It implements the following functions:

- connect() & disconnect(): to connect/disconnect from the Myo.
- get_name(): to get the name assigned to the Myo.
- get_firmware(): to get the firmware of the Myo.
- get_battery_level(): to get the actual battery level of the Myo.
- vibrate(): to make the Myo vibrate from 1 to 3 seconds.
- set_leds(): to change the color of the logo (see comments in code for more info)
- start_raw(): to initialize collection of raw EMG data at about 50Hz.
- start_raw_fast(): to initialize collection of raw EMG data at about 200Hz (depends on RPi).
- collect_raw(): to collect raw EMG data at about 50Hz (must be used with start_raw()).
- collect_raw_fast(): to collect raw EMG data at about 200Hz (must be used with start_raw_fast()).
- sleep_mode(): to put the Myo in different sleep mode.
- power_off(): to power off the Myo.
- main(): to run the whole process.

In main() is defined the MAC address of the Myo. Please change it to your own. This address can simply be found by plugging the Myo to your computer via USB to access it as an external device. The MAC address should be then in one of the listed file.
Once gatttool launched, EMG data are collected in rawData and can then be sent out via serial.

## filtering.py
In filtering.py is the function data_filtering() which applies a moving window average smoothing on raw data. The size of this window is defined by rawWinSize. Data can also be saved into a text file with the function save_output_to_file().

## common.py
Here are common functions to read data packets.

# Installation
In order to install the different libraries and packages to run this code on your RPi, you will have to do the following:

First enable bluetooth on RPi in /boot/config.txt by commenting the following 2 lines:
```
#dtoverlay=pi3-miniuart-bt
#dtoverlay=pi3-disable-bt
```
You might have to reboot for the changes to take place.

Then download the source for BlueZ (I used version 5.43):
```
wget http://www.kernel.org/pub/linux/bluetooth/bluez-5.43.tar.xz
or
wget https://mirrors.edge.kernel.org/pub/linux/bluetooth/bluez-5.43.tar.xz
```
and unpack it:
```
tar xvf bluez-5.43.tar.xz
```
Change the directory:
```
cd bluez-5.43/
```
Install the following libraries:
```
sudo apt-get update
sudo apt-get install -y libusb-dev libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev
```
Build BlueZ with the standard configuration:
```
./configure
```
Start the compilation with standard make (be patient):
```
make
```
And install it:
```
sudo make install
```

## Authors

* **Charles Lambelet**
