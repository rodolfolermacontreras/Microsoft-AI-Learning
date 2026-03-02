# Hardware Shopping List

Complete parts list for the home server build. Based on **Option 2: HP Z440 + RTX 3080** (best balance of performance, expandability, and budget at ~$1,000 all-in).

---

## Budget Target: $1,000 USD (all-in)

---

## 1. Core Workstation

**Refurbished HP Z440 Workstation Tower**

| Spec | Target | Notes |
|---|---|---|
| CPU | Xeon E5-1630 v3 (4C/8T @ 3.7 GHz) or better | E5-1650 v3/v4 or E5-1660 v3/v4 are nice upgrades |
| RAM | 32 GB DDR4 ECC | Starting point; upgradeable to 64+ GB later |
| Storage | 2 TB HDD (included) | Keep for bulk media/backups |
| PSU | 700 W (90% efficient) | Very common in Z440; critical for RTX 3080 |
| Condition | Refurbished/used, without high-end GPU | Cheaper without GPU -- we add our own |

**eBay Search Strings:**
```
HP Z440 32GB 2TB 700W workstation tower
HP Z440 E5-1630 v3 32GB no GPU
HP Z440 Xeon 32GB DDR4 tower workstation
```

**What to check in listings:**
- PSU wattage (must be 700 W, not 525 W variant)
- Number of PCIe 8-pin power connectors (need 2 for the RTX 3080)
- Physical condition photos (bent fins on CPU cooler = red flag)
- Seller rating and return policy

**Budget: ~$380-450 USD**

---

## 2. GPU

**Used NVIDIA RTX 3080 (10-12 GB)**

| Spec | Target |
|---|---|
| VRAM | 10 GB GDDR6X (standard) or 12 GB (some variants) |
| TDP | ~320 W |
| Power Connectors | 2x 8-pin PCIe |
| Brands (any) | ASUS, MSI, Gigabyte, EVGA, Zotac |

**eBay Search Strings:**
```
RTX 3080 10GB used tested
RTX 3080 12GB used working
NVIDIA RTX 3080 -3080Ti -FE
```

**What to check:**
- "Tested and working" in description
- No mining history if possible (ask seller)
- Card length fits Z440 tower (standard ATX size works; avoid 3-slot monsters)
- All fans spin (ask for video or check return policy)
- 2x 8-pin power connectors required

**Budget: ~$325-400 USD**

---

## 3. Storage (System Drive)

**1 TB SATA SSD**

| Spec | Target |
|---|---|
| Type | 2.5" SATA III SSD (guaranteed Z440 compatibility) |
| Capacity | 1 TB |
| Use | OS (Ubuntu), Docker images, code, active datasets |
| Brands | Crucial MX500, Samsung 870 EVO, WD Blue |

The Z440's 2 TB HDD stays as bulk storage for media, backups, and datasets.

**Budget: ~$60 USD (new)**

---

## 4. RAM (if needed)

**Additional DDR4 ECC RAM**

Only buy if the Z440 ships with less than 32 GB.

| Spec | Target |
|---|---|
| Type | DDR4 ECC RDIMM (must match existing DIMMs) |
| Target total | 32 GB minimum |
| Search | "HP Z440 DDR4 ECC 16GB" or "DDR4 2133 ECC RDIMM 16GB" |

**Budget: ~$50-70 USD (only if needed)**

---

## 5. Networking

### 5a. PCIe Wi-Fi 6/6E + Bluetooth Card

| Spec | Target |
|---|---|
| Interface | PCIe x1 or x4 (Z440 has spare slots) |
| Standard | Wi-Fi 6 (802.11ax) or Wi-Fi 6E |
| Bluetooth | 5.0+ |
| Antenna | External antennas on rear bracket |

The Z440 supports PCIe WLAN cards natively. This gives wireless connectivity plus Bluetooth for peripherals without using USB ports.

**Budget: ~$25-35 USD**

### 5b. Ethernet Cables

| Item | Quantity |
|---|---|
| Cat 6 Ethernet cable (various lengths) | 2-3 |
| Use | Server-to-router, server-to-switch, Pi connections |

The Z440 has 1x Gigabit Ethernet built in. For wired connections to Raspberry Pis and your home router.

**Budget: ~$10-15 USD**

---

## 6. USB Expansion

**Powered USB 3.0 Hub (7-port)**

| Spec | Target |
|---|---|
| Ports | 4-7 USB 3.0 Type-A |
| Power | External power supply (its own brick) |
| Use | Raspberry Pis, external drives, microcontrollers, Zigbee dongles |

Must be *powered* (has its own wall adapter) so it does not draw from the workstation's USB power budget.

**Budget: ~$25-35 USD**

---

## 7. Cooling and Acoustics

### 7a. Case Fans (1-2 pcs)

