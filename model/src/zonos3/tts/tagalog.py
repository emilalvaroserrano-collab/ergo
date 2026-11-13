"""Tagalog (Filipino): letter-to-sound and text normalization.

Two gaps for Tagalog in the shared stack:

- espeak-ng has no Tagalog voice here, so ``zonos3.tts.phonemes`` cannot guess words missing from the pronunciation
  lexicon. ``tagalog_ipa`` is a rule-based Tagalog G2P for those words (the lexicon itself carries the curated
  WikiPron pronunciations).
- ``zyphra_textnorm`` has no Tagalog grammar (the registry's empty ``nemo``), so numbers, currency, dates,
  abbreviations and symbols used to reach the model as written and were not read at all. ``normalize`` verbalizes
  them in native Tagalog.

Pronunciation groups (U+E000 IPA U+E001) and nonverbal markup are left as typed, like the Rust normalizer does.
"""

from __future__ import annotations

import re
import unicodedata

from zonos3.tts.markup import NONVERBAL_MARKUP_TAGS

# --- Letter-to-sound ---------------------------------------------------------------------------------------------

_VOWELS = frozenset("aeiou")
# Tagalog abakada letters; loans keep the spelling-to-sound adaptations of the first Wiktionary reading
# (v -> b, z -> s), which is what most Tagalog words and names use. j is the English loan /dʒ/; the lexicon
# carries the Spanish names read with /h/ (Jose, Juan, ...).
_LETTERS = {
    "b": "b",
    "k": "k",
    "d": "d",
    "g": "ɡ",
    "h": "h",
    "l": "l",
    "m": "m",
    "n": "n",
    "p": "p",
    "r": "ɾ",
    "s": "s",
    "t": "t",
    "w": "w",
    "y": "j",
    "f": "f",
}
_IRREGULAR = {
    "mga": "maŋa",  # the plural marker is read ma-nga
    "ng": "naŋ",  # the particle is read nang, not ng
    "ng̃": "naŋ",
    "oo": "ʔoʔo",
    "noong": "noʔoŋ",
    "noon": "noʔon",
    "doon": "doʔon",
}


def tagalog_ipa(word: str) -> str | None:
    """Rule-based Tagalog IPA of one word, or None when it has no Tagalog reading.

    Tagalog orthography is close to phonemic: ``ng`` is /ŋ/, vowel-initial words take a glottal stop, a hyphen
    between vowels is a glottal stop (``pag-asa``), and Spanish loans use the abakada adaptations. Stress and the
    unwritten final glottal stop cannot be recovered from plain spelling (the lexicon has them for known words).
    """
    text = unicodedata.normalize("NFC", word).casefold().replace("’", "'")
    if text in _IRREGULAR:
        return _IRREGULAR[text]
    if not text or any(not (c.isalpha() or c in "-'") for c in text):
        return None

    phones: list[str] = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        nxt2 = text[i + 2] if i + 2 < n else ""
        if c == "-":
            if nxt in _VOWELS:
                phones.append("ʔ")
            i += 1
            continue
        if c == "'":
            # A contraction apostrophe after a vowel keeps the word's final glottal stop: gabi't, dalawampu't.
            if i and text[i - 1] in _VOWELS:
                phones.append("ʔ")
            i += 1
            continue
        if c == "ñ":
            phones += ["n", "j"]
            i += 1
            continue
        if c == "n" and nxt == "g":
            phones.append("ŋ")
            i += 2
            continue
        if c == "t" and nxt == "s":
            phones += ["t", "s"]
            i += 2
            continue
        if c == "c" and nxt == "h":
            phones.append("t͡ʃ")
            i += 2
            continue
        if c == "s" and nxt == "h":
            phones.append("ʃ")
            i += 2
            continue
        if c == "q" and nxt == "u":
            phones.append("k")
            i += 2
            continue
        if c == "l" and nxt == "l":
            phones.append("l")
            i += 2
            continue
        if c == "r" and nxt == "r":
            phones.append("r")
            i += 2
            continue
        if c == "g" and nxt == "u" and nxt2 in "ei":
            phones.append("ɡ")
            i += 2
            continue
        if c == "c":
            phones.append("s" if nxt in "ei" else "k")
            i += 1
            continue
        if c == "x":
            phones += ["k", "s"]
            i += 1
            continue
        if c == "j":
            phones.append("dʒ")
            i += 1
            continue
        if c in "vz":
            phones.append("b" if c == "v" else "s")
            i += 1
            continue
        if c in _VOWELS:
            phones.append(c)
            i += 1
            continue
        if c in _LETTERS:
            phones.append(_LETTERS[c])
            i += 2 if nxt == c else 1  # geminates are single consonants in Tagalog
            continue
        return None

    if phones and phones[0] in _VOWELS:
        phones.insert(0, "ʔ")
    return "".join(phones)


