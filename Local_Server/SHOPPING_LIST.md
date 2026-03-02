# Shopping List -- $1,000 Budget (Everything Included)

A single, prioritized buying guide that fits the HP Z440 server, networking,
AND an initial Raspberry Pi starter kit into a $1,000 total budget.

Organized as **Phase 1** (buy now, get building) and **Phase 2** (add later as
projects grow). Every dollar is accounted for.

---

## Budget Summary

| Category | Phase 1 Cost | Notes |
|---|---|---|
| Server core (Z440 + RTX 3080) | $660-750 | The workhorse |
| Storage (1 TB SSD) | $55 | System drive |
| Networking (Wi-Fi + cables) | $35 | Wireless + wired |
| USB hub | $25 | For Pi, drives, dongles |
| Cooling + power | $35 | Quiet operation + surge protector |
| Raspberry Pi starter kit | $90-110 | 1 Pi + sensors + accessories |
| **TOTAL** | **$900-1,010** | Target: under $1,000 |

Savings levers if you go over $1,000:
- Skip the extra case fan (-$12) -- the Z440 stock cooling is adequate at first
- Use a basic power strip instead of a surge protector (-$10)
- Start with a Pi Zero 2W instead of Pi 4 (-$20)
- Hunt harder on eBay for the Z440 or RTX 3080 (prices vary by $50+ weekly)

---

## Phase 1 -- Buy Now ($1,000)

### 1. HP Z440 Workstation Tower -- $350-400

This is the foundation. Buy refurbished from eBay or a reputable refurb seller.

| Spec | Minimum | Ideal |
|---|---|---|
| CPU | Xeon E5-1620 v3 (4C/8T) | E5-1650 v3 (6C/12T) or better |
| RAM | 16 GB DDR4 ECC | 32 GB DDR4 ECC |
| Storage | Any HDD included | 2 TB HDD |
| PSU | 700 W (NOT the 525 W variant) | 700 W |
| GPU | None / basic Quadro (remove it) | None |
| OS | Any or none | Does not matter -- installing Ubuntu |

**eBay search strings (copy-paste these):**
```
HP Z440 Xeon 32GB 700W tower -SFF
HP Z440 E5-1650 v3 32GB workstation
HP Z440 workstation 32GB DDR4 tower
HP Z440 E5-1630 v3 32GB no GPU
```

**Red flags -- skip the listing if:**
- PSU is 525 W (not enough for RTX 3080)
- Small Form Factor (SFF) chassis -- GPU will not fit
- Stock photos only, no actual pictures of the unit
- Seller has less than 95% positive feedback
- No return policy

**Green flags -- good listing signs:**
- "Tested and working" with actual boot photo
- 700 W PSU confirmed in description or photos
- 32 GB RAM already installed (saves $50-70)
- Located domestically (cheaper + faster shipping)

**IMPORTANT: If RAM is only 16 GB**, add a 16 GB DDR4 ECC RDIMM kit (~$25-35
used). Search: `DDR4 2133 ECC RDIMM 16GB HP Z440`

---

### 2. Used NVIDIA RTX 3080 -- $300-350

The GPU for ML inference, photo classification, audio separation, and local LLM
experiments. The 10 GB VRAM version is fine (12 GB variant costs more and is
harder to find).

| Spec | Value |
|---|---|
| VRAM | 10 GB GDDR6X (standard) |
| TDP | ~320 W |
| Power connectors | 2x 8-pin PCIe |
| Physical size | 2-slot preferred (some 2.5-slot models also fit) |

**eBay search strings:**
```
RTX 3080 10GB used tested working
RTX 3080 10GB -3080Ti -FE -3090
NVIDIA RTX 3080 used GPU working
EVGA RTX 3080 used  
MSI RTX 3080 used
```

**Before buying, verify:**
- "Tested and working" in description
- Photos show the actual card (not stock images)
- All fans visible and intact
- Ask seller about mining history (light mining is usually OK; heavy 24/7 mining
  means worn fans and thermal paste)
- Dual 8-pin power connectors visible
- Seller accepts returns (at least 14 days)

**Budget tip:** EVGA and Zotac cards tend to be cheaper than ASUS/MSI.
Filter eBay by "Buy It Now" + "Free Shipping" + price low-to-high.

---

### 3. Storage: 1 TB SATA SSD -- $55

The system drive for Ubuntu, Docker images, code, and active project data.
The Z440's included HDD stays for bulk media (photos, music, camera clips).

