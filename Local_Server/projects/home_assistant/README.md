# Home Assistant

Central home automation hub that ties together all edge devices, cameras, sensors, and services.

---

## Goal

- Unified dashboard for the entire home (garden, cameras, music, lights, etc.)
- Automations (e.g., turn on lights at sunset, alert if camera detects a person at night)
- Integrate all Raspberry Pi nodes
- Mobile app for remote control
- Voice assistant integration (optional)

---

## Why Home Assistant

[Home Assistant](https://www.home-assistant.io/) is the most popular open-source home automation platform.

- Integrates with 2,000+ devices and services
- Runs in Docker
- Beautiful dashboards (Lovelace UI)
- Powerful automations (YAML or visual editor)
- Mobile app (iOS and Android)
- Integrates with MQTT (our Pi sensors), Frigate (cameras), and more

---

## Docker Compose

```yaml
# docker-compose.yml
version: "3.8"

services:
  homeassistant:
    image: ghcr.io/home-assistant/home-assistant:stable
    container_name: homeassistant
    restart: always
    privileged: true
    network_mode: host
    volumes:
      - /opt/server/data/homeassistant:/config
      - /etc/localtime:/etc/localtime:ro
    environment:
      - TZ=America/Chicago  # Adjust to your timezone
```

---

## Integrations Plan

| Integration | Purpose | How |
|---|---|---|
| **MQTT** | Receive sensor data from all Pi nodes | Built-in MQTT integration |
| **Frigate** | Camera events and object detection | Frigate integration (HACS) |
| **Immich** | (Optional) Show recent photos on dashboard | REST API |
| **InfluxDB** | Long-term sensor data history | InfluxDB integration |
| **Zigbee** | Smart lights, plugs, buttons (via USB dongle) | ZHA or Zigbee2MQTT |
| **Wi-Fi devices** | Smart plugs, bulbs, etc. | Various integrations |

---

## Setup Steps

1. Create config directory:
   ```bash
   sudo mkdir -p /opt/server/data/homeassistant
   sudo chown -R $USER:$USER /opt/server/data/homeassistant
   ```
2. Deploy:
   ```bash
   docker compose up -d
   ```
3. Access at `http://homeserver.local:8123`
4. Run through the onboarding wizard
5. Add MQTT integration (point to `localhost:1883`)
6. Add Frigate integration via HACS
7. Build dashboards

---

## Note

This is a lower-priority project. Deploy after Photo Server, Music Server, and Security Camera are running. Home Assistant then ties everything together into a single control plane.

---

## Status

- [ ] Home Assistant deployed
- [ ] MQTT integration configured
- [ ] Frigate integration connected
- [ ] Dashboard built
- [ ] Mobile app configured
- [ ] Automations set up
