#!/usr/bin/env python3
"""Download the immutable P4.23.2 source and verify its SHA-256 before use."""
import argparse, hashlib, pathlib, urllib.request

URL = "https://raw.githubusercontent.com/Shubhamnpk/yonepse/d26f543b0b88d38a47020235aef66ccecf3d11c1/data/floor_sheet/daily/2025-07-28.json"
EXPECTED_SHA256 = "4b37929a86d1f2a3f09526afc874186dd716e90eec2736904ef5ec37d4dd71e0"
EXPECTED_BYTES = 8563784

def main():
    p = argparse.ArgumentParser()
    p.add_argument("output", type=pathlib.Path)
    args = p.parse_args()
    data = urllib.request.urlopen(URL, timeout=60).read()
    digest = hashlib.sha256(data).hexdigest()
    if len(data) != EXPECTED_BYTES or digest != EXPECTED_SHA256:
        raise SystemExit(f"source verification failed: bytes={len(data)} sha256={digest}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    print(f"verified {len(data)} bytes sha256={digest} -> {args.output}")

if __name__ == "__main__":
    main()
