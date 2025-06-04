# Piso WiFi Controller

## Short Description & Significance
A self-hosted, coin-operated WiFi gateway designed for “Piso WiFi” setups. Devices connect to a captive portal, insert coins via a coin acceptor, and receive time-limited internet access. This project streamlines the entire flow—from device registration to time management and network enforcement—using a FastAPI backend and Linux networking tools. It empowers small businesses or informal vendors to offer pay-per-use WiFi without relying on proprietary hardware.

---

## Overview
The Piso WiFi Controller runs on a Linux SBC (e.g., Orange Pi or Raspberry Pi) and performs the following roles:
1. **Captive Portal Backend** (FastAPI):  
   - Registers devices by MAC address.  
   - Tracks time remaining and session status.  
   - Exposes endpoints for coin insertion, time queries, and device management.

2. **Network Manager** (Python + iptables):  
   - Reads the SQLite database to allow or block clients based on remaining time.  
   - Inserts custom iptables rules to ACCEPT or DROP traffic per MAC.  
   - Redirects new or expired clients to the captive portal landing page.

3. **Time Manager** (Python + cron/systemd):  
   - Decrements each device’s time_remaining at regular intervals.  
   - Automatically marks sessions as inactive when time expires.

4. **Coin Acceptor Integration**:  
   - Listens for pulses from a coin acceptor hardware module.  
   - On coin insertion, calls the FastAPI endpoint to add time to the corresponding MAC’s session.

5. **Captive Portal Frontend** (Static HTML/JS):  
   - Displays the user’s remaining time and buttons to insert coins.  
   - Automatically polls the backend to update time remaining in real time.  
   - Redirects all HTTP requests from unpaid or expired clients to the portal page.

---

## Features
- **MAC-Based Device Registration**  
  No personal data required—each device is tracked and billed by its MAC address.
  [x] Done

- **Coin-Operated Time Credit**  
  Insert ₱1 or ₱5 coins (or other denominations), which map to fixed time increments.
  [ ] Done

- **Automated Time Decrement**  
  Runs a scheduled task to subtract time at regular intervals and deactivate sessions upon expiration.
  [x] Done

- **Dynamic Firewall Rules**  
  Uses custom iptables chains to allow or block client traffic based on session status.
  [ ] Done

- **Captive Portal Redirect**  
  All new or expired devices are redirected to a landing page for payment/instruction.
  [ ] Done

- **Admin-Friendly API Endpoints**  
  CRUD operations for devices, querying session status, and force-ending sessions.
  [ ] Done

---

## Technologies Used
- **FastAPI** (Python) – Captive portal backend and REST API framework  
- **SQLite** – Lightweight relational database for device/session storage  
- **Python 3** – Core language for backend logic, network manager, and time manager  
- **iptables** – Linux firewall tool for per-MAC traffic control  
- **dnsmasq** – (Optional) DHCP/DNS server to assign IP addresses and redirect DNS queries  
- **Coin Acceptor Module** – Hardware interface delivering pulses on coin insertion  
- **HTML / JavaScript** – Captive portal frontend, displaying time-remaining and payment options  
- **systemd / cron** – Scheduling tools for automatic service startup and periodic tasks

---

## Roadmap & Plans

1. **Phase 1: Core Functionality (Completed)**  
   - Database schema and `DeviceService` for CRUD.  
   - FastAPI endpoints for saving devices, adding/reducing time, and fetching status.  
   - `time_manager.py` to decrement time periodically.  
   - `network_manager.py` to enforce iptables rules based on session state.  
   - Static HTML/JS portal that reads MAC from query and displays time remaining.

2. **Phase 2: Hardware Integration & Deployment**  
   - Integrate coin acceptor listener script to credit time automatically.  
   - Configure `dnsmasq` for DHCP and captive DNS redirection.  
   - Harden iptables rules for HTTPS redirection (optional).  
   - Automate startup via `setup.sh` to initialize port forwarding, iptables, and services.

3. **Phase 3: Improvements & Advanced Features**  
   - **SMS/QR Code Top-Up**  
     - Integrate with a local SMS API or Twilio for OTP verification.  
     - Generate voucher codes for one-time or recurring access.  
   - **Bandwidth Throttling**  
     - Use `tc` to limit per-client speeds, reducing tethering abuse.  
   - **Admin Dashboard**  
     - Build an Angular/React SPA to view active sessions, revenue, and logs in real time.  
   - **Usage Analytics & Reporting**  
     - Store transaction history and generate daily/weekly revenue reports.  
   - **Multi-Plan & Voucher System**  
     - Allow custom time packages and generate printable voucher stickers.  

4. **Phase 4: Scaling & Maintenance**  
   - Migrate to **PostgreSQL** (or MySQL) for larger deployments.  
   - Containerize services with Docker for easier updates and backup.  
   - Add automated backups of the database to a remote server.  
   - Implement failover mechanisms to handle SBC reboots without losing sessions.

---

> This project democratizes WiFi access by enabling low-cost, pay-per-use connectivity that can be deployed by entrepreneurs, small cafés, or remote community centers. It leverages open-source software and inexpensive SBC hardware to replace costly proprietary kiosks and subscription platforms. By combining FastAPI’s performance with Linux’s reliable networking tools, the Piso WiFi Controller provides a flexible, maintainable foundation for any coin- or voucher-based internet access service.
