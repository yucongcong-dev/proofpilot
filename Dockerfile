FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8080
CMD ["sh", "-c", "python3 -c 'import os; from web import ThreadingHTTPServer, Handler; ThreadingHTTPServer((\"0.0.0.0\", int(os.environ.get(\"PORT\", \"8080\"))), Handler).serve_forever()'"]
