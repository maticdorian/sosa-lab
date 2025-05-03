import base64

import webauthn
from fastapi import HTTPException, APIRouter
from starlette.requests import Request
from starlette.responses import Response
from webauthn.helpers.structs import PublicKeyCredentialDescriptor, UserVerificationRequirement

from sosa_lab.schemas import CreateCredentialsRequest, RegisterCredentialsRequest, AuthCredentialsRequest, \
    VerifyCredentialsRequest

auth_database = {}

router = APIRouter(
    prefix="/api/passkeys",
)


@router.post("/options/register", response_class=Response)
async def create_credentials(request: Request, create_creds_request: CreateCredentialsRequest):
    options = webauthn.generate_registration_options(
        rp_id='localhost',
        rp_name='SosaLab',
        user_name=create_creds_request.username,
    )
    request.session['webauthn_register_challenge'] = base64.b64encode(options.challenge).decode()

    return webauthn.options_to_json(options)


@router.post("/register", response_class=Response)
async def register_credentials(request: Request, register_creds_request: RegisterCredentialsRequest):
    expected_challenge = base64.b64decode(request.session['webauthn_register_challenge'].encode())
    registration = webauthn.verify_registration_response(
        credential=register_creds_request.registrationResponse,
        expected_challenge=expected_challenge,
        expected_rp_id='localhost',
        expected_origin='http://localhost:8000',
    )

    auth_database[register_creds_request.username] = {
        'public_key': registration.credential_public_key,
        'sign_count': registration.sign_count,
        'credential_id': registration.credential_id,
    }


@router.post("/options/authenticate", response_class=Response)
async def authenticate_credentials(request: Request, auth_creds_request: AuthCredentialsRequest):
    try:
        user_creds = auth_database[auth_creds_request.username]
    except KeyError:
        raise HTTPException(status_code=404, detail='user not found')

    options = webauthn.generate_authentication_options(
        rp_id='localhost',
        allow_credentials=[
            PublicKeyCredentialDescriptor(id=user_creds['credential_id'])
        ],
        user_verification=UserVerificationRequirement.DISCOURAGED,
    )
    request.session['webauthn_auth_challenge'] = base64.b64encode(options.challenge).decode()

    return webauthn.options_to_json(options)


@router.post('/authenticate')
async def auth_post(request: Request, verify_creds_request: VerifyCredentialsRequest):
    expected_challenge = base64.b64decode(request.session['webauthn_auth_challenge'].encode())
    try:
        user_creds = auth_database[verify_creds_request.username]
    except KeyError:
        raise HTTPException(status_code=404, detail='user not found')

    auth = webauthn.verify_authentication_response(
        credential=verify_creds_request.authenticationResponse,
        expected_challenge=expected_challenge,
        expected_rp_id='localhost',
        expected_origin='http://localhost:8000',
        credential_public_key=user_creds['public_key'],
        credential_current_sign_count=user_creds['sign_count'],
    )
    user_creds['sign_count'] = auth.new_sign_count
    request.session['username'] = verify_creds_request.username
