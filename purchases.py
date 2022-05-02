import datetime
from fastapi import APIRouter
from fastapi import HTTPException, Header
from typing import Optional
import repository
from pydantic import BaseModel

router = APIRouter()


class Purchase(BaseModel):
    purchase_id: Optional[int] = None
    purchase_date: datetime.datetime
    trader: Optional[str] = ""
    material_id: int
    price: float
    quantity: float
    sum: float


@router.get("/purchase/")
async def purchases_list(material_id: int = 0, begin_date: str = "", end_date: str = "", token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()

    par = []
    query = "SELECT p.*, m.*, round(p.price * p.quantity,2) AS sum FROM purchases p LEFT OUTER JOIN materials m ON p.material_id = m.material_id WHERE true "

    if material_id != 0:
        query = query + " AND p.material_id = %s "
        par.append(material_id)

    if begin_date != "":
        query = query + " AND date(p.purchase_date) >= date(%s) "
        par.append(begin_date)

    if end_date != "":
        query = query + " AND date(p.purchase_date) <= date(%s) "
        par.append(end_date)

    query = query + " ORDER BY purchase_date"
    cursor.execute(query, par)
    res = []
    for row in cursor.fetchall():
        res.append({cursor.description[i][0]: value for i, value in enumerate(row)})
    return res


@router.get("/purchase/{purchase_id}")
async def purchase_card(purchase_id: int, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    query = "SELECT p.*, m.*, round(p.price * p.quantity,2) AS sum FROM purchases p LEFT OUTER JOIN materials m ON p.material_id = m.material_id WHERE p.purchase_id = %s"
    cursor.execute(query, (purchase_id,))
    row = cursor.fetchone()
    res = {cursor.description[i][0]: value for i, value in enumerate(row)}
    return res


@router.post("/purchase/")
async def purchase_insert_update(item: Purchase, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    if item.purchase_id is None or item.purchase_id == 0:
        query = "INSERT INTO purchases (purchase_date, trader, material_id, price, quantity) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (item.purchase_date, item.trader, item.material_id, item.price, item.quantity))
    else:
        query = "UPDATE purchases SET purchase_date = %s, trader = %s, material_id = %s, price = %s, quantity = %s WHERE purchase_id = %s"
        cursor.execute(query, (item.purchase_date, item.trader, item.material_id, item.price, item.quantity, item.purchase_id,))
    return


@router.delete("/purchase/{purchase_id}")
async def purchase_delete(purchase_id: int, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    query = "DELETE from purchases WHERE purchase_id = %s"
    cursor.execute(query, (purchase_id,))
    return