# --- Number words ------------------------------------------------------------------------------------------------

_ONES = ("sero", "isa", "dalawa", "tatlo", "apat", "lima", "anim", "pito", "walo", "siyam")
_TEENS = {
    10: "sampu",
    11: "labing-isa",
    12: "labindalawa",
    13: "labintatlo",
    14: "labing-apat",
    15: "labinlima",
    16: "labing-anim",
    17: "labimpito",
    18: "labing-walo",
    19: "labinsiyam",
}
_TENS = {
    20: "dalawampu",
    30: "tatlumpu",
    40: "apatnapu",
    50: "limampu",
    60: "animnapu",
    70: "pitumpu",
    80: "walumpu",
    90: "siyamnapu",
}
_HUNDREDS = {
    1: "isang daan",
    2: "dalawang daan",
    3: "tatlong daan",
    4: "apat na raan",
    5: "limang daan",
    6: "anim na raan",
    7: "pitong daan",
    8: "walong daan",
    9: "siyam na raan",
}
_SCALES = ("", "libo", "milyon", "bilyon", "trilyon", "kuwadrilyon")
_ORDINAL_IRREGULAR = {1: "una", 2: "ikalawa", 3: "ikatlo"}
_MONTHS = "Enero|Pebrero|Marso|Abril|Mayo|Hunyo|Hulyo|Agosto|Setyembre|Oktubre|Nobyembre|Disyembre"


def _link(phrase: str) -> str:
    """Attach the Tagalog linker to the last word of ``phrase``: -ng after a vowel, -g after n, na otherwise."""
    last = phrase.rsplit(" ", 1)[-1]
    if last and last[-1] in _VOWELS:
        return phrase + "ng"
    if last.endswith("n"):
        return phrase + "g"
    return phrase + " na"


def _below_100(n: int) -> str:
    if n < 10:
        return _ONES[n]
    if n < 20:
        return _TEENS[n]
    tens, rest = divmod(n, 10)
    word = _TENS[tens * 10]
    return f"{word}'t {_below_100(rest)}" if rest else word


def _below_1000(n: int) -> str:
    hundreds, rest = divmod(n, 100)
    parts = []
    if hundreds:
        parts.append(_HUNDREDS[hundreds])
    if rest:
        if parts:
            parts.append("at")
        parts.append(_below_100(rest))
    return " ".join(parts)


def number_words(n: int) -> str:
    """Native Tagalog cardinal of a non-negative integer."""
    if n == 0:
        return "sero"
    if n >= 1000 ** len(_SCALES):
        return " ".join(_ONES[int(d)] for d in str(n))  # beyond kuwadrilyon: read the digits
    groups: list[tuple[int, str]] = []
    scale = 0
    while n:
        n, rest = divmod(n, 1000)
        if rest:
            words = _below_1000(rest)
            if scale:
                words = f"{_link(words)} {_SCALES[scale]}"
            groups.append((rest, words))
        scale += 1
    groups.reverse()
    result = groups[0][1]
    for rest, words in groups[1:]:
        result += (" at " if rest < 100 else ", ") + words
    return result


def ordinal_words(n: int) -> str:
    """Tagalog ordinal: una, ikalawa, ikatlo, then ika- + the cardinal (ikaapat, ikalima, ...)."""
    if n in _ORDINAL_IRREGULAR:
        return _ORDINAL_IRREGULAR[n]
    return f"ika{number_words(n)}"


