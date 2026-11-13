"""Build a Tagalog pronunciation lexicon (LMDB) from WikiPron broad transcription.

The shared pronunciation lexicon format (``zonos3.tts.phonemes``) needs a ``meta`` record and one named DB per
language. This builder fills ``tgl`` from WikiPron's Tagalog scrape (``tgl_latn_broad.tsv``), keeping the first
Wiktionary pronunciation of each headword: the alternative readings are mostly Spanish/English doublets, and a single
pronunciation is what the model reads (ambiguous entries are left out of the TTS pronunciation input).

Usage::

    .venv/bin/python tools/build_tagalog_lexicon.py [--tsv tgl_latn_broad.tsv] [--out assets/lexicons/tagalog.lmdb]

Without ``--tsv`` the file is downloaded from WikiPron. The output is a committed runtime asset, so rerun this only
when the upstream scrape or our headword normalization changes.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

import lmdb
from zonos3.tts.phonemes import LEXICON_VERSION, normalize_headword

WIKIPRON_URL = "https://raw.githubusercontent.com/CUNY-CL/wikipron/master/data/scrape/tsv/tgl_latn_broad.tsv"
DEFAULT_OUT = Path(__file__).resolve().parent.parent / "assets" / "lexicons" / "tagalog.lmdb"


def read_entries(tsv: str) -> dict[str, str]:
    """First pronunciation per normalized headword, IPA joined into the lexicon's unspaced notation."""
    entries: dict[str, str] = {}
    skipped = 0
    for line in tsv.splitlines():
        if not line or line.startswith("#"):
            continue
        headword, _, ipa = line.partition("\t")
        key = normalize_headword(headword)
        if not key or len(key.encode()) > 500 or " " in key:
            skipped += 1  # word-mode lookup never sees multiword keys
            continue
        if key in entries:
            continue
        value = ipa.replace(" ", "")
        if value:
            entries[key] = value
    print(f"{len(entries)} headwords ({skipped} skipped)", file=sys.stderr)
    return entries


def build(entries: dict[str, str], out: Path, source: str) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        raise SystemExit(f"{out} already exists; remove it first to rebuild")
    env = lmdb.open(str(out), map_size=1 << 26, max_dbs=8, subdir=True)
    try:
        db = env.open_db(b"tgl")
        with env.begin(write=True, db=db) as txn:
            for headword in sorted(entries):
                txn.put(headword.encode(), entries[headword].encode())
        meta = {
            "version": LEXICON_VERSION,
            "languages": {
                "tgl": {
                    "mode": "words",
                    "script": "Latn",
                    "words": len(entries),
                    "gold": len(entries),
                    "sources": ["wikipron"],
                }
            },
            "sources": [{"name": "WikiPron", "url": source, "license": "CC BY-SA 4.0"}],
        }
        with env.begin(write=True) as txn:
            txn.put(b"meta", json.dumps(meta, ensure_ascii=False, sort_keys=True).encode())
    finally:
        env.close()
    print(f"wrote {out} ({sum(p.stat().st_size for p in out.iterdir()) / 1e6:.1f} MB)", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tsv", type=Path, help="local tgl_latn_broad.tsv (downloaded when omitted)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help=f"output LMDB directory (default: {DEFAULT_OUT})")
    args = parser.parse_args()
    if args.tsv:
        tsv = args.tsv.read_text(encoding="utf8")
        source = str(args.tsv)
    else:
        print(f"downloading {WIKIPRON_URL}", file=sys.stderr)
        with urllib.request.urlopen(WIKIPRON_URL, timeout=120) as response:
            tsv = response.read().decode("utf8")
        source = WIKIPRON_URL
    build(read_entries(tsv), args.out, source)


if __name__ == "__main__":
    main()