| Option | Price | Notes |
|---|---|---|
| Crucial MX500 1 TB | ~$55 | Best value, reliable |
| Samsung 870 EVO 1 TB | ~$60 | Slightly faster |
| WD Blue 1 TB SATA | ~$55 | Also solid |

Buy new (SSDs are cheap enough that used is not worth the risk).

**Search:** `1TB SATA SSD 2.5 inch` on Amazon or Newegg.

---

### 4. Networking -- $35

#### 4a. PCIe Wi-Fi 6 Card with Bluetooth -- $25

Plugs into a spare PCIe x1 slot on the Z440. Gives the server wireless
connectivity plus Bluetooth for future peripherals.

| Option | Price | Features |
|---|---|---|
| TP-Link Archer TX3000E | ~$25-30 | Wi-Fi 6, Bluetooth 5.0, 2 antennas |
| Intel AX200 based card (generic) | ~$15-20 | Wi-Fi 6, Bluetooth 5.0 |
| Fenvi FV-AX3000 | ~$20-25 | Wi-Fi 6, Bluetooth 5.0 |

**Search:** `PCIe WiFi 6 Bluetooth desktop card AX200` on Amazon.

**Note:** Even though the Z440 has built-in Gigabit Ethernet, Wi-Fi is useful for:
- Initial setup before running Ethernet cable
- Fallback if wired connection has issues
- Bluetooth for wireless keyboard during setup
- Communicating with Pi devices on the same Wi-Fi network

#### 4b. Ethernet Cables (2-3 pcs) -- $10

| Cable | Use |
|---|---|
| Cat 6, 6 ft | Server to router/switch |
| Cat 6, 10 ft | Spare / Pi connection |
| Cat 6, 25 ft (optional) | If router is far from server |

**Search:** `Cat 6 ethernet cable pack` on Amazon (~$10 for a 3-pack).

---

### 5. Powered USB 3.0 Hub -- $25

External hub with its own power supply. Keeps USB peripherals from draining
the Z440's ports and provides enough power for Pi boards if you want to
power one directly from the hub during development.

| Option | Price | Ports |
|---|---|---|
| Anker 7-Port USB 3.0 Hub (powered) | ~$25 | 7x USB-A |
| Amazon Basics 7-Port USB 3.0 Hub | ~$22 | 7x USB-A |
| Sabrent 7-Port USB 3.0 Hub | ~$20 | 7x USB-A |

**Search:** `powered USB 3.0 hub 7 port` on Amazon.

---

### 6. Cooling + Power -- $35

#### 6a. Quiet 120 mm Case Fan (1 pc) -- $12

One additional intake fan for the front of the Z440. Keeps the RTX 3080
cooler so its own fans do not ramp to full speed (which is loud).

| Option | Price | Noise |
|---|---|---|
| Arctic P12 PWM | ~$8 | Very quiet, great value |
| Noctua NF-P12 redux | ~$14 | Premium, near-silent |
| be quiet! Pure Wings 2 | ~$12 | Very quiet |

**Search:** `120mm quiet case fan PWM` on Amazon.

Buy just ONE fan to start. Add a second later if temperatures are high.

#### 6b. Surge Protector -- $15

Protects the server, USB hub, and router from power spikes.

| Option | Price | Notes |
|---|---|---|
| Any 6-outlet surge protector | ~$15 | 1000+ joule rating |
| With USB ports | ~$18 | Handy for charging |

#### 6c. Thermal Paste (optional) -- $8

Only needed if you re-seat the CPU cooler. Skip this unless the Z440 runs hot
after initial testing.

---

### 7. Raspberry Pi Starter Kit -- $90-110

This is your **first edge node**. Use it for the garden monitor project
(highest Pi priority per the project pipeline), then reuse for other projects
or buy additional Pis later.

#### 7a. Raspberry Pi Board -- $45-55

| Option | Price | RAM | Best For |
|---|---|---|---|
| Raspberry Pi 4 Model B (4 GB) | ~$55 | 4 GB | General use, camera, sensors |
| Raspberry Pi 4 Model B (2 GB) | ~$45 | 2 GB | Sensors only (no camera/ML) |
| Raspberry Pi 5 (4 GB) | ~$60 | 4 GB | More power, but costs more |

**Recommendation:** Raspberry Pi 4 (4 GB) -- best balance of capability and cost.
The 4 GB model handles camera streaming, sensor reading, and running MQTT client
code comfortably.

