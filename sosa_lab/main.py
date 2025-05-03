import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.templating import Jinja2Templates
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from sosa_lab.routes import router as auth_router, auth_database

secret_key = '9c580e0641762c32eab407257d924c25d5c8dd44a67d9efb4403038ae783c37c'
templates = Jinja2Templates(directory="templates")
app = FastAPI(middleware=[
    Middleware(
        SessionMiddleware,
        secret_key=secret_key,
        session_cookie='webauthn-demo',
        same_site='strict',
    )
])
app.include_router(auth_router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    if 'username' not in request.session:
        return RedirectResponse("/", status_code=302)
    username = request.session['username']
    if username not in auth_database:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse(request=request, name="profile.html", context={"username": username})


def start():
    """Launched with `poetry run start` at root level"""

    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == '__main__':
    start()
