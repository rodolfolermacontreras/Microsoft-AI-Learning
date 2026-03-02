# Server Setup Guide

Step-by-step instructions to go from bare hardware to a fully configured Docker + GPU home server running Ubuntu.

---

## Phase 1: Hardware Assembly

### 1.1 Install the GPU

1. Power off the Z440 and unplug it
2. Remove the side panel (one thumbscrew on the rear)
3. Remove any existing GPU (Quadro card) if present
4. Insert the RTX 3080 into the top PCIe x16 slot (blue slot, closest to CPU)
5. Connect **both** 8-pin PCIe power cables from the PSU to the GPU
6. Secure the GPU bracket with the retention clip or screw
7. Replace the side panel

### 1.2 Install the SSD

1. Mount the 1 TB SATA SSD in an available 2.5" bay (or use an adapter bracket)
2. Connect a SATA data cable from the SSD to a SATA port on the motherboard
3. Connect a SATA power cable from the PSU to the SSD

### 1.3 Install Additional Components

- **Wi-Fi card**: Insert into a free PCIe x1 slot; attach external antennas to the rear bracket
- **Extra case fans**: Mount in front (intake) and/or rear (exhaust) positions; connect to fan headers or use Molex adapters

### 1.4 First Boot Test

1. Connect monitor, keyboard, mouse
2. Power on and enter BIOS (press F10 on HP splash screen)
3. Verify all hardware is detected: CPU, RAM amount, drives, GPU
4. Set boot order: USB first (for Ubuntu installer), then SSD

---

## Phase 2: Ubuntu Installation

### 2.1 Create Bootable USB

On another computer:

1. Download **Ubuntu 24.04.x LTS Server** ISO from https://ubuntu.com/download/server
2. Flash to USB drive using:
   - **Windows**: Rufus (https://rufus.ie) or balenaEtcher
   - **Linux/Mac**: `dd` or balenaEtcher

### 2.2 Install Ubuntu Server

1. Boot from USB
2. Choose **Ubuntu Server** (not desktop -- lighter, better for 24/7 headless use)
3. During installation:
   - **Storage**: Use the 1 TB SSD as the boot/root drive; leave the 2 TB HDD untouched for now
   - **Partition**: Let the installer use the whole SSD (guided/automatic is fine)
   - **Username**: Pick something short (e.g., `admin` or your first name)
   - **Hostname**: Something memorable (e.g., `homeserver`, `z440`, `localbox`)
   - **OpenSSH server**: YES -- install it (you will manage the server remotely)
   - **Snaps**: Skip featured server snaps for now
4. Reboot after installation, remove USB

### 2.3 Post-Install Basics

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y \
    curl wget git htop tmux neofetch \
    build-essential net-tools \
    openssh-server ufw

# Enable firewall with SSH access
sudo ufw allow OpenSSH
sudo ufw enable

# Set timezone
sudo timedatectl set-timezone America/Chicago  # adjust to your timezone

# Mount the 2 TB HDD for bulk storage
sudo mkdir -p /mnt/storage
# Find the HDD device name
lsblk
# Format if needed (WARNING: erases data):
# sudo mkfs.ext4 /dev/sdX
# Add to /etc/fstab for auto-mount at boot:
# UUID=<your-uuid>  /mnt/storage  ext4  defaults  0  2
```

### 2.4 Configure SSH Access

From your laptop/desktop, connect without needing a monitor:

```bash
ssh your_username@homeserver.local
# or use the IP address:
ssh your_username@192.168.x.x
```

Find the server's IP:
```bash
# On the server
ip addr show
```

---

## Phase 3: NVIDIA GPU Setup

### 3.1 Install NVIDIA Drivers

```bash
# Add NVIDIA driver repository
sudo apt install -y linux-headers-$(uname -r)
sudo apt install -y nvidia-driver-550  # or latest recommended version

# Reboot
sudo reboot
```

### 3.2 Verify GPU

```bash
# Check GPU is detected
nvidia-smi

# Expected output: shows RTX 3080, driver version, CUDA version, VRAM
```

### 3.3 Install CUDA Toolkit (for ML workloads)

```bash
# Install CUDA toolkit
sudo apt install -y nvidia-cuda-toolkit

# Verify
nvcc --version
```

### 3.4 Quiet GPU Tips

```bash
# Cap GPU power for quieter operation (250W instead of 320W default)
sudo nvidia-smi -pl 250

# Make persistent across reboots: add to /etc/rc.local or a systemd service
```

---

## Phase 4: Docker Setup

### 4.1 Install Docker Engine

```bash
# Remove old versions
sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null

# Add Docker's official GPG key and repository
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your user to the docker group (no sudo needed for docker commands)
sudo usermod -aG docker $USER

# Log out and back in, then verify
docker run hello-world
```

### 4.2 Install NVIDIA Container Toolkit

This lets Docker containers access the GPU:

```bash
# Add NVIDIA Container Toolkit repository
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt update
sudo apt install -y nvidia-container-toolkit

# Configure Docker to use NVIDIA runtime
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Test GPU in Docker
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
```

### 4.3 Install Portainer (Container Management UI)

```bash
docker volume create portainer_data

docker run -d \
  -p 8000:8000 \
  -p 9443:9443 \
  --name portainer \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest
```

Access at: `https://homeserver.local:9443`

---

## Phase 5: Core Services

### 5.1 Create Docker Data Directories

```bash
# Main data directory on the SSD
sudo mkdir -p /opt/server/data

# Media directory on the 2 TB HDD
sudo mkdir -p /mnt/storage/media
sudo mkdir -p /mnt/storage/photos
sudo mkdir -p /mnt/storage/music
sudo mkdir -p /mnt/storage/cameras

# Set ownership
sudo chown -R $USER:$USER /opt/server /mnt/storage
```

### 5.2 Install Mosquitto MQTT Broker

For Raspberry Pi communication:

```bash
docker run -d \
  --name mosquitto \
  --restart=always \
  -p 1883:1883 \
  -p 9001:9001 \
  -v /opt/server/data/mosquitto/config:/mosquitto/config \
  -v /opt/server/data/mosquitto/data:/mosquitto/data \
  -v /opt/server/data/mosquitto/log:/mosquitto/log \
  eclipse-mosquitto
```

### 5.3 Quick Validation

After completing all phases, run this checklist:

```bash
# System info
neofetch

# GPU working
nvidia-smi

# Docker working
docker ps

# GPU in Docker working
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi

# Network accessible (from another machine)
# ssh your_username@homeserver.local
# curl http://homeserver.local:9443
```

---

## Summary: What You Have After Setup

| Service | Port | Purpose |
|---|---|---|
| SSH | 22 | Remote terminal access |
| Portainer | 9443 | Container management web UI |
| Mosquitto MQTT | 1883 | Pi-to-server messaging |
| Docker Engine | -- | Container runtime with GPU support |

From here, each project in [projects/](projects/) has its own Docker Compose setup and deployment instructions.

---

## Maintenance

### Regular Updates

```bash
# System packages
sudo apt update && sudo apt upgrade -y

# Docker containers (with Portainer, or manually)
docker pull <image>
docker compose up -d
```

### Monitoring

```bash
# Live system stats
htop

# GPU monitoring
watch -n 1 nvidia-smi

# Docker container status
docker ps
docker stats
```

### Backups

- Critical configs: `/opt/server/data/` (back up regularly)
- Media: `/mnt/storage/` (the 2 TB HDD)
- Consider setting up a cron job to back up Docker volumes to an external drive
