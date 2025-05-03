from pydantic import BaseModel, Field


class CreateCredentialsRequest(BaseModel):
    username: str = Field()


class RegisterCredentialsRequest(BaseModel):
    username: str = Field()
    registrationResponse: dict = Field()


class AuthCredentialsRequest(BaseModel):
    username: str = Field()


class VerifyCredentialsRequest(BaseModel):
    username: str = Field()
    authenticationResponse: dict = Field()