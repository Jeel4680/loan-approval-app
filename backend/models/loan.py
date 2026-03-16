from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    loan_amount = Column(Numeric(12, 2), nullable=False)
    loan_purpose = Column(String(100), nullable=False)
    loan_term_months = Column(Integer, nullable=False)
    employment_type = Column(String(50), nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=func.now())

    # Relationships — lets us access income_records and decision from application
    income_records = relationship("IncomeRecord", back_populates="application", cascade="all, delete")
    decision = relationship("LoanDecision", back_populates="application", uselist=False, cascade="all, delete")


class IncomeRecord(Base):
    __tablename__ = "income_records"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False)
    month_year = Column(String(7), nullable=False)  # Format: YYYY-MM
    amount = Column(Numeric(12, 2), nullable=False)
    source = Column(String(100))

    application = relationship("LoanApplication", back_populates="income_records")


class LoanDecision(Base):
    __tablename__ = "loan_decisions"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False)
    decision = Column(String(20), nullable=False)
    stability_score = Column(Numeric(5, 2))
    average_monthly_income = Column(Numeric(12, 2))
    income_variance = Column(Numeric(12, 2))
    debt_to_income_ratio = Column(Numeric(5, 2))
    reasoning = Column(String)
    decided_at = Column(DateTime, default=func.now())

    application = relationship("LoanApplication", back_populates="decision")
