"""Pure game rules for the "Is Anyone There?" demo (no Streamlit here, so it is easy to test).

A finished round is stored once in `history` as {"sid", "guess", "ai", "truth"}.
Player and AI are each judged against the recorded count (truth), never against each other.
"""


def tally(history: list) -> dict:
    """Scores and played rounds, always recomputed from history (so a rerun can never count a round twice)."""
    return {
        "rounds": len(history),
        "you": sum(1 for h in history if h["guess"] == h["truth"]),
        "ai": sum(1 for h in history if h["ai"] == h["truth"]),
    }


def streak(history: list) -> int:
    """Number of correct player guesses in a row, counted back from the latest finished round."""
    n = 0
    for h in reversed(history):
        if h["guess"] != h["truth"]:
            break
        n += 1
    return n


def outcome(guess: int, ai: int, truth: int) -> str:
    """'you' = only the player is right, 'both', 'ai' = only the AI is right, 'none'."""
    you_ok, ai_ok = guess == truth, ai == truth
    if you_ok and ai_ok:
        return "both"
    if you_ok:
        return "you"
    if ai_ok:
        return "ai"
    return "none"
