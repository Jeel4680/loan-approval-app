from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from database import get_db
from models.loan import LoanApplication, IncomeRecord
from models.user import User
from services.dependencies import get_current_user

router = APIRouter(prefix="/loans", tags=["Loan Applications"])

# ─────────────────────────────────────────
# REQUEST SCHEMAS
# ─────────────────────────────────────────

class IncomeRecordInput(BaseModel):
    month_year: str        # Format: YYYY-MM e.g. "2024-01"
    amount: float
    source: Optional[str] = "Not specified"

class LoanApplicationInput(BaseModel):
    loan_amount: float
    loan_purpose: str
    loan_term_months: int
    employment_type: str   # freelancer, gig_worker, seasonal, part_time
    income_records: List[IncomeRecordInput]  # At least 3 months required

# ─────────────────────────────────────────
# RESPONSE SCHEMAS
# ─────────────────────────────────────────

class IncomeRecordResponse(BaseModel):
    id: int
    month_year: str
    amount: float
    source: Optional[str]

    model_config = ConfigDict(from_attributes=True) #
        

class LoanApplicationResponse(BaseModel):
    id: int
    loan_amount: float
    loan_purpose: str
    loan_term_months: int
    employment_type: str
    status: str
    income_records: List[IncomeRecordResponse]

    model_config = ConfigDict(from_attributes=True) #
        

# ─────────────────────────────────────────
# SUBMIT LOAN APPLICATION
# ─────────────────────────────────────────

@router.post("/apply", status_code=201)
def apply_for_loan(
    request: LoanApplicationInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate minimum income records
    if len(request.income_records) < 3:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least 3 months of income records."
        )

    # Validate loan amount
    if request.loan_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Loan amount must be greater than 0."
        )

    # Validate loan term
    if request.loan_term_months < 3 or request.loan_term_months > 360:
        raise HTTPException(
            status_code=400,
            detail="Loan term must be between 3 and 360 months."
        )

    # Create the loan application
    application = LoanApplication(
        user_id=current_user.id,
        loan_amount=request.loan_amount,
        loan_purpose=request.loan_purpose,
        loan_term_months=request.loan_term_months,
        employment_type=request.employment_type,
        status="pending"
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    # Add income records linked to this application
    for record in request.income_records:
        income = IncomeRecord(
            application_id=application.id,
            month_year=record.month_year,
            amount=record.amount,
            source=record.source
        )
        db.add(income)

    db.commit()
    db.refresh(application)

    return {
        "message": "Loan application submitted successfully! ✅",
        "application_id": application.id,
        "status": application.status,
        "income_records_count": len(request.income_records)
    }

# ─────────────────────────────────────────
# GET ALL MY APPLICATIONS
# ─────────────────────────────────────────

@router.get("/my-applications")
def get_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    applications = db.query(LoanApplication).filter(
        LoanApplication.user_id == current_user.id
    ).all()

    if not applications:
        return {"message": "No applications found.", "applications": []}

    result = []
    for app in applications:
        result.append({
            "id": app.id,
            "loan_amount": float(app.loan_amount),
            "loan_purpose": app.loan_purpose,
            "loan_term_months": app.loan_term_months,
            "employment_type": app.employment_type,
            "status": app.status,
            "created_at": str(app.created_at),
            "income_records_count": len(app.income_records)
        })

    return {"applications": result, "total": len(result)}

# ─────────────────────────────────────────
# GET SINGLE APPLICATION WITH FULL DETAILS
# ─────────────────────────────────────────

@router.get("/application/{application_id}")
def get_application_details(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application = db.query(LoanApplication).filter(
        LoanApplication.id == application_id,
        LoanApplication.user_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found."
        )

    income_records = []
    for record in application.income_records:
        income_records.append({
            "month_year": record.month_year,
            "amount": float(record.amount),
            "source": record.source
        })

    # Sort income records by date
    income_records.sort(key=lambda x: x["month_year"])

    return {
        "id": application.id,
        "loan_amount": float(application.loan_amount),
        "loan_purpose": application.loan_purpose,
        "loan_term_months": application.loan_term_months,
        "employment_type": application.employment_type,
        "status": application.status,
        "created_at": str(application.created_at),
        "income_records": income_records,
        "decision": application.decision
    }
