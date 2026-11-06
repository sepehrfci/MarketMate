FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt ./requirements.txt
ARG PIP_INDEX_URL=https://pypi.org/simple
RUN pip install --index-url "$PIP_INDEX_URL" --no-cache-dir -r requirements.txt

COPY app ./app

ENV APP_NAME=MarketMate
ENV APP_ENV=development

RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
