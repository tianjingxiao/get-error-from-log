# Flashing Rig Script


[![Travis](https://img.shields.io/badge/language-Python-red.svg)]()
[![Travis](https://img.shields.io/badge/MacOS--9cf?logo=Apple&style=social)]()


Repository for all hub3 flashing related programs

the link to projcet documents is [here](https://occuspace.atlassian.net/wiki/spaces/OC/pages/1324548109/Project+The+Flash).

This repository contains:

1. A [flash python script](https://github.com/Waitz-Inc/the-flash/blob/main/flash.py) to automaticatly get image and STM32 programmer path and run the flash process
2. A [fuse MAC script](https://github.com/Waitz-Inc/the-flash/blob/main/occu_mac_generator.py) to assign MAC address to hubs.



## Table of Contents

- [Background](#Background)
- [How to use](#How-to-use)
- [Function](#Function)
- [Test case](#Test-case)
- [Todo](#Todo)

## Background

This document outlines the design and implementation of Occuspace’s flashing rig for our Hub3’s. Run on MacOS.

Previously we can only flash board one by one, each will take 1~2 minutes depending on the user’s computer, or longer. The goal of this project is to create a system using a USB hub and ethernet switch with POE(power over ethernet) to flash 8 or more boards at a time.



## How to use

This project uses [STM32CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html). Go check this out if you don't have it locally installed.

Once you have already install the STM32CubeProgrammer and have a flash image in your computer.
```sh
$ python flash.py
```
Before start the script, please make sure you have the correct image version set up in [flash python script](https://github.com/Waitz-Inc/the-flash/blob/main/flash.py).
```sh
ImagineVersion = "Treeline-imagine-occuspace-eMMC-v99.01.09.tsv"
```


## Function

* Get hubs' serial number and power-up order
* Get STM32 programmer and image path
* Automatically start to flash once a new board is connected
* Return information as MAC address, power-up order when a board is finished flashing
* Return information as MAC address, power-up order when a flashed board is unplugged
* Return information when a board is interrupted during the flash process

## Test case

The result when running this script should be:
```
**************************************************
Flashing process begin
**************************************************
003C00473430511536383630
970
Board is still flashing
003C003B3430511536383630
2861
Started flashing board 003C003B3430511536383630
```
The first time running this script will take about 1 minute to find the path. After the flash process finish, it will tell information as:
```
Board with serial number: 003C003B3430511536383630 and order: 1 is done flashing and has MAC: 04:d9:21:38:30:a8. It can now be unplugged
```
User can now unplug the board with order 1, it will tell information as:
```
Board with serial number: 003C003B3430511536383630 has been unplugged and has MAC: 04:d9:21:93:6b:c9. It was plugged in order: 1
```
If the board is unpluged or the STM32Programmer has some error before the flashing process finish, it will tell information as:
```
Board with serial number: 003C003B3430511536383630 has been unplugged prior to completing flashing. It was plugged in order: 1
Please check if there was a flashing error"
```
And also return the error code(under development)
```
Flashing process for board 003C003B3430511536383630 with order 1 errored out with error {status.stderr.read()}
```
## Todo
- Connect to DB
- Change UI to table
- Error handling
- Investigate MAC fusing problem
