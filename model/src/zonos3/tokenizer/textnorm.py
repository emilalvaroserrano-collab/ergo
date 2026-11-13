"""TTS text normalization: zyphra_textnorm (Rust ports of the NeMo grammars, github.com/Zyphra/zyphra-textnorm).

Converts written text to its spoken form ("$5.32" -> "five dollars thirty two cents") before tokenization, in the
grammar of the request language's ``nemo`` package (registries/languages.json), with the nonverbal markup the model
reads kept as typed. Tagalog has no NeMo grammar and uses the native normalizer in ``zonos3.tts.tagalog`` instead.
Disable globally with ZONOS3_TTS_NORM=0, or per request via the text_normalization flag.
"""

from __future__ import annotations

import os

import zyphra_textnorm

from zonos3 import languages
from zonos3.tts.markup import NONVERBAL_MARKUP_TAGS
from zonos3.tts.tagalog import normalize as normalize_tagalog

collapse_line_breaks = zyphra_textnorm.collapse_line_breaks


def normalization_enabled() -> bool:
    return os.environ.get("ZONOS3_TTS_NORM", "1") != "0"


class TTSTextNormalizer:
    """The Rust normalizer for server language codes, keeping the nonverbal markup; memoized inside. ``normalize``
    never raises: unsupported languages come back with line breaks collapsed."""

    def __init__(self) -> None:
        self._tn = zyphra_textnorm.Normalizer(NONVERBAL_MARKUP_TAGS)

    def normalize(self, text: str, language: str) -> str:
        lang = languages.BY_CODE.get(language)
        if lang is not None and lang.code == "tl":
            return normalize_tagalog(collapse_line_breaks(text))
        # Languages without a NeMo grammar (the registry's empty `nemo`) pass through as written.
        if lang is None or not lang.nemo:
            return collapse_line_breaks(text)
        return self._tn.normalize(text, lang.nemo)


def load_normalizer() -> TTSTextNormalizer | None:
    """The server's normalizer (None with ZONOS3_TTS_NORM=0)."""
    return TTSTextNormalizer() if normalization_enabled() else None


def normalize_request_text(text: str, language: str, normalizer) -> str:
    """A request's text as the prompt builder gets it: line breaks collapsed (also when normalization is off), then
    ``normalizer.normalize`` (anything with that method; None skips it)."""
    text = collapse_line_breaks(text)
    return text if normalizer is None else normalizer.normalize(text, language)
