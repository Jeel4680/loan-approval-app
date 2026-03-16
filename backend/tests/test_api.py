# test_api.py
# Integration tests for the API endpoints
# These test the full request-response cycle

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# ─────────────────────────────────────────
# HEALTH CHECK TESTS
# ─────────────────────────────────────────

class TestHealthCheck:
    def test_api_is_running(self):
        """Root endpoint should return running status"""
        response = client.get("/")
        assert response.status_code == 200
        assert "status" in response.json()

# ─────────────────────────────────────────
# AUTH ENDPOINT TESTS
# ─────────────────────────────────────────

class TestAuthEndpoints:
    def test_register_new_user(self):
        """Should successfully register a new user"""
        import time
        unique_email = f"testuser_{int(time.time())}@test.com"
        response = client.post("/auth/register", json={
            "full_name": "Test User",
            "email": unique_email,
            "password": "password123"
        })
        assert response.status_code == 201
        assert "user_id" in response.json()

    def test_register_duplicate_email_fails(self):
        """Registering same email twice should fail"""
        import time
        email = f"duplicate_{int(time.time())}@test.com"
        # Register first time
        client.post("/auth/register", json={
            "full_name": "Test User",
            "email": email,
            "password": "password123"
        })
        # Register second time with same email
        response = client.post("/auth/register", json={
            "full_name": "Test User 2",
            "email": email,
            "password": "password456"
        })
        assert response.status_code == 400

    def test_login_valid_credentials(self):
        """Valid credentials should return a JWT token"""
        import time
        email = f"logintest_{int(time.time())}@test.com"
        # Register first
        client.post("/auth/register", json={
            "full_name": "Login Test",
            "email": email,
            "password": "password123"
        })
        # Then login
        response = client.post("/auth/login", json={
            "email": email,
            "password": "password123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    def test_login_wrong_password_fails(self):
        """Wrong password should return 401"""
        import time
        email = f"wrongpass_{int(time.time())}@test.com"
        client.post("/auth/register", json={
            "full_name": "Test",
            "email": email,
            "password": "correctpassword"
        })
        response = client.post("/auth/login", json={
            "email": email,
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    def test_protected_route_without_token_fails(self):
        """Accessing protected route without token should return 403"""
        response = client.get("/auth/me")
        assert response.status_code == 401

# ─────────────────────────────────────────
# LOAN APPLICATION TESTS
# ─────────────────────────────────────────

class TestLoanEndpoints:
    def get_auth_token(self):
        """Helper to register and login, returns token"""
        import time
        email = f"loantest_{int(time.time())}@test.com"
        client.post("/auth/register", json={
            "full_name": "Loan Test User",
            "email": email,
            "password": "password123"
        })
        response = client.post("/auth/login", json={
            "email": email,
            "password": "password123"
        })
        return response.json()["access_token"]

    def test_submit_loan_application(self):
        """Should successfully submit a loan application"""
        token = self.get_auth_token()
        response = client.post(
            "/loans/apply",
            json={
                "loan_amount": 15000,
                "loan_purpose": "Home Renovation",
                "loan_term_months": 24,
                "employment_type": "freelancer",
                "income_records": [
                    {"month_year": "2024-01", "amount": 3200, "source": "Freelance"},
                    {"month_year": "2024-02", "amount": 2800, "source": "Freelance"},
                    {"month_year": "2024-03", "amount": 3500, "source": "Freelance"},
                    {"month_year": "2024-04", "amount": 2900, "source": "Freelance"},
                    {"month_year": "2024-05", "amount": 3100, "source": "Freelance"},
                    {"month_year": "2024-06", "amount": 3000, "source": "Freelance"},
                ]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        assert "application_id" in response.json()

    def test_loan_requires_minimum_3_income_records(self):
        """Should reject application with less than 3 income records"""
        token = self.get_auth_token()
        response = client.post(
            "/loans/apply",
            json={
                "loan_amount": 15000,
                "loan_purpose": "Test",
                "loan_term_months": 24,
                "employment_type": "freelancer",
                "income_records": [
                    {"month_year": "2024-01", "amount": 3000, "source": "Test"},
                    {"month_year": "2024-02", "amount": 3000, "source": "Test"},
                ]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400

    def test_loan_without_token_fails(self):
        """Should reject loan application without auth token"""
        response = client.post(
            "/loans/apply",
            json={
                "loan_amount": 15000,
                "loan_purpose": "Test",
                "loan_term_months": 24,
                "employment_type": "freelancer",
                "income_records": []
            }
        )
        assert response.status_code == 401

    def test_get_my_applications(self):
        """Should return list of user's applications"""
        token = self.get_auth_token()
        response = client.get(
            "/loans/my-applications",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert "applications" in response.json()
