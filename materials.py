from fastapi import APIRouter
from fastapi import HTTPException, Header
from typing import Optional
import repository
from pydantic import BaseModel

router = APIRouter()


class Material(BaseModel):
    material_id: Optional[int] = None
    material_name: str
    part: bool
    measure: str
    article: str


@router.get("/material/")
async def materials_list(filter_name: str = "", filter_part: Optional[bool] = None, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    par = []
    query = "SELECT * FROM materials WHERE true "
    if filter_name != "":
        query = query + " AND position(upper(%s) in upper(material_name)) > 0 "
        par.append(filter_name)
    if filter_part is not None:
        query = query + " AND part = %s "
        par.append(filter_part)
    query = query + " ORDER BY material_name"
    cursor.execute(query, par)
    res = []
    for row in cursor.fetchall():
        res.append({cursor.description[i][0]: value for i, value in enumerate(row)})
    return res


@router.get("/material/{material_id}")
async def material_card(material_id: int, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    query = "SELECT * FROM materials WHERE material_id = %s"
    cursor.execute(query, (material_id,))
    row = cursor.fetchone()
    res = {cursor.description[i][0]: value for i, value in enumerate(row)}
    return res


@router.post("/material/")
async def material_insert_update(item: Material, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    if item.material_id is None or item.material_id == 0:
        query = "INSERT INTO materials (material_name, part, measure, article) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (item.material_name, item.part, item.measure, item.article,))
    else:
        query = "UPDATE materials SET material_name = %s, part = %s, measure = %s, article = %s WHERE material_id = %s"
        cursor.execute(query, (item.material_name, item.part, item.measure, item.article, item.material_id,))
    return


@router.delete("/material/{material_id}")
async def material_delete(material_id: int, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    query = "DELETE from materials WHERE material_id = %s"
    cursor.execute(query, (material_id,))
    return
