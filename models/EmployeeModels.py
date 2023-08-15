from pydantic import BaseModel, field_validator
from typing import Optional
from sqlalchemy import Column, Integer, String, Date, Boolean, MetaData
from sqlalchemy.orm import DeclarativeBase


metadata = MetaData()
# Базовая модель
class Base(DeclarativeBase):
    pass

# Модель данных для сотрудника
class Employee(Base):
    __tablename__ = "employees"
    metadata
    id = Column(String, primary_key=True, index=True)
    role = Column(String)
    email = Column(String)
    experience = Column(Integer)
    deletion_date = Column(String)
    is_active = Column(Boolean, default=True)

# Модель данных для запроса создания/обновления сотрудника
class EmployeeCreateUpdate(BaseModel):
    id: str
    role: Optional[str] = None
    email: Optional[str] = None
    experience: int
    deletion_date: str
# Валидация данных
    @field_validator('id')
    def validate_passport_id(cls, value):
        if not re.match(r'^\d{4}-\d{6}$', value):
            raise ValueError('Invalid passport ID format')
        return value
    @field_validator('role')
    def validate_role(cls, value):
        if not value:
            return value
        if not re.fullmatch('Админ', value) or re.fullmatch('Работник', value):
            raise ValueError('Invalid role. Choose <Админ> or <Работник>')
        return value
    @field_validator('email')
    def validate_email(cls, value):
        if not value:
            return value
        if not re.match(r'[\w.-]+@[\w-]+\.[\w.]+', value):
            raise ValueError('Invalid EMAIL format')
        return value



# Модель данных для ответа о сотруднике
class EmployeeResponse(BaseModel):
    id: str
    role: str
    email: str
    experience: int
    deletion_date: str