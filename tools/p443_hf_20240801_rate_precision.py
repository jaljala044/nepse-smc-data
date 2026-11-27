"""Diagnose the 2024-08-01 HF amount/rate mismatch pattern; never rewrite rows."""
import argparse
import csv
import json
from collections import Counter
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


def quantile(values, fraction):
    ordered = sorted(values)
    index = int((len(ordered) - 1) * fraction)
    return ordered[index]


def analyze_rows(rows):
    if not rows:
        raise ValueError("no invalid rows supplied")
    symbols, contracts, buyers, sellers = set(), set(), set(), set()
    abs_deviations = []
    tie_count = 0
    rounded_matches = 0
    integer_rate_rows = 0
    mismatches = []
    error_counts = Counter()
    dates = set()

    for row in rows:
        error_counts[row["error"]] += 1
        dates.add(row["date"])
        symbol = row["symbol"].strip().upper()
        contract = row["contract"].strip()
        buyer = row["buyer"].strip()
        seller = row["seller"].strip()
        try:
            quantity = Decimal(row["quantity"])
            rate = Decimal(row["rate"])
            amount = Decimal(row["amount"])
        except (InvalidOperation, KeyError, TypeError):
            raise ValueError("non-numeric source field in invalid-row evidence")
        if (
            not quantity.is_finite()
            or not rate.is_finite()
            or not amount.is_finite()
            or quantity <= 0
            or quantity != quantity.to_integral_value()
            or rate <= 0
            or amount <= 0
        ):
            raise ValueError("invalid quantity/rate/amount in diagnostic input")

        implied_rate = amount / quantity
        deviation = implied_rate - rate
        abs_deviations.append(abs(deviation))
        if rate == rate.to_integral_value():
            integer_rate_rows += 1
        if abs(deviation) == Decimal("0.5"):
            tie_count += 1
        rounded_rate = implied_rate.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        if rounded_rate == rate:
            rounded_matches += 1
        else:
            mismatches.append({
                "contract": contract,
                "symbol": symbol,
                "buyer": buyer,
                "seller": seller,
                "quantity": str(quantity),
                "stored_rate": str(rate),
                "amount": str(amount),
                "implied_rate": str(implied_rate),
                "difference_implied_minus_stored": str(deviation),
                "nearest_integer_half_up": str(rounded_rate),
            })
        symbols.add(symbol)
        contracts.add(contract)
        buyers.add(buyer)
        sellers.add(seller)

    if dates != {"2024-08-01"}:
        raise ValueError("diagnostic input must contain only 2024-08-01 rows")
    if error_counts != Counter({"amount_arithmetic_mismatch": len(rows)}):
        raise ValueError("diagnostic input must contain only amount arithmetic failures")
    if len(rows) != 72500:
        raise ValueError(f"unexpected 2024-08-01 invalid-row count: {len(rows)}")
    if integer_rate_rows != len(rows):
        raise ValueError("stored rate values are not all whole-rupee values")
    if rounded_matches != 72496 or len(mismatches) != 4:
        raise ValueError("whole-rupee rate-rounding pattern changed; manual review required")
    if any(value > Decimal("0.5") for value in abs_deviations):
        raise ValueError("implied unit rate exceeds the half-rupee diagnostic envelope")

    return {
        "date": "2024-08-01",
        "input_rows": len(rows),
        "strict_amount_arithmetic_failures": len(rows),
        "symbols": len(symbols),
        "unique_raw_contract_number_values": len(contracts),
        "buyer_broker_ids": len(buyers),
        "seller_broker_ids": len(sellers),
        "stored_rate_whole_rupee_rows": integer_rate_rows,
        "implied_rate_within_half_rupee_rows": len(rows),
        "implied_rate_abs_deviation_quantiles": {
            "min": str(min(abs_deviations)),
            "p50": str(quantile(abs_deviations, 0.50)),
            "p90": str(quantile(abs_deviations, 0.90)),
            "p99": str(quantile(abs_deviations, 0.99)),
            "max": str(max(abs_deviations)),
        },
        "implied_rate_rounds_half_up_to_stored_rate": rounded_matches,
        "exact_half_rupee_tie_rows": tie_count,
        "half_up_rounding_exception_rows": mismatches,
        "diagnostic_hypothesis": "The source rate field may have been rounded to whole rupees while amount retains a more precise unit price.",
        "diagnostic_status": "SYSTEMATIC_RATE_PRECISION_LOSS_PATTERN_REVIEW_ONLY",
        "source_authority": "UNKNOWN",
        "independent_confirmation": "NOT_AVAILABLE_IN_THIS_AUDIT",
        "amount_or_rate_reconstruction_authorized": False,
        "rows_changed": 0,
        "rows_deduplicated": 0,
        "rows_promoted": 0,
        "promotion_allowed": False,
        "limitations": [
            "This is a numerical pattern diagnostic, not proof of the original exchange rate or transaction amount.",
            "Do not replace stored rate with amount/quantity or use the implied rate in canonical OHLCV without independent evidence.",
            "The four half-rupee tie exceptions need row-level review; rounding convention is not established.",
            "Repeated contract numbers remain a separate session/source identity issue.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with open(args.input, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    report = analyze_rows(rows)
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
