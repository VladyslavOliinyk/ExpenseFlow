"""
Tests for the SQL-based duplicate detection logic.
Uses the pure _is_dup_candidate function — no DB or AI mocks needed.
"""
from datetime import date

from app.routers.claims import _is_dup_candidate


def test_identical_claim_is_duplicate():
    assert _is_dup_candidate(
        100.0, date(2026, 9, 1), "Office supplies for team",
        100.0, date(2026, 9, 1), "Office supplies for team",
    ) is True


def test_slight_amount_diff_within_threshold_is_duplicate():
    # 3% difference — within the 5% threshold
    assert _is_dup_candidate(
        100.0, date(2026, 9, 1), "Printer paper",
        103.0, date(2026, 9, 1), "Printer paper",
    ) is True


def test_amount_diff_above_threshold_not_duplicate():
    # 6% difference — exceeds the 5% threshold
    assert _is_dup_candidate(
        100.0, date(2026, 9, 1), "Printer paper",
        106.0, date(2026, 9, 1), "Printer paper",
    ) is False


def test_date_within_3_days_is_duplicate():
    assert _is_dup_candidate(
        100.0, date(2026, 9, 1), "Conference hotel",
        100.0, date(2026, 9, 4), "Conference hotel",
    ) is True


def test_date_4_days_apart_not_duplicate():
    assert _is_dup_candidate(
        100.0, date(2026, 9, 1), "Conference hotel",
        100.0, date(2026, 9, 5), "Conference hotel",
    ) is False


def test_different_description_not_duplicate():
    assert _is_dup_candidate(
        100.0, date(2026, 9, 1), "Flight to London for client meeting",
        100.0, date(2026, 9, 1), "Annual Figma license renewal",
    ) is False


def test_similar_description_is_duplicate():
    # Typo / minor wording difference — should still match
    assert _is_dup_candidate(
        200.0, date(2026, 9, 2), "Hotel stay for the team conference",
        200.0, date(2026, 9, 2), "Hotel stay for team conference",
    ) is True


def test_all_three_conditions_must_hold():
    # Good description and date match but amount too different
    assert _is_dup_candidate(
        100.0, date(2026, 9, 1), "Office supplies",
        200.0, date(2026, 9, 1), "Office supplies",
    ) is False
