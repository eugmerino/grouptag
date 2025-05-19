# Dockerfile

FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /workspace

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos necesarios
COPY requirements.txt .

# Instala dependencias de Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia el resto del proyecto
COPY . .

# Expone el puerto donde correrá Django
EXPOSE 8000

# Comando por defecto
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]