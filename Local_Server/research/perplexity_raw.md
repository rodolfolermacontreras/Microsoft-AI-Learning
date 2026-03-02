# Perplexity Research -- Full Conversation (Unedited)

Raw research conversation from Perplexity AI used to plan the home server build.
Saved here for reference. The cleaned-up version is in [hardware_research.md](hardware_research.md).

---

## Prompt 1: Initial Research

> Want to build a small server at home to develop projects taking advantage of vibe coding.
> So I need a small and powerful computer. Memory. GPU as I might need to run ML models
> for classification or other tasks. Get me a list of items to buy. I'm looking to spend the
> least but still good quality. So it is OK to look at eBay.

### Response

You'll get the best price/performance by buying a used ex-office workstation (Dell/HP/Lenovo)
plus a used midrange NVIDIA GPU with at least 8-12 GB VRAM, and upgrading RAM/SSD as needed.

**Overall strategy:**
- Base: Used workstation tower (Dell Precision, HP Z, Lenovo ThinkStation) from eBay,
  with at least a recent quad-core+ CPU and 16-32 GB RAM.
- GPU: Used NVIDIA RTX 3060 (12 GB) or RTX 3090 (24 GB) if you find a good deal;
  both are strong for ML and well supported.
- Storage: 1 TB NVMe SSD for OS + projects, optional cheap SATA SSD for bulk.
- OS: Linux (Ubuntu) to avoid Windows driver overhead and make CUDA/PyTorch installs easier.

**Core tower (used workstation) -- search on eBay:**
- Dell Precision 5820 / 3620 / 3640
- HP Z440 / Z640
- Lenovo ThinkStation P520 / P320

Target specs:
- CPU: 6-8 cores (Intel Xeon E5 v3/v4 or Intel i7 8th gen+)
- RAM: 32 GB DDR4
- PSU: At least 650 W
- Budget: ~$200-350 shipped

**GPU (used, NVIDIA):**
- Best value baseline: NVIDIA RTX 3060 12 GB (~$200-280 used)
- Stretch option: NVIDIA RTX 3090 24 GB (~$500-650 used)

**Memory:** Target 32 GB total (2x16 GB DDR4), ~$50-70 for extra kit.

**Storage:** 1 TB NVMe SSD ~$50-70 new. Extra 1-2 TB SATA ~$30-60.

**Example target build:**
- "Dell Precision 5820 Xeon 8-core 32GB RAM no GPU" ~$300
- Add: RTX 3060 12 GB used ~$230
- Add: 1 TB NVMe SSD ~$60
- **Total: ~$590**

---

## Prompt 2: Table with Prices and Specs

> Get me a table with prices and specs for different options. Pros and cons.

### Towers (base systems)

| Option | Example | Price | CPU | RAM | Storage | Pros | Cons |
|---|---|---|---|---|---|---|---|
| A | Dell Precision 3620, i7-6700, 32 GB, 1 TB SSD | ~$300 | i7-6700 4C/8T 3.4 GHz | 32 GB DDR4 | 1 TB SSD | Cheap, 32 GB + 1 TB included | Older 4-core; PSU ~365-400 W |
| B | HP Z440, Xeon E5-1630 v3, 32 GB, 2 TB HDD | ~$350-400 | Xeon E5-1630 4C/8T 3.7 GHz | 32 GB DDR4 | 2 TB HDD | Robust workstation, 600-700 W PSU | Needs SSD; only 4 cores |
| C | HP Z440, E5-2697 v3 14C, 8 GB, no HDD | ~$250-300 | Xeon E5-2697 14C/28T 2.6 GHz | 8 GB DDR4 | None | Tons of cores | Must buy RAM + SSD |
| D | Lenovo P520, Xeon W-2135, 32 GB | ~$400-450 | Xeon W-2135 6C/12T 3.7 GHz | 32 GB DDR4 | None | Newer platform, strong per-core | More expensive; needs SSD |
| E | Dell Precision T3420, i7-7700, 32 GB, 500 GB NVMe | ~$320-350 | i7-7700 4C/8T 3.6 GHz | 32 GB DDR4 | 500 GB NVMe | Small, quiet | SFF: limited GPU size |

### GPUs

| Option | Price | VRAM | TDP | Pros | Cons |
|---|---|---|---|---|---|
| G1: RTX 3060 12 GB | ~$230-280 | 12 GB | ~170 W | Great perf/price; enough VRAM | Not ideal for very large LLMs |
| G2: RTX 3090 24 GB | ~$550-750 | 24 GB | ~350 W | Huge VRAM; top-tier for local AI | Needs 750 W+ PSU; noisy |

### Suggested Bundles

