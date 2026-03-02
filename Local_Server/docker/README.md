# Docker Strategy

How all services are organized and managed using Docker and Docker Compose on the home server.

---

## Directory Layout

```
/opt/server/
+-- data/                        # All persistent data (on SSD)
|   +-- portainer/               # Portainer config
|   +-- mosquitto/               # MQTT broker data
|   +-- immich/                  # Immich (photo server)
|   +-- navidrome/               # Music server config
|   +-- frigate/                 # Camera NVR config
|   +-- influxdb/                # Time-series DB
|   +-- grafana/                 # Dashboard config
|   +-- telegraf/                # MQTT-to-InfluxDB bridge
|   +-- homeassistant/           # Home Assistant config
+-- compose/                     # Docker Compose files
    +-- core.yml                 # Portainer + MQTT + reverse proxy
    +-- photos.yml               # Immich stack
    +-- music.yml                # Navidrome
    +-- cameras.yml              # Frigate
    +-- monitoring.yml           # InfluxDB + Grafana + Telegraf
    +-- homeassistant.yml        # Home Assistant

/mnt/storage/                    # Bulk data (on 2 TB HDD)
+-- photos/                      # Immich photo uploads
+-- music/                       # Music library + karaoke output
+-- cameras/                     # Frigate recordings and clips
```

---

## Naming Conventions

| Convention | Rule |
|---|---|
| Container names | Lowercase, descriptive (`immich_server`, `navidrome`, `frigate`) |
| Compose files | Named by function (`photos.yml`, `music.yml`) |
| Volumes | Bind mounts to `/opt/server/data/<service>/` |
| Networks | Use default bridge; explicit networks only if isolation needed |

---

## Common Commands

```bash
# Start a service stack
docker compose -f compose/photos.yml up -d

# Stop a service
docker compose -f compose/photos.yml down

# View logs
docker logs -f immich_server

# Check all running containers
docker ps

# Live resource usage
docker stats

# Pull latest images and recreate
docker compose -f compose/photos.yml pull
docker compose -f compose/photos.yml up -d

# Clean up unused images
docker image prune -f
```

---

## GPU Access in Containers

Any container needing the RTX 3080 must include this in its compose file:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

Or run with `--gpus all` flag:

```bash
docker run --gpus all my-gpu-image
```

Requires the NVIDIA Container Toolkit to be installed (see [SERVER_SETUP.md](../SERVER_SETUP.md)).

---

## Port Map

| Port | Service | Notes |
|---|---|---|
| 22 | SSH | Remote access |
| 1883 | Mosquitto MQTT | Pi-to-server messaging |
| 2283 | Immich | Photo server web UI |
| 3000 | Grafana | Dashboards |
| 4533 | Navidrome | Music streaming |
| 5000 | Frigate | Camera NVR web UI |
| 8086 | InfluxDB | Time-series API |
| 8123 | Home Assistant | Home automation |
| 9443 | Portainer | Container management |

---

## Backup Strategy

- **Config data** (`/opt/server/data/`): Weekly backup to external USB drive or network share
- **Media** (`/mnt/storage/`): Periodic sync to external drive for critical files
- **Docker volumes**: Use `docker run --rm -v <volume>:/source -v /backup:/target alpine tar czf /target/backup.tar.gz /source`
