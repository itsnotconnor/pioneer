"""
ffprobe


Input #0, mp3, from '/home/cnelson/Music/King Gizzard & The Lizard Wizard - Polygondwanaland.mp3':
  Metadata:
    title           : Polygondwanaland
    artist          : King Gizzard & The Lizard Wizard
    track           : 2
    album           : Polygondwanaland
    comment         : Visit https://kinggizzard.bandcamp.com
    TSRC            : AUTZK1700076
    album_artist    : King Gizzard & The Lizard Wizard
    date            : 2017
  Duration: 00:03:33.00, start: 0.025056, bitrate: 268 kb/s
  Stream #0:0: Audio: mp3 (mp3float), 44100 Hz, stereo, fltp, 262 kb/s
      Metadata:
        encoder         : LAME3.99r
      Side data:
        replaygain: track gain - -8.200000, track peak - unknown, album gain - unknown, album peak - unknown,
  Stream #0:1: Video: mjpeg (Baseline), yuvj444p(pc, bt470bg/unknown/unknown), 700x700 [SAR 72:72 DAR 1:1], 90k tbr, 90k tbn (attached pic)
      Metadata:
        title           : cover
        comment         : Cover (front)

"""


import subprocess
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

@dataclass
class Song:
    #absolute file path for song
    path: str
    # rest is metadata
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    album_artist: Optional[str] = None
    track: Optional[str] = None
    date: Optional[str] = None
    comment: Optional[str] = None
    duration: Optional[float] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    codec: Optional[str] = None
    has_cover: bool = False
    extra: dict = field(default_factory=dict)

    @property
    def duration_formatted(self) -> Optional[str]:
        if self.duration is None:
            return None
        minutes, seconds = divmod(int(self.duration), 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}" if hours else f"{minutes:02}:{seconds:02}"


KNOWN_TAGS = {"title", "artist", "album", "album_artist", "track", "date", "comment"}


def probe_file(path: str | Path) -> Song:
    """Run ffprobe (IN JSON MODE!!) on a file and return metadata."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(path),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {path}: {result.stderr.strip()}")

    data = json.loads(result.stdout)
    fmt = data.get("format", {})
    streams = data.get("streams", [])
    tags = {k.lower(): v for k, v in fmt.get("tags", {}).items()}

    # Separate known tags from extras
    known = {k: tags[k] for k in KNOWN_TAGS if k in tags}
    extra = {k: v for k, v in tags.items() if k not in KNOWN_TAGS}

    # Pull audio/video stream info
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    has_cover = any(
        s.get("codec_type") == "video" and s.get("disposition", {}).get("attached_pic")
        for s in streams
    )

    return Song(
        path=str(path),
        title=known.get("title"),
        artist=known.get("artist"),
        album=known.get("album"),
        album_artist=known.get("album_artist"),
        track=known.get("track"),
        date=known.get("date"),
        comment=known.get("comment"),
        duration=float(fmt["duration"]) if "duration" in fmt else None,
        bitrate=int(fmt["bit_rate"]) // 1000 if "bit_rate" in fmt else None,
        sample_rate=int(audio["sample_rate"]) if audio and "sample_rate" in audio else None,
        channels=audio.get("channels") if audio else None,
        codec=audio.get("codec_name") if audio else None,
        has_cover=has_cover,
        extra=extra,
    )


def scan_library(root: str | Path, extensions: set[str] = {".mp3", ".flac", ".m4a", ".ogg", ".wav"}) -> list[Song]:
    """Recursively scan a directory and probe all audio files."""
    root = Path(root)
    tracks = []

    for file in sorted(root.rglob("*")):
        if file.suffix.lower() not in extensions:
            ##print(f"Skipping {file} unsupported file type/is a directory...")
            continue
        try:
            tracks.append(probe_file(file))
        except Exception as e:
            print(f"[WARN] Skipping {file}: {e}")

    ##print(f"Found Tracks: {tracks}")
    return tracks


if __name__ == "__main__":
    target = "/home/cnelson/Music" ##eventually /mnt/...
    tracks = scan_library(target)

    for t in tracks:
        print(f"\n{'─' * 50}")
        print(f"  File:     {Path(t.path).name}")
        print(f"  Title:    {t.title or '(unknown)'}")
        print(f"  Artist:   {t.artist or '(unknown)'}")
        print(f"  Album:    {t.album or '(unknown)'}")
        print(f"  Track:    {t.track or '—'}")
        print(f"  Year:     {t.date or '—'}")
        print(f"  Duration: {t.duration_formatted or '—'}")
        print(f"  Bitrate:  {f'{t.bitrate} kb/s' if t.bitrate else '—'}")
        # print(f"  Codec:    {t.codec or '—'} @ {t.sample_rate} Hz" if t.sample_rate else f"  Codec:    {t.codec or '—'}")
        # print(f"  Cover:    {'Yes' if t.has_cover else 'No'}")
        # if t.extra:
        #     print(f"  Extra:    {t.extra}")


    # Log json output
    with open("tracks.json", "w") as f:
        for t in tracks:
            json.dump(t.__dict__, f, indent=4)
