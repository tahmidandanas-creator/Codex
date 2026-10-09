# Codex

WiFi Defense & Hardening Toolkit for Termux.

Codex helps you detect attacks against YOUR network, audit YOUR router,
and harden YOUR WiFi setup. It is a blue-team tool — it does not attack.

## Features
- Scan nearby networks and flag Evil Twin networks
- Check current WiFi encryption (WEP/WPA/WPA2/WPA3)
- Check current Wifi signal strength + blocker (within 30 second with 15 frame)
- Audit router for open ports (telnet, SSH, UPnP)
- Map devices on your LAN
- Detect ARP spoofing

## Install
Download both Termux and Termux:API from F-droid app

Grand location permission by
Go to android setting → Apps → Termux:API → Permissions → Location → Allow all the time

Then

Write this to install
```bash
pkg update -y && pkg upgrade -y
pkg install python git
pkg install termux-api nmap netcat-openbsd -y
pip install git+https://github.com/Scientia/codex.git
Codex 
