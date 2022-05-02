from fastapi import APIRouter
from fastapi import HTTPException, Header
from typing import Optional
import repository
from pydantic import BaseModel

router = APIRouter()


class DiscountCard(BaseModel):
    card_number: str
    customer_name: str
    customer_telephone: str
    percent_off: int


@router.get("/discount_card/")
async def discount_cards_list(token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    query = "SELECT * FROM discount_cards ORDER BY card_number"
    cursor.execute(query)
    res = []
    for row in cursor.fetchall():
        res.append({cursor.description[i][0]: value for i, value in enumerate(row)})
    return res


@router.get("/discount_card/{card_number}")
async def discount_card(card_number: str, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    query = "SELECT * FROM discount_cards WHERE card_number = %s"
    cursor.execute(query, (card_number,))
    row = cursor.fetchone()
    res = {cursor.description[i][0]: value for i, value in enumerate(row)}
    return res


@router.get("/discount_card_percent/{card_number}")
async def discount_card(card_number: str, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    query = "SELECT percent_off FROM discount_cards WHERE card_number = %s"
    cursor.execute(query, (card_number,))
    row = cursor.fetchone()
    res = {cursor.description[i][0]: value for i, value in enumerate(row)}
    return res["percent_off"]


@router.post("/discount_card/")
async def discount_card_insert(item: DiscountCard, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    query = "INSERT INTO discount_cards (card_number, customer_name, customer_telephone, percent_off) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (item.card_number, item.customer_name, item.customer_telephone, item.percent_off,))
    return


@router.put("/discount_card/")
async def discount_card_update(item: DiscountCard, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    query = "UPDATE discount_cards SET customer_name = %s, customer_telephone = %s, percent_off = %s WHERE card_number = %s"
    cursor.execute(query, (item.customer_name, item.customer_telephone, item.percent_off, item.card_number,))
    return


@router.delete("/discount_card/{card_number}")
async def discount_card_delete(card_number: str, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    query = "DELETE from discount_cards WHERE card_number = %s"
    cursor.execute(query, (card_number,))
    return
