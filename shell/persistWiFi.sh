#!/bin/bash
if ! [ "$(ping -c 1 192.168.20.1)" ]; then
    sudo ifdown wlan0
    sudo ifup wlan0
fi
