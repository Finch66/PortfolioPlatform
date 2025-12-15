FROM python:3.11-slim

# 1. Evita bytecode inutili
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 2. Directory di lavoro
WORKDIR /app

# 3. Dipendenze di sistema minime
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. Copia dipendenze Python
COPY pyproject.toml .

# 5. Installa dipendenze
RUN pip install --upgrade pip \
    && pip install .

# 6. Copia codice applicativo
COPY app ./app

# 7. Comando di avvio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
