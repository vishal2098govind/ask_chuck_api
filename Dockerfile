FROM python:3.11.2

WORKDIR /app

COPY . /app

ENV HOST=0.0.0.0

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["fastapi", "run", "./ask_chuck_api/main.py", "--port", "8080"]