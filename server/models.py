from pydantic import BaseModel

class AddCustomerRequest(BaseModel):
    phone: str
    name: str
    birth_date: str

class BonusTransactionRequest(BaseModel):
    phone: str
    amount: float