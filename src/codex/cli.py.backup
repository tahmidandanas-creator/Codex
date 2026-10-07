#!/usr/bin/env python3
"""Codex - WiFi Defense Toolkit for Termux."""

import os
import sys
import subprocess
import re

G = "\033[92m"; Y = "\033[93m"; C = "\033[96m"; X = "\033[0m"

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True,
            stderr=subprocess.STDOUT, text=True)
    except Exception as e:
        return str(e)

def clear():
    os.system("clear")

def scan_networks():
    print("[*] Scanning nearby networks...")
    out = run("termux-wifi-scaninfo")
    ssids = re.findall(r'"ssid"\s*:\s*"([^"]+)"', out)
    if not ssids:
        print("[!] No data. Install Termux:API app and run: pkg install termux-api")
        return
    for s in ssids:
        print(f"  {s}")

def check_encryption():
    out = run("termux-wifi-connectioninfo")
    print(out)

def menu():
    print(f"\n{C}=== Codex WiFi Defense ==={X}")
    print("  [1] Scan nearby networks")
    print("  [2] Check my encryption")
    print("  [3] Exit")

def main():
    while True:
        clear()
        menu()
        try:
            c = input(f"\n{C}codex > {X}").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if c == "1":
            scan_networks()
            input("Enter to continue...")
        elif c == "2":
            check_encryption()
            input("Enter to continue...")
        elif c == "3":
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
