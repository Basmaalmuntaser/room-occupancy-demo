"""Tests for the game rules and the room illustration (no API or Streamlit needed)."""
from game_logic import outcome, streak, tally
from ui_assets import room_scene
from ui_text import TXT


def rec(guess, ai, truth):
    return {"sid": "x", "guess": guess, "ai": ai, "truth": truth}


def test_outcomes_are_judged_against_recorded_count():
    assert outcome(2, 1, 2) == "you"
    assert outcome(2, 2, 2) == "both"
    assert outcome(1, 2, 2) == "ai"
    assert outcome(0, 1, 3) == "none"


def test_tally_and_streak():
    hist = [rec(1, 1, 1), rec(2, 0, 2), rec(3, 3, 0), rec(0, 1, 0), rec(2, 2, 2)]
    assert tally(hist) == {"rounds": 5, "you": 4, "ai": 2}
    assert streak(hist) == 2
    assert streak([]) == 0
    assert tally([]) == {"rounds": 0, "you": 0, "ai": 0}


def test_closed_room_never_shows_people():
    closed = room_scene(False)
    assert 'class="pp"' not in closed
    assert "door-open" not in closed


def test_revealed_room_shows_recorded_count():
    for n in range(4):
        assert room_scene(True, n).count('class="pp"') == n


def test_both_languages_have_same_keys():
    assert set(TXT["en"]) == set(TXT["ar"])
