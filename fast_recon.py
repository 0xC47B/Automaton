import socket
import whois
import requests
import dns.resolver
import json
import subprocess
import time

# Optional: API Key for Shodan
SHODAN_API_KEY = "YOUR_SHODAN_API_KEY"

def get_ip(hostname):
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return "Tidak dapat menemukan IP"

def get_whois_info(hostname):
    try:
        w = whois.whois(hostname)
        return w
    except Exception as e:
        return f"Gagal mengambil WHOIS: {e}"

def get_dns_records(domain):
    record_types = ['A', 'MX', 'NS', 'TXT', 'CNAME', 'AAAA', 'CAA']
    records = {}
    for record in record_types:
        try:
            answers = dns.resolver.resolve(domain, record)
            records[record] = [str(r) for r in answers]
        except:
            records[record] = []
    return records

def get_headers(domain):
    try:
        r = requests.get(f"http://{domain}", timeout=5)
        return dict(r.headers)
    except:
        return "Tidak bisa mendapatkan header HTTP"

def banner_grab(ip, port=80):
    try:
        s = socket.socket()
        s.settimeout(3)
        s.connect((ip, port))
        s.send(b"HEAD / HTTP/1.1\r\nHost: "+ip.encode()+b"\r\n\r\n")
        banner = s.recv(1024).decode(errors="ignore")
        s.close()
        return banner
    except Exception as e:
        return f"Gagal banner grab: {e}"

def geoip_lookup(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}")
        return r.json()
    except:
        return "Gagal GeoIP lookup"

def reverse_dns(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "Tidak tersedia"

def asn_info(ip):
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json")
        return r.json()
    except:
        return "Gagal mengambil ASN info"

def subdomains_crtsh(domain):
    try:
        r = requests.get(f"https://crt.sh/?q=%25.{domain}&output=json")
        subdomains = list(set([entry['name_value'] for entry in r.json()]))
        return subdomains
    except:
        return []

def shodan_lookup(ip):
    if SHODAN_API_KEY == "YOUR_SHODAN_API_KEY":
        return "Masukkan API Key Shodan untuk fitur ini."
    try:
        r = requests.get(f"https://api.shodan.io/shodan/host/{ip}?key={SHODAN_API_KEY}")
        return r.json()
    except:
        return "Gagal mendapatkan info dari Shodan"

def run_nmap(ip):
    try:
        result = subprocess.check_output(["nmap", "-sV", "-Pn", ip], stderr=subprocess.DEVNULL)
        return result.decode()
    except:
        return "Nmap tidak tersedia atau gagal dijalankan"

# ===============================
#       MAIN PROGRAM
# ===============================

if __name__ == "__main__":
    hostname = input("Masukkan Domain: ").strip()
    ip_address = get_ip(hostname)

    print(f"\n[+] Domain       : {hostname}")
    print(f"[+] IP Address   : {ip_address}")
    print(f"[+] Reverse DNS  : {reverse_dns(ip_address)}")

    print("\n[+] WHOIS Info:")
    print(get_whois_info(hostname))

    print("\n[+] DNS Records:")
    print(json.dumps(get_dns_records(hostname), indent=2))

    print("\n[+] HTTP Headers:")
    print(json.dumps(get_headers(hostname), indent=2))

    print("\n[+] Banner Grabbing:")
    print(banner_grab(ip_address))

    print("\n[+] GeoIP Info:")
    print(json.dumps(geoip_lookup(ip_address), indent=2))

    print("\n[+] ASN/ISP Info:")
    print(json.dumps(asn_info(ip_address), indent=2))

    print("\n[+] Subdomain (crt.sh):")
    subs = subdomains_crtsh(hostname)
    print(f"Ditemukan {len(subs)} subdomain.")
    for sub in subs:
        print("-", sub)

    print("\n[+] Shodan Info:")
    print(json.dumps(shodan_lookup(ip_address), indent=2))

    print("\n[+] Nmap Scan:")
    print(run_nmap(ip_address))
