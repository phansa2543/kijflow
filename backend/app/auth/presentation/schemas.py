from pydantic import BaseModel

class RegistrationRequest(BaseModel):
    email: str
    password: str

class RegistrationResponse(BaseModel):
    message: str

class RegistrationErrorDetail(BaseModel):
    code: str
    message: str

class RegistrationErrorResponse(BaseModel):
    error: RegistrationErrorDetail

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    message: str