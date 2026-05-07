FROM python:3.11-bookworm

WORKDIR /app

COPY pyproject.toml .
RUN pip install uv && uv pip install .

COPY app ./app

CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
