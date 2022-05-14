#### Инструкция по запуску:

1. Для запуска образа с базой данных необходимо запустить в терминале следующую команду:
```bash
docker run --name some-mysql -e MYSQL_ROOT_PASSWORD=mysecretpassword -d mysql:latest
```

2. После создания новой БД необходимо создать требуемые таблицы, при помощи находящегося в проекте скрипта:
```bash
python3 create_tables.py 
```

3. Перед запуском сервиса, необходимо установить требуемые pip-пакеты:
```bash
pip3 install -r requirements.txt
```

3. Запуск сервиса осуществляется командой:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

4. Для просмотра документации к API сервиса можно перейти по ссылке:
http://0.0.0.0:8000/docs

