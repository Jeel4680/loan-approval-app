import statistics
from typing import List
import math

# ─────────────────────────────────────────
# INTEREST RATES BY EMPLOYMENT TYPE
# These reflect real Canadian lending rates
# ─────────────────────────────────────────
INTEREST_RATES = {
    "full_time":   0.07,   # 7%  - most stable
    "part_time":   0.10,   # 10% - moderate risk
    "freelancer":  0.13,   # 13% - higher risk
    "gig_worker":  0.15,   # 15% - higher risk
    "seasonal":    0.14,   # 14% - higher risk
    "other":       0.15    # 15% - default
}

def get_interest_rate(employment_type: str) -> float:
    """Return annual interest rate based on employment type"""
    return INTEREST_RATES.get(employment_type.lower(), 0.15)

def calculate_monthly_payment(loan_amount: float, annual_rate: float, term_months: int) -> float:
    """
    Calculate monthly payment using amortization formula.
    M = P * [r(1+r)^n] / [(1+r)^n - 1]
    """
    if annual_rate == 0:
        return loan_amount / term_months

    r = annual_rate / 12  # monthly rate
    n = term_months

    payment = loan_amount * (r * math.pow(1 + r, n)) / (math.pow(1 + r, n) - 1)
    return round(payment, 2)

def calculate_total_interest(monthly_payment: float, term_months: int, loan_amount: float) -> float:
    """Calculate total interest paid over loan lifetime"""
    total_paid = monthly_payment * term_months
    return round(total_paid - loan_amount, 2)

def calculate_income_stats(income_amounts: List[float]) -> dict:
    """Calculate all statistics from monthly income amounts"""
    if not income_amounts or len(income_amounts) < 3:
        raise ValueError("At least 3 months of income data required")

    n = len(income_amounts)
    avg = sum(income_amounts) / n

    if avg == 0:
        return {
            "average": 0, "variance": 0, "std_deviation": 0,
            "stability_score": 0, "min_income": 0, "max_income": 0,
            "months_analyzed": n
        }

    std_dev = statistics.stdev(income_amounts) if n > 1 else 0
    cv = (std_dev / avg) * 100
    stability_score = max(0, min(100, 100 - cv))

    return {
        "average": round(avg, 2),
        "variance": round(std_dev ** 2, 2),
        "std_deviation": round(std_dev, 2),
        "stability_score": round(stability_score, 2),
        "min_income": round(min(income_amounts), 2),
        "max_income": round(max(income_amounts), 2),
        "months_analyzed": n
    }

def calculate_dti(monthly_payment: float, avg_monthly_income: float) -> float:
    """
    Calculate Debt-to-Income ratio using REAL monthly payment (with interest)
    DTI = (monthly payment / average monthly income) * 100
    """
    if avg_monthly_income == 0:
        return 100.0
    dti = (monthly_payment / avg_monthly_income) * 100
    return round(dti, 2)

def generate_reasoning(
    stability_score: float,
    dti: float,
    avg_income: float,
    months_analyzed: int,
    employment_type: str,
    decision: str,
    monthly_payment: float,
    annual_rate: float,
    total_interest: float
) -> str:
    """Generate plain English explanation of the loan decision"""
    reasons = []

    # Stability reasoning
    if stability_score >= 70:
        reasons.append(f"Income stability score: {stability_score}/100 (Strong ✅)")
    elif stability_score >= 50:
        reasons.append(f"Income stability score: {stability_score}/100 (Moderate ⚠️)")
    else:
        reasons.append(f"Income stability score: {stability_score}/100 (High variability ❌)")

    # Interest rate reasoning
    reasons.append(f"Interest rate applied: {annual_rate*100:.1f}% annually (based on {employment_type} employment)")

    # Payment reasoning
    reasons.append(f"Monthly payment: ${monthly_payment:,.2f} (includes principal + interest)")
    reasons.append(f"Total interest over loan lifetime: ${total_interest:,.2f}")

    # DTI reasoning
    if dti <= 30:
        reasons.append(f"Debt-to-income ratio: {dti}% (Excellent ✅)")
    elif dti <= 45:
        reasons.append(f"Debt-to-income ratio: {dti}% (Acceptable ⚠️)")
    else:
        reasons.append(f"Debt-to-income ratio: {dti}% (Too high ❌ - recommended under 40%)")

    # Average income
    reasons.append(f"Average monthly income: ${avg_income:,.2f} over {months_analyzed} months")

    # Final decision
    if decision == "approved":
        reasons.append("✅ APPROVED: Your income profile meets our lending criteria.")
    elif decision == "review":
        reasons.append("⚠️ MANUAL REVIEW: Your application needs further assessment.")
    else:
        reasons.append("❌ DENIED: Your current income profile does not meet our minimum criteria.")

    return " | ".join(reasons)

def make_loan_decision(
    income_amounts: List[float],
    loan_amount: float,
    loan_term_months: int,
    employment_type: str
) -> dict:
    """
    Main function — full loan analysis with real interest calculation
    """
    # Step 1: Calculate income statistics
    stats = calculate_income_stats(income_amounts)

    # Step 2: Get interest rate for employment type
    annual_rate = get_interest_rate(employment_type)

    # Step 3: Calculate real monthly payment WITH interest
    monthly_payment = calculate_monthly_payment(loan_amount, annual_rate, loan_term_months)

    # Step 4: Calculate total interest paid
    total_interest = calculate_total_interest(monthly_payment, loan_term_months, loan_amount)

    # Step 5: Calculate DTI using real payment
    dti = calculate_dti(monthly_payment, stats["average"])

    # Step 6: Make decision
    stability = stats["stability_score"]
    if stability >= 60 and dti <= 40:
        decision = "approved"
    elif stability >= 40 and dti <= 55:
        decision = "review"
    else:
        decision = "denied"

    # Step 7: Generate reasoning
    reasoning = generate_reasoning(
        stability_score=stability,
        dti=dti,
        avg_income=stats["average"],
        months_analyzed=stats["months_analyzed"],
        employment_type=employment_type,
        decision=decision,
        monthly_payment=monthly_payment,
        annual_rate=annual_rate,
        total_interest=total_interest
    )

    return {
        "decision": decision,
        "stability_score": stability,
        "average_monthly_income": stats["average"],
        "income_variance": stats["variance"],
        "debt_to_income_ratio": dti,
        "reasoning": reasoning,
        "interest_details": {
            "annual_interest_rate": f"{annual_rate*100:.1f}%",
            "monthly_payment": monthly_payment,
            "total_repayment": round(monthly_payment * loan_term_months, 2),
            "total_interest_paid": total_interest
        },
        "breakdown": {
            "min_income": stats["min_income"],
            "max_income": stats["max_income"],
            "std_deviation": stats["std_deviation"],
            "months_analyzed": stats["months_analyzed"]
        }
    }
