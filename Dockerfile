FROM python:3.12-alpine

WORKDIR /app

RUN adduser -D -u 99 -G users app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

USER 99:100

CMD ["python", "-u", "main.py"]
