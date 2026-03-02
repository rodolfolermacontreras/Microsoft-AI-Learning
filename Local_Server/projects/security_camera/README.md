# Security Camera Classifier

AI-powered security camera monitoring using HuggingFace models for person/animal/vehicle detection.

---

## Goal

- Monitor security cameras around the house
- Classify what appears in the feed (person, animal, vehicle, package, etc.)
- Send alerts when specific events are detected
- Record and review clips
- Use HuggingFace models for custom classification tasks
- Run detection on the GPU for real-time performance

---

## Components

### 1. Camera NVR: Frigate

[Frigate](https://frigate.video/) is an open-source NVR (Network Video Recorder) with real-time AI object detection.

**Why Frigate:**
- Built for home use with low latency
- GPU-accelerated object detection (NVIDIA supported)
- Integrates with Home Assistant
- Supports RTSP, ONVIF, and USB cameras
- Records only when events happen (saves storage)
- Zones, masks, and custom detection areas

### 2. Custom Classification: HuggingFace Models

For tasks beyond basic detection (e.g., "is this person a family member?"), use HuggingFace Transformers models:

- **YOLO** (object detection) -- fast, accurate, GPU-optimized
- **CLIP** (image-text matching) -- "is this a delivery person?"
- **Face recognition** -- identify specific people
- **Custom fine-tuned models** -- trained on your own data

---

## Architecture

```
Cameras (RTSP/USB)
        |
        v
  Frigate NVR (GPU detection)
        |
        +-- Detected events --> MQTT --> Home Assistant (alerts)
        +-- Clips/Snapshots --> /mnt/storage/cameras/
        +-- Custom pipeline --> HuggingFace model (classification)
                                    |
                                    v
                              MQTT notification / dashboard
```

---

## Docker Compose (Frigate)

```yaml
# docker-compose.yml
version: "3.8"

services:
  frigate:
    image: ghcr.io/blakeblackshear/frigate:stable
    container_name: frigate
    restart: always
    privileged: true
    shm_size: "256mb"
    ports:
      - "5000:5000"   # Web UI
      - "8554:8554"   # RTSP restream
      - "8555:8555"   # WebRTC
    volumes:
      - /opt/server/data/frigate/config:/config
      - /mnt/storage/cameras:/media/frigate
      - type: tmpfs
        target: /tmp/cache
        tmpfs:
          size: 1000000000
    environment:
      - FRIGATE_RTSP_PASSWORD=changeme
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=all
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### Frigate Config (config/config.yml)

```yaml
mqtt:
  host: homeserver.local  # Your MQTT broker
  port: 1883

detectors:
  ov:
    type: openvino
    device: GPU

cameras:
  front_door:
    ffmpeg:
      inputs:
        - path: rtsp://user:pass@192.168.1.100:554/stream
          roles:
            - detect
            - record
    detect:
      width: 1280
      height: 720
      fps: 5
    objects:
      track:
        - person
        - car
        - dog
        - cat
    record:
      enabled: true
      retain:
        days: 7
      events:
        retain:
          default: 14

  # Add more cameras as needed:
  # backyard:
  #   ...
```

---

## Custom HuggingFace Classification Pipeline

For advanced classification beyond Frigate's built-in detection:

```python
"""classify_camera_event.py -- Custom classifier for camera events."""

import torch
from PIL import Image
from transformers import pipeline

# Load a classification model (runs on GPU)
classifier = pipeline(
    "image-classification",
    model="google/vit-base-patch16-224",
    device=0,  # GPU
)

# Or use CLIP for open-vocabulary detection
clip_classifier = pipeline(
    "zero-shot-image-classification",
    model="openai/clip-vit-base-patch32",
    device=0,
)


def classify_snapshot(image_path: str) -> dict:
    """Classify a camera snapshot using ViT."""
    image = Image.open(image_path)
    results = classifier(image)
    return {r["label"]: round(r["score"], 3) for r in results[:5]}


def detect_custom_classes(image_path: str, labels: list[str]) -> dict:
    """Use CLIP for zero-shot classification with custom labels."""
    image = Image.open(image_path)
    results = clip_classifier(image, candidate_labels=labels)
    return {r["label"]: round(r["score"], 3) for r in results}


if __name__ == "__main__":
    # Example: classify a snapshot
    result = detect_custom_classes(
        "/mnt/storage/cameras/snapshots/front_door.jpg",
        labels=["delivery person", "family member", "stranger", "animal", "vehicle"],
    )
    print(result)
```

---

## Camera Options

| Type | Examples | Connection | Notes |
|---|---|---|---|
| IP Camera (RTSP) | Reolink, Amcrest, Hikvision | Ethernet/Wi-Fi via RTSP URL | Best quality and reliability |
| USB Webcam | Logitech C920/C930 | USB to server directly | Simple but limited to server location |
| Raspberry Pi Camera | Pi Camera Module v3 | Pi streams RTSP to server | Flexible placement, DIY |

### Raspberry Pi as Camera Node

```bash
# On the Pi: install and run an RTSP server
sudo apt install -y libcamera-apps
libcamera-vid -t 0 --inline --width 1280 --height 720 --framerate 15 \
  -o - | ffmpeg -i - -c:v copy -f rtsp rtsp://0.0.0.0:8554/camera
```

Then in Frigate config, use: `rtsp://pi_ip:8554/camera`

---

## Setup Steps

1. Create camera storage:
   ```bash
   sudo mkdir -p /mnt/storage/cameras
   sudo mkdir -p /opt/server/data/frigate/config
   sudo chown -R $USER:$USER /mnt/storage/cameras /opt/server/data/frigate
   ```
2. Write `config/config.yml` with your camera RTSP URLs
3. Deploy:
   ```bash
   docker compose up -d
   ```
4. Access Frigate UI at `http://homeserver.local:5000`
5. Verify cameras are streaming and detection is working
6. (Optional) Set up custom HuggingFace pipeline for advanced classification

---

## Status

- [ ] Camera(s) purchased and installed
- [ ] Frigate Docker Compose created
- [ ] Frigate config with camera URLs
- [ ] GPU detection verified
- [ ] Recording working (events saved to /mnt/storage)
- [ ] MQTT alerts connected
- [ ] Custom HuggingFace classifier tested