def decimal_words(number: str) -> str:
    whole, _, fraction = number.replace(",", "").partition(".")
    words = number_words(int(whole or 0))
    if fraction:
        digits = " ".join(_ONES[int(d)] for d in fraction)
        words = f"{words} punto {digits}"
    return words


# --- Text normalization ------------------------------------------------------------------------------------------

# Words that do not take the number linker after them: a number before a conjunction, a particle, a pronoun or a
# preposition is read on its own ("lima at anim", "5 na libro" already carries its linker).
_NO_LINKER = frozenset(
    """at o ng nang na sa si ni kay mula hanggang para dahil pero kung habang pagkatapos bago ay ito iyan iyon
    ako ikaw siya kami tayo kayo sila ko mo niya namin natin ninyo nila""".split()
)
_UNITS = {
    "kg": "kilo",
    "km": "kilometro",
    "cm": "sentimetro",
    "mm": "milimetro",
    "ml": "mililitro",
    "mL": "mililitro",
    "l": "litro",
    "L": "litro",
    "mg": "miligramo",
    "g": "gramo",
    "m": "metro",
    "s": "segundo",
    "min": "minuto",
    "hr": "oras",
    "oras": "oras",
    "araw": "araw",
    "linggo": "linggo",
    "buwan": "buwan",
    "taon": "taon",
}
_ABBREVIATIONS = (
    (r"\bGng\.", "Ginang"),
    (r"\bBb\.", "Binibini"),
    (r"\bG\.(?=\s+[A-ZÁÉÍÓÚÑ])", "Ginoo"),
    (r"\bDok\.", "Doktor"),
    (r"\bDr\.", "Doktor"),
    (r"\bAtty\.", "Abogado"),
    (r"\bEngr\.", "Inhinyero"),
    (r"\bProf\.", "Propesor"),
    (r"\bSen\.", "Senador"),
    (r"\bRep\.", "Representante"),
    (r"\bGov\.", "Gobernador"),
    (r"\bLt\.", "Tenyente"),
    (r"\bGen\.", "Heneral"),
    (r"\bCol\.", "Koronel"),
    (r"\bPng\.", "Pangulo"),
    (r"\bBrgy\.", "Barangay"),
    (r"\bDept\.", "Departamento"),
    (r"\bUniv\.", "Unibersidad"),
    (r"\bTel\.", "Telepono"),
    (r"\bSta\.", "Santa"),
    (r"\bSto\.", "Santo"),
    (r"\bJr\.", "Junior"),
    (r"\bSr\.", "Senior"),
    (r"\bNo\.(?=\s*\d)", "Numero"),
    (r"\bBlg\.", "Bilang"),
    (r"\batbp\.", "at iba pa"),
    (r"\betc\.", "at iba pa"),
    (r"\bhal\.", "halimbawa"),
    (r"\bMr\.", "Ginoo"),
    (r"\bMrs\.", "Ginang"),
    (r"\bMs\.", "Binibini"),
    (r"\bCapt\.", "Kapitan"),
    (r"\bSgt\.", "Sargento"),
    (r"\bCorp\.", "Korporasyon"),
    (r"\bInc\.", "Inkorporada"),
    (r"\bCo\.", "Kompanya"),
    (r"\bLtd\.", "Limitado"),
    (r"\bAve\.", "Abenida"),
    (r"\bBlvd\.", "Bulebar"),
    (r"\bRd\.", "Kalsada"),
    (r"\bRm\.", "Silid"),
    (r"\bBldg\.", "Gusali"),
    (r"\bFlr\.", "Palapag"),
    (r"\bFil\.", "Filipino"),
    (r"\bPil\.", "Pilipinas"),
    (r"\bhrs\.", "oras"),
    (r"\bmin\.", "minuto"),
    (r"\bseg\.", "segundo"),
)
_CURRENCIES = {
    "₱": "piso",
    "PHP": "piso",
    "P": "piso",
    "$": "dolyar",
    "USD": "dolyar",
    "€": "euro",
    "EUR": "euro",
    "£": "libra",
    "GBP": "libra",
    "¥": "yen",
    "JPY": "yen",
}
_PROTECTED_RE = re.compile(rf"(\ue000[^\ue001]*\ue001|</?(?:{'|'.join(map(re.escape, NONVERBAL_MARKUP_TAGS))})\s*/?>)")
_TIME_RE = re.compile(r"\b([01]?\d|2[0-3]):([0-5]\d)\b(?:\s*(AM|PM|am|pm|A\.M\.|P\.M\.))?")
_AMPM_RE = re.compile(r"\b(\d{1,2})\s*(AM|PM|am|pm|A\.M\.|P\.M\.)\b")
_ORDINAL_RE = re.compile(r"\bika-(\d{1,3})\b", re.IGNORECASE)
_ENGLISH_ORDINAL_RE = re.compile(r"\b(\d{1,3})(?:st|nd|rd|th)\b", re.IGNORECASE)
_RANGE_RE = re.compile(r"(?<![\w-])(\d+)\s*[-–—]\s*(\d+)(?![\w-])")
_UNIT_RE = re.compile(r"(?<![\w.])(\d+(?:[.,]\d+)?)\s*(kg|km|cm|mm|mL|ml|L|mg|g|m|min|hr|s)\b")
_CURRENCY_RE = re.compile(
    r"(?<![\w])(₱|PHP|USD|EUR|GBP|JPY|\$|€|£|¥)\s*(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
# The everyday peso shorthand (P25, P 1,250.50), uppercase only to leave words like "P5" in codes alone.
_PESO_RE = re.compile(r"(?<![A-Za-z])P\s*(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\b")
_CURRENCY_WORD_RE = re.compile(
    r"(?<![\w.])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\s*(pesos?|piso|dolyar|dollars?|euro|euros?|libra|yen|sentimo|cents?)\b",
    re.IGNORECASE,
)
_PERCENT_RE = re.compile(r"(?<![\w.])(\d+(?:[.,]\d+)?)\s*%")
_DATE_DAY_FIRST_RE = re.compile(rf"(?i)\b(\d{{1,2}})\s+(?:ng\s+)?({_MONTHS})\b")
_DATE_MONTH_FIRST_RE = re.compile(rf"(?i)\b({_MONTHS})\s+(\d{{1,2}})\b")
_SYMBOLS = (
    ("&", "at"),
    ("@", "at"),
    ("=", "katumbas ng"),
    ("°C", "gradong Celsius"),
    ("°F", "gradong Fahrenheit"),
    ("°", "grado"),
    ("№", "numero"),
    ("#", "numero "),
    ("₱", "piso"),
)


def _next_word(text: str, end: int) -> str | None:
    match = re.match(r"[ \t]+([A-Za-zÁÉÍÓÚÑáéíóúñ]+)", text[end:])
    return match.group(1).casefold() if match else None


def _number_words_with_linker(number: str, text: str, end: int) -> str:
    """The number in words, with the linker when it modifies the following word ("5 libro" -> "limang libro")."""
    words = decimal_words(number)
    following = _next_word(text, end)
    if following and following not in _NO_LINKER:
        return _link(words)
    return words


def _money(amount: str, unit: str) -> str:
    whole, _, fraction = amount.replace(",", "").partition(".")
    whole_n = int(whole or 0)
    cents = int((fraction + "00")[:2]) if fraction else 0
    parts = []
    if whole_n or not cents:
        parts.append(f"{_link(number_words(whole_n))} {unit}" if whole_n else f"{number_words(0)} {unit}")
    if cents:
        parts.append(f"{_link(number_words(cents))} sentimo")
    return " at ".join(parts)


def _time_words(hour: int, minute: int, meridiem: str | None) -> str:
    hour12 = hour % 12 or 12
    words = "ikaisa" if hour12 == 1 else ordinal_words(hour12)
    if minute == 30:
        words += " at kalahati"
    elif minute:
        words += f" at {number_words(minute)} minuto"
    if meridiem:
        suffix = meridiem.upper().replace(".", "")
        if hour == 12 and suffix == "PM":
            words += " ng tanghali"
        elif hour == 12:
            words += " ng hatinggabi"
        else:
            words += " ng umaga" if suffix == "AM" else " ng hapon"
    return words


def _day_words(day: str) -> str:
    return ordinal_words(int(day))


def _normalize_plain(text: str) -> str:
    # 24/7 is an idiom, not a fraction; at/o is the written "and/or".
    text = re.sub(r"\b24\s*/\s*7\b", "dalawampu't apat na oras, pitong araw", text)
    text = re.sub(r"\bat/o\b", "at o", text, flags=re.IGNORECASE)
    # Ranges: 5-6 -> lima hanggang anim.
    text = _RANGE_RE.sub(lambda m: f"{number_words(int(m.group(1)))} hanggang {number_words(int(m.group(2)))}", text)
    # Currency symbols and ISO codes.
    text = _CURRENCY_RE.sub(lambda m: _money(m.group(2), _CURRENCIES[m.group(1).upper()]), text)
    text = _PESO_RE.sub(lambda m: _money(m.group(1), "piso"), text)
    # Currency words after a number: 5 piso -> limang piso.
    text = _CURRENCY_WORD_RE.sub(lambda m: f"{_link(decimal_words(m.group(1)))} {_currency_word(m.group(2))}", text)
    # Percent.
    text = _PERCENT_RE.sub(lambda m: f"{_link(decimal_words(m.group(1)))} porsiyento", text)
    # Clock times, before plain numbers.
    text = _TIME_RE.sub(lambda m: _time_words(int(m.group(1)), int(m.group(2)), m.group(3)), text)
    text = _AMPM_RE.sub(lambda m: _time_words(int(m.group(1)), 0, m.group(2)), text)
    # Ordinals first, so "ika-5 ng Mayo" is ika + lima, not ika + ikalima.
    text = _ORDINAL_RE.sub(lambda m: ordinal_words(int(m.group(1))), text)
    text = _ENGLISH_ORDINAL_RE.sub(lambda m: ordinal_words(int(m.group(1))), text)
    # Dates: "25 ng Mayo" and "Mayo 25".
    text = _DATE_DAY_FIRST_RE.sub(lambda m: f"{_day_words(m.group(1))} ng {m.group(2).capitalize()}", text)
    text = _DATE_MONTH_FIRST_RE.sub(lambda m: f"{m.group(1).capitalize()} {_day_words(m.group(2))}", text)
    # Units: 5kg -> limang kilo.
    text = _UNIT_RE.sub(lambda m: f"{_link(decimal_words(m.group(1)))} {_UNITS[m.group(2)]}", text)
    # Remaining numbers; a sentence-final period is punctuation, not a decimal point.
    text = re.sub(
        r"(?<![\w.,])([+-]?)(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?![\w,]|\.\d)",
        lambda m: _signed_number(m.group(1), m.group(2), m.string, m.end()),
        text,
    )
    # Abbreviations, then the remaining symbols.
    for pattern, replacement in _ABBREVIATIONS:
        text = re.sub(pattern, replacement, text)
    for symbol, replacement in _SYMBOLS:
        text = text.replace(symbol, replacement)
    return text


def _currency_word(word: str) -> str:
    word = word.casefold()
    if word.startswith("peso") or word == "piso":
        return "piso"
    if word.startswith("dollar") or word == "dolyar":
        return "dolyar"
    if word.startswith("euro"):
        return "euro"
    if word.startswith("libra"):
        return "libra"
    if word.startswith("yen"):
        return "yen"
    if word.startswith("sentimo") or word.startswith("cent"):
        return "sentimo"
    return word


def _signed_number(sign: str, number: str, text: str, end: int) -> str:
    prefix = "minus " if sign == "-" else "plus " if sign == "+" else ""
    if prefix:
        return prefix + decimal_words(number)
    return _number_words_with_linker(number, text, end)


def normalize(text: str) -> str:
    """Native Tagalog verbalization of numbers, currency, dates, times, abbreviations and symbols.

    Pronunciation groups and nonverbal markup are preserved exactly. Line breaks are collapsed by the caller
    (``zonos3.tokenizer.textnorm``), like the Rust grammars.
    """
    parts = _PROTECTED_RE.split(text)
    for i in range(0, len(parts), 2):
        parts[i] = _normalize_plain(parts[i])
    return "".join(parts)
