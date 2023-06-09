FROM python:3.9-slim AS compile-image

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ARG UID=1000
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y build-essential gcc default-libmysqlclient-dev && \
    useradd -m -r -u ${UID} user && \
    chown user requirements.txt 

USER user

RUN pip3 install --user --upgrade pip && \
    pip3 install --user -r requirements.txt

# ---------------------------------
FROM python:3.9-slim AS build-image

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ARG UID=1000

WORKDIR /src/app

RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev && \
    useradd -m -r -u ${UID} user && \
    mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media && \
    chown -R user /vol && \
    chmod -R 755 /vol/web

USER user

COPY --from=compile-image /home/user/.local /home/user/.local

ENV PATH=/home/user/.local/bin:$PATH

COPY . .

CMD ["sh", "./scripts/entrypoint.sh"]
