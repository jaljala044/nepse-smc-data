"""Extract the single pinned overlay without unpacking untrusted archive paths."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
from .historical_quarantine import MANIFEST, load_holds


def retrieve(archive, output):
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    archive = Path(archive)
    with archive.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != manifest["artifact_sha256"]:
        raise ValueError("Pinned artifact digest mismatch")
    size = manifest["overlay_bytes"]
    matches = []
    with ZipFile(archive) as z:
        for member in z.infolist():
            if member.is_dir() or member.file_size != size:
                continue
            with z.open(member) as stream:
                raw = stream.read(size + 1)
            if len(raw) == size and hashlib.sha256(raw).hexdigest() == manifest["overlay_sha256"]:
                matches.append(raw)
    if len(matches) != 1:
        raise ValueError("Expected exactly one pinned overlay")
    output = Path(output)
    with output.open("xb") as stream:
        stream.write(matches[0])
    try:
        load_holds(output)
    except Exception:
        output.unlink()
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    retrieve(args.archive, args.output)