**Search:** `Raspberry Pi 4 Model B 4GB` on Amazon or Adafruit.

#### 7b. Pi Essentials -- $25-30

These are required to run the Pi. Buy as a bundle if possible.

| Item | Price | Notes |
|---|---|---|
| USB-C power supply (5V 3A, official or CanaKit) | ~$8 | Must be 3A or higher for Pi 4 |
| MicroSD card (32 GB, Class 10 / A1) | ~$8 | SanDisk or Samsung; 32 GB is plenty |
| Pi case (with fan or passive cooling) | ~$8 | Protects the board; Argon or Flirc are great |
| Micro-HDMI to HDMI cable (for initial setup) | ~$5 | Only needed once to configure Wi-Fi/SSH |

**Search:** `CanaKit Raspberry Pi 4 starter kit` (often bundles all of the above
for ~$25-30, sometimes cheaper than buying separately).

**Pro tip:** After the initial setup (configure Wi-Fi + enable SSH), you never
need a monitor/keyboard on the Pi again. Everything runs headless, just like the
server.

#### 7c. Sensors for Garden Monitor Project -- $15-25

The first project using the Pi. These sensors connect directly to the Pi's GPIO
pins with jumper wires.

| Sensor | Price | What It Measures | GPIO Connection |
|---|---|---|---|
| DHT22 (AM2302) | ~$5-8 | Temperature + humidity | Digital, 1 pin + power |
| Soil moisture sensor (capacitive) | ~$3-5 | Soil water content | Analog via ADS1115 ADC |
| ADS1115 ADC module | ~$3-5 | Converts analog to digital | I2C (SDA + SCL pins) |
| Jumper wires (M-F, 40 pcs) | ~$3 | Connect sensors to GPIO | Various |
| Mini breadboard | ~$2 | Prototyping connections | N/A |

**Search:** `DHT22 sensor module Arduino` and `capacitive soil moisture sensor`
on Amazon. These are the same sensors used for Arduino projects -- they work
identically with the Pi.

**Optional add-on (buy later):**
- BH1750 light sensor (~$3) -- measures sunlight intensity
- Pi Camera Module v3 (~$25-35) -- plant health photos for ML classification
- Waterproof enclosure (~$10-15) -- for permanent outdoor deployment

---

## Phase 1 Total Budget Breakdown

```
PHASE 1 -- BUY NOW
===================

SERVER CORE:
  HP Z440 tower (32 GB, 700W PSU)            $350-400
  NVIDIA RTX 3080 10 GB (used)               $300-350
  1 TB SATA SSD (new)                        $55
                                         Subtotal: $705-805

NETWORKING + USB:
  PCIe Wi-Fi 6 + Bluetooth card              $20-25
  Ethernet cables (3-pack)                   $10
  Powered USB 3.0 hub (7-port)              $22-25
                                         Subtotal: $52-60

COOLING + POWER:
  120 mm quiet case fan (1 pc)               $10-12
  Surge protector                            $15
                                         Subtotal: $25-27

RASPBERRY PI STARTER:
  Pi 4 Model B (4 GB)                        $55
  Power supply + SD card + case + cable      $25-30
  DHT22 + soil moisture sensor + ADC         $15-20
  Jumper wires + breadboard                  $5
                                         Subtotal: $100-110

===========================================
GRAND TOTAL:                             $882-1,002
===========================================
```

**Where to save if you are over $1,000:**
- Get a Z440 with 16 GB RAM and upgrade later (-$30 on the tower)
- Buy a Pi 4 (2 GB) instead of 4 GB (-$10)
- Skip the extra case fan for now (-$12)
- Hunt for an RTX 3080 under $300 (they appear regularly on eBay)

---

## Phase 2 -- Expand Later ($150-300 per wave)

Once the server and first Pi are running, add hardware per project:

### Wave 1: More Sensors + Outdoor Deploy (~$50-60)

| Item | Price | For Project |
|---|---|---|
| Waterproof enclosure for Pi | $10-15 | Garden monitor (permanent outdoor install) |
| BH1750 light sensor | $3-5 | Garden monitor |
| Pi Camera Module v3 | $25-35 | Garden monitor (plant health ML) |
| Longer USB-C power cable (10 ft) | $8 | Reaching outdoor power outlet |

### Wave 2: Second Pi + Security Camera (~$100-150)

