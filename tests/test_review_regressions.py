"""Testes adicionais (não alteram os fornecidos): agregação mensal, arredondamento,
desempate do ranking, entrada sem confirmadas e caminhos de erro/encoding do CLI."""

from __future__ import annotations

import csv
import os
import subprocess
import sys
from pathlib import Path

from helpers import BASE, COLUMNS, PROJECT_ROOT, SRC_DIR, run_cli

RATES = "currency,rate_to_brl\nBRL,1.000000\nUSD,5.420000\nEUR,5.880000\n"


def _invoke(tmp_path: Path, input_bytes: bytes, rates_text: str = RATES):
    """Roda o CLI sem exigir sucesso; devolve o CompletedProcess."""
    input_path = tmp_path / "reservas.csv"
    rates_path = tmp_path / "rates.csv"
    input_path.write_bytes(input_bytes)
    rates_path.write_text(rates_text, encoding="utf-8")
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(SRC_DIR) + os.pathsep + environment.get("PYTHONPATH", "")
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "onfly_report", "--input", str(input_path), "--rates", str(rates_path),
         "--output", str(tmp_path / "report.json")],
        cwd=str(PROJECT_ROOT), env=environment, capture_output=True, text=True, timeout=60,
    )


def _csv_bytes(rows: list[dict[str, str]], prefix: bytes = b"") -> bytes:
    import io

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows({**BASE, **row} for row in rows)
    return prefix + buffer.getvalue().encode("utf-8")


def test_by_month_groups_by_checkin_sorted_and_excludes_non_confirmed(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "checkin_date": "2025-02-05", "checkout_date": "2025-02-06", "amount": "50.00"},
            {"reservation_id": "R-2", "checkin_date": "2025-01-10", "checkout_date": "2025-01-13", "amount": "100.00"},
            # atravessa a virada de mês: entra no mês do check-in
            {"reservation_id": "R-3", "checkin_date": "2025-01-30", "checkout_date": "2025-02-02", "amount": "200.00"},
            {"reservation_id": "R-4", "checkin_date": "2025-02-10", "checkout_date": "2025-02-12",
             "status": "CANCELLED", "amount": "999.00"},
        ],
    )
    assert report["by_month"] == [
        {"month": "2025-01", "reservations": 2, "room_nights": 6, "total_brl": "300.00"},
        {"month": "2025-02", "reservations": 1, "room_nights": 1, "total_brl": "50.00"},
    ]


def test_money_rounds_half_up_only_on_serialization(tmp_path):
    report = run_cli(tmp_path, [{"reservation_id": "R-1", "amount": "10.005"}])
    assert report["summary"]["total_amount_brl"] == "10.01"  # half-even daria 10.00

    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "amount": "0.004"},
            {"reservation_id": "R-2", "amount": "0.004"},
        ],
    )
    # soma exata 0.008 -> 0.01; arredondar por linha antes de somar daria 0.00
    assert report["summary"]["total_amount_brl"] == "0.01"


def test_top_hotels_tie_breaks_by_hotel_id_and_respects_top(tmp_path):
    rows = [
        {"reservation_id": "R-1", "hotel_id": "H02", "hotel_name": "B", "amount": "100.00"},
        {"reservation_id": "R-2", "hotel_id": "H01", "hotel_name": "A", "amount": "100.00"},
        {"reservation_id": "R-3", "hotel_id": "H03", "hotel_name": "C", "amount": "200.00"},
    ]
    report = run_cli(tmp_path, rows, top=5)
    assert [h["hotel_id"] for h in report["top_hotels"]] == ["H03", "H01", "H02"]
    report = run_cli(tmp_path, rows, top=2)
    assert [h["hotel_id"] for h in report["top_hotels"]] == ["H03", "H01"]


def test_no_confirmed_reservations_yields_zeroed_report(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "status": "CANCELLED"},
            {"reservation_id": "R-2", "status": "NO_SHOW"},
        ],
    )
    assert report["summary"]["total_reservations"] == 2
    assert report["summary"]["total_room_nights"] == 0
    assert report["summary"]["total_amount_brl"] == "0.00"
    assert report["summary"]["average_nightly_rate_brl"] == "0.00"
    assert report["by_month"] == []
    assert report["top_hotels"] == []


def test_utf8_bom_is_accepted(tmp_path):
    process = _invoke(tmp_path, _csv_bytes([{}], prefix=b"\xef\xbb\xbf"))
    assert process.returncode == 0, process.stderr


def test_missing_rate_is_input_error_exit_2(tmp_path):
    process = _invoke(tmp_path, _csv_bytes([{"currency": "GBP"}]))
    assert process.returncode == 2
    assert "GBP" in process.stderr


def test_non_utf8_input_is_input_error_exit_2(tmp_path):
    process = _invoke(tmp_path, b"reservation_id,\xff\xfe\n")
    assert process.returncode == 2
