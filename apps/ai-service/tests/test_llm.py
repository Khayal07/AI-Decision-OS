"""Tests for the LLM JSON extraction helper (no network)."""

from app.router.llm import extract_json


def test_extract_plain_json() -> None:
    assert extract_json('{"a": 1}') == '{"a": 1}'


def test_extract_fenced_json() -> None:
    text = '```json\n{"a": 1}\n```'
    assert extract_json(text) == '{"a": 1}'


def test_extract_json_with_prose() -> None:
    text = 'Here is the result:\n{"winner": "A"}\nDone.'
    assert extract_json(text) == '{"winner": "A"}'
