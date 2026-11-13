# Pronunciation lexicons

`tagalog.lmdb` is the Tagalog (`tgl`) pronunciation lexicon served by `--tts-phoneme-lexicon`. It is built from
WikiPron's Tagalog broad transcription scrape (`tgl_latn_broad.tsv`, first Wiktionary pronunciation per headword),
which is CC BY-SA 4.0. The `tgl` DB stores one unspaced IPA value per normalized headword; `meta` declares
`mode: "words"` and `version: 1`.

Rebuild (the output directory must not exist):

```bash
.venv/bin/python tools/build_tagalog_lexicon.py --tsv tgl_latn_broad.tsv --out assets/lexicons/tagalog.lmdb
```

Without `--tsv` the script downloads
`https://raw.githubusercontent.com/CUNY-CL/wikipron/master/data/scrape/tsv/tgl_latn_broad.tsv`.

Words missing from the lexicon (and the studio's `guess` requests) use the built-in rule-based Tagalog G2P in
`zonos3.tts.tagalog`; espeak-ng has no Tagalog voice. Text normalization for Tagalog is native as well
(`zonos3.tts.tagalog.normalize`, wired through `zonos3.tokenizer.textnorm`).
