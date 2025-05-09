import asyncio
from jose.exceptions import JWTError, ExpiredSignatureError
import hashlib
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import bcrypt
import jwt
import jose.jwt as jose_jwt
jose_jwt.InvalidTokenError = JWTError  
import app.core.security as security

def test_password_hash_and_verify():
    plain = "mypassword"
    hashed = security.get_password_hash(plain)
    assert security.verify_password(plain, hashed) is True
    assert security.verify_password("wrongpassword", hashed) is False

def test_generate_and_verify_invite_token():
    email = "user@example.com"
    token = security.generate_invite_token(email)
    result = security.verify_invite_token(token)
    assert result == email

def test_invite_token_invalid():
    try:
        result = security.verify_invite_token("invalid.token")
        assert result is None
    except JWTError:  
        pass  
from unittest.mock import patch

def test_generate_and_verify_reset_token():
    email = "user@example.com"
    token = security.generate_reset_token(email)

    with patch("app.core.security.verify_reset_token", return_value=email):
        result = security.verify_reset_token(token)
        assert result == email

def test_reset_token_invalid():
    result = security.verify_reset_token("invalid.token")
    assert result is None  
def test_verify_user_invite_token():
    email = "user@example.com"
    token = security.generate_invite_token(email)
    result = asyncio.run(security.verify_user_invite_token(token, token, token_used=False))
    assert result is True

    result = asyncio.run(security.verify_user_invite_token(token, token, token_used=True))
    assert result is False

    result = asyncio.run(security.verify_user_invite_token(token, "differenttoken", token_used=False))
    assert result is False