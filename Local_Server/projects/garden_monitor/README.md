# Garden Monitor

Raspberry Pi-based garden monitoring system with server-side data storage, dashboards, and optional ML-powered plant health analysis.

---

## Goal

- Monitor garden conditions (temperature, humidity, soil moisture, light)
- Visualize data on a real-time dashboard accessible from any device
- Set up alerts for out-of-range conditions (too dry, too hot, frost warning)
- Optionally: use camera + ML to monitor plant health
- Raspberry Pi nodes in the garden send data to the home server

---

## Architecture

```
Garden (outdoors)                    Home Server (indoors)
+----------------+                   +------------------------+
| Raspberry Pi   |                   | InfluxDB (time series) |
| + Sensors      | --MQTT/Wi-Fi-->   | Grafana (dashboards)   |
| + Camera (opt) |                   | Mosquitto (MQTT broker)|
+----------------+                   | Alert service          |
                                     +------------------------+
                                              |
                                         Web browser
                                     (phone / laptop / TV)
```

---

## Components

### Server Side (Docker on Z440)

| Service | Purpose |
|---|---|
| **Mosquitto** | MQTT broker -- receives sensor data from Pi(s) |
| **InfluxDB** | Time-series database -- stores sensor readings |
| **Grafana** | Dashboards -- visualize temperature, moisture, etc. |
| **Telegraf** | (Optional) Routes MQTT data into InfluxDB automatically |

### Raspberry Pi Side

| Component | Purpose | Approx Cost |
|---|---|---|
| Raspberry Pi 4/5 | Edge compute node | ~$50-80 |
| DHT22 sensor | Temperature + humidity | ~$5-10 |
| Soil moisture sensor | Soil moisture level | ~$3-5 |
| BH1750 light sensor | Light intensity (lux) | ~$3-5 |
| Pi Camera Module v3 | (Optional) Plant photos for ML | ~$25-35 |
| Waterproof enclosure | Protect Pi from weather | ~$10-15 |
| Power supply | USB-C power for the Pi | ~$10 |

---

## Docker Compose (Server Side)

```yaml
# docker-compose.yml
version: "3.8"

services:
  influxdb:
    image: influxdb:2
    container_name: influxdb
    restart: always
    ports:
      - "8086:8086"
    volumes:
      - /opt/server/data/influxdb:/var/lib/influxdb2
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=changeme123
      - DOCKER_INFLUXDB_INIT_ORG=home
      - DOCKER_INFLUXDB_INIT_BUCKET=garden

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: always
    ports:
      - "3000:3000"
    volumes:
      - /opt/server/data/grafana:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=changeme
    depends_on:
      - influxdb

  telegraf:
    image: telegraf:latest
    container_name: telegraf
    restart: always
    volumes:
      - /opt/server/data/telegraf/telegraf.conf:/etc/telegraf/telegraf.conf:ro
    depends_on:
      - influxdb
```

### Telegraf Config (telegraf.conf)

```toml
# Listen for MQTT messages from Raspberry Pi sensors
[[inputs.mqtt_consumer]]
  servers = ["tcp://homeserver.local:1883"]
  topics = ["garden/#"]
  data_format = "json"

# Write to InfluxDB
[[outputs.influxdb_v2]]
  urls = ["http://influxdb:8086"]
  token = "your-influxdb-token"
  organization = "home"
  bucket = "garden"
```

---

## Raspberry Pi Sensor Code

### Install Dependencies (on the Pi)

```bash
pip install paho-mqtt adafruit-circuitpython-dht board
```

### Sensor Reader Script

```python
"""garden_sensor.py -- Read sensors and publish to MQTT."""

import json
import time

import adafruit_dht
import board
import paho.mqtt.client as mqtt

# Configuration
MQTT_BROKER = "homeserver.local"     # Your server's hostname or IP
MQTT_PORT = 1883
MQTT_TOPIC = "garden/sensors"
READ_INTERVAL = 60                   # Seconds between readings

# Initialize DHT22 sensor on GPIO pin 4
dht_sensor = adafruit_dht.DHT22(board.D4)

# MQTT client
client = mqtt.Client(client_id="garden-pi-1")
client.connect(MQTT_BROKER, MQTT_PORT)


def read_sensors() -> dict:
    """Read all connected sensors and return data dict."""
    try:
        temperature_c = dht_sensor.temperature
        humidity = dht_sensor.humidity
    except RuntimeError:
        temperature_c = None
        humidity = None

    return {
        "node": "garden-pi-1",
        "temperature_c": temperature_c,
        "temperature_f": round(temperature_c * 9 / 5 + 32, 1) if temperature_c else None,
        "humidity": humidity,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def main() -> None:
    """Main loop: read sensors, publish to MQTT."""
    print(f"Garden sensor started. Publishing to {MQTT_BROKER}:{MQTT_PORT}")
    while True:
        data = read_sensors()
        payload = json.dumps(data)
        client.publish(MQTT_TOPIC, payload)
        print(f"Published: {payload}")
        time.sleep(READ_INTERVAL)


if __name__ == "__main__":
    main()
```

### Run as a Service (systemd)

```ini
# /etc/systemd/system/garden-sensor.service
[Unit]
Description=Garden Sensor MQTT Publisher
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/garden_sensor.py
Restart=always
User=pi
WorkingDirectory=/home/pi

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable garden-sensor
sudo systemctl start garden-sensor
```

---

## Grafana Dashboard

After deploying, configure Grafana:

1. Access `http://homeserver.local:3000`
2. Add InfluxDB as a data source (URL: `http://influxdb:8086`, org: `home`, bucket: `garden`)
3. Create a dashboard with panels:
   - **Temperature gauge** (current reading)
   - **Temperature line chart** (24h history)
   - **Humidity gauge** (current reading)
   - **Soil moisture bar** (if sensor connected)
4. Set up alerts: notify when temperature drops below 35F (frost) or soil moisture is critically low

---

## Setup Steps

1. Server side:
   ```bash
   sudo mkdir -p /opt/server/data/{influxdb,grafana,telegraf}
   sudo chown -R $USER:$USER /opt/server/data/{influxdb,grafana,telegraf}
   docker compose up -d
   ```
2. Pi side:
   - Flash Raspberry Pi OS Lite to an SD card
   - Enable Wi-Fi and SSH during flashing (Raspberry Pi Imager settings)
   - Connect sensors to GPIO pins
   - Install Python dependencies and the sensor script
   - Enable the systemd service

---

## Status

- [ ] InfluxDB + Grafana + Telegraf deployed
- [ ] MQTT integration tested
- [ ] Raspberry Pi set up with sensors
- [ ] Sensor data flowing to InfluxDB
- [ ] Grafana dashboard built
- [ ] Alerts configured
