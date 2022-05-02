import datetime
from fastapi import APIRouter
from fastapi import HTTPException, Header
from typing import Optional, List
import repository
from pydantic import BaseModel

router = APIRouter()


class OrderService(BaseModel):
    order_id: Optional[int] = None
    order_line: Optional[int] = None
    service_id: Optional[int] = None
    quantity: Optional[float] = 0
    price: Optional[float] = 0


class OrderMaterials(BaseModel):
    order_id: Optional[int] = None
    order_line: Optional[int] = None
    material_id: Optional[int] = None
    quantity: Optional[float] = 0


class OrderStaffers(BaseModel):
    order_id: Optional[int] = None
    order_line: Optional[int] = None
    staffer_id: Optional[int] = None
    ktu: Optional[int] = 0


class Order(BaseModel):
    order_id: Optional[int] = None
    order_date: datetime.datetime
    car: Optional[str] = ""
    card_number: Optional[str] = ""
    percent_off: Optional[int] = 0
    total: Optional[float] = 0
    discounted_total: Optional[float] = 0
    order_services: Optional[List[OrderService]] = []
    order_materials: Optional[List[OrderMaterials]] = []
    order_staffers: Optional[List[OrderStaffers]] = []


@router.get("/order/")
async def orders_list(card_number: str = "", begin_date: str = "", end_date: str = "",
                      token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()

    par = []
    query = """SELECT o.*,
                    max(d.customer_telephone) AS customer_telephone,
                    count(s.order_line) AS order_lines,
                    coalesce(sum(round(s.price * s.quantity,2)),0) AS total,
                    coalesce(sum(round(s.price * s.quantity * (100 - o.percent_off) /100,2)),0) AS discounted_total
                FROM orders o
                LEFT OUTER JOIN discount_cards d ON o.card_number = d.card_number
                LEFT OUTER JOIN order_services s ON o.order_id = s.order_id
                WHERE true """

    if card_number != "":
        query = query + " AND o.card_number = %s "
        par.append(card_number)

    if begin_date != "":
        query = query + " AND date(o.order_date) >= date(%s) "
        par.append(begin_date)

    if end_date != "":
        query = query + " AND date(o.order_date) <= date(%s) "
        par.append(end_date)

    query = query + " GROUP BY o.order_id, o.order_date ORDER BY order_date"
    cursor.execute(query, par)
    res = [
        {cursor.description[i][0]: value for i, value in enumerate(row)}
        for row in cursor.fetchall()
    ]
    return res


@router.get("/order/{order_id}")
async def order_card(order_id: int, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()

    # шапка
    query = "SELECT o.* FROM orders o WHERE o.order_id = %s"
    cursor.execute(query, (order_id,))
    row = cursor.fetchone()
    res = {cursor.description[i][0]: value for i, value in enumerate(row)}

    # услуги
    query = """SELECT o.*, s.service_name, coalesce(round(o.price * o.quantity,2),0) AS sum 
            FROM order_services o 
            LEFT OUTER JOIN services s ON o.service_id = s.service_id
            WHERE o.order_id = %s 
            ORDER BY o.order_line"""
    cursor.execute(query, (order_id,))
    order_services = [
        {cursor.description[i][0]: value for i, value in enumerate(row)}
        for row in cursor.fetchall()
    ]
    res["order_services"] = order_services

    # материалы
    query = """SELECT o.*, s.material_name 
            FROM order_materials o 
            LEFT OUTER JOIN materials s ON o.material_id = s.material_id
            WHERE o.order_id = %s 
            ORDER BY o.order_line"""
    cursor.execute(query, (order_id,))
    order_materials = [
        {cursor.description[i][0]: value for i, value in enumerate(row)}
        for row in cursor.fetchall()
    ]
    res["order_materials"] = order_materials

    # ремонтники
    query = """SELECT o.*, s.staffer_name 
            FROM order_staffers o 
            LEFT OUTER JOIN staffers s ON o.staffer_id = s.staffer_id
            WHERE o.order_id = %s 
            ORDER BY o.order_line"""
    cursor.execute(query, (order_id,))
    order_staffers = [
        {cursor.description[i][0]: value for i, value in enumerate(row)}
        for row in cursor.fetchall()
    ]
    res["order_staffers"] = order_staffers

    return res


@router.post("/order/")
async def purchase_insert_update(item: Order, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    if item.order_id is None or item.order_id == 0:
        query = "INSERT INTO orders (order_date, car, card_number, percent_off) VALUES (%s, %s, %s, %s) RETURNING order_id"
        cursor.execute(query, (item.order_date, item.car, item.card_number, item.percent_off))
        order_id = cursor.fetchone()[0]
    else:
        query = "UPDATE orders SET order_date = %s, car = %s, card_number = %s, percent_off = %s WHERE order_id = %s"
        cursor.execute(query, (item.order_date, item.car, item.card_number, item.percent_off, item.order_id))
        order_id = item.order_id
        query = "DELETE from order_services WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        query = "DELETE from order_materials WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        query = "DELETE from order_staffers WHERE order_id = %s"
        cursor.execute(query, (order_id,))

    # услуги
    if len(item.order_services) > 0:
        for x in item.order_services:
            x.order_id = order_id
        args_str = ','.join(cursor.mogrify("(%s,%s,%s,%s,%s)", (x.order_id, x.order_line, x.service_id, x.price, x.quantity,)).decode('utf-8') for x in item.order_services)
        cursor.execute("INSERT INTO order_services (order_id, order_line, service_id, price, quantity)  VALUES " + args_str)

    # материалы
    if len(item.order_materials) > 0:
        for x in item.order_materials:
            x.order_id = order_id
        args_str = ','.join(cursor.mogrify("(%s,%s,%s,%s)", (x.order_id, x.order_line, x.material_id, x.quantity,)).decode('utf-8') for x in item.order_materials)
        cursor.execute("INSERT INTO order_materials (order_id, order_line, material_id, quantity)  VALUES " + args_str)

    # ремонтники
    if len(item.order_staffers) > 0:
        for x in item.order_staffers:
            x.order_id = order_id
        args_str = ','.join(cursor.mogrify("(%s,%s,%s,%s)", (x.order_id, x.order_line, x.staffer_id, x.ktu,)).decode('utf-8') for x in item.order_staffers)
        cursor.execute("INSERT INTO order_staffers (order_id, order_line, staffer_id, ktu)  VALUES " + args_str)
    return


@router.delete("/order/{order_id}")
async def purchase_delete(order_id: int, token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    query = "DELETE from orders WHERE order_id = %s"
    cursor.execute(query, (order_id,))
    return
