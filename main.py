import jwt
import passlib.pwd
from typing import Dict
from fastapi import FastAPI, HTTPException
from starlette.responses import RedirectResponse

from models import User
from schemas import RegisterSchema, LoginSchema, PasswordResetSchema, User_Pydantic

app = FastAPI(
    openapi_url="/api/v1/openapi.json",
    redoc_url="/api/v1/docs",
    title="OAuth2 Authorization Microservice",
    description="A production grade OAuth2 authorization microservice that can perform register, login, and password resets",
)

# @app.post("/api/v1/register", response_model=User, status_code=201)
# async def register(data: RegisterSchema):
#     user = await User.filter(email=data.email).first()
#     if user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     user = await User.filter(username=data.username).first()
#     if user:
#         raise HTTPException(status_code=400, detail="Username already registered")
#     hashed_password = passlib.pwd.genhash(data.password)
#     user = await User.create(
#         username=data.username,
#         full_name=data.full_name,
#         email=data.email,
#         phone=data.phone,
#         password=hashed_password,
#     )
#     return user

@app.post("/api/v1/register", response_model=User_Pydantic, status_code=201)
async def register(data: RegisterSchema):
    """
    Register a new user.
    
    Parameters:
    - data (RegisterSchema): Request data.
    
    Returns:
    - User: Registered user.
    """
    user = await User.filter(email=data.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await User.filter(username=data.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    salt = passlib.pwd.genword(length=32)  # Generate a random salt
    hashed_password = passlib.pwd.hash(data.password, salt=salt)  # Hash the password with the salt
    user = await User.create(
        username=data.username,
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        password=hashed_password,
        salt=salt,  # Store the salt in the database
    )
    return await User_Pydantic.from_tortoise_orm(user)

# @app.post("/api/v1/login", response_model=User)
# async def login(data: LoginSchema):
#     user = await User.filter(username=data.username).first()
#     if not user:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     if not passlib.pwd.verify(data.password, user.password):
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     if not user.is_active:
#         raise HTTPException(status_code=400, detail="User is inactive")
#     access_token = jwt.encode({"sub": user.id}, "secret", algorithm="HS256")
#     return {"access_token": access_token, "token_type": "bearer"}
@app.post("/api/v1/login", response_model=Dict[str, str])
async def login(data: LoginSchema):
    """
    Authorize user.
    
    Parameters:
    - data (LoginSchema): Request data.
    
    Returns:
    - Dict[str, str]: Access token and token type.
    """
    user = await User.filter(username=data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not passlib.pwd.verify(data.password, user.password, salt=user.salt): # Verify the password with the salt
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is inactive")
    access_token = jwt.encode({"sub": user.id}, "secret", algorithm="HS256")
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/v1/password/reset", response_model=Dict[str, str])
async def password_reset(data: PasswordResetSchema):
    """
    Reset user password.
    
    Parameters:
    - data (PasswordResetSchema): Request data.

    Returns:
    - Message: Password reset email sent.
    """
    user = await User.filter(email=data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    # Generate a password reset token and send it to the user's email
    reset_token = jwt.encode({"sub": user.id}, "secret", algorithm="HS256")
    await send_reset_email(user.email, reset_token)
    return {"message": "Password reset email sent"}

@app.get("/api/v1/password/reset/{token}")
async def password_reset_confirm(token: str):
    """
    Confirm password reset.

    Parameters:
    - token (str): Password reset token.

    Returns:
    - RedirectResponse: Redirect to password reset page.
    """
    try:
        data = jwt.decode(token, "secret", algorithms=["HS256"])
        user_id = data["sub"]
    except jwt.JWTError:
        raise HTTPException(status_code=404, detail="Invalid token")
    user = await User.filter(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return RedirectResponse(url="/reset_password.html")

# @app.post("/api/v1/password/reset/{token}", response_model=User)
# async def password_reset_complete(token: str, data: RegisterSchema):
#     try:
#         jwt.decode(token, "secret", algorithms=["HS256"])
#     except jwt.JWTError:
#         raise HTTPException(status_code=404, detail="Invalid token")
#     user = await User.filter(email=data.email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="Email not found")
#     hashed_password = passlib.pwd.genhash(data.password)
#     user.password = hashed_password
#     await user.save()
#     return {"message": "Password reset successfully"}
@app.post("/api/v1/password/reset/{token}", response_model=Dict[str, str])
async def password_reset_complete(token: str, data: RegisterSchema):
    """
    Complete password reset.

    Parameters:
    - token (str): Password reset token.
    - data (RegisterSchema): Request data.

    Returns:
    - Message: Password reset successfully.
    """
    try:
        jwt.decode(token, "secret", algorithms=["HS256"])
    except jwt.JWTError:
        raise HTTPException(status_code=404, detail="Invalid token")
    user = await User.filter(email=data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    salt = passlib.pwd.genword(length=32)  # Generate a random salt
    hashed_password = passlib.pwd.hash(data.password, salt=salt)  # Hash the password with the salt
    user.password = hashed_password
    user.salt = salt  # Store the salt in the database
    await user.save()
    return {"message": "Password reset successfully"}

async def send_reset_email(email: str, reset_token: str):
    """
    Send password reset email.

    Parameters:
    - email (str): User email.
    - reset_token (str): Password reset token.

    Returns:
    - None
    """
    # Use aiosmtplib to send the password reset email with the reset token
    pass
