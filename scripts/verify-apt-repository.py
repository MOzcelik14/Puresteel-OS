#!/usr/bin/env python3
"""Read-only verification of the published Puresteel APT archive.

Uses the *committed public key*; this script never imports or accesses a
signing private key. Run it before and after publishing a signed release.
"""
import argparse
import gzip
import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "docs/apt"
DIST = ARCHIVE / "dists/stable"
INDEX = DIST / "main/binary-amd64/Packages"
KEY = ARCHIVE / "puresteel-archive-keyring.asc"


def fail(message):
    raise SystemExit("Puresteel APT integrity check failed: " + message)


def checked(command):
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode:
        fail(" ".join(str(arg) for arg in command[:2]) + ": " +
             (result.stderr or result.stdout)[-1200:].strip())
    return result.stdout.strip()


def fields(paragraph):
    return dict(
        line.split(": ", 1)
        for line in paragraph.splitlines()
        if ": " in line and not line.startswith((" ", "\t"))
    )


def verify(require_current=False, require_version=None):
    for target in (KEY, DIST / "InRelease", DIST / "Release",
                   DIST / "Release.gpg", INDEX, Path(str(INDEX) + ".gz")):
        if not target.is_file():
            fail("missing " + str(target.relative_to(ROOT)))

    with tempfile.TemporaryDirectory(prefix="puresteel-apt-public-key-") as tmp:
        keyring = Path(tmp) / "archive.gpg"
        checked(["gpg", "--batch", "--yes", "--dearmor", "-o",
                 str(keyring), str(KEY)])
        checked(["gpgv", "--keyring", str(keyring), str(DIST / "InRelease")])
        checked(["gpgv", "--keyring", str(keyring),
                 str(DIST / "Release.gpg"), str(DIST / "Release")])

    release = (DIST / "Release").read_text(encoding="utf-8")
    hashes = {}
    in_sha256 = False
    for line in release.splitlines():
        if line == "SHA256:":
            in_sha256 = True
            continue
        if in_sha256:
            if not line.startswith((" ", "\t")):
                break
            columns = line.split()
            if len(columns) != 3:
                fail("malformed SHA256 section in Release")
            digest, size, name = columns
            if not re.fullmatch(r"[a-fA-F0-9]{64}", digest) or not size.isdigit():
                fail("malformed SHA256 entry: " + name)
            hashes[name] = (digest.lower(), int(size))

    for name in ("main/binary-amd64/Packages",
                 "main/binary-amd64/Packages.gz"):
        if name not in hashes:
            fail("Release does not attest " + name)
        path = DIST / name
        digest, size = hashes[name]
        if len(path.read_bytes()) != size:
            fail("size mismatch for " + name)
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            fail("checksum mismatch for " + name)

    if gzip.decompress(Path(str(INDEX) + ".gz").read_bytes()) != INDEX.read_bytes():
        fail("Packages.gz does not match Packages")

    entries = [fields(chunk) for chunk in INDEX.read_text(encoding="utf-8").split("\n\n")
               if chunk.strip()]
    if not entries:
        fail("Packages index is empty")
    center_versions = []
    archive_root = ARCHIVE.resolve()
    for entry in entries:
        for required in ("Package", "Version", "Filename", "SHA256", "Size"):
            if not entry.get(required):
                fail("index entry lacks " + required)
        relative = Path(entry["Filename"])
        if (relative.is_absolute() or ".." in relative.parts or
                relative.parts[:3] != ("pool", "main", "p")):
            fail("invalid pool path " + entry["Filename"])
        package = (ARCHIVE / relative).resolve()
        if not package.is_relative_to(archive_root) or not package.is_file():
            fail("missing or unsafe pool package " + entry["Filename"])
        content = package.read_bytes()
        if len(content) != int(entry["Size"]):
            fail("size mismatch for " + entry["Filename"])
        if hashlib.sha256(content).hexdigest() != entry["SHA256"].lower():
            fail("checksum mismatch for " + entry["Filename"])
        for field in ("Package", "Version", "Architecture"):
            actual = checked(["dpkg-deb", "-f", str(package), field])
            if actual != entry.get(field, ""):
                fail(field + " metadata mismatch for " + entry["Filename"] +
                     ": expected " + repr(entry.get(field, "")) +
                     ", got " + repr(actual))
        if entry["Package"] == "puresteel-center":
            center_versions.append(entry["Version"])

    if require_current or require_version:
        expected = require_version or (ROOT / "packages/puresteel-center/VERSION").read_text().strip()
        if expected not in center_versions:
            fail("required Center version " + expected +
                 " is not included in the signed Packages index")

    print("Puresteel APT signature, Release checksums, gzip index and " +
          str(len(entries)) + " pool package(s): VERIFIED")
    if center_versions:
        print("Signed puresteel-center version(s): " + ", ".join(center_versions))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-current", action="store_true",
                        help="Require source Center version in the signed index")
    parser.add_argument("--require-version", metavar="DEBIAN_VERSION",
                        help="Require a specific signed Center version (rolling release)")
    args = parser.parse_args()
    try:
        verify(args.require_current, args.require_version)
    except (OSError, ValueError, gzip.BadGzipFile) as error:
        fail(str(error))
