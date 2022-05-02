from fastapi import APIRouter
from fastapi import HTTPException, Header
from typing import Optional
import repository

router = APIRouter()

# *** Отчет по выполненным работам

@router.get("/executed_works/")
async def executed_works(begin_date: str = "", end_date: str = "", token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()
    par = []
    query = """SELECT coalesce(sum(round(s.price * s.quantity,2)),0) AS sum,
           count(o.order_id) AS orders,
           avg(o.percent_off) AS average_percent_off,
           max(o.percent_off) AS max_percent_off,
           r.service_name,
           string_agg(distinct o.order_id::varchar,',') AS order_ids,
           coalesce(sum(round(s.price * s.quantity * (100 - o.percent_off) /100,2)),0) AS discount_sum
        FROM order_services s
        LEFT OUTER JOIN orders o ON o.order_id = s.order_id
        LEFT OUTER JOIN services r ON s.service_id = r.service_id
        WHERE true"""

    if begin_date != "":
        query = query + " AND date(o.order_date) >= date(%s) "
        par.append(begin_date)

    if end_date != "":
        query = query + " AND date(o.order_date) <= date(%s) "
        par.append(end_date)

    query = query + " GROUP BY r.service_name ORDER BY r.service_name"
    cursor.execute(query, par)
    res = [
        {cursor.description[i][0]: value for i, value in enumerate(row)}
        for row in cursor.fetchall()
    ]
    print(res)
    return res


# *** Ведомость по материалам

@router.get("/materials_using/")
async def materials_using(is_available: bool = False, begin_date: str = "", end_date: str = "", token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()

    query = """WITH incoming_begin AS
         (SELECT material_id, SUM(quantity) AS incoming_sum_begin
          FROM purchases
          WHERE date(purchase_date) < date(%(d1)s)
          GROUP BY material_id),
     outgoing_begin AS
         (SELECT om.material_id, SUM(om.quantity) AS outgoing_sum_begin
          FROM order_materials om
                   INNER JOIN orders o2 on om.order_id = o2.order_id
          WHERE date(o2.order_date) < date(%(d1)s)
          GROUP BY om.material_id),
     incoming AS
         (SELECT material_id,
                 SUM(quantity)                                  AS incoming_sum,
                 string_agg(distinct purchase_id::varchar, ',') AS purchase_ids
          FROM purchases
          WHERE date(purchase_date) BETWEEN date(%(d1)s) AND date(%(d2)s)
          GROUP BY material_id),
     outgoing AS
         (SELECT om.material_id,
                 SUM(om.quantity)                               AS outgoing_sum,
                 string_agg(distinct om.order_id::varchar, ',') AS order_ids
          FROM order_materials om
                   INNER JOIN orders o2 on om.order_id = o2.order_id
          WHERE date(o2.order_date) BETWEEN date(%(d1)s) AND date(%(d2)s)
          GROUP BY om.material_id)
    SELECT m.material_name,
           i.purchase_ids,
           o.order_ids,
           coalesce(i_b.incoming_sum_begin, 0)                                       AS incoming_sum_begin,
           coalesce(o_b.outgoing_sum_begin, 0)                                       AS outgoing_sum_begin,
           coalesce(i_b.incoming_sum_begin, 0) - coalesce(o_b.outgoing_sum_begin, 0) AS balance_begin,
           coalesce(i.incoming_sum, 0)                                               AS incoming_sum,
           coalesce(o.outgoing_sum, 0)                                               AS outgoing_sum,
           coalesce(i_b.incoming_sum_begin, 0) - coalesce(o_b.outgoing_sum_begin, 0) + coalesce(i.incoming_sum, 0) -
           coalesce(o.outgoing_sum, 0)                                               AS balance_end
    FROM materials m
             FULL JOIN incoming_begin i_b on m.material_id = i_b.material_id
             FULL JOIN outgoing_begin o_b on m.material_id = o_b.material_id
             FULL JOIN incoming i on m.material_id = i.material_id
             FULL JOIN outgoing o on m.material_id = o.material_id
    WHERE %(all)s
       OR coalesce(i_b.incoming_sum_begin, 0) - coalesce(o_b.outgoing_sum_begin, 0) + coalesce(i.incoming_sum, 0) -
          coalesce(o.outgoing_sum, 0) > 0
    ORDER BY m.material_name"""

    cursor.execute(query, {'d1': begin_date, 'd2': end_date, 'all': not is_available})
    res = [
        {cursor.description[i][0]: value for i, value in enumerate(row)}
        for row in cursor.fetchall()
    ]
    print(res)
    return res


# *** Зарплата ремонтников

@router.get("/salary/")
async def salary(coeff: int = 0, begin_date: str = "", end_date: str = "", token: Optional[str] = Header(None)):
    if token is None or not repository.check_token(token):
        raise HTTPException(status_code=401, detail="Token missing or incorrect")
    cursor = repository.connection.cursor()

    query = """WITH orders_sum AS
             (SELECT o.order_id, SUM(round(sr.quantity * sr.price, 2)) AS orders_sum
              FROM order_services sr
                       INNER JOIN orders o ON o.order_id = sr.order_id
              WHERE date(o.order_date) BETWEEN date(%(d1)s) AND date(%(d2)s)
              GROUP BY o.order_id),
         orders_staff AS
             (SELECT st.order_id,
                     st.staffer_id,
                 st.ktu,
                 coalesce(sm.orders_sum, 0) AS orders_sum,
                     round(st.ktu * %(coeff)s * coalesce(sm.orders_sum, 0) / 10000, 2) AS zp
              FROM order_staffers st
                       INNER JOIN orders o ON o.order_id = st.order_id
                       LEFT OUTER JOIN orders_sum sm ON st.order_id = sm.order_id
              WHERE date(o.order_date) BETWEEN date(%(d1)s) AND date(%(d2)s)
             )
    SELECT st.order_id, st.staffer_id, st.ktu, st.zp, st.orders_sum, '' AS staffer_name
    FROM orders_staff st
    UNION
    SELECT 0, st.staffer_id, round(AVG(st.ktu),2), SUM(st.zp), SUM(st.orders_sum), MAX(s.staffer_name)
    FROM orders_staff st
             INNER JOIN staffers s ON st.staffer_id = s.staffer_id
    GROUP BY st.staffer_id
    ORDER BY staffer_id, order_id"""

    cursor.execute(query, {'d1': begin_date, 'd2': end_date, 'coeff': coeff})
    res = [
        {cursor.description[i][0]: value for i, value in enumerate(row)}
        for row in cursor.fetchall()
    ]
    print(res)
    return res
