from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from database import engine, Base
from models.user import User
from models.loan import LoanApplication, IncomeRecord, LoanDecision
from routes.auth import router as auth_router
from routes.loans import router as loans_router
from routes.decisions import router as decisions_router
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LoanIQ API",
    description="AI-powered loan approval for unstable income earners",
    version="2.0.0",
    swagger_ui_parameters={"persistAuthorization": True}
)

security = HTTPBearer()

# Allow all origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(loans_router)
app.include_router(decisions_router)

@app.get("/")
def health_check():
    return {
        "status": "LoanIQ API is running ✅",
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/db-test")
def test_database():
    try:
        with engine.connect() as connection:
            return {"database": "Connected ✅"}
    except Exception as e:
        return {"database": "Connection failed ❌", "error": str(e)}
