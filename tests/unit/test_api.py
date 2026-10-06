from __future__ import annotations

import pytest

from synthguard.api import first_result, screen_payload
from synthguard.samples import TOO_SHORT


def test_screen_payload_from_fasta() -> None:
    body = {"fasta": ">plasmid-backbone-fragment\n" + ("ATG" * 40)}
    payload = screen_payload(body)
    assert payload["detection_only"] is True
    assert payload["results"]


def test_screen_payload_too_short() -> None:
    payload = screen_payload({"sequence": TOO_SHORT, "query_id": "short"})
    assert payload["exit_code"] == 1
    assert payload["results"][0]["status"] == "NOT_SCREENABLE"


def test_screen_payload_requires_input() -> None:
    with pytest.raises(ValueError):
        screen_payload({})
    result = first_result({"sequence": "ATG" + "AAA" * 30 + "TAA"})
    assert result.query_id == "query"
