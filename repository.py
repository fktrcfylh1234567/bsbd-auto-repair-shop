import psycopg2
from datetime import datetime

connection = psycopg2.connect(dbname='auto_repair_shop', user='postgres', password='mysecretpassword', host='localhost')
connection.autocommit = True
print("Connected to the database")

users = {}


def check_token(token):
    value = users.get(token)
    if value is None:
        return False
    users[token]['sync'] = datetime.now()
    return True