| Item | Price | For Project |
|---|---|---|
| Raspberry Pi 4 (4 GB) | $55 | Security camera / rover |
| Pi power supply + SD card + case | $25 | Essentials |
| USB webcam or RTSP IP camera | $25-50 | Security camera feed for Frigate |

### Wave 3: Kids Projects -- RC Car (~$95-155)

| Item | Price | For Project |
|---|---|---|
| Raspberry Pi 4 (2 GB) or spare Pi | $45 | RC car brain |
| Motor driver HAT (L298N or Adafruit) | $15-25 | Drive motors |
| 4WD robot car chassis kit (motors + wheels) | $15-25 | Physical car body |
| Pi Camera Module or USB webcam | $15-30 | Onboard camera |
| Battery pack (6x AA or LiPo + regulator) | $10-15 | Portable power |
| Jumper wires + breadboard | $5 | Connections |

### Wave 4: Garden Rover (~$105-160)

| Item | Price | For Project |
|---|---|---|
| Raspberry Pi 4 (2-4 GB) | $45-55 | Rover brain |
| 4WD weatherproof rover chassis | $25-40 | Outdoor chassis |
| Pi Camera Module (wide angle) | $20-30 | Garden photos |
| Motor driver (L298N) | $10 | Drive motors |
| Battery pack (rechargeable) | $15-25 | Portable power |

### Wave 5: Home Automation (~$50-80)

| Item | Price | For Project |
|---|---|---|
| Zigbee USB dongle (Sonoff Zigbee 3.0) | $15-20 | Home Assistant integration |
| Smart plugs (Zigbee, 4-pack) | $25-35 | Control lights/devices |
| Temperature sensors (Zigbee, 2-pack) | $15-25 | Indoor monitoring |

---

## Complete Shopping Checklist

Print this out or copy to a note-taking app. Check items off as you buy.

```
PHASE 1 -- BUY NOW (target: $1,000)
=====================================

SERVER:
[ ] HP Z440 tower
    Xeon E5-1630 v3+, 32 GB DDR4 ECC, 700 W PSU
    eBay search: "HP Z440 Xeon 32GB 700W tower -SFF"
    VERIFY: 700W PSU, tower (not SFF), actual photos, good seller

[ ] NVIDIA RTX 3080 10 GB (used)
    eBay search: "RTX 3080 10GB used tested working -3080Ti -FE"
    VERIFY: tested/working, all fans intact, dual 8-pin, returns accepted

[ ] 1 TB SATA SSD
    Amazon: Crucial MX500 1TB or Samsung 870 EVO 1TB

[ ] DDR4 ECC RAM (ONLY if Z440 comes with < 32 GB)
    Search: "DDR4 2133 ECC RDIMM 16GB HP Z440"

NETWORKING:
[ ] PCIe Wi-Fi 6 + Bluetooth card
    Amazon: "PCIe WiFi 6 Bluetooth desktop card AX200"

[ ] Ethernet cables (3-pack, Cat 6)
    Amazon: "Cat 6 ethernet cable pack"

[ ] Powered USB 3.0 hub (7-port)
    Amazon: "powered USB 3.0 hub 7 port"

COOLING + POWER:
[ ] 120 mm quiet case fan
    Amazon: "Arctic P12 PWM 120mm" (~$8, best value)

[ ] Surge protector (6+ outlets, 1000+ joules)

RASPBERRY PI:
[ ] Raspberry Pi 4 Model B (4 GB)
    Amazon or Adafruit: "Raspberry Pi 4 Model B 4GB"

[ ] Pi power supply (USB-C, 5V 3A)
    Amazon: "official Raspberry Pi 4 power supply" or CanaKit

[ ] MicroSD card (32 GB, Class 10 / A1+)
    Amazon: "SanDisk 32GB microSD A1"

[ ] Pi case with cooling
    Amazon: "Raspberry Pi 4 case with fan" or Argon ONE

[ ] Micro-HDMI to HDMI cable
    Amazon: "micro HDMI to HDMI cable"

[ ] DHT22 temperature/humidity sensor
    Amazon: "DHT22 AM2302 sensor module"

[ ] Capacitive soil moisture sensor
    Amazon: "capacitive soil moisture sensor"

[ ] ADS1115 ADC module
    Amazon: "ADS1115 16-bit ADC module"

[ ] Jumper wires (male-to-female, 40 pcs)
    Amazon: "jumper wires male female 40 pack"

[ ] Mini breadboard
    Amazon: "mini breadboard" or "half-size breadboard"


PHASE 2 -- BUY LATER (as budget allows)
=========================================

[ ] Waterproof enclosure for outdoor Pi         ~$10-15
[ ] BH1750 light sensor                         ~$3-5
[ ] Pi Camera Module v3                          ~$25-35
[ ] Second Raspberry Pi 4 (4 GB)                 ~$55
[ ] USB webcam or IP camera (for Frigate)        ~$25-50
[ ] RC car chassis kit + motor driver            ~$30-50
[ ] Zigbee USB dongle (for Home Assistant)       ~$15-20
[ ] UPS battery backup (for 24/7 reliability)    ~$80-120
```

