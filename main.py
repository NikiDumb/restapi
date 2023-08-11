from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from loguru import logger
import re
import uvicorn

# Создание приложения FastAPI
app = FastAPI()

# CORS (на ютубе мужик сказал что он очень нужен для деплоя)
#app.add_middleware(
#    CORSMiddleware,
#    allow_origins=["*"],
#    allow_methods=["GET", "POST", "PUT", "DELETE"],
#    allow_headers=["*"],
#)

# Подключение к базе данных PostgreSQL
DATABASE_URL = "postgresql://employeeapi:restapi@localhost/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
class Base(DeclarativeBase):
    pass

# Модель данных для сотрудника
class Employee(Base):
    __tablename__ = "employees"
    id = Column(String, primary_key=True, index=True)
    role = Column(String)
    email = Column(String)
    experience = Column(Integer)
    deletion_date = Column(String)

# Создание таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Модель данных для запроса создания/обновления сотрудника
class EmployeeCreateUpdate(BaseModel):
    id: str
    role: str
    email: str
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
        if not re.fullmatch('Админ', value) or re.fullmatch('Работник', value):
            raise ValueError('Invalid role. Choose <Админ> or <Работник>')
        return value
    @field_validator('email')
    def validate_email(cls, value):
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

# Логгирование
@app.middleware("http://127.0.0.1:8000")
async def log_requests(request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response
# Получить информацию о сотруднике по идентификатору
@app.get("/employee/{id}", response_model=EmployeeResponse)
async def get_employee(id: str):
    db = SessionLocal()
    employee = db.query(Employee).filter(Employee.id == id).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

# Получить информацию о всех сотрудниках с пагинацией
@app.get("/employee")
async def get_employees(current_page: int = 1, page_size: int = 10):
    db = SessionLocal()
    employees = db.query(Employee).offset((current_page - 1) * page_size).limit(page_size).all()
    if len(employees) == 0:
        raise HTTPException(status_code=404, detail="There is no employees")
    return employees

# Сохранить информацию о сотруднике
@app.post("/employee", response_model=EmployeeResponse)
async def create_employee(employee: EmployeeCreateUpdate):
    db = SessionLocal()
    existing_employee = db.query(Employee).filter(Employee.id == employee.id).first()
    if existing_employee:
        db.delete(existing_employee)
        db.commit()
    new_employee = Employee(
        id=employee.id,
        role=employee.role,
        email=employee.email,
        experience=employee.experience,
        deletion_date=employee.deletion_date
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

# Обновить информацию о сотруднике
@app.put("/employee", response_model=EmployeeResponse)
async def update_employee(employee: EmployeeCreateUpdate):
    db = SessionLocal()
    existing_employee = db.query(Employee).filter(Employee.id == employee.id).first()
    if existing_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    if employee.role:
        existing_employee.role = employee.role
    if employee.email:
        existing_employee.email = employee.email
    if employee.experience:
        existing_employee.experience = employee.experience
    if employee.deletion_date:
        existing_employee.deletion_date = employee.deletion_date
    db.commit()
    db.refresh(existing_employee)
    return existing_employee

# Удалить сотрудника
@app.delete("/employee/{id}")
async def delete_employee(id: str):
    db = SessionLocal()
    existing_employee = db.query(Employee).filter(Employee.id == id).first()
    if existing_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(existing_employee)
    db.commit()
    return {"message": "Employee deleted successfully"}



if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)