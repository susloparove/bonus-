from fastapi import FastAPI
from server.transactions import add_bonus, deduct_bonus
from server.customers import add_customer, get_customer, list_customers

# Инициализация FastAPI
app = FastAPI()

# Маршруты для клиентов
@app.post("/customers/add")
def add_customer_route(phone: str, name: str, birth_date: str, role: str = "client"):
    return add_customer(phone, name, birth_date, role)

@app.get("/customers/{phone}")
def get_customer_route(phone: str):
    return get_customer(phone)

@app.get("/customers")
def list_customers_route():
    return list_customers()

# Маршруты для транзакций
@app.post("/transactions/add-bonus")
def add_bonus_route(phone: str, amount: float, operator: str):
    return add_bonus(phone, amount, operator)

@app.post("/transactions/deduct-bonus")
def deduct_bonus_route(phone: str, amount: float, operator: str):
    return deduct_bonus(phone, amount, operator)