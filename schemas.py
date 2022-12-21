from pydantic import BaseModel
from tortoise import Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator

from models import User


Tortoise.init_models(["models"], "models")
Tortoise._init_timezone(use_tz=True, timezone='Africa/Nairobi')

User_Pydantic = pydantic_model_creator(User, name="User")

class RegisterSchema(BaseModel):
    """
     Register request schema.
    
    Parameters:
    - username (str): User's username.
    - full_name (str): User's full name.
    - email (str): User's email.
    - phone (str): User's phone number.
    - password (str): User's hashed password.
    """
    username: str
    full_name: str
    email: str
    phone: str
    password: str

class LoginSchema(BaseModel):
    """
    Login request schema.
    
    Parameters:
    - username (str): User's username.
    - password (str): User's hashed password.
    """
    username: str
    password: str

class PasswordResetSchema(BaseModel):
    """
    PasswordReset request schema.
    
    Parameters:
    - email (str): User's email.
    """
    email: str
