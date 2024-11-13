#! /bin/bash

## run this script with sudo to set up exertnal radio for attack
airmon-ng check kill ## kill any program interfering with airmon
airmon-ng start wlan1
