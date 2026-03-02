# Music Server

A self-hosted music streaming server with karaoke file generation capabilities.

---

## Goal

- Stream personal music library to any device (phone, TV, laptop)
- Organize and manage a large music collection
- Generate karaoke tracks by separating vocals from instrumentals
- Family-friendly access over the home network

---

## Components

### 1. Music Streaming: Navidrome

[Navidrome](https://www.navidrome.org/) is a lightweight, open-source music server compatible with Subsonic clients.

**Why Navidrome:**
- Very lightweight (runs on minimal resources)
- Web UI + mobile apps (Subsonic-compatible: DSub, Symfonium, play:Sub)
- Supports MP3, FLAC, OGG, AAC, WMA
- Transcoding on the fly
- Multi-user support
- Scrobbling (Last.fm integration)

### 2. Karaoke Generation: Demucs

[Demucs](https://github.com/facebookresearch/demucs) is Meta's music source separation model. It splits any song into stems: vocals, drums, bass, other.

**Why Demucs:**
- State-of-the-art audio separation quality
- GPU-accelerated (perfect for our RTX 3080)
- Produces clean instrumental tracks for karaoke
- Open source (MIT license)

---

## Architecture

```
Music Library (/mnt/storage/music/)
        |
        +-- Navidrome (streaming) --> Phone / TV / Laptop
        |
        +-- Demucs (GPU) --> Karaoke Tracks
                |
                +-- vocals.wav
                +-- no_vocals.wav (instrumental / karaoke)
                +-- drums.wav
                +-- bass.wav
```

---

## Docker Compose (Navidrome)

```yaml
# docker-compose.yml
version: "3.8"

services:
  navidrome:
    image: deluan/navidrome:latest
    container_name: navidrome
    restart: always
    ports:
      - "4533:4533"
    environment:
      ND_SCANSCHEDULE: 1h
      ND_LOGLEVEL: info
      ND_BASEURL: ""
    volumes:
      - /opt/server/data/navidrome:/data
      - /mnt/storage/music:/music:ro
```

---

## Karaoke Pipeline (Demucs)

### Install Demucs (in a Docker container or virtualenv)

```bash
# Option A: Direct install with GPU support
pip install demucs torch torchaudio

# Option B: Docker (GPU)
docker run --rm --gpus all \
  -v /mnt/storage/music:/input \
  -v /mnt/storage/music/karaoke:/output \
  demucs-gpu \
  python -m demucs --two-stems vocals -o /output /input/song.mp3
```

### Generate Karaoke Track

```bash
# Separate vocals from instrumentals
python -m demucs --two-stems vocals -o ./output "path/to/song.mp3"

# Output:
#   output/htdemucs/song/vocals.wav        (just the voice)
#   output/htdemucs/song/no_vocals.wav     (instrumental = karaoke track)
```

### Batch Processing Script (Example)

```python
"""batch_karaoke.py -- Generate karaoke tracks for all songs in a directory."""

import subprocess
from pathlib import Path

MUSIC_DIR = Path("/mnt/storage/music/to_process")
OUTPUT_DIR = Path("/mnt/storage/music/karaoke")

def generate_karaoke(song_path: Path) -> None:
    """Run Demucs to separate vocals from a song."""
    cmd = [
        "python", "-m", "demucs",
        "--two-stems", "vocals",
        "-o", str(OUTPUT_DIR),
        str(song_path),
    ]
    subprocess.run(cmd, check=True)
    print(f"Done: {song_path.name}")

def main() -> None:
    """Process all audio files in the music directory."""
    extensions = {".mp3", ".flac", ".wav", ".m4a", ".ogg"}
    songs = [f for f in MUSIC_DIR.iterdir() if f.suffix.lower() in extensions]

    print(f"Found {len(songs)} songs to process")
    for song in songs:
        generate_karaoke(song)

if __name__ == "__main__":
    main()
```

---

## Setup Steps

1. Create music directories:
   ```bash
   sudo mkdir -p /mnt/storage/music
   sudo mkdir -p /mnt/storage/music/karaoke
   sudo mkdir -p /opt/server/data/navidrome
   sudo chown -R $USER:$USER /mnt/storage/music /opt/server/data/navidrome
   ```
2. Copy your music files to `/mnt/storage/music/`
3. Deploy Navidrome:
   ```bash
   docker compose up -d
   ```
4. Access at `http://homeserver.local:4533`
5. Install a Subsonic client on your phone (DSub for Android, play:Sub for iOS)
6. For karaoke: run Demucs on selected tracks, output goes to the karaoke folder

---

## Status

- [ ] Music library organized on server
- [ ] Navidrome deployed and accessible
- [ ] Mobile app connected
- [ ] Demucs installed with GPU support
- [ ] First karaoke track generated
- [ ] Batch processing pipeline working
