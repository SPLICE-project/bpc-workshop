#!/usr/bin/env bash
#This is script finds the channel a specific BSSID uses
#This script should be run with "sudo"

## checking that number of args is ok
if [ $# -ne 2 ]; then
  echo "USAGE: ./find_channel.sh <BSSID> <capture time>"
  exit -1
fi

## cheking that time input (capture time) is a number
if ! [[ $2 =~ ^[0-9]+$ ]]; then
  echo "capture time is not a number!"
  exit -2
fi

## checking that time input (capture time) is not too long)
if (($2 > 25)); then
  echo "Capturing time is too large!"
  exit -3
fi

## checking that the corre bssid is given
norm_bssid=$(echo "$1" | awk '{print tolower($0)}')
if [ "$norm_bssid" != "FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE" ]; then
  echo "Incorrect BSSID"
  exit -4
fi

## Getting the channel

echo "SCANNING NETWORK FOR ""$2" " SECONDS"
tmux new-session -d -s ses "airodump-ng --bssid "$1" -w capt --output-format csv wlan1"
sleep $2
tmux send-keys -t ses C-c
tmux kill-session -t ses
echo "SCANNING DONE"

echo "GETTING CHANNEL FOR BSSID " "$1""..."
python3 grab_channel.py
rm -f *.csv
