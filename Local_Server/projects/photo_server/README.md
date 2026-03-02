# Photo Server

A local, self-hosted alternative to Google Photos with AI-powered features.

---

## Goal

Replace Google Photos with a private, local solution that supports:

- Photo and video upload from phones and computers
- Automatic face detection and recognition
- Object and scene classification
- Location-based organization (GPS metadata)
- Search by content ("find photos of dogs at the beach")
- Shared albums for the family
- Mobile app access

---

## Recommended Tool: Immich

[Immich](https://immich.app/) is the leading open-source Google Photos alternative. It supports GPU acceleration for ML features.

### Why Immich

- Active development, large community
- Mobile apps (iOS and Android)
- GPU-accelerated face detection and recognition
- CLIP-based smart search (search by description)
- Automatic backups from phone
- Shared libraries for families
- Self-hosted, all data stays local

---

## Architecture

```
Phone App (Immich)  -->  Immich Server  -->  PostgreSQL (metadata)
                              |
                              +-->  Redis (job queue)
                              +-->  ML Service (GPU) -- face detection, CLIP
                              +-->  /mnt/storage/photos/ (originals)
```

---

## Docker Compose (Starter Template)

```yaml
# docker-compose.yml
version: "3.8"

services:
  immich-server:
    image: ghcr.io/immich-app/immich-server:release
    container_name: immich_server
    restart: always
    ports:
      - "2283:2283"
    volumes:
      - /mnt/storage/photos:/usr/src/app/upload
      - /etc/localtime:/etc/localtime:ro
    environment:
      - DB_HOSTNAME=immich_postgres
      - DB_USERNAME=postgres
      - DB_PASSWORD=changeme
      - DB_DATABASE_NAME=immich
      - REDIS_HOSTNAME=immich_redis
    depends_on:
      - redis
      - database

  immich-machine-learning:
    image: ghcr.io/immich-app/immich-machine-learning:release
    container_name: immich_machine_learning
    restart: always
    volumes:
      - model-cache:/cache
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  redis:
    image: redis:7
    container_name: immich_redis
    restart: always

  database:
    image: tensorchord/pgvecto-rs:pg16-v0.2.1
    container_name: immich_postgres
    restart: always
    environment:
      - POSTGRES_PASSWORD=changeme
      - POSTGRES_USER=postgres
      - POSTGRES_DB=immich
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
  model-cache:
```

---

## Setup Steps

1. Create the photos storage directory:
   ```bash
   sudo mkdir -p /mnt/storage/photos
   sudo chown $USER:$USER /mnt/storage/photos
   ```
2. Copy the `docker-compose.yml` above and adjust passwords
3. Deploy:
   ```bash
   docker compose up -d
   ```
4. Access at `http://homeserver.local:2283`
5. Install the Immich app on your phone and connect to the server
6. Configure automatic backup from phone camera roll

---

## Storage Estimates

- Average photo: ~5 MB
- Average short video: ~50 MB
- 10,000 photos + 500 videos = ~75 GB
- The 2 TB HDD can hold ~400,000 photos at this rate

---

## Status

- [ ] Immich Docker Compose created
- [ ] Database initialized
- [ ] GPU ML service verified
- [ ] Mobile app connected
- [ ] Family members added
- [ ] Automatic backup enabled
