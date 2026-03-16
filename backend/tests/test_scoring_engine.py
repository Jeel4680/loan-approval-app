# test_scoring_engine.py
# Tests for the loan scoring engine — the brain of our app

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.scoring_engine import (
    calculate_income_stats,
    calculate_dti,
    calculate_monthly_payment,
    calculate_total_interest,
    get_interest_rate,
    make_loan_decision
)

# ─────────────────────────────────────────
# INTEREST RATE TESTS
# ─────────────────────────────────────────

class TestInterestRates:
    def test_full_time_gets_lowest_rate(self):
        """Full time employees should get the best interest rate"""
        rate = get_interest_rate("full_time")
        assert rate == 0.07

    def test_gig_worker_gets_higher_rate(self):
        """Gig workers are higher risk so get higher rate"""
        rate = get_interest_rate("gig_worker")
        assert rate == 0.15

    def test_freelancer_rate(self):
        rate = get_interest_rate("freelancer")
        assert rate == 0.13

    def test_unknown_employment_gets_default_rate(self):
        """Unknown employment type should get default (highest) rate"""
        rate = get_interest_rate("unknown_type")
        assert rate == 0.15

    def test_rates_are_between_0_and_1(self):
        """All rates should be valid percentages between 0 and 1"""
        employment_types = ["full_time", "part_time", "freelancer", "gig_worker", "seasonal"]
        for emp_type in employment_types:
            rate = get_interest_rate(emp_type)
            assert 0 < rate < 1, f"Rate for {emp_type} should be between 0 and 1"

# ─────────────────────────────────────────
# MONTHLY PAYMENT TESTS
# ─────────────────────────────────────────

class TestMonthlyPayment:
    def test_basic_payment_calculation(self):
        """Test standard loan payment calculation"""
        # $10,000 at 12% annual for 12 months
        payment = calculate_monthly_payment(10000, 0.12, 12)
        # Expected ~$888.49
        assert 880 < payment < 900

    def test_larger_loan_means_larger_payment(self):
        """Larger loan should result in larger monthly payment"""
        payment_small = calculate_monthly_payment(10000, 0.12, 24)
        payment_large = calculate_monthly_payment(20000, 0.12, 24)
        assert payment_large > payment_small

    def test_longer_term_means_smaller_payment(self):
        """Longer repayment term should mean smaller monthly payment"""
        payment_short = calculate_monthly_payment(10000, 0.12, 12)
        payment_long = calculate_monthly_payment(10000, 0.12, 60)
        assert payment_long < payment_short

    def test_payment_is_positive(self):
        """Monthly payment should always be positive"""
        payment = calculate_monthly_payment(15000, 0.13, 24)
        assert payment > 0

    def test_total_repayment_exceeds_principal(self):
        """Total repayment should always be more than the loan amount (interest)"""
        loan_amount = 15000
        payment = calculate_monthly_payment(loan_amount, 0.13, 24)
        total = payment * 24
        assert total > loan_amount

# ─────────────────────────────────────────
# INCOME STATS TESTS
# ─────────────────────────────────────────

class TestIncomeStats:
    def test_stable_income_gets_high_stability_score(self):
        """Perfectly stable income should score close to 100"""
        stable_income = [3000, 3000, 3000, 3000, 3000, 3000]
        stats = calculate_income_stats(stable_income)
        assert stats["stability_score"] >= 95

    def test_unstable_income_gets_low_stability_score(self):
        """Highly variable income should get a low stability score"""
        unstable_income = [500, 5000, 200, 8000, 100, 6000]
        stats = calculate_income_stats(unstable_income)
        assert stats["stability_score"] < 50

    def test_average_income_calculation(self):
        """Average should be correctly calculated"""
        incomes = [2000, 3000, 4000]
        stats = calculate_income_stats(incomes)
        assert stats["average"] == 3000.0

    def test_minimum_3_months_required(self):
        """Should raise error with less than 3 months"""
        with pytest.raises(ValueError):
            calculate_income_stats([2000, 3000])

    def test_min_max_income_correct(self):
        """Min and max should be correct"""
        incomes = [1000, 5000, 3000, 2000, 4000, 6000]
        stats = calculate_income_stats(incomes)
        assert stats["min_income"] == 1000.0
        assert stats["max_income"] == 6000.0

    def test_stability_score_between_0_and_100(self):
        """Stability score must always be between 0 and 100"""
        various_incomes = [
            [1000, 1000, 1000],
            [100, 9000, 500, 8000, 200],
            [3000, 3100, 2900, 3050, 2950]
        ]
        for incomes in various_incomes:
            stats = calculate_income_stats(incomes)
            assert 0 <= stats["stability_score"] <= 100

