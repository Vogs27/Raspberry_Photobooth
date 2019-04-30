# Raspberry_Photobooth
A button controlled Raspberry Pi photobooth
---
This is a simple Python program that allows you to take and print some photos in an automated way.
It's tested on Raspberry Pi 3 v1 and Python 2.7 but it should also on others Raspberry versions.

It use 3 simple backlighted arcade buttons to control the flow of itself on a non touchscreen display, providing some money saving.

GPIO allocation:
|            Button name | Raspberry 3 BCM pin | Raspberry 1 V1 BCM pin |
|-----------------------:|:-------------------:|:----------------------:|
|             Red button |          4          |            4           |
|           Green button |          3          |            1           |
|           White button |          2          |            0           |
|   Red button backlight |          23         |           23           |
| Green button backlight |          22         |           22           |
| White button backlight |          27         |           21           |
|           Flash output |          17         |           17           |

The printer is connected via Cups, so you can use any cups compatible printer.

---
##Todo

*Remove all unused libs
*Add keyboard interrupt to exit
*Make an external configuration file
