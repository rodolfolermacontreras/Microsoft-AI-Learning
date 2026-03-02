# Planned Projects

Overview of all projects to be built and deployed on the home server.

---

## Project Pipeline

| # | Project | Stack | GPU Needed | Pi Integration | Priority |
|---|---|---|---|---|---|
| 1 | [Photo Server](photo_server/) | Immich, PostgreSQL, Redis | Yes (ML features) | No | High |
| 2 | [Music Server](music_server/) | Navidrome, Demucs, CDG tools | Yes (audio separation) | No | High |
| 3 | [Security Camera](security_camera/) | Frigate, HuggingFace, MQTT | Yes (detection) | Yes (camera feeds) | Medium |
| 4 | [Garden Monitor](garden_monitor/) | InfluxDB, Grafana, MQTT | No (optional ML) | Yes (sensors) | Medium |
| 5 | [Home Assistant](home_assistant/) | Home Assistant, MQTT, Zigbee | No | Yes (all devices) | Low (after others) |

---

## Development Approach

Each project follows the same pattern:

1. **Research** -- evaluate open-source options, pick the best fit
2. **Docker Compose** -- define the service stack in a `docker-compose.yml`
3. **Configuration** -- set environment variables, volumes, networking
4. **Deploy** -- `docker compose up -d`
5. **Test** -- verify from phone/laptop on the LAN
6. **Iterate** -- vibe code custom features or integrations with AI agents

---

## Shared Infrastructure

All projects share these base services (set up in [SERVER_SETUP.md](../SERVER_SETUP.md)):

- **Docker Engine** with NVIDIA Container Toolkit
- **Portainer** for container management
- **Mosquitto MQTT** for Pi-to-server messaging
- **Reverse proxy** (Nginx Proxy Manager or Caddy) for clean local URLs
