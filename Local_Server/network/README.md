# Network Architecture

How the home server, Raspberry Pis, and family devices communicate on the local network.

---

## Network Topology

```
Internet
    |
[Home Router / Wi-Fi AP]
    |
    +-- 192.168.x.10  Homeserver (HP Z440) -- Ethernet (primary) + Wi-Fi (backup)
    |
    +-- 192.168.x.20  Raspberry Pi #1 (Garden) -- Wi-Fi
    +-- 192.168.x.21  Raspberry Pi #2 (Camera) -- Wi-Fi or Ethernet
    +-- 192.168.x.22  Raspberry Pi #3 (Camera) -- Wi-Fi or Ethernet
    |
    +-- 192.168.x.100+ Family devices (phones, laptops, TVs) -- Wi-Fi
```

---

## IP Addressing

**Recommendation:** Assign static IPs (or DHCP reservations in your router) for the server and Pi nodes so addresses do not change.

| Device | IP (example) | Role |
|---|---|---|
| Home Router | 192.168.1.1 | Gateway + DHCP + Wi-Fi |
| HP Z440 Server | 192.168.1.10 | All services |
| Garden Pi | 192.168.1.20 | Sensors + MQTT |
| Camera Pi #1 | 192.168.1.21 | RTSP stream |
| Camera Pi #2 | 192.168.1.22 | RTSP stream |

Set static IP on the server (`/etc/netplan/01-netcfg.yaml`):

```yaml
network:
  version: 2
  ethernets:
    eno1:
      dhcp4: false
      addresses:
        - 192.168.1.10/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 1.1.1.1
```

Apply: `sudo netplan apply`

---

## Communication Protocols

| Protocol | Port | Use Case |
|---|---|---|
| **MQTT** | 1883 | Sensor data from Pis to server (lightweight, reliable) |
| **RTSP** | 554 / 8554 | Camera video streams to Frigate |
| **HTTP** | Various | Web UIs (Immich, Grafana, Navidrome, etc.) |
| **SSH** | 22 | Remote management of server and Pis |

---

## MQTT Topic Structure

Standardized topic naming for all Pi nodes:

```
home/
+-- garden/
|   +-- sensors          # Temperature, humidity, moisture readings (JSON)
|   +-- alerts           # Threshold alerts from Pi
+-- cameras/
|   +-- front_door       # Frigate events
|   +-- backyard         # Frigate events
+-- server/
    +-- status           # Server health metrics
    +-- alerts           # Service alerts
```

Example MQTT message:

```json
{
  "node": "garden-pi-1",
  "temperature_c": 24.5,
  "humidity": 62.3,
  "soil_moisture": 45,
  "timestamp": "2026-03-02T14:30:00Z"
}
```

---

## Raspberry Pi Setup Checklist

For each new Pi node:

1. Flash **Raspberry Pi OS Lite** (64-bit) using Raspberry Pi Imager
2. During flashing, configure:
   - Hostname (e.g., `garden-pi-1`)
   - Wi-Fi network and password
   - Enable SSH with your public key
   - Username and password
3. Boot the Pi and SSH in: `ssh pi@garden-pi-1.local`
4. Update: `sudo apt update && sudo apt upgrade -y`
5. Install Python + MQTT client: `pip install paho-mqtt`
6. Install sensor-specific libraries (DHT22, BH1750, etc.)
7. Deploy and enable the sensor script as a systemd service
8. Verify data appears on the MQTT broker: `mosquitto_sub -h homeserver.local -t "garden/#"`

---

## DNS / Local Hostnames

Use mDNS (`.local` addresses) for easy access without remembering IPs:

- `homeserver.local` -- the Z440
- `garden-pi-1.local` -- garden Raspberry Pi
- Avahi (mDNS) is built into Ubuntu and Raspberry Pi OS

Or set up a local DNS zone in your router if it supports it.

---

## Firewall (Server)

UFW rules on the server:

```bash
sudo ufw allow OpenSSH           # Port 22
sudo ufw allow 1883/tcp          # MQTT
sudo ufw allow 2283/tcp          # Immich
sudo ufw allow 3000/tcp          # Grafana
sudo ufw allow 4533/tcp          # Navidrome
sudo ufw allow 5000/tcp          # Frigate
sudo ufw allow 8086/tcp          # InfluxDB
sudo ufw allow 8123/tcp          # Home Assistant
sudo ufw allow 9443/tcp          # Portainer
sudo ufw enable
```

---

## Security Notes

- All services are **local network only** (no port forwarding to the internet)
- If you need remote access (outside the house), use a VPN (WireGuard or Tailscale)
- Change all default passwords before going live
- Keep the server and Pi OS updated regularly
