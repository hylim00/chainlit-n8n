# Gunakan Python slim agar image kecil
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy file requirements dan install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh project
COPY . .

# Expose port default Chainlit
EXPOSE 8000

# Jalankan Chainlit
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000", "-h"]
