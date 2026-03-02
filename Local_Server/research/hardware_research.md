# Hardware Research Notes

Research notes from planning the home server build. Sources include Perplexity AI deep research, Reddit threads, and eBay pricing data (collected early 2025).

---

## Goal

Build a 24/7 home server for under $1,000 that can:

- Replace Google Photos with local AI-powered photo management
- Stream music and generate karaoke tracks using GPU-accelerated source separation
- Run security camera NVR with real-time object detection
- Collect garden sensor data from Raspberry Pis and display dashboards
- Serve as a general-purpose platform for learning Docker, Linux, and ML

---

## Options Considered

### Option 1: Raspberry Pi Cluster

- 3-4 Raspberry Pi 5 (8 GB) at ~$80 each
- Advantage: Low power, quiet, modular
- Disadvantage: No GPU (cannot run Immich ML, Demucs, Frigate with HW detection)
- Verdict: **Rejected** -- not enough compute for ML workloads

### Option 2: Refurbished Workstation + Used GPU (CHOSEN)

- HP Z440 or Dell Precision T7810 workstation
- NVIDIA RTX 3080 (used)
- Advantage: Desktop-class CPU + full GPU + ECC RAM + reliable PSU
- Disadvantage: Larger, more power draw, fan noise (mitigated with fan swap)
- Verdict: **Selected** -- best performance per dollar for GPU workloads

### Option 3: Mini PC (Intel NUC / Beelink)

- Compact, low power, silent
- Disadvantage: No PCIe slot for GPU
- Verdict: **Rejected** -- cannot add discrete GPU

### Option 4: Custom Build (New Parts)

- Full control over components
- Disadvantage: $1,500+ for comparable specs
- Verdict: **Over budget**

---

## Why HP Z440

| Feature | HP Z440 |
|---|---|
| CPU Socket | LGA 2011-v3 (Xeon E5-1600/2600 v3/v4) |
| RAM | DDR4 ECC (up to 256 GB) |
| PCIe | x16 Gen 3 slot (fits RTX 3080) |
| PSU | 700W 80+ Gold (enough for RTX 3080 at 320W TDP) |
| Typical eBay Price | $100-200 (with CPU + 16-32 GB RAM) |
| Build Quality | Enterprise-grade, designed for 24/7 |
| Notes | Must verify 700W PSU (some ship with 525W) |

### CPU Options (LGA 2011-v3)

| CPU | Cores/Threads | Base/Boost | TDP | eBay Price |
|---|---|---|---|---|
| Xeon E5-1630 v3 | 4/8 | 3.7/3.8 GHz | 140W | Included |
| Xeon E5-1650 v3 | 6/12 | 3.5/3.8 GHz | 140W | ~$20 |
| Xeon E5-2680 v4 | 14/28 | 2.4/3.3 GHz | 120W | ~$30 |

The E5-1650 v3 is a good upgrade if the included CPU feels slow. For Docker workloads, single-thread speed matters more than core count.

---

## Why RTX 3080

| Feature | Value |
|---|---|
| VRAM | 10 GB GDDR6X (12 GB on some models) |
| CUDA Cores | 8704 |
| TDP | 320W (can power-cap to 200W with nvidia-smi) |
| PyTorch Support | Full CUDA 11.x/12.x support |
| HuggingFace Models | Runs ViT, CLIP, Whisper, Demucs (all fit in 10 GB) |
| Frigate | Supports TensorRT for fast object detection |
| Immich ML | GPU-accelerated CLIP embeddings for photo search |
| eBay Price (used) | $250-350 (2025) |

### Alternatives Considered

| GPU | VRAM | Price | Notes |
|---|---|---|---|
| RTX 3060 12 GB | 12 GB | $180-220 | More VRAM but slower compute |
| RTX 3070 | 8 GB | $200-280 | Less VRAM, slightly slower |
| RTX 3080 | 10-12 GB | $250-350 | Best balance (chosen) |
| RTX 3090 | 24 GB | $700+ | Overkill for this use case |

The 3080 was selected for its balance of VRAM, compute, and price. If budget is tight, the 3060 12 GB is a reasonable fallback (more VRAM for large models, slower inference).

---

## Full Shopping List

| Component | Specification | Est. Price | Where to Buy |
|---|---|---|---|
| HP Z440 Workstation | Xeon E5-1630 v3+, 32 GB DDR4, 700W PSU | $150-200 | eBay |
| NVIDIA RTX 3080 | 10 GB, used | $250-350 | eBay |
| NVMe SSD | 1 TB (for OS + Docker + configs) | $60-80 | Amazon |
| HDD | 2 TB 3.5" 7200 RPM (for media storage) | $40-50 | Amazon |
| PCIe M.2 Adapter | If Z440 has no M.2 slot | $10 | Amazon |
| Wi-Fi 6 Card | Intel AX210 PCIe (if no Ethernet near server) | $15-20 | Amazon |
| USB Hub | Powered, 4+ ports | $15 | Amazon |
| Case Fans | 2x 120mm quiet fans (Noctua or Arctic) | $20-30 | Amazon |
| **Total** | | **$560-745** | |

Remaining budget for Raspberry Pis and sensors:

| Component | Est. Price |
|---|---|
| Raspberry Pi 4/5 (8 GB) x2 | $80-160 |
| DHT22 sensor x2 | $10 |
| Soil moisture sensor x2 | $10 |
| USB camera or Pi Camera Module | $15-30 |
| Breadboard + jumper wires | $10 |
| MicroSD cards (32 GB) x2 | $10 |

**Grand total estimate: $700-975**

---

## Power and Heat Considerations

- RTX 3080 at stock: 320W TDP
- Power cap to 200W: `sudo nvidia-smi -pl 200` (reduces heat significantly with ~15% perf loss)
- Z440 at idle: ~50-80W
- Z440 under full GPU load: ~400-500W
- Estimated monthly power cost: $10-20 (at US average rates)
- **Tip:** Run GPU-heavy tasks (Demucs, model training) during off-peak hours or schedule them

---

## Noise Management

- Replace the stock rear fan with a Noctua NF-A12x25
- The Z440 CPU cooler is designed for Xeon TDP, usually quiet enough
- The RTX 3080 fans ramp under load; power capping helps
- Place the server in a closet, garage, or utility room if noise is a concern
- A 24/7 server at idle is typically 30-35 dBA (quiet room level)

---

## Key Risks and Mitigations

| Risk | Mitigation |
|---|---|
| GPU does not fit in Z440 case | Measure PCIe clearance (~270-310 mm); most 3080 reference cards fit |
| PSU does not have enough PCIe 8-pin connectors | Verify 700W PSU model before buying; may need 6-pin to 8-pin adapter |
| Used GPU is defective | Buy from seller with return policy; test immediately |
| Workstation has lower wattage PSU | Confirm 700W in listing photos or seller description |
| Overheating in enclosed space | Monitor temps via `nvidia-smi` and `sensors`; ensure airflow |
| Ubuntu driver issues | Use `ubuntu-drivers autoinstall` for NVIDIA 550 drivers |

---

## Sources

- Perplexity AI deep research (January 2025)
- r/homelab, r/selfhosted, r/homeserver (Reddit)
- eBay sold listings for pricing data
- Immich, Navidrome, Frigate official documentation
- NVIDIA Container Toolkit documentation
