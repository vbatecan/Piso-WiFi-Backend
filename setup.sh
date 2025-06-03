#!/usr/bin/env bash

# Exit on any error, because every command is important
set -e

# Enable IPv4 forwarding (temporary)
echo "[+] Enabling IPv4 forwarding..."
sysctl -w net.ipv4.ip_forward=1

# Make it persistent across reboots
echo "[+] Making IPv4 forwarding persistent..."
sudo sed -i '/^#*net.ipv4.ip_forward/s/^#*//' /etc/sysctl.conf
sudo sed -i '/net.ipv4.ip_forward/ s/=.*/=1/' /etc/sysctl.conf
sudo sysctl -p

# * Your interfaces (adjust as needed)
WAN_IFACE="eth0"     # Internet source (Ethernet or USB dongle)
LAN_IFACE="eth1"     # Connected to WiFi router or Access Point

# Flush old rules
echo "[+] Flushing iptables rules..."
sudo iptables -F
sudo iptables -t nat -F

# Set up NAT (internet sharing from WAN → LAN), the orange pi or the raspberry pi is in the middle of the network
echo "[+] Setting up NAT..."
sudo iptables -t nat -A POSTROUTING -o "$WAN_IFACE" -j MASQUERADE
sudo iptables -A FORWARD -i "$WAN_IFACE" -o "$LAN_IFACE" -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i "$LAN_IFACE" -o "$WAN_IFACE" -j ACCEPT

# Save iptables rules (for persistence, depends on distro)
if command -v netfilter-persistent &> /dev/null; then
    echo "[+] Saving iptables rules..."
    sudo netfilter-persistent save
elif command -v iptables-save &> /dev/null; then
    echo "[!] Consider saving rules manually: sudo iptables-save > /etc/iptables/rules.v4"
fi

echo "[✓] Setup completed."