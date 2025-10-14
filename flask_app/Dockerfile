# /proyek-forwarding-docker/flask_app/Dockerfile

# Gunakan base image Python yang ringan
FROM python:3.9-slim

# Set working directory di dalam container
WORKDIR /app

# ❗️PENTING: Install socat di dalam container
# Aplikasi kita butuh 'socat' untuk melakukan port forwarding
RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*

# Copy file requirements dan install library Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file dari folder flask_app ke dalam container
COPY . .

# Perintah untuk menjalankan aplikasi saat container start
# Gunicorn adalah WSGI server yang lebih production-ready daripada server bawaan Flask
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]