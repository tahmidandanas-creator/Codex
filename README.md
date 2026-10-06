# Codex

WiFi Defense & Hardening Toolkit for Termux.

Codex helps you detect attacks against YOUR network, audit YOUR router,
and harden YOUR WiFi setup. It is a blue-team tool — it does not attack.

## Features
- Scan nearby networks and flag Evil Twin networks
- Check current WiFi encryption (WEP/WPA/WPA2/WPA3)
- Check if WPS is enabled (and warn you)
- Audit router for open ports (telnet, SSH, UPnP)
- Map devices on your LAN
- Detect ARP spoofing

## Install

```bash
pkg install python git
pip install git+https://github.com/Scientia/codex.git