| Bundle | Components | Total | Pros | Cons |
|---|---|---|---|---|
| Budget sweet spot | Dell 3620 + RTX 3060 | ~$550 | Lowest cost; ready to go | Older CPU; PSU concerns |
| Workstation focus | HP Z440 + RTX 3060 + 1 TB SSD | ~$660 | Better PSU; more robust | Higher idle power |
| Modern Xeon + mid GPU | P520 + RTX 3060 + 1 TB SSD | ~$760 | Strong perf; good value | More upfront; VRAM limited |
| "Go big" VRAM | P520 + RTX 3090 + 1 TB SSD | ~$1,160 | 24 GB VRAM; future-proof | Highest cost, noise, power |

---

## Prompt 3: $1,000 Budget with Cooling and Pi Integration

> Yes $1,000 for all in all. With everything included.
> I need to run it in my home. So take care of cooling and noise.
> Also I might be using this to integrate with Raspberry Pi for edge projects around the house.

### Response

For $1,000 all-in, quiet home use, and Pi integration, the best fit is a single-GPU
workstation with a used RTX 4070/3080-class card (not 3090 -- too expensive and hot).

**Three bundle options within budget:**

| Bundle | Base + GPU | Total | Noise / Thermals |
|---|---|---|---|
| 1. Quiet value | Dell 3620 ($300) + RTX 4070 ($460) | ~$760 | 200-220 W GPU; moderate |
| 2. Workstation + headroom | HP Z440 ($380) + SSD ($60) + RTX 3080 ($325) | ~$765 | 320 W but better PSU |
| 3. Modern Xeon + cooler GPU | Lenovo P520 ($450) + SSD ($60) + RTX 4070 ($460) | ~$970 | Efficient GPU; quiet |

**Why not 3090:** ~$650-900 alone, leaving too little for base system. 350 W TDP = more noise.

**Cooling / noise tips:**
- Tower chassis (not SFF) with front intake + rear exhaust fans
- Set balanced fan curve; cap GPU power at 80-90% if noise bothers you
- Place on floor/under desk with clearance; avoid closed cabinets

**Pi integration:**
- Docker, MQTT brokers, and local APIs on the workstation
- Train models on workstation, export ONNX/TF Lite to deploy on Pi

---

## Prompt 4: Option 2 Selected -- Expandable Server

> Second option looks good, as I need WiFi and USB hub too.
> Need to create a local server that can expand in different directions like
> monitoring local garden, repository of music (management),
> or any other project that now I can vibe code for my family.

### Response

Option 2 (HP Z440 + RTX 3080) confirmed. Refined parts list:

**Base:** HP Z440, Xeon E5-1630 v3+, 32 GB DDR4 ECC, 2 TB HDD, 700 W PSU
**GPU:** Used RTX 3080 (10-12 GB)
**Extras:** Wi-Fi 6 PCIe card, powered USB 3.0 hub, 1-2 quiet 120 mm fans

Budget breakdown:
- Z440 + 32 GB + HDD: ~$380-450
- 1 TB SSD: ~$60
- RTX 3080: ~$325-400
- Wi-Fi + USB hub + fans: ~$70-100
- **Total: ~$835-1,010**

**Expandable vision:**
1. Garden monitoring: Home Assistant, InfluxDB, Pi sensors, custom ML classifiers
2. Music repository: Navidrome, Jellyfin, Plex
3. Vibe code projects: Containers, LLMs, dashboards, AI tools for family
4. Pi edge integration: MQTT broker, model export to Pi

---

## Prompt 5: Full Shopping List

> Yes, let's get a full list of items to buy. Or to get all together.

### Final Checklist

- [ ] HP Z440 tower, Xeon E5-1630 v3+, 32 GB DDR4 ECC, 2 TB HDD, 700 W PSU
- [ ] Used RTX 3080 (10-12 GB, dual 8-pin, fits standard ATX)
- [ ] 1 TB SATA SSD (Crucial/Samsung/WD)
- [ ] Extra DDR4 ECC RAM to reach 32 GB total (only if needed)
- [ ] PCIe Wi-Fi 6/6E + Bluetooth card
- [ ] Powered USB 3.0 hub (at least 4 ports, with power brick)
- [ ] 1-2 quiet 120 mm case fans
- [ ] Optional thermal paste
- [ ] Surge-protected power strip
- [ ] Ethernet cables for Pi(s)/router connections
- [ ] Monitor + keyboard + mouse (if you don't reuse existing ones)

### eBay Search Strings

- Tower: "HP Z440 32GB 2TB 700W workstation tower" or "HP Z440 E5-1630 v3 32GB no GPU"
- GPU: "RTX 3080 10GB used" or "RTX 3080 12GB used tested"
