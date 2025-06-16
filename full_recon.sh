#!/bin/bash

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <target-domain-or-IP>"
  exit 1
fi

TARGET=$1
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
OUTDIR="recon_$TARGET_$DATE"
mkdir "$OUTDIR"

echo "[*] Starting reconnaissance on $TARGET"
sleep 1

# WHOIS
echo "[*] Running WHOIS..."
whois "$TARGET" > "$OUTDIR/whois.txt"

# DNS Info
echo "[*] Gathering DNS Info..."
dig "$TARGET" ANY +short > "$OUTDIR/dns_any.txt"
host "$TARGET" > "$OUTDIR/host.txt"
nslookup "$TARGET" > "$OUTDIR/nslookup.txt"

# Ping
echo "[*] Pinging target..."
ping -c 4 "$TARGET" > "$OUTDIR/ping.txt"

# Nmap
echo "[*] Running Nmap scan..."
nmap -sC -sV -oN "$OUTDIR/nmap_basic.txt" "$TARGET"

# HTTP Headers
echo "[*] Fetching HTTP headers..."
curl -I "http://$TARGET" > "$OUTDIR/http_headers.txt" 2>/dev/null

# Subdomain enum (if tool available)
if command -v sublist3r >/dev/null 2>&1; then
  echo "[*] Running Sublist3r..."
  sublist3r -d "$TARGET" -o "$OUTDIR/subdomains.txt"
elif command -v amass >/dev/null 2>&1; then
  echo "[*] Running Amass..."
  amass enum -d "$TARGET" -o "$OUTDIR/subdomains.txt"
else
  echo "[!] Subdomain enumeration tool (Sublist3r or Amass) not found"
fi

# Directory bruteforce (dirb/gobuster)
if command -v dirb >/dev/null 2>&1; then
  echo "[*] Running Dirb..."
  dirb "http://$TARGET" > "$OUTDIR/dirb.txt"
elif command -v gobuster >/dev/null 2>&1; then
  echo "[*] Running Gobuster..."
  gobuster dir -u "http://$TARGET" -w /usr/share/wordlists/dirb/common.txt -o "$OUTDIR/gobuster.txt"
else
  echo "[!] Directory enumeration tool (Dirb or Gobuster) not found"
fi

# Nikto Scan
if command -v nikto >/dev/null 2>&1; then
  echo "[*] Running Nikto..."
  nikto -h "$TARGET" > "$OUTDIR/nikto.txt"
else
  echo "[!] Nikto not found"
fi

# SSL Scan
if [[ "$TARGET" == https* || "$TARGET" == *443 ]]; then
  if command -v sslscan >/dev/null 2>&1; then
    echo "[*] Running SSLScan..."
    sslscan "$TARGET" > "$OUTDIR/sslscan.txt"
  fi
fi

echo "[+] Recon complete. Output saved to: $OUTDIR"
