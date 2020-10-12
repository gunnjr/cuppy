#!/bin/bash
attempts=0
maxAttempts=5


while [[ ( $attempts -lt $maxAttempts ) && ( ! "$(ping -c 1 192.168.20.1)" ) ]]
do
    attempts=$((attempts+1))
    echo `date` ": WiFi Down. Attempting to Reconnect ($attempts of $maxAttempts)..."
    # sudo ifdown wlan0
    sleep 2
    # sudo ifup wlan0
done

if  [ ! "$(ping -c 1 192.168.20.1)" ]; then
    echo "Failed to reconnect to WiFi after $attempts attempts."
fi
