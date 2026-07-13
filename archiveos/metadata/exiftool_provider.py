from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Iterable

from .providers import Metadata, MetadataProvider


class ExifToolProvider(MetadataProvider):
    def __init__(self) -> None:
        if shutil.which("exiftool") is None:
            raise RuntimeError("exiftool not found. Install: sudo apt install libimage-exiftool-perl")

    def name(self) -> str:
        return "exiftool"

    def extract(self, files: Iterable[Path]) -> Dict[str, Metadata]:
        paths = [str(p) for p in files]
        if not paths:
            return {}
        cmd = [
            "exiftool",
            "-m",
            "-q",
            "-q",
            "-j",
            "-DateTimeOriginal",
            "-CreateDate",
            "-Model",
            "-LensModel",
            "-SerialNumber",
            "-GPSLatitude",
            "-GPSLongitude",
            "-ImageWidth",
            "-ImageHeight",
            "-Duration",
        ] + paths
        proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
        # exiftool may return non-zero when some files are unreadable but still emit useful JSON.
        if not proc.stdout.strip() and proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or f"exiftool failed with code {proc.returncode}")
        rows = json.loads(proc.stdout or "[]")
        out: Dict[str, Metadata] = {}
        for row in rows:
            src = str(row.get("SourceFile", ""))
            if not src:
                continue
            out[src] = {
                "DateTimeOriginal": row.get("DateTimeOriginal"),
                "CreateDate": row.get("CreateDate"),
                "Model": row.get("Model"),
                "LensModel": row.get("LensModel"),
                "SerialNumber": row.get("SerialNumber"),
                "GPSLatitude": row.get("GPSLatitude"),
                "GPSLongitude": row.get("GPSLongitude"),
                "ImageWidth": row.get("ImageWidth"),
                "ImageHeight": row.get("ImageHeight"),
                "Duration": row.get("Duration"),
            }
        return out
