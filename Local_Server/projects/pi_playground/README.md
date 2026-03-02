# Pi Playground -- Toys, Games, and Gadgets for Kids

Raspberry Pi-based physical computing projects that the whole family can play with. The server provides the brain (ML models, game logic, APIs), and the Pis provide the body (motors, LEDs, screens, buttons).

---

## Project Ideas

| Idea | Hardware | Server Role | Difficulty |
|---|---|---|---|
| RC Car with camera | Pi + motor HAT + Pi Camera | Stream video to phone; optional obstacle detection via ML | Beginner |
| LED light show | Pi + NeoPixel strip + button | Music-reactive visualizer; Navidrome sends audio data | Beginner |
| Retro game console | Pi + controllers + TV | RetroPie; server hosts ROM library and save backups | Beginner |
| Voice-controlled robot | Pi + microphone + motors | Server runs Whisper (speech-to-text) + command parser | Intermediate |
| Treasure hunt game | Pi + GPS module + screen | Server generates clues via OpenAI API; Pi shows hints | Intermediate |
| Drawing robot (plotter) | Pi + stepper motors + pen holder | Server generates SVG from text prompt (DALL-E or Stable Diffusion) | Intermediate |
| Smart piggy bank | Pi + coin sensor + e-ink display | Server tracks savings in a database; sends encouragement via speaker | Beginner |

---

## Architecture Pattern

```
+-------------------+         Wi-Fi / MQTT          +------------------+
|   HP Z440 Server  | <---------------------------> |  Raspberry Pi    |
|                   |                                |                  |
|  - ML inference   |    Command: "turn left"        |  - Motors        |
|  - Game logic     |    Sensor: camera frame        |  - Camera        |
|  - API calls      |    Audio: voice clip           |  - LEDs          |
|  - Data storage   |    Response: text / image      |  - Buttons       |
+-------------------+                                +------------------+
```

Communication options:
- **MQTT** for lightweight commands and sensor data (recommended)
- **HTTP/REST** for larger payloads (images, audio files)
- **WebSocket** for real-time streaming (video, game state)

---

## Getting Started (RC Car Example)

### Parts List (per car)

| Part | Est. Price |
|---|---|
| Raspberry Pi 4 (2 GB or 4 GB) | $35-55 |
| Motor driver HAT (L298N or Adafruit Motor HAT) | $15-25 |
| 4WD robot car chassis kit (with motors + wheels) | $15-25 |
| Pi Camera Module or USB webcam | $15-30 |
| Battery pack (6x AA or LiPo + regulator) | $10-15 |
| Jumper wires + breadboard | $5 |
| **Total per car** | **$95-155** |

### Software Stack

**On the Pi:**

```python
# car_controller.py
# Listens for MQTT commands and drives motors

import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

# Motor pins (adjust for your HAT)
MOTOR_LEFT_FWD = 17
MOTOR_LEFT_REV = 18
MOTOR_RIGHT_FWD = 22
MOTOR_RIGHT_REV = 23

GPIO.setmode(GPIO.BCM)
for pin in [MOTOR_LEFT_FWD, MOTOR_LEFT_REV, MOTOR_RIGHT_FWD, MOTOR_RIGHT_REV]:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)


def drive(direction: str) -> None:
    """Set motor pins based on direction command."""
    GPIO.output(MOTOR_LEFT_FWD, GPIO.LOW)
    GPIO.output(MOTOR_LEFT_REV, GPIO.LOW)
    GPIO.output(MOTOR_RIGHT_FWD, GPIO.LOW)
    GPIO.output(MOTOR_RIGHT_REV, GPIO.LOW)

    if direction == "forward":
        GPIO.output(MOTOR_LEFT_FWD, GPIO.HIGH)
        GPIO.output(MOTOR_RIGHT_FWD, GPIO.HIGH)
    elif direction == "backward":
        GPIO.output(MOTOR_LEFT_REV, GPIO.HIGH)
        GPIO.output(MOTOR_RIGHT_REV, GPIO.HIGH)
    elif direction == "left":
        GPIO.output(MOTOR_RIGHT_FWD, GPIO.HIGH)
    elif direction == "right":
        GPIO.output(MOTOR_LEFT_FWD, GPIO.HIGH)
    elif direction == "stop":
        pass  # all LOW already


def on_message(client, userdata, msg):
    command = msg.payload.decode()
    print(f"Received: {command}")
    drive(command)


client = mqtt.Client()
client.connect("homeserver.local", 1883)
client.subscribe("home/toys/car1/command")
client.on_message = on_message
client.loop_forever()
```

**On the server (web controller):**

A simple web page with arrow buttons that publishes MQTT messages. Can be built with Flask + paho-mqtt in under 50 lines.

---

## Tips

- Start with the simplest project (LED strip or RC car) to learn the Pi + MQTT + server pattern
- Once the pattern clicks, every new toy is just a variation: different sensors, different actuators, same communication flow
- Let the kids help with wiring and testing -- visible LEDs and moving motors are great for learning
- Use the server's GPU only when you need ML (voice control, image recognition); most toy projects are CPU-only on both ends

---

## Status

- [ ] First Pi toy project selected
- [ ] Parts ordered
- [ ] MQTT communication tested (Pi to server)
- [ ] Working prototype
