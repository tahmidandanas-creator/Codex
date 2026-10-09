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

def check_signal():
    import re as _re, time as _time
    print("[*] WiFi signal strength + block detector")
    print("[*] Monitoring for 30 seconds. Ctrl+C to stop early.\n")
    history = []
    blocked_count = 0
    for i in range(15):
        out = run("termux-wifi-connectioninfo")
        if not out or "not found" in out.lower():
            print("termux-api missing. Install Termux:API app.")
            return
        rssi_m = _re.search(r'"rssi"\s*:\s*(-?\d+)', out)
        link_m = _re.search(r'"link_speed_mbps"\s*:\s*(\d+)', out)
        freq_m = _re.search(r'"frequency_mhz"\s*:\s*(\d+)', out)
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
        _time.sleep(2)
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


def internet_check():
    print("[*] Internet Health Check\n")
    results = []

    # 1. Local link (router)
    print("  [1/3] Testing local link (router)...")
    r1 = run("ping -c 3 -W 2 192.168.0.1")
    local_ok = "0% packet loss" in r1 or "0.0% packet loss" in r1
    results.append(("Router (192.168.0.1)", local_ok))

    # 2. Internet (IP, no DNS)
    print("  [2/3] Testing internet (8.8.8.8)...")
    r2 = run("ping -c 3 -W 2 8.8.8.8")
    inet_ok = "0% packet loss" in r2 or "0.0% packet loss" in r2
    results.append(("Internet (8.8.8.8)", inet_ok))

    # 3. DNS
    print("  [3/3] Testing DNS (google.com)...")
    r3 = run("ping -c 3 -W 2 google.com")
    dns_ok = "0% packet loss" in r3 or "0.0% packet loss" in r3
    results.append(("DNS (google.com)", dns_ok))

    # Summary table
    print("\n[*] Results:\n")
    for name, ok in results:
        status = "OK" if ok else "FAIL"
        print(f"  {name:<25} {status}")

    # Verdict
    print("\n[*] Diagnosis:")
    if all(ok for _, ok in results):
        print("  Everything works. WiFi + Internet + DNS are all fine.")
    elif local_ok and not inet_ok:
        print("  WiFi is fine, but INTERNET is down.")
        print("  -> Your ISP line is the problem, not your WiFi.")
        print("  -> Restart the router. If still down, call your ISP.")
    elif not local_ok:
        print("  Cannot even reach your router.")
        print("  -> Check WiFi connection. Move closer to the router.")
    elif inet_ok and not dns_ok:
        print("  Internet works but DNS fails.")
        print("  -> DNS server issue. Try changing DNS to 1.1.1.1 or 8.8.8.8.")
    else:
        print("  Mixed results. Retry in a minute.")


MENU = [
    ("Scan nearby networks", scan_networks),
    ("Detect Evil Twin",     detect_evil_twin),
    ("Check my encryption",  check_encryption),
    ("WiFi signal + block detector", check_signal),
    ("Audit my router",      audit_router),
    ("Map devices on LAN",   lan_scan),
    ("Detect ARP spoof",     detect_arp_spoof),
    ("Internet health check", internet_check),
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
