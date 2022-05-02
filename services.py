from fastapi import APIRouter
from fastapi import HTTPException, Header
from typing import Optional
import repository
from pydantic import BaseModel

router = APIRouter()


class Service(BaseModel):
    service_id: Optional[int] = None
    service_name: str
    price: float


@router.get("/service/")
async def services_list(filter_name: str = "", token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    query = "SELECT * FROM services "
    if filter_name != "":
        query = query + " WHERE position(upper(%s) in upper(service_name)) > 0 "
    query = query + " ORDER BY service_name"
    cursor.execute(query, (filter_name,))
    res = []
    for row in cursor.fetchall():
        res.append({cursor.description[i][0]: value for i, value in enumerate(row)})
    return res


@router.get("/service/{service_id}")
async def service_card(service_id: int, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    query = "SELECT * FROM services WHERE service_id = %s"
    cursor.execute(query, (service_id,))
    row = cursor.fetchone()
    res = {cursor.description[i][0]: value for i, value in enumerate(row)}
    return res


@router.get("/service_price/{service_id}")
async def service_priced(service_id: int, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    query = "SELECT price FROM services WHERE service_id = %s"
    cursor.execute(query, (service_id,))
    row = cursor.fetchone()
    res = {cursor.description[i][0]: value for i, value in enumerate(row)}
    return res["price"]


@router.post("/service/")
async def service_insert_update(item: Service, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    if item.service_id is None or item.service_id == 0:
        query = "INSERT INTO services (service_name, price) VALUES (%s, %s)"
        cursor.execute(query, (item.service_name, item.price,))
    else:
        query = "UPDATE services SET service_name = %s, price = %s WHERE service_id = %s"
        cursor.execute(query, (item.service_name, item.price, item.service_id,))
    return


@router.delete("/service/{service_id}")
async def service_delete(service_id: int, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    query = "DELETE from services WHERE service_id = %s"
    cursor.execute(query, (service_id,))
    return
