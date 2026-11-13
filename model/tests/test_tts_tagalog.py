"""Tagalog (Filipino) letter-to-sound and native text normalization."""

from __future__ import annotations

import pytest
from zonos3.tts.tagalog import decimal_words, normalize, number_words, ordinal_words, tagalog_ipa


@pytest.mark.parametrize(
    "number,words",
    [
        (0, "sero"),
        (1, "isa"),
        (10, "sampu"),
        (11, "labing-isa"),
        (15, "labinlima"),
        (19, "labinsiyam"),
        (20, "dalawampu"),
        (21, "dalawampu't isa"),
        (25, "dalawampu't lima"),
        (99, "siyamnapu't siyam"),
        (100, "isang daan"),
        (101, "isang daan at isa"),
        (123, "isang daan at dalawampu't tatlo"),
        (400, "apat na raan"),
        (1000, "isang libo"),
        (1001, "isang libo at isa"),
        (1234, "isang libo, dalawang daan at tatlumpu't apat"),
        (21000, "dalawampu't isang libo"),
        (100000, "isang daang libo"),
        (1000000, "isang milyon"),
        (10**18, "isa sero sero sero sero sero sero sero sero sero sero sero sero sero sero sero sero sero sero"),
    ],
)
def test_number_words(number, words):
    assert number_words(number) == words


@pytest.mark.parametrize(
    "number,words",
    [(1, "una"), (2, "ikalawa"), (3, "ikatlo"), (4, "ikaapat"), (5, "ikalima"), (21, "ikadalawampu't isa")],
)
def test_ordinal_words(number, words):
    assert ordinal_words(number) == words


def test_decimal_words_reads_the_fraction_digit_by_digit():
    assert decimal_words("1,250.50") == ("isang libo, dalawang daan at limampu punto lima sero")


@pytest.mark.parametrize(
    "text,expected",
    [
        # A number before a noun takes the linker; before a particle or pronoun it does not.
        ("May 25 na libro ako at 3 lapis.", "May dalawampu't lima na libro ako at tatlong lapis."),
        ("5 at 6", "lima at anim"),
        ("Tatlo.", "Tatlo."),
        ("3.", "tatlo."),
        # Ordinals run before the date grammar, so ika-5 is not read as ika-ikalima.
        ("Si Gng. Santos ay dumating noong ika-5 ng Mayo.", "Si Ginang Santos ay dumating noong ikalima ng Mayo."),
        ("Nasa ika-21 ng Hunyo 2026.", "Nasa ikadalawampu't isa ng Hunyo dalawang libo at dalawampu't anim."),
        # Currency, percent, units, times and ranges.
        ("Ang halaga ay ₱1,250.50.", "Ang halaga ay isang libo, dalawang daan at limampung piso at limampung sentimo."),
        ("$5.50", "limang dolyar at limampung sentimo"),
        ("5 piso at 2 dollars", "limang piso at dalawang dolyar"),
        ("P25", "dalawampu't limang piso"),
        ("₱0", "sero piso"),
        ("25% ng mga tao", "dalawampu't limang porsiyento ng mga tao"),
        ("5kg at 3km", "limang kilo at tatlong kilometro"),
        ("5mL at 2L", "limang mililitro at dalawang litro"),
        ("3.5 metro", "tatlo punto limang metro"),
        ("3:30 PM", "ikatlo at kalahati ng hapon"),
        ("12:00 AM", "ikalabindalawa ng hatinggabi"),
        ("5-6 na araw", "lima hanggang anim na araw"),
        ("24/7", "dalawampu't apat na oras, pitong araw"),
        ("at/o", "at o"),
        # Abbreviations and a lone peso sign.
        ("G. Santos at Bb. Reyes", "Ginoo Santos at Binibini Reyes"),
        ("atbp. hal. 5", "at iba pa halimbawa lima"),
        ("₱", "piso"),
        # Decimal and signed numbers.
        ("3.5", "tatlo punto lima"),
        ("-5 degrees", "minus lima degrees"),
    ],
)
def test_normalize(text, expected):
    assert normalize(text) == expected


def test_normalize_keeps_pronunciation_groups_and_nonverbal_markup():
    group = "\ue000skwɜːrəl\ue001"
    assert normalize(f"{group} 5 <laugh/> 3") == f"{group} lima <laugh/> tatlo"
    assert normalize("<shouting>5</shouting>") == "<shouting>lima</shouting>"


@pytest.mark.parametrize(
    "word,ipa",
    [
        ("mga", "maŋa"),
        ("ng", "naŋ"),
        ("kumusta", "kumusta"),
        ("umaga", "ʔumaɡa"),  # vowel-initial words take a glottal stop
        ("Pilipinas", "pilipinas"),
        ("pag-asa", "paɡʔasa"),  # a hyphen before a vowel is a glottal stop
        ("gabi't", "ɡabiʔt"),  # so is a contraction apostrophe after a vowel
        ("mangga", "maŋɡa"),  # ng is one phone
        ("piña", "pinja"),
        ("jeep", "dʒeep"),
        ("computer", "komputeɾ"),
        ("", None),
        ("abc123", None),
        ("hello!", None),
    ],
)
def test_tagalog_ipa(word, ipa):
    assert tagalog_ipa(word) == ipa
