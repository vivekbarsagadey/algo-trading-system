FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Use the wrapper script `uv` so the command is consistent with local usage
CMD ["./uv"]
