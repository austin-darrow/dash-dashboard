FROM python:3.11-slim

RUN apt-get update && apt-get upgrade -y

COPY requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /app

COPY . .

EXPOSE 8050

CMD ["python", "app.py"]