# ─────────────────────────────────────────
# DTI TESTS
# ─────────────────────────────────────────

class TestDTI:
    def test_dti_calculation(self):
        """DTI should be monthly payment / avg income * 100"""
        dti = calculate_dti(monthly_payment=500, avg_monthly_income=2000)
        assert dti == 25.0

    def test_zero_income_returns_100_dti(self):
        """Zero income should return 100% DTI (worst case)"""
        dti = calculate_dti(monthly_payment=500, avg_monthly_income=0)
        assert dti == 100.0

    def test_high_payment_high_dti(self):
        """High monthly payment relative to income = high DTI"""
        dti = calculate_dti(monthly_payment=2000, avg_monthly_income=2500)
        assert dti > 50

    def test_low_payment_low_dti(self):
        """Low monthly payment relative to income = low DTI"""
        dti = calculate_dti(monthly_payment=300, avg_monthly_income=6000)
        assert dti < 10

# ─────────────────────────────────────────
# FULL DECISION TESTS
# ─────────────────────────────────────────

class TestLoanDecision:
    def test_stable_income_low_dti_gets_approved(self):
        """Stable income + low loan amount = approved"""
        stable_incomes = [4000, 4100, 3900, 4050, 3950, 4000]
        result = make_loan_decision(
            income_amounts=stable_incomes,
            loan_amount=5000,
            loan_term_months=24,
            employment_type="freelancer"
        )
        assert result["decision"] == "approved"

    def test_unstable_income_high_loan_gets_denied(self):
        """Very unstable income + huge loan = denied"""
        unstable_incomes = [500, 8000, 200, 7000, 300, 6000]
        result = make_loan_decision(
            income_amounts=unstable_incomes,
            loan_amount=80000,
            loan_term_months=12,
            employment_type="gig_worker"
        )
        assert result["decision"] == "denied"

    def test_decision_has_required_fields(self):
        """Decision result must contain all required fields"""
        result = make_loan_decision(
            income_amounts=[3000, 3200, 2800, 3100, 2900, 3000],
            loan_amount=15000,
            loan_term_months=24,
            employment_type="freelancer"
        )
        required_fields = [
            "decision", "stability_score", "average_monthly_income",
            "income_variance", "debt_to_income_ratio", "reasoning",
            "interest_details", "breakdown"
        ]
        for field in required_fields:
            assert field in result, f"Missing field: {field}"

    def test_decision_is_valid_value(self):
        """Decision must be one of three valid values"""
        result = make_loan_decision(
            income_amounts=[3000, 3200, 2800, 3100, 2900, 3000],
            loan_amount=15000,
            loan_term_months=24,
            employment_type="freelancer"
        )
        assert result["decision"] in ["approved", "review", "denied"]

    def test_interest_details_present(self):
        """Interest details should always be in the result"""
        result = make_loan_decision(
            income_amounts=[3000, 3200, 2800, 3100, 2900, 3000],
            loan_amount=15000,
            loan_term_months=24,
            employment_type="freelancer"
        )
        assert "interest_details" in result
        assert "monthly_payment" in result["interest_details"]
        assert "total_interest_paid" in result["interest_details"]
        assert result["interest_details"]["total_interest_paid"] > 0