---

## Where to Buy (by item type)

| Source | Best For | Tips |
|---|---|---|
| **eBay** | Z440 tower, RTX 3080, used RAM | Filter: Buy It Now + Free Shipping + Domestic |
| **Amazon** | SSD, Wi-Fi card, USB hub, fans, surge protector, Pi, sensors | Subscribe and Save or used/refurb options for more savings |
| **Adafruit** | Raspberry Pi boards, sensors, HATs, wiring | Reliable stock; quality tutorials for every product |
| **Micro Center** | Pi boards, SSDs (in-store deals) | Check for in-store-only Pi pricing (often cheapest) |
| **AliExpress** | Sensors in bulk (DHT22, soil, breadboards) | Cheap but 2-4 week shipping; good for Phase 2 bulk buys |
| **Newegg** | SSD, Wi-Fi card | Often price-matches Amazon; check for combos |

---

## Order of Purchase (Recommended)

Buy in this order so you can start building as soon as possible:

1. **Week 1: Order the Z440 + RTX 3080 on eBay** -- These take the longest to
   arrive (3-7 days for domestic shipping). Start hunting immediately. Set up
   eBay saved searches with the strings above to get notifications on new
   listings.

2. **Week 1: Order Amazon items** -- SSD, Wi-Fi card, USB hub, fan, surge
   protector, ethernet cables. These arrive in 1-2 days with Prime.

3. **Week 1-2: Order Pi + sensors** -- From Amazon or Adafruit. If Amazon has
   the Pi 4 in stock, order there. If not, check Adafruit or Micro Center.

4. **Week 2-3: Hardware arrives** -- Follow [SERVER_SETUP.md](SERVER_SETUP.md)
   to assemble the Z440, install Ubuntu, set up Docker, and deploy first
   services.

5. **Week 3-4: Pi arrives** -- Flash Raspberry Pi OS, install Python + MQTT
   client, connect sensors, and deploy the garden monitor code from
   [garden_monitor/README.md](projects/garden_monitor/README.md).

---

## Cost Optimization Tips

1. **Set eBay alerts.** Saved searches with email notifications catch deals the
   moment they are listed. Prices on the Z440 and RTX 3080 fluctuate $30-75
   week to week.

2. **Buy sensor bundles.** Amazon sells "37 sensor kit for Arduino/Pi" packs for
   ~$15-20 that include DHT22, soil moisture, light, motion, and dozens more.
   Good value if you plan multiple projects.

3. **CanaKit bundles.** The CanaKit Raspberry Pi 4 Starter Kit (~$70-80) bundles
   the Pi board + case + power supply + SD card + HDMI cable. Often cheaper than
   buying each piece separately.

4. **Refurbished SSDs.** Crucial and Samsung sell manufacturer-refurbished SSDs
   at 20-30% off. Perfectly fine for a home server.

5. **Check local listings.** Facebook Marketplace and Craigslist sometimes have
   HP Z-series towers for less than eBay, and you can inspect before buying.

6. **Skip the monitor.** If you have any laptop or existing monitor, use it for
   initial Ubuntu setup, then switch to headless/SSH. No need to buy a dedicated
   server monitor.

---

## Related Documentation

- [HARDWARE.md](HARDWARE.md) -- Detailed specs, pre-purchase checklists, and
  future upgrade paths
- [SERVER_SETUP.md](SERVER_SETUP.md) -- Step-by-step setup guide once hardware
  arrives
- [OVERVIEW.md](OVERVIEW.md) -- How the whole system works together
- [projects/garden_monitor/](projects/garden_monitor/) -- First Pi project to
  build after hardware arrives
- [DEV_WORKFLOW.md](DEV_WORKFLOW.md) -- How to code and deploy from your laptop
