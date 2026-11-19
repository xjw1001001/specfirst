"""The run record and its cost (PLAN.md section 9.2, cost; docs/decisions/ADR-010.md,
decisions 7 and 8).

`run.json` of a run says what ran on what, what it cost and whether that was
within its budget. Cost is read from the `result` event of the transcript:
tokens by kind and by model, turns, the time the API took; the harness
measures the wall time. Dollars are computed from the tokens with PRICES,
beside the CLI's own `total_cost_usd`. On the owner's subscription no money
is charged per token: the figure is what the run would cost on the API.

A record is a log of a run and may hold its wall time (rule R4 allows clocks
in logs). The files the scorer reads hold none.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

RECORD = 1  # the version of the run record

# US dollars per million tokens, Claude API, as the claude-api reference of
# 2026-11-03 gives them: input, output, cache write 5 minutes, cache write 1 hour,
# cache read. Cache writes are 1.25 and 2 times the input price, a cache read a tenth.
PRICES = {
    "claude-opus-5-5": (4.00, 20.00, 5.00, 8.00, 0.20),
    "claude-sonnet-5-5": (2.00, 10.00, 2.50, 4.00, 0.10),
    "claude-haiku-5-5": (0.10, 0.50, 0.125, 0.20, 0.01),
    "claude-haiku-4-5": (1.00, 5.00, 1.25, 2.00, 0.10),
}
MODEL = "claude-opus-5-5"


@dataclass(frozen=True)
class Budget:
    turns: int
    seconds: int
    usd: float


# ADR-010, decision 8.
BUDGETS = {
    "R": Budget(turns=100, seconds=45 * 60, usd=10.0),
    "S": Budget(turns=0, seconds=10 * 60, usd=0.0),
    "C": Budget(turns=0, seconds=10 * 60, usd=0.0),
    "probe": Budget(turns=10, seconds=10 * 60, usd=1.0),
}


def price(model: str) -> tuple[float, ...] | None:
    """The prices of a model; an ID with a date suffix takes the ID it starts with."""
    for known in sorted(PRICES, key=len, reverse=True):
        if model == known or model.startswith(known + "-"):
            return PRICES[known]
    return None


def _number(usage: dict, *names: str) -> int:
    for name in names:
        value = usage.get(name)
        if isinstance(value, (int, float)):
            return int(value)
    return 0


def tokens_by_model(result: dict, asked: str = MODEL) -> dict[str, dict[str, int]]:
    """Tokens by model and kind from a `result` event. A CLI that names no model in
    `modelUsage` gives its `usage` to the model asked for."""
    found: dict[str, dict[str, int]] = {}
    for model, usage in sorted((result.get("modelUsage") or {}).items()):
        if isinstance(usage, dict):
            found[model] = {
                "input": _number(usage, "inputTokens", "input_tokens"),
                "output": _number(usage, "outputTokens", "output_tokens"),
                "cache_write": _number(usage, "cacheCreationInputTokens",
                                       "cache_creation_input_tokens"),
                "cache_read": _number(usage, "cacheReadInputTokens", "cache_read_input_tokens"),
            }
    usage = result.get("usage") or {}
    total = {"input": _number(usage, "input_tokens"), "output": _number(usage, "output_tokens"),
             "cache_write": _number(usage, "cache_creation_input_tokens"),
             "cache_read": _number(usage, "cache_read_input_tokens")}
    if not found and any(total.values()):
        found[asked] = total
    return found


def dollars(result: dict, asked: str = MODEL) -> tuple[float, list[str]]:
    """What the tokens of a run cost on the API, and the models without a price. Cache
    writes take the one-hour price when the run wrote any one-hour cache."""
    usage = result.get("usage") or {}
    hour = _number(usage.get("cache_creation") or {}, "ephemeral_1h_input_tokens") > 0
    total, unknown = 0.0, []
    for model, counts in tokens_by_model(result, asked).items():
        prices = price(model)
        if prices is None:
            if any(counts.values()):
                unknown.append(model)
            continue
        inp, out, write5, write1, read = prices
        total += (counts["input"] * inp + counts["output"] * out
                  + counts["cache_write"] * (write1 if hour else write5)
                  + counts["cache_read"] * read) / 1_000_000
    return round(total, 6), unknown


def cost(result: dict | None, wall_seconds: float, asked: str = MODEL) -> dict:
    """The cost dimension of section 9.2 for a run, from its `result` event."""
    result = result or {}
    by_model = tokens_by_model(result, asked)
    usd, unknown = dollars(result, asked)
    totals = {kind: sum(counts[kind] for counts in by_model.values())
              for kind in ("input", "output", "cache_write", "cache_read")}
    return {
        "tokens": totals,
        "tokens_by_model": by_model,
        "turns": _number(result, "num_turns"),
        "wall_seconds": round(wall_seconds, 1),
        "api_seconds": round(_number(result, "duration_api_ms") / 1000, 1),
        "usd": usd,
        "usd_cli": result.get("total_cost_usd"),
        "unpriced_models": unknown,
    }


def budget_dict(budget: Budget) -> dict:
    return asdict(budget)


def over_budget(record: dict) -> list[str]:
    """Why a run record is not a run that ended within its budget."""
    found = []
    budget = record.get("budget") or {}
    spent = record.get("cost") or {}
    end = record.get("end") or {}
    if not end.get("result"):
        found.append("the reader did not end with a result event")
    if end.get("is_error"):
        found.append(f"the reader ended with an error: {end.get('message')}")
    if end.get("stopped"):
        found.append("the harness stopped the reader at its time limit")
    if spent.get("unpriced_models"):
        found.append(f"no price for {', '.join(spent['unpriced_models'])}")
    for name, limit, have in (("turns", budget.get("turns"), spent.get("turns")),
                              ("seconds", budget.get("seconds"), spent.get("wall_seconds")),
                              ("usd", budget.get("usd"), spent.get("usd"))):
        if not isinstance(limit, (int, float)) or not isinstance(have, (int, float)):
            found.append(f"{name}: no limit or no figure in the record")
        elif have > limit:
            found.append(f"{name}: {have} is over the budget of {limit}")
    return found
