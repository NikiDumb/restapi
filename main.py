from models.EmployeeModels import Employee, EmployeeResponse, EmployeeCreateUpdate
from database.db import get_async_session
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker
from loguru import logger
from typing import Optional
import re
import uvicorn

# Создание приложения FastAPI
app = FastAPI()



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
    valid_id = EmployeeCreateUpdate.validate_passport_id(id) #отдает 500 а не 422
    db = await get_async_session()
    employee = db.query(Employee).filter(Employee.id == valid_id and Employee.is_active == True).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

# Получить информацию о всех сотрудниках с пагинацией
@app.get("/employee", response_model=list[EmployeeResponse])
async def get_employees(current_page: int = 1, page_size: int = 10):
    db = await get_async_session()
    employees = db.query(Employee).filter(Employee.is_active == True).offset((current_page - 1) * page_size).limit(page_size).all()
    if len(employees) == 0:
        raise HTTPException(status_code=404, detail="There is no employees")
    return employees

# Сохранить информацию о сотруднике
@app.post("/employee", response_model=EmployeeResponse)
async def create_employee(employee: EmployeeCreateUpdate):
    db = await get_async_session()
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
@app.patch("/employee", response_model=EmployeeResponse)
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
    existing_employee.is_active = False
    db.commit()
    return {"message": "Employee deleted successfully"}



if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)