"""Optional POST /screen handler. The demo does not start a server."""

from __future__ import annotations

from typing import Any

from synthguard.fasta import parse_fasta
from synthguard.schemas import ScreenResult
from synthguard.screen import screen_sequence


def screen_payload(body: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a JSON body the way POST /screen would.

    Accepted keys: fasta (text) or sequence (raw). Detection only.
    """

    fasta = body.get("fasta")
    sequence = body.get("sequence")
    if isinstance(fasta, str) and fasta.strip():
        records = parse_fasta(fasta)
        if not records:
            raise ValueError("fasta contained no records")
        results = [screen_sequence(record.sequence, query_id=record.header) for record in records]
    elif isinstance(sequence, str) and sequence.strip():
        query_id = str(body.get("query_id") or "query")
        results = [screen_sequence(sequence.strip().upper(), query_id=query_id)]
    else:
        raise ValueError("POST /screen requires fasta or sequence")
    return {
        "results": [item.model_dump(mode="json") for item in results],
        "exit_code": max(item.exit_code for item in results),
        "detection_only": True,
    }


def first_result(body: dict[str, Any]) -> ScreenResult:
    payload = screen_payload(body)
    return ScreenResult.model_validate(payload["results"][0])
