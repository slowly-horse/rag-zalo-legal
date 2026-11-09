from __future__ import annotations

import unicodedata

from src.ingest.clean import normalize_text


def test_collapses_spaces_but_preserves_newlines():
    cleaned = normalize_text("1.  Khoản một\n2.   Khoản hai")
    assert cleaned == "1. Khoản một\n2. Khoản hai"


def test_normalizes_to_nfc():
    decomposed = unicodedata.normalize("NFD", "Điều")
    assert decomposed != "Điều"
    assert normalize_text(decomposed) == "Điều"


def test_nfc_makes_visually_identical_words_compare_equal():
    a = normalize_text(unicodedata.normalize("NFD", "quyết định"))
    b = normalize_text(unicodedata.normalize("NFC", "quyết định"))
    assert a == b


def test_collapses_excess_blank_lines():
    assert normalize_text("a\n\n\n\n\nb") == "a\n\nb"


def test_strips_trailing_whitespace_before_newline():
    assert normalize_text("a   \nb") == "a\nb"


def test_handles_empty_input():
    assert normalize_text("") == ""
    assert normalize_text(None) == ""


def test_clean_flattens_newlines_absent():
    assert normalize_text("  Điều 1.   Phạm vi  ") == "Điều 1. Phạm vi"


def test_replaces_nbsp():
    assert normalize_text("Nội\u00a0dung") == "Nội dung"
    assert normalize_text("Điều\u00a01") == "Điều 1"


def test_preserves_norma_text():
    text = "Điều 1. Phạm vi\n\n1. Nội dung"
    assert normalize_text(text) == text