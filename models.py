import tortoise.fields
from tortoise.models import Model

class User(Model):
    """
    User model.
    
    Parameters:
    - id (int): User ID.
    - username (str): User's username.
    - full_name (str): User's full name.
    - email (str): User's email.
    - phone (str): User's phone number.
    - password (str): User's hashed password.
    - is_active (bool): Indicates whether the user is active.
    - created_at (datetime): Date and time when the user was created.
    - updated_at (datetime): Date and time when the user was last updated.
    """
    username = tortoise.fields.CharField(max_length=50, unique=True)
    full_name = tortoise.fields.CharField(max_length=100)
    email = tortoise.fields.CharField(max_length=100, unique=True)
    phone = tortoise.fields.CharField(max_length=15)
    password = tortoise.fields.CharField(max_length=200)
    salt = tortoise.fields.CharField(max_length=32)  # Store the salt in the database
    is_active = tortoise.fields.BooleanField(default=True)
    created_at = tortoise.fields.DatetimeField(auto_now_add=True)
    updated_at = tortoise.fields.DatetimeField(auto_now=True)
