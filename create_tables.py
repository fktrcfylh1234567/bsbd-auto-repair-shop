import psycopg2


def create_db():
    connection = psycopg2.connect(dbname='postgres', user='postgres', password='mysecretpassword', host='localhost')
    connection.autocommit = True
    cursor = connection.cursor()
    cursor.execute('DROP DATABASE auto_repair_shop')
    cursor.execute('CREATE DATABASE auto_repair_shop')
    cursor.close()
    connection.close()


def create_tables():
    connection = psycopg2.connect(dbname='auto_repair_shop', user='postgres', password='mysecretpassword', host='localhost')
    connection.autocommit = True
    cursor = connection.cursor()

    query = """CREATE TABLE IF NOT EXISTS staffers (
        staffer_id serial PRIMARY KEY,
        staffer_name varchar,
        role varchar,
        login varchar,
        password varchar)"""
    cursor.execute(query)

    query = """CREATE TABLE IF NOT EXISTS discount_cards (
        card_number varchar PRIMARY KEY,
        customer_name varchar,
        customer_telephone varchar,
        percent_off integer)"""
    cursor.execute(query)

    query = """CREATE TABLE IF NOT EXISTS services (
        service_id serial PRIMARY KEY,
        service_name varchar NOT NULL,
        price numeric(10,2))"""
    cursor.execute(query)

    query = """CREATE TABLE IF NOT EXISTS materials (
        material_id serial PRIMARY KEY,
        material_name varchar NOT NULL,
        part boolean,
        measure varchar,
        article varchar)"""
    cursor.execute(query)

    query = """CREATE TABLE IF NOT EXISTS orders (
        order_id serial PRIMARY KEY,
        order_date timestamp NOT NULL,
        car varchar,
        card_number varchar,
        percent_off integer"""
    cursor.execute(query)

    query = """CREATE TABLE IF NOT EXISTS order_services (
        order_id integer NOT NULL REFERENCES orders ON DELETE CASCADE,
        order_line integer NOT NULL,
        service_id integer NOT NULL REFERENCES services ON DELETE RESTRICT,
        price numeric(10,2),
        quantity numeric(10,2)"""
    cursor.execute(query)

    query = """CREATE TABLE IF NOT EXISTS order_materials (
        order_id integer NOT NULL REFERENCES orders ON DELETE CASCADE,
        order_line integer NOT NULL,
        material_id integer NOT NULL REFERENCES materials ON DELETE RESTRICT,
        quantity numeric(10,2))"""
    cursor.execute(query)

    query = """CREATE TABLE IF NOT EXISTS order_staffers (
        order_id integer NOT NULL REFERENCES orders ON DELETE CASCADE,
        order_line integer NOT NULL,
        staffer_id integer NOT NULL REFERENCES staffers ON DELETE RESTRICT,
        ktu integer)"""
    cursor.execute(query)

    query = """CREATE TABLE IF NOT EXISTS purchases (
        purchase_id serial PRIMARY KEY,
        purchase_date timestamp NOT NULL,
        trader varchar,
        material_id integer NOT NULL REFERENCES materials ON DELETE RESTRICT,
        price numeric(10,2),
        quantity numeric(10,2),
        sum numeric(10,2))"""
    cursor.execute(query)

    cursor.execute("""INSERT INTO staffers (staffer_name, role, login, password) VALUES ('Администратор', 'manager', 'admin', '1234')""")
    cursor.execute("""SELECT * FROM staffers""")
    print("staffers =", cursor.fetchall())

    cursor.close()
    connection.close()


if __name__ == "__main__":
    # create_db()
    # create_tables()
    print("Done!")