| Spec | Target |
|---|---|
| Size | 120 mm |
| Type | Quiet-focused (low dB rating) |
| Brands | Noctua NF-P12, Arctic P12, be quiet! Pure Wings 2 |
| Placement | 1 front intake, 1 rear exhaust |

The Z440 chassis supports additional fans. Adding 1-2 quiet fans keeps the RTX 3080's own fans from ramping hard, significantly reducing noise.

**Budget: ~$20-30 USD**

### 7b. Thermal Paste (optional)

Only needed if re-seating the CPU cooler or re-pasting the GPU after purchase.

- Arctic MX-4 or Noctua NT-H1 (~$7-10)

---

## 8. Power and Protection

**Surge Protector / Power Strip**

| Spec | Target |
|---|---|
| Outlets | 6+ (server, monitor, USB hub brick, router, etc.) |
| Surge protection | Yes (rated in joules) |
| Optional | UPS (uninterruptible power supply) for 24/7 operation |

A UPS is optional but recommended for a 24/7 server to survive short power outages and shut down cleanly.

**Budget: ~$15-25 USD (surge protector) or ~$80-120 (basic UPS)**

---

## 9. Peripherals (if not reusing existing)

| Item | Notes | Budget |
|---|---|---|
| Monitor | Any 1080p or 1440p (only needed for initial setup; can go headless after) | ~$0-100 |
| Keyboard + Mouse | Any basic set | ~$0-25 |

Once Ubuntu and SSH are configured, you can manage the server headlessly from any laptop.

---

## Shopping Checklist

Copy this and check items off as you buy:

```
HARDWARE SHOPPING CHECKLIST
===========================

CORE:
- [ ] HP Z440 tower (Xeon E5-1630 v3+, 32 GB, 700 W PSU, 2 TB HDD)  ~$380-450
- [ ] NVIDIA RTX 3080 (10-12 GB, used, tested, dual 8-pin)            ~$325-400
- [ ] 1 TB SATA SSD (Crucial/Samsung/WD)                               ~$60

MEMORY (only if base < 32 GB):
- [ ] DDR4 ECC RAM to reach 32 GB total                                ~$50-70

NETWORKING + USB:
- [ ] PCIe Wi-Fi 6/6E + Bluetooth card                                 ~$25-35
- [ ] Powered USB 3.0 hub (4-7 ports, with power brick)                ~$25-35
- [ ] Ethernet cables (Cat 6, 2-3 pcs)                                 ~$10-15

COOLING:
- [ ] 1-2 quiet 120mm case fans (Noctua/Arctic/be quiet!)              ~$20-30
- [ ] Thermal paste (optional, Arctic MX-4)                             ~$8

POWER:
- [ ] Surge protector / power strip                                     ~$15-25

PERIPHERALS (if needed):
- [ ] Monitor (any 1080p+)                                             ~$0-100
- [ ] Keyboard + mouse                                                  ~$0-25

                                                          TOTAL: ~$900-1,000
```

---

## Pre-Purchase Verification Checklist

Before clicking "Buy" on the Z440, confirm:

- [ ] PSU is 700 W (not the 525 W variant)
- [ ] Has at least 2x PCIe 8-pin power connectors (or plan for adapters)
- [ ] Tower chassis (not SFF) -- full-size for GPU clearance
- [ ] Listing shows actual photos (not stock images)
- [ ] Seller has good feedback (95%+ on eBay)
- [ ] Return policy exists (at least 30 days)

Before clicking "Buy" on the RTX 3080, confirm:

- [ ] Listed as "tested and working"
- [ ] All fans visible and intact in photos
- [ ] Card is standard ATX size (not a triple-slot monster)
- [ ] Dual 8-pin PCIe power connectors
- [ ] Seller shows actual card (not stock photos)

---

## Home Placement Tips

- Place the tower on the floor or under a desk with 3-4 inches of clearance on all sides
- Keep intake (front) and exhaust (rear) unobstructed -- never in a closed cabinet
- In BIOS: set a "balanced" fan curve (not "performance")
- In Linux: optionally cap GPU power to 80-90% via `nvidia-smi` for quieter operation:
  ```bash
  sudo nvidia-smi -pl 250   # Cap at 250W instead of 320W default
  ```
- The Z440 is designed for office use and is inherently quieter than consumer towers

---

## Future Upgrades Path

Once the base system is running and you want more capacity:

| Upgrade | When | Cost |
|---|---|---|
| RAM to 64 GB | When running many containers + large models simultaneously | ~$50-80 |
| Second 2 TB SSD | When media library grows beyond HDD capacity | ~$100 |
| Better CPU (E5-1650 v4, 6C) | If CPU becomes a bottleneck (unlikely for most workloads) | ~$30-50 used |
| Second GPU | If you need more VRAM / parallel inference (needs PCIe slot + power) | Varies |
| UPS battery backup | For true 24/7 reliability through power outages | ~$80-120 |
| Raspberry Pi nodes | As you add garden sensors, cameras, displays around the house | ~$50-80 each |
