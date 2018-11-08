# Overview

This project allows to read raw data from the Myo armband with the Raspberry Pi 3 or Zero W. The code uses the bluez library to connect via bluetooth low energy (BLE) the Myo to the Raspberry.

The reading protocol is based on the work of dzhu (https://github.com/dzhu/myo-raw).

# Requirements

- python >=2.7
- bluez 5.43
- pexpect
- serial
- numpy
