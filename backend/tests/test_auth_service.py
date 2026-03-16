# test_auth_service.py
# Tests for authentication — password hashing and JWT tokens

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)

# ─────────────────────────────────────────
# PASSWORD TESTS
# ─────────────────────────────────────────

class TestPasswordHashing:
    def test_password_gets_hashed(self):
        """Password should not be stored as plain text"""
        password = "mypassword123"
        hashed = hash_password(password)
        assert hashed != password

    def test_correct_password_verifies(self):
        """Correct password should verify successfully"""
        password = "mypassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) == True

    def test_wrong_password_fails(self):
        """Wrong password should not verify"""
        hashed = hash_password("correctpassword")
        assert verify_password("wrongpassword", hashed) == False

    def test_empty_password_hashes(self):
        """Empty password should still hash without error"""
        hashed = hash_password("")
        assert hashed is not None
        assert len(hashed) > 0

    def test_same_password_different_hashes(self):
        """Same password hashed twice should produce different hashes (bcrypt salt)"""
        password = "mypassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2

    def test_long_password_handled(self):
        """Long passwords should be handled without error (bcrypt 72 char limit)"""
        long_password = "a" * 100
        hashed = hash_password(long_password)
        assert verify_password(long_password, hashed) == True

# ─────────────────────────────────────────
# JWT TOKEN TESTS
# ─────────────────────────────────────────

class TestJWTTokens:
    def test_token_is_created(self):
        """Token should be created successfully"""
        token = create_access_token({"sub": "1", "email": "test@test.com"})
        assert token is not None
        assert len(token) > 0

    def test_valid_token_verifies(self):
        """Valid token should verify and return payload"""
        payload = {"sub": "1", "email": "test@test.com"}
        token = create_access_token(payload)
        decoded = verify_token(token)
        assert decoded is not None
        assert decoded["sub"] == "1"
        assert decoded["email"] == "test@test.com"

    def test_invalid_token_returns_none(self):
        """Invalid/tampered token should return None"""
        result = verify_token("this.is.not.a.valid.token")
        assert result is None

    def test_empty_token_returns_none(self):
        """Empty token should return None"""
        result = verify_token("")
        assert result is None

    def test_token_contains_user_id(self):
        """Token payload should contain user ID"""
        token = create_access_token({"sub": "42", "email": "user@test.com"})
        decoded = verify_token(token)
        assert decoded["sub"] == "42"
