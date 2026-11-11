import pytest

from src.answer.formatters import (
    NOT_FOUND_MESSAGE,
    attach_citations,
    format_response,
    format_source,
    format_sources,
)

EVIDENCE = [
    {"source": "kito_manual.pdf", "page": 1, "text": "Full charge time: 90 minutes at the Kito Dock."},
    {"source": "kito_manual.pdf", "page": 1, "text": "Place the Kito Dock on a flat floor."},
    {"source": "notes.docx", "page": None, "text": "The office opens at 8 am."},
]


def test_source_with_page():
    assert format_source("kito_manual.pdf", 1) == "kito_manual.pdf, page 1"


def test_source_without_page():
    assert format_source("notes.docx", None) == "notes.docx"


def test_numbers_become_sources():
    answer = "Kito charges in 90 minutes [1]. The office opens at 8 am [3]."
    expected = "Kito charges in 90 minutes [kito_manual.pdf, page 1]. The office opens at 8 am [notes.docx]."
    assert attach_citations(answer, EVIDENCE) == expected


def test_unknown_number_is_removed():
    assert attach_citations("A made-up fact [9].", EVIDENCE) == "A made-up fact."


def test_sources_only_used_once_in_order():
    answer = "Opens at 8 [3]. Charges in 90 minutes [1] at the dock [2]. Opens at 8 [3]. Made up [9]."
    assert format_sources(answer, EVIDENCE) == ["notes.docx", "kito_manual.pdf, page 1"]


def test_response_with_sources():
    result = format_response("Kito charges in 90 minutes.", ["kito_manual.pdf, page 1"])
    assert result == "Kito charges in 90 minutes.\n\nSources:\n- kito_manual.pdf, page 1"


@pytest.mark.parametrize("answer", ["NOT_FOUND", "NOT_FOUND.", "\nNOT_FOUND\n"])
def test_not_found_message(answer):
    assert format_response(answer, []) == NOT_FOUND_MESSAGE