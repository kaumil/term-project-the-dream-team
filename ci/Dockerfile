FROM quay.io/bitnami/python:3.8.6-prod-debian-10-r81

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ci_test.py create_tables.py users.py images.py transaction.py logger.py ./

CMD ["python", "ci_test.py", "users", "30000", "images", "30001", "transaction", "30002", "logger", "30003"]
