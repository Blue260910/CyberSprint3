# Usa uma imagem base oficial do Python
FROM python:3.9-slim

# CORREÇÃO: Cria um usuário não-root para o aplicativo
RUN groupadd --gid 1000 appgroup && useradd --uid 1000 --gid appgroup --shell /bin/false --create-home appuser

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos de dependência e os instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação para o container
COPY . .

# Expõe a porta que a aplicação vai rodar
EXPOSE 8080

# Troca para o usuário não-root antes de rodar a aplicação
USER appuser

# Comando para rodar a aplicação usando Gunicorn, que é um servidor de produção
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
