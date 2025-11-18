FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin SELURUH folder proyek ke dalam container
COPY . .

# Buat folder laporan
RUN mkdir -p /app/reports

ENTRYPOINT ["python", "scanner_v7.py"]