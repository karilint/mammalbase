############################
# Compile stage
############################
FROM python:3.11-slim AS compile-image

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ARG UID=1000

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libffi-dev \
        python3-dev \
        default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -r -u ${UID} user \
    && chown user requirements.txt

USER user

RUN pip3 install --user --upgrade pip && \
    pip3 install --user -r requirements.txt


############################
# Runtime stage
############################
FROM python:3.11-slim AS build-image

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ARG UID=1000

WORKDIR /src/app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -r -u ${UID} user \
    && mkdir -p /vol/web/static \
    && mkdir -p /vol/web/media \
    && chown -R user /vol \
    && chmod -R 755 /vol/web

USER user

COPY --from=compile-image /home/user/.local /home/user/.local

ENV PATH=/home/user/.local/bin:$PATH

COPY . .

CMD ["sh", "./scripts/entrypoint.sh"]
