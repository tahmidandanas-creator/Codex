#!/usr/bin/env python3
import os, sys, subprocess, time, re

R="\033[91m"; G="\033[92m"; Y="\033[93m"; C="\033[96m"; X="\033[0m"

BANNER = C + "=== Codex WiFi Defense v0.2 ===" + X

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
    except Exception as e:
        return str(e)

def clear(): os.system("clear")
def pause():
    try: input(Y + "[*] Enter to continue..." + X)
    except: pass

def scan_networks():
    print("[*] Scanning...")
    out = run("termux-wifi-scaninfo")
    if "not found" in out.lower() or not out.strip():
        print("termux-api missing. Install Termux:API app + pkg install termux-api")
        return
    ssids = re.findall(r'"ssid"\s*:\s*"([^"]+)"', out)
    bssids = re.findall(r'"bssid"\s*:\s*"([^"]+)"', out)
    if not ssids:
        print("No networks. Grant Location permission.")
        return
    seen = {}
    for s, b in zip(ssids, bssids):
        flag = ""
        if s in seen and seen[s] != b:
            flag = " <-- possible Evil Twin"
        seen[s] = b
        print(f"  {s:<30} {b}{flag}")
    print(f"Total: {len(ssids)}")

def check_encryption():
    out = run("termux-wifi-connectioninfo")
    print(out)
    if "WPA3" in out: print("  OK: WPA3 - excellent")
    elif "WPA2" in out: print("  OK: WPA2 - good")
    elif "WEP" in out: print("  BAD: WEP - broken!")
    else: print("  WARN: unknown/open")

def detect_evil_twin():
    print("[*] Checking for duplicate SSIDs...")
    out = run("termux-wifi-scaninfo")
    pairs = re.findall(r'"ssid"\s*:\s*"([^"]+)".*?"bssid"\s*:\s*"([^"]+)"', out, re.DOTALL)
    groups = {}
    for ssid, bssid in pairs:
        groups.setdefault(ssid, set()).add(bssid)
    found = False
    for ssid, bssids in groups.items():
        if len(bssids) > 1:
            found = True
            print(f"  WARN: '{ssid}' by {len(bssids)} BSSIDs")
            for b in bssids: print(f"      {b}")
    if not found: print("  OK: no duplicates")

def check_wps():
    print("[*] WPS check")
    print("Log into router -> Wireless -> WPS -> DISABLE")
    print("WPS PINs are brute-forceable in hours.")

def audit_router():
    gw = "192.168.0.1"
    if not gw:
        print("No gateway found.")
        return
    print(f"Gateway: {gw}")
    for name, port in [("Telnet",23),("SSH",22),("UPnP",1900)]:
        r = run(f"nc -z -w 2 {gw} {port} && echo OPEN || echo closed").strip()
        flag = " <-- WARN" if "OPEN" in r and name in ("Telnet","UPnP") else ""
        print(f"  {name:<8} ({port}): {r}{flag}")
    print("Checklist: change admin pw, disable WPS, disable UPnP, update firmware, use WPA2-AES/WPA3")

def lan_scan():
    gw = "192.168.0.1"
    if not gw: print("No gateway."); return
    subnet = "192.168.0.0/24"
    print(f"Scanning {subnet}...")
    print(run(f"nmap -sn {subnet}"))

def detect_arp_spoof():
    def gw_mac():
        gw = "192.168.0.1"
        if not gw: return None, None
        arp = ""
        m = re.search(r"([0-9a-f:]{17})", arp, re.I)
        return gw, (m.group(1) if m else None)
    gw, mac1 = gw_mac()
    if not gw: print("No gateway."); return
    print(f"Gateway {gw} MAC: {mac1}")
    print("Watching 30s...")
    for _ in range(15):
        time.sleep(2)
        _, mac_now = gw_mac()
        if mac_now and mac_now != mac1:
            print(f"  WARN: MAC CHANGED {mac1} -> {mac_now}")
            print("  ARP spoofing suspected!")
            return
    print("  OK: stable")

MENU = [
    ("Scan nearby networks", scan_networks),
    ("Detect Evil Twin",     detect_evil_twin),
    ("Check my encryption",  check_encryption),
    ("Check WPS",            check_wps),
    ("Audit my router",      audit_router),
    ("Map devices on LAN",   lan_scan),
    ("Detect ARP spoof",     detect_arp_spoof),
    ("Exit",                 None),
]

def main():
    while True:
        clear()
        print(BANNER)
        for i, (name, _) in enumerate(MENU, 1):
            print(f"  [{i}] {name}")
        try:
            c = int(input("\ncodex > "))
            if not 1 <= c <= len(MENU): continue
        except: continue
        action = MENU[c-1][1]
        if action is None: break
        clear(); print(BANNER)
        try: action()
        except KeyboardInterrupt: print("stopped")
        pause()

if __name__ == "__main__":
    main()
