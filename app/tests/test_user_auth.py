# tests/test_auth_service.py

import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, MagicMock
from app.services.auth_service import AuthService
from app.db.models import User
from app.core.security import security

# Mock data
class UserData:
    email = "test@example.com"
    full_name = "Test User"
    password = "testpassword"

class OTPData:
    email = "test@example.com"
    otp = "123456"

@pytest.mark.asyncio
async def test_register_user_existing_email(mocker):
    # Arrange
    db_session = AsyncMock()
    mock_user = User(email=UserData.email, full_name="Existing User", password="hashedpassword")
    db_session.execute.return_value.scalars.return_value.first.return_value = mock_user

    # Act and Assert
    with pytest.raises(HTTPException) as excinfo:
        await AuthService.register_user(db_session, UserData)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail == "Email already registered."


@pytest.mark.asyncio
async def test_register_user_success(mocker):
    # Arrange
    db_session = AsyncMock()
    db_session.execute.return_value.scalars.return_value.first.return_value = None
    mocker.patch("app.core.security.security.hash_password", return_value="hashedpassword")
    mocker.patch("app.core.security.security.encrypt", return_value="encryptedfullname")

    # Act
    new_user = await AuthService.register_user(db_session, UserData)

    # Assert
    assert new_user.email == UserData.email
    assert new_user.full_name == "encryptedfullname"
    assert new_user.password == "hashedpassword"
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(new_user)


@pytest.mark.asyncio
async def test_login_user_invalid_credentials(mocker):
    # Arrange
    db_session = AsyncMock()
    db_session.execute.return_value.scalars.return_value.first.return_value = None

    # Act and Assert
    with pytest.raises(HTTPException) as excinfo:
        await AuthService.login_user(db_session, UserData.email, UserData.password)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Invalid credentials."


@pytest.mark.asyncio
async def test_login_user_success(mocker):
    # Arrange
    db_session = AsyncMock()
    mock_user = User(email=UserData.email, password="hashedpassword", otp_code=None)
    db_session.execute.return_value.scalars.return_value.first.return_value = mock_user
    mocker.patch("app.core.security.security.verify_password", return_value=True)
    mocker.patch("app.core.security.security.generate_otp", return_value="123456")

    # Act
    otp_code = await AuthService.login_user(db_session, UserData.email, UserData.password)

    # Assert
    assert otp_code == "123456"
    assert mock_user.otp_code == "123456"
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(mock_user)


@pytest.mark.asyncio
async def test_verify_otp_invalid_otp(mocker):
    # Arrange
    db_session = AsyncMock()
    mock_user = User(email=UserData.email, otp_code="654321")
    db_session.execute.return_value.scalars.return_value.first.return_value = mock_user

    # Act and Assert
    with pytest.raises(HTTPException) as excinfo:
        await AuthService.verify_otp(db_session, OTPData)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Invalid OTP."


@pytest.mark.asyncio
async def test_verify_otp_success(mocker):
    # Arrange
    db_session = AsyncMock()
    mock_user = User(email=UserData.email, otp_code=OTPData.otp)
    db_session.execute.return_value.scalars.return_value.first.return_value = mock_user
    mocker.patch("app.core.security.security.create_access_token", return_value="access_token")

    # Act
    token = await AuthService.verify_otp(db_session, OTPData)

    # Assert
    assert token == "access_token"
    assert mock_user.otp_code is None  # OTP should be cleared after verification
    db_session.commit.assert_called_once()
