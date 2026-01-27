FROM python:3.11-slim

# Activăm depozitele non-free pentru unrar
RUN sed -i 's/main/main contrib non-free non-free-firmware/g' /etc/apt/sources.list.d/debian.sources || \
    sed -i 's/main/main contrib non-free/g' /etc/apt/sources.list

RUN apt-get update && \
    apt-get install -y p7zip-full p7zip-rar jq && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiem separat modulele și scriptul principal
COPY subsro /app/subsro
COPY main.py /app/main.py
COPY run.sh /app/run.sh

RUN mkdir -p /data && chmod 777 /data

RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]