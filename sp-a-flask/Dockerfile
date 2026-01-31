# Imagem base leve do Python
FROM python:3.9-slim

# Pasta de trabalho dentro do container
WORKDIR /app

# Instalar dependências do sistema necessárias para compilar bibliotecas (opcional, mas bom pra garantir)
RUN apt-get update && apt-get install -y gcc libffi-dev && rm -rf /var/lib/apt/lists/*

# Copiar dependências e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Expor a porta 5000
EXPOSE 5000

# Rodar o app
CMD ["python", "app.py"]