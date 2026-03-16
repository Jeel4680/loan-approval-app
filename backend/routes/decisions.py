from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.loan import LoanApplication, LoanDecision
from models.user import User
from services.dependencies import get_current_user
from services.scoring_engine import make_loan_decision

router = APIRouter(prefix="/decisions", tags=["Loan Decisions"])

def get_final_decision(rule_decision: str, ml_decision: str) -> str:
    """
    Dual validation — both models must agree to approve.
    If they disagree → review.
    Both deny → denied.
    """
    if rule_decision == ml_decision:
        return rule_decision  # Both agree
    if rule_decision == "denied" or ml_decision == "denied":
        return "review"       # One says deny → review
    return "review"           # Any disagreement → review

@router.post("/evaluate/{application_id}")
def evaluate_loan(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application = db.query(LoanApplication).filter(
        LoanApplication.id == application_id,
        LoanApplication.user_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found.")

    if application.decision:
        return {
            "message": "Application already evaluated.",
            "decision": application.decision.decision,
            "stability_score": float(application.decision.stability_score),
            "reasoning": application.decision.reasoning
        }

    income_amounts = [float(r.amount) for r in application.income_records]
    if len(income_amounts) < 3:
        raise HTTPException(status_code=400, detail="Not enough income records.")

    # Step 1: Rule-based decision
    rule_result = make_loan_decision(
        income_amounts=income_amounts,
        loan_amount=float(application.loan_amount),
        loan_term_months=application.loan_term_months,
        employment_type=application.employment_type
    )

    # Step 2: ML decision
    from ml.predictor import predict_loan, get_employment_encoding
    from services.scoring_engine import calculate_income_stats, calculate_dti, get_interest_rate, calculate_monthly_payment
    import math

    stats = calculate_income_stats(income_amounts)
    annual_rate = get_interest_rate(application.employment_type)
    r = annual_rate / 12
    n = application.loan_term_months
    monthly_payment = float(application.loan_amount) * (r * math.pow(1+r,n)) / (math.pow(1+r,n)-1)
    dti = calculate_dti(monthly_payment, stats["average"])
    avg_annual = stats["average"] * 12
    lti = float(application.loan_amount) / avg_annual if avg_annual > 0 else 10

    features = {
        "stability_score": stats["stability_score"],
        "average_monthly_income": stats["average"],
        "income_variance": stats["variance"],
        "debt_to_income_ratio": dti,
        "min_income": stats["min_income"],
        "max_income": stats["max_income"],
        "loan_amount": float(application.loan_amount),
        "loan_term_months": application.loan_term_months,
        "employment_type_encoded": get_employment_encoding(application.employment_type),
        "months_of_data": stats["months_analyzed"],
        "loan_to_income_ratio": round(lti, 2)
    }

    ml_result = predict_loan(features)
    ml_decision = ml_result.get("ml_decision", rule_result["decision"])

    # Step 3: Final decision — dual validation
    final_decision = get_final_decision(rule_result["decision"], ml_decision)

    # Save to database
    decision = LoanDecision(
        application_id=application.id,
        decision=final_decision,
        stability_score=rule_result["stability_score"],
        average_monthly_income=rule_result["average_monthly_income"],
        income_variance=rule_result["income_variance"],
        debt_to_income_ratio=rule_result["debt_to_income_ratio"],
        reasoning=rule_result["reasoning"]
    )
    db.add(decision)
    application.status = final_decision
    db.commit()

    return {
        "message": "Loan evaluated! ✅",
        "application_id": application_id,
        "final_decision": final_decision.upper(),
        "rule_based_decision": rule_result["decision"].upper(),
        "ml_decision": ml_decision.upper(),
        "decisions_agreed": rule_result["decision"] == ml_decision,
        "stability_score": rule_result["stability_score"],
        "average_monthly_income": rule_result["average_monthly_income"],
        "debt_to_income_ratio": rule_result["debt_to_income_ratio"],
        "interest_details": rule_result["interest_details"],
        "reasoning": rule_result["reasoning"],
        "breakdown": rule_result["breakdown"]
    }

@router.get("/result/{application_id}")
def get_decision(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application = db.query(LoanApplication).filter(
        LoanApplication.id == application_id,
        LoanApplication.user_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found.")

    if not application.decision:
        return {"message": "Not yet evaluated. Call /decisions/evaluate/{id} first."}

    d = application.decision
    income_amounts = [float(r.amount) for r in application.income_records]

    from services.scoring_engine import get_interest_rate, calculate_monthly_payment, calculate_total_interest
    annual_rate = get_interest_rate(application.employment_type)
    monthly_payment = calculate_monthly_payment(float(application.loan_amount), annual_rate, application.loan_term_months)
    total_interest = calculate_total_interest(monthly_payment, application.loan_term_months, float(application.loan_amount))

    return {
        "application_id": application_id,
        "loan_amount": float(application.loan_amount),
        "loan_purpose": application.loan_purpose,
        "employment_type": application.employment_type,
        "decision": d.decision.upper(),
        "stability_score": float(d.stability_score),
        "average_monthly_income": float(d.average_monthly_income),
        "income_variance": float(d.income_variance),
        "debt_to_income_ratio": float(d.debt_to_income_ratio),
        "interest_details": {
            "annual_interest_rate": f"{annual_rate*100:.1f}%",
            "monthly_payment": monthly_payment,
            "total_repayment": round(monthly_payment * application.loan_term_months, 2),
            "total_interest_paid": total_interest
        },
        "reasoning": d.reasoning,
        "income_history": income_amounts,
        "decided_at": str(d.decided_at)
    }

@router.get("/my-results")
def get_all_my_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    applications = db.query(LoanApplication).filter(
        LoanApplication.user_id == current_user.id
    ).all()

    results = []
    for app in applications:
        if app.decision:
            from services.scoring_engine import get_interest_rate, calculate_monthly_payment
            annual_rate = get_interest_rate(app.employment_type)
            monthly_payment = calculate_monthly_payment(float(app.loan_amount), annual_rate, app.loan_term_months)
            results.append({
                "application_id": app.id,
                "loan_amount": float(app.loan_amount),
                "loan_purpose": app.loan_purpose,
                "decision": app.decision.decision.upper(),
                "stability_score": float(app.decision.stability_score),
                "debt_to_income_ratio": float(app.decision.debt_to_income_ratio),
                "annual_interest_rate": f"{annual_rate*100:.1f}%",
                "monthly_payment": monthly_payment,
                "decided_at": str(app.decision.decided_at)
            })

    return {"results": results, "total": len(results)}

@router.post("/ml-evaluate/{application_id}")
def ml_evaluate_loan(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from ml.predictor import predict_loan, get_employment_encoding
    from services.scoring_engine import calculate_income_stats, calculate_dti, get_interest_rate, calculate_monthly_payment
    import math

    application = db.query(LoanApplication).filter(
        LoanApplication.id == application_id,
        LoanApplication.user_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found.")

    income_amounts = [float(r.amount) for r in application.income_records]
    if len(income_amounts) < 3:
        raise HTTPException(status_code=400, detail="Not enough income records.")

    stats = calculate_income_stats(income_amounts)
    annual_rate = get_interest_rate(application.employment_type)
    r = annual_rate / 12
    n = application.loan_term_months
    monthly_payment = float(application.loan_amount) * (r * math.pow(1+r,n)) / (math.pow(1+r,n)-1)
    dti = calculate_dti(monthly_payment, stats["average"])
    avg_annual = stats["average"] * 12
    lti = float(application.loan_amount) / avg_annual if avg_annual > 0 else 10

    features = {
        "stability_score": stats["stability_score"],
        "average_monthly_income": stats["average"],
        "income_variance": stats["variance"],
        "debt_to_income_ratio": dti,
        "min_income": stats["min_income"],
        "max_income": stats["max_income"],
        "loan_amount": float(application.loan_amount),
        "loan_term_months": application.loan_term_months,
        "employment_type_encoded": get_employment_encoding(application.employment_type),
        "months_of_data": stats["months_analyzed"],
        "loan_to_income_ratio": round(lti, 2)
    }

    ml_result = predict_loan(features)
    rule_decision = "approved" if stats["stability_score"] >= 60 and dti <= 40 else \
                   "review" if stats["stability_score"] >= 40 and dti <= 55 else "denied"
    final = get_final_decision(rule_decision, ml_result.get("ml_decision", "review"))

    return {
        "application_id": application_id,
        "comparison": {
            "rule_based_decision": rule_decision.upper(),
            "ml_decision": ml_result.get("ml_decision", "N/A").upper(),
            "final_decision": final.upper(),
            "decisions_agree": rule_decision == ml_result.get("ml_decision")
        },
        "ml_details": {
            "model_type": ml_result.get("model_type"),
            "confidence_in_decision": f"{ml_result.get('confidence_in_decision')}%",
            "confidence_breakdown": ml_result.get("confidence")
        },
        "input_features": {
            "stability_score": stats["stability_score"],
            "average_monthly_income": stats["average"],
            "debt_to_income_ratio": dti,
            "loan_to_income_ratio": round(lti, 2),
            "employment_type": application.employment_type
        }
    }
