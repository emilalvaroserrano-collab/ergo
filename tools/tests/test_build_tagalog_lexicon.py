"""tools/build_tagalog_lexicon.py: WikiPron parsing and the LMDB it writes."""

from __future__ import annotations

import json

import build_tagalog_lexicon
import lmdb
import pytest


def test_read_entries_keeps_the_first_pronunciation_and_joins_the_phones():
    tsv = "\n".join(
        [
            "'day\td a j",
            "'day\td e",
            "A\ta",
            "a\tʔ a",  # the same normalized headword: the first reading wins
            "buwan ng wika\tb u w a n",  # word-mode lookup never sees multiword keys
            "kumusta\tk u m u s t a",
        ]
    )
    assert build_tagalog_lexicon.read_entries(tsv) == {
        "'day": "daj",
        "a": "a",
        "kumusta": "kumusta",
    }


def test_build_writes_meta_and_the_tgl_db(tmp_path):
    out = tmp_path / "tagalog.lmdb"
    build_tagalog_lexicon.build({"mga": "maŋa", "ng": "naŋ"}, out, "test-source")
    env = lmdb.open(str(out), readonly=True, max_dbs=8)
    try:
        with env.begin() as txn:
            meta = json.loads(txn.get(b"meta"))
        assert meta["version"] == 1
        assert meta["languages"]["tgl"]["mode"] == "words"
        assert meta["languages"]["tgl"]["words"] == 2
        assert meta["sources"] == [{"name": "WikiPron", "url": "test-source", "license": "CC BY-SA 4.0"}]
        db = env.open_db(b"tgl")
        with env.begin(db=db) as txn:
            assert txn.get(b"mga") == "maŋa".encode()
            assert txn.get(b"ng") == "naŋ".encode()
    finally:
        env.close()
    with pytest.raises(SystemExit):
        build_tagalog_lexicon.build({"mga": "maŋa"}, out, "test-source")
