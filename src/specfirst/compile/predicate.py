"""`applies_when`: a predicate over design features (PLAN.md sections 5.2 and 6.2).

Grammar: feature names such as `design.has_exposure`, joined with `and`,
`or`, `not` and parentheses. `not` binds tightest, then `and`, then `or`.
"""

from __future__ import annotations

import re

_TOKEN = re.compile(r"\s*(\(|\)|[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*)")
_WORDS = ("and", "or", "not")


class PredicateError(ValueError):
    """The text is not a predicate."""


def _tokens(text: str) -> list[str]:
    tokens = []
    pos = 0
    while pos < len(text):
        if text[pos:].strip() == "":
            break
        match = _TOKEN.match(text, pos)
        if not match:
            raise PredicateError(f"cannot read '{text[pos:].strip()}'")
        tokens.append(match.group(1))
        pos = match.end()
    if not tokens:
        raise PredicateError("the predicate is empty")
    return tokens


def parse(text: str) -> object:
    """The tree of a predicate: a name, ("not", x), ("and", x, y) or ("or", x, y)."""
    tokens = _tokens(text)
    pos = 0

    def peek() -> str | None:
        return tokens[pos] if pos < len(tokens) else None

    def take() -> str:
        nonlocal pos
        if pos >= len(tokens):
            raise PredicateError("the predicate ends too early")
        pos += 1
        return tokens[pos - 1]

    def atom() -> object:
        token = take()
        if token == "(":
            inner = disjunction()
            if take() != ")":
                raise PredicateError("a parenthesis is not closed")
            return inner
        if token == "not":
            return ("not", atom())
        if token in (")", "and", "or"):
            raise PredicateError(f"'{token}' is out of place")
        return token

    def conjunction() -> object:
        left = atom()
        while peek() == "and":
            take()
            left = ("and", left, atom())
        return left

    def disjunction() -> object:
        left = conjunction()
        while peek() == "or":
            take()
            left = ("or", left, conjunction())
        return left

    tree = disjunction()
    if pos != len(tokens):
        raise PredicateError(f"'{tokens[pos]}' is out of place")
    return tree


def names(tree: object) -> set[str]:
    """The feature names a predicate reads."""
    if isinstance(tree, str):
        return {tree}
    found: set[str] = set()
    for child in tree[1:]:
        found |= names(child)
    return found


def evaluate(tree: object, features: dict[str, bool]) -> bool:
    """The value of a predicate for the features of one design."""
    if isinstance(tree, str):
        if tree not in features:
            raise PredicateError(f"the design does not say whether {tree} holds")
        return bool(features[tree])
    if tree[0] == "not":
        return not evaluate(tree[1], features)
    if tree[0] == "and":
        return evaluate(tree[1], features) and evaluate(tree[2], features)
    return evaluate(tree[1], features) or evaluate(tree[2], features)
