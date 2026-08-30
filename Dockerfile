# Deadbolt — reprodução em ambiente limpo, SEM chave de API.
#
#   docker build -t deadbolt .
#   docker run --rm deadbolt
#
# O comando padrão produz a tabela final lendo o ground truth congelado e as
# gravações em recordings/. Nenhuma chamada de rede, nenhuma credencial.
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends make git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# dependências do corpus: necessárias apenas para REGERAR o ground truth
# (`make ground-truth`), o que o juiz pode fazer para conferir os 216/170/46.
RUN pip install --no-cache-dir "mutmut==3.7.0" "pytest>=8" "text-unidecode>=1.3"

COPY . /app
ENV PY=python DEADBOLT_MODE=replay PYTHONPATH=/app/src

CMD ["make", "all", "PY=python"]
