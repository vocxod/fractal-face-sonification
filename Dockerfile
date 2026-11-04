FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

# 1. Устанавливаем базовые утилиты и репозиторий deadsnakes
RUN apt-get update && apt-get install -y \
    software-properties-common \
    gpg-agent \
    ca-certificates \
    curl \
    && add-apt-repository ppa:deadsnakes/ppa -y \
    && apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3.11-distutils \
    ffmpeg \
    libsm6 \
    libxext6 \
    git \
    && rm -rf /var/lib/apt/lists/*

# 2. Настраиваем альтернативы для python3 и устанавливаем актуальный pip
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && curl -sS https://bootstrap.pypa.io/get-pip.py | python3

WORKDIR /workspace

# 3. Копируем файл зависимостей и ставим их
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# 4. Копируем остальные файлы проекта
COPY . .

EXPOSE 8501
EXPOSE 8000

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
