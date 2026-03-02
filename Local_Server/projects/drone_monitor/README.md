# Drone Monitor -- Autonomous Garden Surveillance

A small camera drone (or ground rover) that patrols the garden on a schedule, captures images, and sends them to the server for ML-based classification (plant health, pest detection, intruder alerts).

---

## Concept

```
+-----------+     Wi-Fi      +------------------+
|   Drone   | ------------> |   HP Z440 Server  |
|  (Pi +    |   Photos via  |                   |
|   Camera) |   MQTT/HTTP   |  - Classify image |
|           |               |  - Store in DB    |
|           | <------------ |  - Alert if issue |
+-----------+   Commands    +------------------+
                                     |
                              Grafana dashboard
                              + phone notification
```

---

## Hardware Options

### Option A: Camera Drone (aerial)

| Part | Est. Price | Notes |
|---|---|---|
| Pre-built programmable drone (Tello EDU or CoDrone) | $100-150 | Tello has a Python SDK; great for beginners |
| OR: DIY drone frame + Pi Zero 2W + flight controller | $150-250 | More complex but fully custom |
| Extra batteries | $20-40 | Tello gets ~13 min per battery |

### Option B: Ground Rover (simpler, no FAA concerns)

| Part | Est. Price | Notes |
|---|---|---|
| Raspberry Pi 4 (2-4 GB) | $35-55 | |
| 4WD rover chassis + motors | $25-40 | Weatherproof chassis recommended |
| Pi Camera Module (wide angle) | $20-30 | |
| Battery pack (rechargeable) | $15-25 | USB power bank or LiPo |
| Motor driver (L298N) | $10 | |
| **Rover total** | **$105-160** | |

**Recommendation:** Start with Option B (ground rover). Simpler to build, no flight regulations, easier to debug, and captures garden images at plant level. Upgrade to aerial later if desired.

---

## Software Architecture

### On the Rover (Raspberry Pi)

```python
# rover_patrol.py
# Drives a preset route, takes photos, sends to server

import time
import paho.mqtt.client as mqtt
from picamera2 import Picamera2
import base64
import json

MQTT_HOST = "homeserver.local"
MQTT_PORT = 1883
PHOTO_TOPIC = "home/garden/drone/photos"
STATUS_TOPIC = "home/garden/drone/status"

camera = Picamera2()
camera.configure(camera.create_still_configuration())

client = mqtt.Client()
client.connect(MQTT_HOST, MQTT_PORT)


def capture_and_send(location_tag: str) -> None:
    """Capture a photo and publish it to MQTT as base64."""
    camera.start()
    time.sleep(1)
    image_array = camera.capture_array()
    camera.stop()

    # Encode as JPEG bytes then base64
    from PIL import Image
    import io
    img = Image.fromarray(image_array)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=80)
    b64_image = base64.b64encode(buffer.getvalue()).decode()

    payload = json.dumps({
        "location": location_tag,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "image_b64": b64_image,
    })
    client.publish(PHOTO_TOPIC, payload)
    print(f"Sent photo from {location_tag}")


# Simple waypoint patrol (replace with motor control for real rover)
waypoints = ["garden_north", "garden_south", "garden_east", "flower_bed"]

for wp in waypoints:
    # TODO: drive to waypoint using motor commands
    capture_and_send(wp)
    time.sleep(5)

client.publish(STATUS_TOPIC, "patrol_complete")
client.disconnect()
```

### On the Server (classification pipeline)

```python
# classify_garden_image.py
# Subscribes to drone photos, runs classification, stores results

import paho.mqtt.client as mqtt
import json
import base64
from PIL import Image
import io
import torch
from transformers import pipeline

# Load a zero-shot image classifier (runs on GPU)
classifier = pipeline(
    "zero-shot-image-classification",
    model="openai/clip-vit-base-patch32",
    device=0,
)

LABELS = [
    "healthy plant",
    "diseased plant",
    "pest damage",
    "dry soil",
    "weed",
    "animal in garden",
    "normal ground",
]


def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    image_bytes = base64.b64decode(data["image_b64"])
    image = Image.open(io.BytesIO(image_bytes))

    results = classifier(image, candidate_labels=LABELS)
    top_label = results[0]["label"]
    top_score = results[0]["score"]

    print(f"[{data['location']}] {top_label} ({top_score:.2f})")

    # Store result (InfluxDB, SQLite, or file)
    # Alert if pest/disease detected
    if top_label in ["diseased plant", "pest damage"] and top_score > 0.5:
        print(f"ALERT: {top_label} detected at {data['location']}")
        # TODO: send notification (Home Assistant, email, etc.)


client = mqtt.Client()
client.connect("localhost", 1883)
client.subscribe("home/garden/drone/photos")
client.on_message = on_message
client.loop_forever()
```

---

## Patrol Schedule

Use a cron job or systemd timer on the Pi:

```bash
# Every morning at 7:00 AM
0 7 * * * /usr/bin/python3 /home/pi/rover_patrol.py
```

Or trigger patrols on demand via MQTT from Home Assistant or a phone button.

---

## Future Enhancements

- Train a custom plant health model on your own garden photos (fine-tune on the server GPU)
- Add soil moisture sensor to the rover (sample soil at each waypoint)
- Time-lapse: stitch daily photos into weekly growth animations
- Upgrade to aerial drone for overhead canopy shots

---

## Status

- [ ] Rover hardware assembled
- [ ] Camera captures and sends photos via MQTT
- [ ] Server classification pipeline running
- [ ] Grafana dashboard showing patrol results
- [ ] Automated daily patrol schedule
