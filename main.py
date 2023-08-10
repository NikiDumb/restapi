from fastapi import FastAPI, status
from pydantic import BaseModel, field_validator, ValidationError
import re

app = FastAPI()


class Employee(BaseModel):
    passport: str
    role: str
    email_adress: str
    experience: int
    removed_date: str

    @field_validator('passport')
    def validate_passport(cls, value):
        if not re.match(r'^\d{4}-\d{6}$', value):
            raise ValueError('Invalid passport format')
        return value

    @field_validator('email_adress')
    def validate_email(cls, value):
        if not re.match(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'):
            raise ValueError('Invalid email format')
        return value


@app.get("/")
def greetigs():
    return {'answer': 'hello, budy'}
