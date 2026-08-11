FROM python:3.13-slim
WORKDIR app/
COPY . .

RUN pip install .

EXPOSE 8000
CMD uvicorn --host 0.0.0.0 src.app:app
