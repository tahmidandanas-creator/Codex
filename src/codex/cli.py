#!/usr/bin/env python3
"""Codex - WiFi Defense Toolkit for Termux."""

import os
import sys
import subprocess
import time
import re

# Colors for the terminal
R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"; C = "\033[96m"; B = "\033[1m"; X = "\033[0m"

# The big CodeX logo in Sky Blue (C)
BANNER = f"""{C}{B}
   ▄████▄   ▒█████  ▓█████▄ ▓█████ ▒██   ██▒
  ▒██▀ ▀█  ▒██▒  ██▒▒██▀ ██▌▓█   ▀ ▒▒ █ █ ▒░
  ▒▓█    ▄ ▒██░  ██▒░██   █▌▒███   ░░  █   ░
  ▒▓▓▄ ▄██▒▒██   ██░░▓█▄   ▌▒▓█  ▄  ░ █ █ ▒ 
  ▒ ▓███▀ ░░ ████▓▒░░▒████▓ ░▒████▒▒██▒ ▒██▒
{X}{C}       WiFi Defense Toolkit{X}
"""

def run(cmd, capture=False):
    try:
        if capture:
            return subprocess.check_output(cmd, shell=True,
                stderr=subprocess.STDOUT, text=True)
        subprocess.run(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        return e.output or ""
    except Exception as e:
        return str(e)

def clear():
    os.system("clear")

def pause():
    try:
        input(f"\n{Y}[*] Press Enter to continue...{X}")
    except (EOFError, KeyboardInterrupt):
        pass

# --- FEATURES ---

def scan_networks():
    print("[*] Scanning nearby networks...")
    out = run("termux-wifi-scaninfo", capture=True)
    if not out or "not found" in out.lower():
        print(f"{Y}[!] termux-api missing. Install Termux:API app.{X}")
        return
    ssids = re.findall(r'"ssid"\s*:\s*"([^"]+)"', out)
    bssids = re.findall(r'"bssid"\s*:\s*"([^"]+)"', out)
    if not ssids:
        print("[!] No networks found. Grant Location permission to Termux:API.")
        return
    print(f"\n{'SSID':<30} {'BSSID':<20} Flag")
    print("-" * 65)
    seen = {}
    for s, b in zip(ssids, bssids):
        flag = ""
        if s in seen and seen[s] != b:
            flag = f"{R}possible Evil Twin{X}"
        seen[s] = b
        print(f"{s:<30} {b:<20} {flag}")
    print(f"\n[*] Total APs: {len(ssids)}")

def detect_evil_twin():
    print("[*] Checking for duplicate SSIDs (Evil Twin signal)...")
    out = run("termux-wifi-scaninfo", capture=True)
    pairs = re.findall(r'"ssid"\s*:\s*"([^"]+)".*?"bssid"\s*:\s*"([^"]+)"', out, re.DOTALL)
    groups = {}
    for ssid, bssid in pairs:
        groups.setdefault(ssid, set()).add(bssid)
    found = False
    for ssid, bssids in groups.items():
        if len(bssids) > 1:
            found = True
            print(f"  {R}⚠ '{ssid}' advertised by {len(bssids)} BSSIDs:{X}")
            for b in bssids:
                print(f"      {b}")
    if not found:
        print(f"  {G}✓ No duplicate SSIDs detected.{X}")

def check_encryption():
    out = run("termux-wifi-connectioninfo", capture=True)
    if not out or "not found" in out.lower():
        print(f"{Y}[!] termux-api missing.{X}")
        return
    print(out)
    if "WPA3" in out:
        print(f"{G}  ✓ WPA3 — excellent{X}")
    elif "WPA2" in out:
        print(f"{G}  ✓ WPA2 — good (prefer AES){X}")
    elif "WEP" in out:
        print(f"{R}  ⚠ WEP — completely broken!{X}")
    else:
        print(f"{Y}  ⚠ Unknown or open network{X}")

def check_signal():
    print("[*] WiFi signal strength + block detector")
    print("[*] Monitoring for 30 seconds. Ctrl+C to stop early.\n")
    history = []
    blocked_count = 0
    for i in range(15):
        out = run("termux-wifi-connectioninfo", capture=True)
        if not out or "not found" in out.lower():
            print("termux-api missing. Install Termux:API app.")
            return
        rssi_m = re.search(r'"rssi"\s*:\s*(-?\d+)', out)
        link_m = re.search(r'"link_speed_mbps"\s*:\s*(\d+)', out)
        freq_m = re.search(r'"frequency_mhz"\s*:\s*(\d+)', out)
        if rssi_m:
            rssi = int(rssi_m.group(1))
            bar = "#" * max(0, (rssi + 100) // 5)
            print(f"  [{i+1:02d}] RSSI: {rssi:>4} dBm {bar}")
            history.append(rssi)
            if rssi > -50:
                state = "Excellent"
            elif rssi > -60:
                state = "Good"
            elif rssi > -70:
                state = "Fair"
            elif rssi > -85:
                state = "Weak"
            else:
                state = "Very weak"
            print(f"       Status: {state}")
        else:
            print(f"  [{i+1:02d}] No signal - possible block/deauth attack!")
            blocked_count += 1
        if link_m:
            print(f"       Link speed: {link_m.group(1)} Mbps")
        if freq_m:
            print(f"       Frequency: {freq_m.group(1)} MHz")
        time.sleep(2)
    print("\n[*] Summary:")
    if history:
        avg = sum(history) // len(history)
        print(f"  Average RSSI: {avg} dBm")
        print(f"  Samples: {len(history)}")
    if blocked_count > 0:
        print(f"  WARNING: {blocked_count} samples had NO signal")
        print("  Possible jamming, deauth attack, or router issue.")
    else:
        print("  No signal blocks detected. Connection stable.")

def audit_router():
    gw = "192.168.0.1"
    print(f"[*] Gateway: {gw}\n")
    checks = {
        "Telnet (23)":  f"nc -z -w 2 {gw} 23 && echo OPEN || echo closed",
        "SSH (22)":     f"nc -z -w 2 {gw} 22 && echo OPEN || echo closed",
        "UPnP (1900)":  f"nc -z -w 2 {gw} 1900 && echo OPEN || echo closed",
        "DNS (53)":     f"nc -z -w 2 {gw} 53 && echo OPEN || echo closed",
    }
    for name, cmd in checks.items():
        r = run(cmd, capture=True).strip()
        flag = ""
        if "OPEN" in r and "Telnet" in name:
            flag = f" {R}⚠ disable telnet!{X}"
        if "OPEN" in r and "UPnP" in name:
            flag = f" {Y}⚠ UPnP can expose you{X}"
        print(f"  {name:<15}: {r}{flag}")
    print(f"\n{Y}[*] Checklist:{X}")
    print("  • Change default admin password")
    print("  • Disable WPS")
    print("  • Disable WAN/remote admin")
    print("  • Update firmware")
    print("  • Use WPA3 or WPA2-AES")

def lan_scan():
    subnet = "192.168.0.0/24"
    print(f"[*] Scanning {subnet} (may take a minute)...")
    out = run(f"nmap -sn {subnet}", capture=True)
    if "not found" in out.lower():
        print("[!] nmap not installed. Run: pkg install nmap")
        return
    print(out)

def detect_arp_spoof():
    def gateway_mac():
        gw = "192.168.0.1"
        arp = run(f"grep {gw} /proc/net/arp", capture=True)
        m = re.search(r"([0-9a-f:]{17})", arp, re.I)
        return gw, (m.group(1) if m else None)

    gw, mac1 = gateway_mac()
    print(f"[*] Gateway {gw} MAC: {mac1}")
    print("[*] Watching for changes (30s)...")
    for _ in range(15):
        time.sleep(2)
        _, mac_now = gateway_mac()
        if mac_now and mac_now != mac1:
            print(f"{R}  ⚠ GATEWAY MAC CHANGED: {mac1} → {mac_now}{X}")
            print(f"{R}  ⚠ ARP spoofing suspected!{X}")
            return
    print(f"{G}  ✓ Gateway MAC stable.{X}")

def internet_check():
    print("[*] Internet Health Check\n")
    results = []

    print("  [1/3] Testing local link (router)...")
    r1 = run("ping -c 3 -W 2 192.168.0.1", capture=True)
    local_ok = "0% packet loss" in r1 or "0.0% packet loss" in r1
    results.append(("Router (192.168.0.1)", local_ok))

    print("  [2/3] Testing internet (8.8.8.8)...")
    r2 = run("ping -c 3 -W 2 8.8.8.8", capture=True)
    inet_ok = "0% packet loss" in r2 or "0.0% packet loss" in r2
    results.append(("Internet (8.8.8.8)", inet_ok))

    print("  [3/3] Testing DNS (google.com)...")
    r3 = run("ping -c 3 -W 2 google.com", capture=True)
    dns_ok = "0% packet loss" in r3 or "0.0% packet loss" in r3
    results.append(("DNS (google.com)", dns_ok))

    print("\n[*] Results:\n")
    for name, ok in results:
        status = f"{G}OK{X}" if ok else f"{R}FAIL{X}"
        print(f"  {name:<25} {status}")

    print("\n[*] Diagnosis:")
    if all(ok for _, ok in results):
        print("  Everything works. WiFi + Internet + DNS are all fine.")
    elif local_ok and not inet_ok:
        print("  WiFi is fine, but INTERNET is down.")
        print("  -> Your ISP line is the problem, not your WiFi.")
    elif not local_ok:
        print("  Cannot even reach your router.")
        print("  -> Check WiFi connection. Move closer to the router.")
    elif inet_ok and not dns_ok:
        print("  Internet works but DNS fails.")
        print("  -> DNS server issue. Try changing DNS to 1.1.1.1 or 8.8.8.8.")
    else:
        print("  Mixed results. Retry in a minute.")

# --- MENU & MAIN ---

MENU = [
    ("Scan nearby networks",         scan_networks),
    ("Detect Evil Twin",             detect_evil_twin),
    ("Check my encryption",          check_encryption),
    ("WiFi signal + block detector", check_signal),
    ("Audit my router",              audit_router),
    ("Map devices on LAN",           lan_scan),
    ("Detect ARP spoof",             detect_arp_spoof),
    ("Internet health check",        internet_check),
    ("Exit",                         None),
]

def main():
    # Play the CodeX animation once at startup
    try:
        from .animation import play
        play()
    except Exception:
        pass

    while True:
        clear()
        print(BANNER)
        for i, (name, _) in enumerate(MENU, 1):
            print(f"  {G}[{i}]{X} {name}")
        try:
            c = int(input(f"\n{C}codex > {X}"))
            if not 1 <= c <= len(MENU):
                raise ValueError
        except (ValueError, EOFError):
            continue
        except KeyboardInterrupt:
            print(f"\n{Y}[!] Bye.{X}")
            break
        
        action = MENU[c - 1][1]
        if action is None:
            print(f"{Y}[!] Stay safe.{X}")
            break
            
        clear()
        print(BANNER)
        try:
            action()
        except KeyboardInterrupt:
            print(f"\n{Y}[!] Stopped.{X}")
        pause()

if __name__ == "__main__":
    main()
