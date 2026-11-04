FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libxcb1 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libgl1 \
    libglib2.0-0 \
    fluidsynth \
    ffmpeg \
    soundfont-fluid \
    && rm -rf /var/lib/apt/lists/

# Объявляем аргументы сборки (по умолчанию 1000, если не переданы)
ARG USER_ID=1000
ARG GROUP_ID=1000

# Создаем группу и пользователя с ТОЧНЫМИ ID вашего хоста
RUN groupadd -g ${GROUP_ID} testman && \
    useradd -l -u ${USER_ID} -g testman -m -s /bin/bash testman

WORKDIR /home/testman

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R testman:testman /home/testman

USER testman

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]


