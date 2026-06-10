from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class MobileLoginRequest(BaseModel):
    mobile: str = Field(..., min_length=10, max_length=15, pattern=r"^\+?[0-9]{10,15}$")


class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    mobile: Optional[str] = Field(None, min_length=10, max_length=15)
    password: Optional[str] = Field(None, min_length=6)

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, value):
        if value is not None and not value.replace("+", "").isdigit():
            raise ValueError("Invalid mobile number")
        return value


class OTPRequest(BaseModel):
    identifier: str = Field(..., description="Email or mobile number")
    purpose: str = Field(..., pattern=r"^(login|register|forgot_password)$")


class OTPVerifyRequest(BaseModel):
    identifier: str
    otp_code: str = Field(..., min_length=4, max_length=10)
    purpose: str = Field(..., pattern=r"^(login|register|forgot_password)$")


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=4, max_length=10)
    new_password: str = Field(..., min_length=6)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)
