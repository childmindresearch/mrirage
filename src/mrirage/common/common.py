from typing import Any


def rep_tuple(n: int, t: Any) -> tuple:
    """
    Expand or constrain tuple to ``n`` elements by repeating its elements.

    Args:
        n: Output element count.
        t: Input tuple (or scalar object).

    Returns:
        Expanded or constrained tuple.
    """
    if not isinstance(t, tuple):
        return tuple(t for _ in range(n))
    if len(t) == n:
        return t
    return tuple(t[i % len(t)] for i in range(n))
