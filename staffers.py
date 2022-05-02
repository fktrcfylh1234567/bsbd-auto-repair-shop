from datetime import datetime
from fastapi import APIRouter
from fastapi import HTTPException, Header
from typing import Optional
import repository
from uuid import uuid4
from pydantic import BaseModel

router = APIRouter()


class Staffer(BaseModel):
    staffer_id: Optional[int] = None
    staffer_name: str
    role: str
    login: str
    password: str


@router.get("/auth/")
async def auth(login: str, password: str):
    if login == "" or password == "":
        raise HTTPException(status_code=401, detail="Missing username or password")
    cursor = repository.connection.cursor()
    query = "SELECT staffer_id, role from staffers where login = %s and password = %s"
    cursor.execute(query, (login, password,))
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    res = {cursor.description[i][0]: value for i, value in enumerate(row)}
    rand_token = str(uuid4())
    res["token"] = rand_token
    repository.users[rand_token] = {'staffer_id': row[0], 'role': row[1], 'sync': datetime.now()}
    print(repository.users)
    return res


@router.get("/staffer/")
async def staffers_list(role: str = "", token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    query = "SELECT staffer_id, staffer_name, role, login FROM staffers "
    if role != "":
        query = query + " WHERE role = %s "
    query = query + "ORDER BY staffer_name"
    cursor.execute(query, (role,))
    res = []
    for row in cursor.fetchall():
        res.append({cursor.description[i][0]: value for i, value in enumerate(row)})
    return res


@router.get("/staffer/{staffer_id}")
async def staffer_card(staffer_id: int, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    query = "SELECT staffer_id, staffer_name, role, login, password FROM staffers WHERE staffer_id = %s"
    cursor.execute(query, (staffer_id,))
    row = cursor.fetchone()
    res = {cursor.description[i][0]: value for i, value in enumerate(row)}
    return res


@router.post("/staffer/")
async def staffer_insert_update(item: Staffer, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    if item.staffer_id is None or item.staffer_id == 0:
        query = "INSERT INTO staffers (staffer_name, role, login, password) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (item.staffer_name, item.role, item.login, item.password,))
    else:
        query = "UPDATE staffers SET staffer_name = %s, role = %s, login = %s, password = %s WHERE staffer_id = %s"
        cursor.execute(query, (item.staffer_name, item.role, item.login, item.password, item.staffer_id,))
    return


@router.delete("/staffer/{staffer_id}")
async def staffer_delete(staffer_id: int, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    query = "DELETE from staffers WHERE staffer_id = %s"
    cursor.execute(query, (staffer_id,))
    return
